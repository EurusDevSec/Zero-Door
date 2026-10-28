# CI correction — PR33

First head `c676c7a3763a6770f60f138419adedb44a0d04e4` failed two jobs in [run40680244467](https://github.com/EurusDevSec/Zero-Door/actions/runs/40680244467): R1 agents loopback HTTP and production Nemesis entrypoints. The Hephaestus matrix job was canceled by fail-fast. Those failures remain recorded; no rerun of unchanged source is used to hide them.

Both failures hit `tests/test_dashboard_modes.py`: the fixture omitted the newly required `ZD_RULES_STATE_FILE`, so the consumer failed closed before its expected decision/audit; its one-tick helper also patched obsolete `time.sleep` instead of `stop.wait`. The original local affected-check selection missed this direct caller. Guard behavior was correct; caller migration was incomplete.

Fix: configure a private temp SQLite path; pass an explicit stop event and stop after its first wait; re-enter each lab's own environment. Existing B0/BM/B1/B2/B3/refusal/dedup/disabled-executor assertions are retained. The real Uvicorn fixture and RT2 actor bundle also configure the path on their existing writable volume. Only actors receive a16MiB bound; driver/console volume behavior stays unchanged. Generated build context now carries the two existing Hephaestus modules required by Docker COPY. No build/apply/deploy/PVC or lab traffic is performed.

Retest: each production dependency pin passes7 dashboard mode tests and4 real process/bundle tests (22additional test runs,171applicable total). Original149component tests and source hashes stay unchanged. New remote CI and independent delta review are still mandatory before merge. This correction does not alter AC or broaden component acceptance to deployed broker/PVC/G3.
