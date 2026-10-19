"""Read-only current hashes and CI bootstrap evidence; no runtime/Done claim."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
m=json.loads((HERE/"delta-manifest.json").read_text())
base=ROOT/"docs/evidence/ZER-12/fix-02/delta-manifest.json"
assert hashlib.sha256(base.read_bytes()).hexdigest()==m["base_manifest_sha256"]
b=json.loads(base.read_text())
count=0
for name in ("sources","evidence","before_sources","prior_evidence","protected","unchanged_dirty"):
    entries=dict(b[name])
    if name=="sources": entries.update(m["source_overrides"])
    for path,h in entries.items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h,path
        count+=1
for name in ("evidence","before_sources"):
    for path,h in m[name].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h,path
        count+=1
before=(HERE/"results/clean-before.txt").read_text()
assert "FileNotFoundError" in before and "scratch/zer37/fixtures.json" in before
after=json.loads((HERE/"results/clean-after.json").read_text())
assert after["links"]=="PASS" and len(after["focused_cases"])==9 and all(x["passed"] for x in after["focused_cases"])
for agent in ("nemesis","hephaestus"):
    s=(HERE/("results/test-ci-"+agent+".txt")).read_text()
    assert "Ran 6 tests" in s and s.rstrip().endswith("OK")
print(json.dumps({"verdict":"PASS","hashed_checks":count,"clean_archive_replay":"PASS","limits":"CI rerun/owner acceptance are separate"}))
