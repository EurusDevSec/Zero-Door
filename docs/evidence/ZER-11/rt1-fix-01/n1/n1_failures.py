"""For every failing test in N1 runs: the largest archive append+fsync, gateway submit and client deliver
times inside that test, and the failure line, so a failure can be matched (or not) to a host I/O stall."""
import json, re, sys
from pathlib import Path
out = []
for d in map(Path, sys.argv[1:]):
    for log in sorted(d.glob("*.log")):
        text = log.read_text(errors="replace")
        fails = re.findall(r"^(FAIL|ERROR): (\w+) \([\w.]+\.(\w+)\.\w+\)", text, re.M)
        if not fails:
            continue
        rows = [json.loads(l) for l in log.with_suffix(".jsonl").read_text().splitlines() if l.strip()]
        for kind, method, cls in fails:
            test = f"{cls}.{method}"
            mine = [r for r in rows if r.get("test") == test]
            block = text.split(f"{kind}: {method}", 1)[1].split("\n======", 1)[0]
            msg = next((l.strip() for l in block.splitlines() if l.strip().startswith(("AssertionError", "KeyError", "Error"))), "")
            mx = lambda k: max((r["ms"] for r in mine if r["kind"] == k), default=None)
            out.append({"run": f"{d.name}/{log.stem}", "test": test, "kind": kind, "message": msg[:160],
                        "max_append_fsync_ms": mx("append"), "max_submit_ms": mx("submit"), "max_deliver_ms": mx("deliver"),
                        "retries": sum(1 for r in mine if r["kind"] == "deliver" and str(r.get("outcome")).startswith("Retry"))})
print(json.dumps(out, indent=1))
