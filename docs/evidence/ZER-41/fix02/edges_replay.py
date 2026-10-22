"""Adapted replay of Codex's retest01 edge probes (scratch/zer13/codex-retest01/edges.py, left untouched).

The original assumes the server keeps reading a dribbled body to the end; a fixed server cuts it at the
request budget and may close or reset early, so this copy accepts a timely 408/close and records it instead
of crashing. Loopback and temp SQLite only; offline.

    python -B docs/evidence/ZER-41/fix02/edges_replay.py <app.py> <out.json>
"""
import importlib.util
import io
import json
import os
import socket
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
APP, OUT = Path(sys.argv[1]).resolve(), Path(sys.argv[2])
SEED = ROOT / "tests/fixtures/zer41/seed.json"
spec = importlib.util.spec_from_file_location("zer41_edges_app", APP)
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)


def start():
    tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
    config = app.Config({"ZD_SQLI_DB_DIR": tmp.name, "ZD_SQLI_SEED": str(SEED), "ZD_SQLI_PORT": "0",
                         "ZD_SQLI_TOPOLOGY": "direct"})
    log = io.StringIO()
    app.LOG = log
    with redirect_stdout(log), redirect_stderr(io.StringIO()):
        httpd, *_ = app.build_server(config)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return tmp, httpd, log


def records(log):
    return [json.loads(x) for x in log.getvalue().splitlines() if x.strip()]


def exchange(port, head, trickle=b"", every=0.8, wait=12):
    """Send head, then trickle one byte per `every` seconds in the background; return the first answer."""
    sock = socket.create_connection(("127.0.0.1", port), timeout=2)
    sock.settimeout(wait)
    stop = threading.Event()

    def sender():
        for byte in trickle:
            if stop.wait(every):
                return
            try:
                sock.sendall(bytes([byte]))
            except OSError:
                return

    began = time.monotonic()
    sock.sendall(head)
    thread = threading.Thread(target=sender, daemon=True)
    thread.start()
    try:
        answer = sock.recv(65536).decode("utf-8", "replace")
    except socket.timeout:
        answer = "<no answer within %ss>" % wait
    except ConnectionResetError:
        answer = "<reset>"
    elapsed = round(time.monotonic() - began, 3)
    stop.set()
    sock.close()
    thread.join(2)
    return answer, elapsed


out = {"app": str(APP)}
tmp, httpd, log = start()
try:
    body = b'{"item":"probe","note":"owned"}'
    answer, elapsed = exchange(httpd.server_address[1], b"POST /fixture/orders HTTP/1.1\r\nHost: local\r\nContent-Length: "
                               + str(len(body)).encode() + b"\r\n\r\n", body)
    out["dribbling_body"] = {"elapsed_s": elapsed, "request_budget_s": app.REQUEST_BUDGET_S,
                             "status_line": answer.split("\r\n", 1)[0], "records": records(log)}
    before = len(records(log))
    answer, _ = exchange(httpd.server_address[1], b"TRACE /health HTTP/1.1\r\nHost: local\r\n\r\n", wait=4)
    out["unhandled_method"] = {"status_line": answer.split("\r\n", 1)[0],
                               "has_request_id": "X-Request-Id" in answer, "html": "<html" in answer.lower(),
                               "new_records": records(log)[before:]}
finally:
    httpd.shutdown()
    httpd.server_close()
    app.LOG = None
    tmp.cleanup()

with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as d:
    env = {"ZD_SQLI_DB_DIR": d, "ZD_SQLI_SEED": str(SEED), "ZD_SQLI_PORT": "0"}
    config = app.Config(env)
    with redirect_stderr(io.StringIO()):
        app.open_or_create(config)
    db = sqlite3.connect(config.db_path)
    db.execute("UPDATE meta SET value=? WHERE key='seed_id'", ("hidden-seed-canary",))
    db.commit()
    db.close()
    kept = config.db_path.read_bytes()
    clean = {k: v for k, v in os.environ.items() if not k.startswith("ZD_SQLI_")}
    result = subprocess.run([sys.executable, "-B", str(APP)], env={**clean, **env}, capture_output=True, text=True,
                            timeout=20)
    streams = result.stdout + result.stderr
    out["startup_failure_process"] = {"returncode": result.returncode, "stderr": result.stderr,
                                      "canary_on_streams": "hidden-seed-canary" in streams,
                                      "traceback_on_streams": "Traceback" in streams,
                                      "db_path_on_streams": d in streams,
                                      "db_kept": config.db_path.read_bytes() == kept}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
print(json.dumps({"dribbling_body": {k: out["dribbling_body"][k] for k in ("elapsed_s", "status_line")},
                  "unhandled_method": {k: out["unhandled_method"][k] for k in ("status_line", "has_request_id")},
                  "startup_failure": {k: v for k, v in out["startup_failure_process"].items() if k != "stderr"}}))
