# Gói hoàn tất ZER-49 — chờ Hoàng duyệt

PREPARED_NOT_AUTHORIZED. Chỉ riêng ZER-49/AC01: evidence→diagnosis Gaia, metric/log đầu vào, latency và DETECTED trước inference/không đổi MTTD.18Gaia+4agent+22adapter+6runner tests đạt; source review độc lập READY sau sửa blocking disk. Gói này không mở Hephaestus/ZER-50.

## Một lượt inference chức năng

- Dùng input benign synthetic cố định tại inference-prep/observation.json, sinh qua đúng Gaia.poll_elasticsearch_logs/Detector bằng telemetry giả. Có metric log_pattern_match=1/threshold0, log sentinelERROR lành tính, ID/timestamp/provenance rõ. Không tạo payload hay gửi request tới fixture; không lấy dữ liệu lab. Đây là chấp nhận chức năng component đã nối, không giả làm deployed/integrated telemetry hoặc formal benchmark.
- Đúng1run/1call/1attempt/0retry tới OpenAI/gpt-6-luna qua Adapter hiện có. HTTPS cố định Responses; store=false, tools=[], service_tier=default, reasoning=none; không provider/model/endpoint khác.
- Request≤8192bytes, output≤256tokens, reservation≤9472tokens, estimate≤0.005USD theo pinned adapter/pricing28Oct2026. Đây là policy estimate, không billing hard cap. Thiếu usage/vượt reservation/refusal/UNKNOWN/ABSTAIN/schema hoặc evidence-ref sai→không PASS và không retry.
- Attempt20s/call25s/async30s. Async là cooperative khi disk I/O: outer run_once.py sở hữu đúng1native Python child, đợi40s, kill nếu quá hạn rồi wait/reap≤5s; không claim server-side cancellation hay no-billing khi outcomeUNKNOWN. Cửa sổ thao tác≤5phút gồm xác minh receipt/process cleanup. Không tiến trình/background/tunnel/lab workload mới;0Docker/build/import/pull/apply/restart,0HTTP fixture/0TCP probe.
- Credential qua Doppler đã dùng ở ZER-48/19, chạy từ primaryR để dùng đúng routing sẵn có. Chỉ cấp key vào child environment; không in/ghi/dump key, không đổi auth/config. Đã kiểm key hiện được cấp=True; không gọi model trong kiểm này. Nếu key/quota/config không sẵn sàng thì dừng.
- Authorization khóa hash proposal+source-manifest; run_once.py defaultPLAN_ONLY, --execute cần approval đúng. Source/input/config đổi thì từ chối. inference-01 được tạo độc quyền và giữ lại kể cả fail/UNKNOWN; không dùng lại approval để chạy02. Không chạy inference khi chưa có câu trả lời duyệt.
- PASS khi model trả diagnosis có schema hợp lệ, evidence ID đúng, không UNKNOWN, context/causation và DETECTED timestamp giữ nguyên; đủ usage/cost,1trace/1attempt, childreaped, raw/receipt/hash khớp và review evidence đạt. Không yêu cầu AI phải phát hiện attack hay thắng đối chứng ở bước này.

Lệnh thực hiện duy nhất, chỉ sau duyệt và ghi authorization.json từ câu trả lời thật:

~~~bash
cd /r/_Projects/Eurus_Workspace/zero_door
doppler run -- /r/_Projects/Eurus_Workspace/zero_door/scratch/zer12/production-nemesis/Scripts/python.exe -B \
  /c/Users/ACER/.codex/worktrees/zer-46-publication/zero_door/docs/evidence/ZER-49/run_once.py --execute \
  --authorization /c/Users/ACER/.codex/worktrees/zer-46-publication/zero_door/docs/evidence/ZER-49/authorization.json
~~~

## Publication có điều kiện

Chỉ sau inference và review đạt: scoped commit/push branch codex/zer-49-gaia-diagnosis, tạo PR, kiểm CI/review, merge, rồi nghiệm thu ZER-49 AC01 và chuyển Done khi tất cả gate đạt. Không coi ZER-20/G4 hoặc issue kế tiếp Done.

Allowlist: agent-orchestrator/gaia/{main.py,diagnosis.py,diagnosis_cli.py,Dockerfile}; tests/test_gaia_diagnosis.py; .github/workflows/ci.yml chỉ Gaia test/runner check/import smoke; docs/evidence/ZER-49/**; NOW và milestone gaia-and-hephaestus.md chỉ delta ZER-49 trên cleanbase. Nếu packaging yêu cầu giữ byte evidence, chỉ thêm .gitattributes scopeZER49; không sửa raw để khớp hash. Giữ27dirty paths cũ/primaryR nguyên, không git addall/forcepush/bypassCI/rules/deploy/notification ngoài yêu cầu.

Lý do cần duyệt: [WORKFLOW](../../delivery/WORKFLOW.md) quy định: “Cloud/model/lab/triển khai là hành động riêng” và “Đây là điều kiện nghiệm thu, không cấp quyền commit/push/merge.” Quyền ZER-19 đã hoàn tất, không tự cấp inference/publication ZER-49. Code/test/review đã làm trước; Hoàng có thể duyệt cả gói có điều kiện một lần, không cần duyệt từng bước nội bộ.
