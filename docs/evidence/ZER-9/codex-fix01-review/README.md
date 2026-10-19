# Codex retest ZER-9 fix-01 — 19/10/2026

**Verdict: NOT_READY.** Phần sửa chính có hiệu lực, nhưng còn hai đường lỗi P2 chặn AC-02. Không nhận tuyên bố “đã sửa đủ 14 finding” như hoàn tất nghiệm thu. Đây là review delta offline; không chạy lab/API, không publication hoặc đổi Linear.

## Target và provenance

- Checkout: zer-9-event-pipeline; HEAD 2af4d33bf02c59d7802901d523b1bb2eb39f05a3; staged rỗng. Review patch fix-01 so với snapshot trước sửa, không coi toàn bộ dirty work của checkout là của Claude.
- [Delta manifest](../fix-01/delta-manifest.json) SHA-256 e20e0660951f6da8f402e2f459bb1530739e853b71a1c171ccd63e7df39d18fc. [README bàn giao](../fix-01/README.md) SHA-256 a01fd06f464102b7256ed04d031dcfad1bb51352cf3f36c8f9e2344e9c1d3547.
- [Intake](intake.json): tất cả mã/test/cấu hình khớp hash sau sửa; note/NOW khác manifest vì được append/prepend sau khi manifest được tạo. Prefix note 82,758 byte khớp e7c7c0cf của lúc nhận writer; NOW chứa nguyên con trỏ trước ở phần lịch sử.
- [Historical check](historical-check.json): 61/62 hash lịch sử khớp; chỉ verification.md đổi đúng allowlist. Raw H/O, receipt, review cũ, package/checksums và tài liệu được bảo vệ giữ nguyên.
- Live read-back ZER-9: In Progress; AC-01/02/03 vẫn chưa check. Đúng URL workspace zero-door; không ghi Linear.

## Hai finding cần sửa

### FX01 — P2 — payload lồng sâu vẫn thoát khỏi quarantine

Nguồn: [Gateway.check:44](../../../../agent-orchestrator/event_pipeline/gateway.py#L44), [KafkaBridge.record:339](../../../../agent-orchestrator/event_pipeline/gateway.py#L339); validator hiện hành ở [contract.py:102–106](../../../../agent-orchestrator/event_pipeline/contract.py#L102) không bắt RecursionError từ đệ quy forbidden_keys.

[Probe độc lập](deep_http.py), [actual result](deep-http-result.json): một DETECTED có payload.extra chứa 520 tầng list, JSON hợp lệ chỉ 2,053 byte, qua strict decode/canonical nhưng gặp RecursionError khi validate. HTTP có token detector hợp lệ trả 503 NOT_DURABLE và không lưu rejection (0 dòng). Khi cùng envelope được ký đúng nguồn rồi đưa vào Kafka giả, recorder dừng với RecursionError, offset vẫn 0, không quarantine và event hợp lệ kế tiếp không được ghi. Restart với offset đó sẽ gặp lại message.

Đây là ca input đã xác thực; không suy ra pod không có key có thể giả chữ ký. Đường HTTP mất rejection là có thể gọi trực tiếp. Nhóm test poison hiện chỉ phủ UTF-8/JSON/NaN/HMAC, chưa phủ JSON lồng sâu vẫn parse được. Cần chặn độ sâu/độ phức tạp ở đường nhận trước mọi bước đệ quy hoặc xử lý lỗi giới hạn dữ liệu có chủ đích; giữ bytes/hash vào quarantine trước commit. Không đổi lỗi I/O/lỗi chương trình bất kỳ thành dữ liệu bị từ chối rồi commit.

Ảnh hưởng: ZR9-01/02 chưa được khép hết; AC-02 còn thiếu. Không cần đổi prose/schema zd-event/1.0.0 để xử lý giới hạn transport này.

### FX02 — P2 — H vẫn nhận thành công sau append bị ghi dở

Nguồn: [Gateway.submit:64–65](../../../../agent-orchestrator/event_pipeline/gateway.py#L64), [Gateway.readiness:118–121](../../../../agent-orchestrator/event_pipeline/gateway.py#L118), [Archive.append:206–215](../../../../agent-orchestrator/event_pipeline/store.py#L206) và [ingest:275](../../../../agent-orchestrator/event_pipeline/store.py#L275).

[Probe độc lập trên HTTP plane H](h_partial_http.py), [actual result](h-partial-result.json): mô phỏng append đã ghi một phần bytes rồi OSError. Request đầu trả 503; /readyz sau đó vẫn 200 READY. Request hợp lệ tiếp theo trả 201 RECORDED và được nối sau phần dòng đứt; đọc raw của run phát JSONDecodeError. Như vậy một event được nhận thành công nhưng archive không thể xuất/đối chiếu.

Đây là fault injection offline, không phải đo đĩa hỏng thật. Nó mô phỏng chính điều mà restart checker đã nhận diện là unsafe; thiếu sót là process đang chạy vẫn tiếp tục ghi. H không có KafkaBridge nên cơ chế bridge.failure mới không bảo vệ đường này; O không Kafka cũng vậy. Test I/O hiện chỉ patch append ném lỗi trước khi ghi trên Kafka, nên không bắt được.

Cần trạng thái lỗi archive/gateway được giữ lại cho cả direct H/O và recorder: lỗi append/fsync/đọc archive hỏng làm readiness 503; request ghi/seal/export sau đó không được báo thành công hay nối thêm vào raw đến khi phục hồi an toàn. Giữ nguyên bytes lỗi, không tự truncate/repair/reset hoặc dùng liveness để restart che lỗi. Lỗi dữ liệu đã quarantine thành công không được làm process chết.

## Retest đã chạy lại

[Kết quả đầy đủ](retest.txt): core 22/22, regression 30/30, agent HTTP 4/4, Bash 37 PASS, Nemesis 3/3 và ZER-37 release 9/9 đều đạt. Verifier --help không lab, thiếu --live bị từ chối đúng (exit 2); YAML 13 document; diff/whitespace sạch.

Script raw cũ nguyên bản ra 57/58: check duy nhất fail là source receipt live-11 so với file hiện tại, lệch đúng 7 file sửa. Check bổ sung source receipt với snapshot trước sửa đạt 10/10. Không chuyển FAIL lịch sử này thành PASS trên revision mới. Raw live-11 còn nguyên và có giá trị cho revision cũ.

Khử false positive C0–C5/v1/ab, nhãn hợp lệ trong stream/target, secret theo actor, actual ES client Gaia qua fake upstream, retry/permanent refusal, reset 409, seal race/restart, export late/global quarantine và tương thích raw cũ đều có kiểm và đã chạy lại. Hai phản ví dụ ở trên nằm ngoài bộ 30 test, đã được Codex và lượt kiểm storage độc lập tái hiện.

## Review cấu trúc và giới hạn

GitNexus được refresh local --pdg --index-only cho working tree này, không embeddings/wiki. Query/context của KafkaBridge.record và Gateway.admit xác nhận handle/check_ready và submit→admit→check/validate; impact/taint/PDG đã tra cho persistence/HTTP/auth/audit/DSL. Taint không có finding được ghi, nhưng graph thiếu receiver/callback edges (ingest 7, reject 4, seal 6 call sites), và detect_changes không phủ trọn untracked modules: kết luận dựa thêm trên source đầy đủ, snapshot delta và probe. Không dùng zero-hit làm bằng chứng an toàn. Log graph ở scratch/zer9/codex-fix01/graph.json.

Hai lượt review đọc storage/recorder và audit/auth/client/DSL/verifier/CI không sửa sản phẩm. Không thấy blocker mới khác trong normal seal/drain/export hoặc key/retry/DSL.

Giới hạn không cộng thành blocker mới của fix-01:

- Nhánh SECRET sạch của audit cũ có thể ra UNKNOWN_MANIFEST_CLASS (false UNKNOWN, không phải false CLEAN); không được ca live hiện tại dùng resource NEUTRAL chạm tới. Nên có test clean SECRET cạnh test leaked SECRET khi sửa nhỏ liên quan; không suy audit tổng quát hoàn chỉnh.
- publish-images chưa needs hai job r1-agent-http/r1-image-build. Trước publication phải kiểm cả hai job đạt trên đúng revision; chưa có CI/branch-protection live proof trong lượt này.
- Async blocking/full-run scans, process một trial và fsync thư mục Windows vẫn là giới hạn đã khai; chưa cho phép trial nghiên cứu hoặc mở rộng nhiều replica.
- Quyền thực tế của Gaia/Hephaestus chưa được chứng minh: live-11 là host source functions + observer pod. Sau khi sửa hai lỗi cần kiểm tích hợp đúng revision/actor boundary; không tự chuyển nghĩa vụ này sang issue khác hay nhận waiver từ handoff.

## Bước tiếp và writer

Gói fix-02 chi tiết đã nối cuối issue note. Claude sửa gom hai finding và retest offline, giữ nguyên fix-01 và báo cáo này. Codex giữ writer tới khi Hoàng chuyển prompt; sau bàn giao Claude trả writer để Codex retest độc lập. Chưa lab mới, chưa commit/push/merge, chưa Hoàng nghiệm thu; ZER-9 và G1 chưa đóng.
