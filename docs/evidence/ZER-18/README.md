## Hoàng đã duyệt publication ZER-18 — 28/10/2026

Hoàng duyệt publication và nghiệm thu component khi đủ gate; [authorization](publication-authorization.json) giữ nguyên trả lời và proposal hash. Đang publication; remote CI/merge/Done còn chờ. Không lab/deploy mới hoặc G3 PASS. Các trạng thái chờ duyệt bên dưới là checkpoint lịch sử.

# ZER-18 — consumer/retry/restart SQLi

**COMPONENT_READY_FOR_PUBLICATION_NOT_DONE — 28/10/2026.** [Live issue](https://linear.app/zero-door/issue/ZER-18/consumer-retry-va-restart-cho-djuong-sqli). Source/offline component verified; no new lab/deployment. [Verification](verification.json), [review](independent-review.md), [hashes](source-hashes.json), [preservation](preservation.json).

| AC | Expected | Evidence / actual | Boundary |
| --- | --- | --- | --- |
| AC01 | Nonblocking consumer, bounded ack/dedup/cooldown/retry; one effective worker action | 15 consumer tests each production pin; maximum3 attempts/30s and90s cooldown survive SQLite reopen. Exact receipt reconciliation, poison skips, one owner and joined shutdown. Go subprocess dispatcher/ledger shows one fake effect per command. | No enabled action executor or deployed broker proof. |
| AC03 | Restart and missing telemetry preserve partial/unknown truth | Four Python process invocations reuse exact decision/IDs, stop after three attempts withUNKNOWN. Go process restart preservesTIMEOUT orDUPLICATE_OUTCOME_UNKNOWN. 14 existing state and24 containment cases retain strict probe/TTL/timeout controls. | Component process/ledger tests. ZER-46 runtime09 remains existing fixture/writer evidence, never a run of this new consumer. |

149 Python test runs and three Go component packages pass. [Results](results/) retain final logs and initial test-fixture failures: Windows cleanup initially preceded SQLite-handle cleanup; corrected ordering. A poison fixture initially used an unconstrained severity; corrected it to unsupported schema plus five structural shapes. Guards/AC were not relaxed. Bandit high-severity/high-confidence scan of three changed event-pipeline files has no findings. Local Go race could not run becauseCGO isdisabled; existing Linux CI race gate remains mandatory before merge.

## Configuration

- Application consumer requires `ZD_RULES_STATE_FILE`; missing/:memory:/invalid path reportsFAILED before polling. Use an existing private writable mounted directory and one owner. Do not point at raw-O/H archives.
- Exact proposal envelope and attempt count persist before send. Matching durable receipt ends transport work; permanent refusal isfinal; exhausted/aged/clock-regressed uncertainty becomesUNKNOWN. Do not reset unknown rows or regenerate IDs to force resend.
- One publish per tick; reads have deadline and20page/10,000record ceiling; journal capacity10,000. Budget/capacity failure remains an error, never truncated success. Cooldown is pacing, not authorization/recovery proof.
- Existing actor verifier gives only Hephaestus `/state/decisions.sqlite` using emptyDir16Mi/fsGroup65532, actor-only mount. It survives process/container restart in thatPod; it does not survive Pod replacement. Deployment requires separately configured persistent storage and proof; this patch creates noPVC.
- One owner thread constructs/polls/closes SQLite. Async cancellation signals stop and joins it; `/healthz.consumer` retains failure/state. API liveness is not recovery.

## Acceptance and next action

Component evidence supports SQLi-only AC01/03 behavior with configured single-owner storage. No new lab/network/broker/model, build/deploy, real action, deployedPVC, Pod replacement, Boutique recovery, KPI orG3/end-to-end PASS is claimed. Remaining live integration is ZER-50/R5 and a separate G3 evidence decision. Supplemental HPA/scale/rollback criteria remain unaccepted.

[Publication package](publication-package.md) is ready for owner approval. No commit/push/PR/remoteCI/merge/Done has been performed forZER-18. Do not infer G3 from issue counts or use this component checkpoint as deployed acceptance.

Rendered test logs normalize CRLF and trailing whitespace only; captured originals remain in ignored scratch/zer18/results and verification retains their original SHA256. No result/timestamp/message is removed.
