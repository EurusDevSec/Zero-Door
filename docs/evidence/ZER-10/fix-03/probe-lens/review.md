# Final independent probe lens — fix-03

Verdict CLEAR for the scoped code: no concrete P1/P2 remains after focused source review and replay. This is code/offline review, not runtime or Linear acceptance.

Read current files and byte snapshots of flows.py, probe.py, sink.py and clock.py; read all test_measurement_boundaries.py and the relevant ownership/CLI consumers. Did not repeat the broad suite or graph work.

Independent replay used owned 127.0.0.1 servers and temporary outboxes:
- stop_io.py/json: cap 10 s, grace 0.3 s, response delay 1.5 s, stop after 0.1 s. H ACK finishes 0.303 s after stop (0 delivered, 2 pending); reference 0.309 s (1 failed sync); active cleanup 0.315 s (GRACE_EXPIRED retained as unresolved). Fix-02 took about 1.4 s after stop. No renewed grace or late ACK acceptance.
- redirect_identity.py/json (307) and redirect_308.py/json (308): SESSION_CHANGED before following the redirect; no foreign request in the log, foreign-product retained, own cart cleanup DONE.

Root cause review:
- Flow.exchange validates the session immediately after the initial response and each followed response, before another hop. Issuance applies only while state.session is None, so a later hop cannot reissue the identity. Frozen cleanup credentials and nonce-proven targets remain independent of the mutable cookie jar.
- ProbeRunner.stop_deadline uses the earliest stop plus grace and stays callable through publisher, sink, reference and cleanup. Deadline composition retains the shared bound rather than freezing min(). Connection/TLS/send waits and body read slices re-read it. Pending outbox events are not marked DELIVERED on timeout.

Architecture, simplicity and language lens: one shared transport and two small deadline helpers keep the policy consistent across business, H and reference calls. No redundant retry layer or side channel was added. Workload cancellation remains separate from bounded cleanup completion. Python stdlib socket/ssl/select fits the existing stdlib-only package; socket closure covers failure paths. Callable deadlines are less obvious than integers, but localized helpers, docstrings and tests make the contract inspectable. Dynamic fake HTTP is not fully indexed; an empty graph result is not proof.

Remaining limits, not new blockers: synchronous OS DNS, SSL context/certificate loading and filesystem fsync may block outside interruptible I/O. Current runtime uses IP literal origins as documented; do not claim a universal process wall cap for arbitrary OS, disk or DNS failures. SIGKILL or power loss cannot clean up; journal/outbox retain what was persisted. A successful trusted TLS exchange was not independently run in this small lens; broader CI/runtime proof remains separate. No new feature requests.

Definition of Done: scoped offline code can advance. Fixture observations, live clock/ACK profile, CI, publication, merge and owner acceptance require their own evidence and authority. No lab, Docker, Kubernetes, API/model, Linear or Git writes. No product/docs/evidence edits; own scratch only. No active jobs remain.
