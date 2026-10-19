# ZER-12/40 — CI contract-fixture bootstrap

**Local clean-runner replay PASS; remote rerun required.** Parent source commit c2edee8, [PR25](https://github.com/EurusDevSec/Zero-Door/pull/25). [First CI run](https://github.com/EurusDevSec/Zero-Door/actions/runs/39291550352):14 jobs success,1 failed (contract release fixture missing),image publish skipped as intended. Go race/vet/Gosec, all5 image build/smokes and both production HTTP graphs succeeded on that head.

The sealed ZER-37 checker opens scratch/zer37/fixtures.json although its fixture is committed at docs/evidence/ZER-37/fixtures.json. Local scratch masked this path dependency. Keep all sealed checker/contract/fixture bytes unchanged; CI now explicitly copies the committed fixture into the expected scratch path before executing the same release check. No gate is skipped or loosened. Workflow regression rejects removing this bootstrap.

Exactly2 source files change: workflow and test_command_guard_ci.py. Six CI test methods pass on each production graph. A fresh git archive of c2edee8 (no inherited scratch) reproduces FileNotFoundError; after the exact mkdir/copy step, the same release script passes9 focused cases, JSON examples and links. [Results](results/clean-after.json). No source runtime change, model, lab, Docker local, Secret or Linear write.

[verify_ci.py](verify_ci.py) checks current source/evidence hashes and the preserved fix-02 chain; older source checkers correctly report drift in these2 sources. Raw logs retain whitespace. Remote status belongs to PR25; not owner acceptance/merge/Done or G1.
