# Codex review — ZER-11 + ZER-39 H-RT1 preparation

**Verdict: CHANGES_REQUIRED / NOT_READY_FOR_RUNTIME.** Review ngày 21/10/2026. Năm lỗi cụ thể trong harness mới phải sửa trước khi xin quyền RT1; không mở thêm milestone hoặc thay AC. ZR11-01/ZR11-02 của gói dashboard fix-01 giữ kết luận retest trước, không mở lại.

## Findings (theo mức độ)

### RT1-01 — P1 — Lỗi I/O bỏ qua khôi phục luôn chạy

**Vị trí:** [Orchestrator.run](../../../infrastructure/scripts/r1_baseline_runtime.py#L975), nhánh exception ở 983–993; P7 bắt lỗi từng bước ở 1397–1407.

Sau P1 đã scale Gaia/Hephaestus về 0, lỗi OSError/ValueError ngoài các lớp HarnessError/DeadlineExceeded không đi qua P7 vì P7 nằm sau try/except, không ở finally. Trong P7, lỗi OSError ở một bước bị phase_safe bắt ngoài vòng lặp, nên các bước cleanup còn lại bị bỏ. Đây là lỗi của harness mới, không phải yêu cầu sửa kho lưu cũ.

**Phản ví dụ chạy được:** tiêm ENOSPC vào Path.write_bytes của file DeleteOptions phía host sau khi Gaia đã về 0. run() ném OSError, cleanup_steps=0, Gaia=0, Hephaestus=0, namespace còn, receipt không có. Đĩa host đầy không được phép làm bỏ thao tác khôi phục qua API vốn vẫn có thể thực hiện.

**Sửa tối thiểu:** P7 trong finally; lỗi bất ngờ thành abort có lý do; mỗi bước cleanup cô lập lỗi để tiếp tục những bước độc lập trong deadline, ghi kết quả best effort. Ghi receipt best effort không được đứng trước/che mất cleanup. Test I/O lỗi ở pha chính và ở bước cleanup đầu, đối chứng khôi phục replica vẫn được thử; không hứa khôi phục thành công khi API/đĩa thật hỏng.

### RT1-02 — P2 — kubectl mặc định bỏ managedFields nên positive control luôn abort

**Vị trí:** [Kube.json](../../../infrastructure/scripts/r1_baseline_runtime.py#L808), consumer [P2](../../../infrastructure/scripts/r1_baseline_runtime.py#L1195).

Kube.json dùng kubectl get -o json không có --show-managed-fields=true. Trợ giúp của kubectl cài trên máy ghi --show-managed-fields=false và chỉ giữ managedFields khi bật. P2 cần manager của spec.replicas bắt đầu bằng kubectl nên mảng manager trống khiến ATTRIBUTION_CONTROL_FAILED. Fake luôn trả managedFields nên các ca hiện có bỏ sót.

**Phản ví dụ:** wrapper fake mô phỏng đúng mặc định kubectl bằng cách bỏ metadata.managedFields khi chưa bật cờ: abort ATTRIBUTION_CONTROL_FAILED, trials=[], cleanup CLEAN. Không cần chạy lab để chứng minh lỗi wiring này.

**Sửa:** bật cờ ở các lần get cần field ownership; fake mô phỏng mặc định thật. Giữ kiểm positive control, không bỏ điều kiện để cho chạy qua.

### RT1-03 — P2 — Positive control không đạt bị ghi đè thành ok=true

**Vị trí:** [Agent.handle](../../../infrastructure/scripts/r1_baseline_runtime.py#L189), kết quả domain ở 311–314; P2 kiểm ở 1178–1181.

handle dùng dict(method(command), ok=True), ghi đè ok=False của cmd_positive_control. Khi chỉ ACK của DECISION gặp Retry, state/classification còn None; self.pc.ok=False nhưng trả host ok=True. P2 do đó không chứng minh được MODE_VIOLATION đã được quarantine bền mà vẫn cho tiếp.

**Sửa:** tách transport/dispatch success khỏi kết quả control hoặc cho control thất bại raise HarnessError. Host phải kiểm valid_o_event_recorded cùng REJECTED và MODE_VIOLATION. Test ACK outage chỉ ở DECISION, sai classification và control thành công; ca không đạt không được tới target mutation P3/P4.

### RT1-04 — P2 — Mất phản hồi create để lại namespace nhưng cleanup báo CLEAN

**Vị trí:** [create](../../../infrastructure/scripts/r1_baseline_runtime.py#L896), ghi self.created chỉ ở 898–901; cleanup_namespace1455 và final_diff1483–1486.

Nếu API đã tạo namespace nhưng phản hồi mất/timeout, write() ném trước khi lưu UID. cleanup_namespace không thấy record nên SKIPPED, final_diff không kiểm namespace đó. Harness báo CLEAN dù tài nguyên mình tạo còn lại.

**Phản ví dụ:** fake thực hiện create Namespace rồi trả TIMEOUT. Kết quả abort WRITE_FAILED, created=[], namespace_left=true, cleanup=CLEAN, final_diff trống.

**Sửa:** theo dõi intent của create trước gửi; reconcile kết quả không rõ bằng get tên/namespace + nhãn nonce, lấy UID rồi cleanup có precondition. Nếu chưa xác định được ownership thì giữ đối tượng và báo INCOMPLETE/UNKNOWN, không xóa theo tên hoặc báo CLEAN. Kiểm chung nhánh create dùng cho namespace, profile/HPA/load pod; không cần một framework mới. Test lost response và đối tượng cùng tên khác UID/nhãn.

### RT1-05 — P2 — Event cũ/downscale bị dùng làm bằng chứng phục hồi của trial hiện tại

**Vị trí:** [collect_events](../../../infrastructure/scripts/r1_baseline_runtime.py#L1344), [interpret](../../../infrastructure/scripts/r1_baseline_runtime.py#L1577).

Collector lấy mọi Event có tiền tố frontend/cartservice trong namespace, không ràng buộc cửa sổ trial hoặc UID đối tượng. interpret chấp nhận SuccessfulCreate cũ cho CTRL; HPA chỉ cần SuccessfulRescale sớm hơn t_rec, không chứng minh đó là scale-up hiện tại. Chạy lại HPA cùng tên có thể còn Events của lượt cũ.

**Phản ví dụ:** SuccessfulCreate lịch sử và danh sách pod thay thế rỗng vẫn ra CONTROLLER_RECOVERY_OBSERVED; Event HPA lịch sử ghi New size:1, metrics below target vẫn ra HPA_RECOVERY_OBSERVED.

**Sửa:** giữ thời gian/UID của fault và các đối tượng đang kiểm; lọc Events theo trial và ownership. CTRL cần UID pod mới/quan hệ ReplicaSet phù hợp; HPA cần bằng chứng replica tăng trong trial do HPA hiện tại, trước t_rec. Thiếu/chồng lấn/sai thứ tự phải ra thiếu bằng chứng/ambiguous, không claim thành công. Test stale Event, wrong UID, downscale-only và current scale-up hợp lệ. Không sửa semantics scorer đã khóa.

## Kiểm chứng độc lập và provenance

- Target: local H-RT1 delta manifest, không phải toàn bộ dirty tree. HEAD 169413303340fc01eea8597c121ce39455892af0, branch zer-10-independent-measurement; staged rỗng; không fetch/switch/commit.
- Linear qua đúng linear_zero_door: ZER-11 và ZER-39 In Progress, URL linear.app/zero-door; AC-04 của cha = AC-01 của con, không thay đổi outcome. AC live được đọc trực tiếp; provenance ở receipt reviewer.
- manifest-rt1.json: 21/21 hash khớp (5 modified,16 added). 190/190 nguồn read-only và10/10 owner protected không đổi.
- Production Nemesis Python3.11.9: suite mới17/17 ở lượt1; Production Hephaestus:17/17. Lượt Nemesis2:17 test, **2 FAIL +1 ERROR**; giữ nguyên toàn bộ log, không bỏ ca lỗi để có PASS.
- Hồi quy độc lập Nemesis: dashboard33/33, modes7/7, CI boundary6/6, check_r1_baselines PASS. Bandit trên harness và verify:exit0.
- Ba phản ví dụ host (RT1-01/02/04) chạy bằng fake kubectl/target và gateway production loopback. Root chạy lại probe domain cho RT1-03/05, assertions đúng. Không tác động cluster thật.
- Read đầy đủ source mới, consumer trực tiếp (entrypoint, test, CI, profile, runbook); diff của3 file implementation/config/documentation có before snapshot, note/NOW là append/prepend. Các source dashboard/measurement/event_pipeline/worker của gói trước không sửa.
- GitNexus reindex local --pdg --index-only hoàn tất. MCP giữ graph cũ rồi transport closed; CLI context/impact dùng index mới để đối chiếu. Taint explain không có CLI tương ứng trên bản cài và MCP không đọc được: không nhận coverage taint hoàn chỉnh; direct source + phản ví dụ là căn cứ finding. Không coi graph trống là an toàn.

## N1 — lỗi ngắt quãng đã có log cụ thể, chưa kết luận nguyên nhân

Lượt chẩn đoán riêng sau đó:3/3 đạt, giữ receipt/raw trong scratch. Lần thu chẩn đoán đầu có3ERROR do script reviewer cố copy file .owner đang khóa; đây là lỗi instrumentation của reviewer, không tính thành lỗi package. Đã bỏ riêng file lock ở lần thu02, không sửa source package.

Lượt Nemesis2: test_total_cap nhận PERSISTENCE(CONTROL_NOT_DURABLE) thay TOTAL_CAP; test_controller_and_hpa... bị ABORTED cùng lý do; test_gap... KeyError B0-HPA vì trial không tới được. Log có WinError10053 khi gateway trả ACK. Đây là biểu hiện quan sát, **chưa chứng minh** nguyên nhân là Windows scheduling, timeout hay lỗi harness. Giữ raw/receipt khi fail; lượt chẩn đoán riêng giữ cả archive/outbox để phân loại. Không nới F-01, bỏ assert hay chuyển lỗi thiếu ACK thành PASS để ổn định test. Nếu là timing fake thì chỉnh thang thời gian/test seam có căn cứ; logic runtime fail closed vẫn phải giữ.

## Đánh giá AC và bước tiếp

AC-01–03: kế thừa review fix-01 trước, delta này không mở lại các lỗi dashboard. AC-04/ZER-39 và G1 **chưa nghiệm thu**: cần sửa năm finding trong một gói, retest offline rồi mới xin quyền RT1 cụ thể. Runtime, Docker/image build, model/API, CI từ xa, publication và Linear **không thực hiện** trong lượt review.

Tự kiểm source không thay, append handoff/note và prepend NOW sau khi chốt report. Mọi evidence trước giữ nguyên. Không yêu cầu Hoàng chấp nhận rủi ro lỗi code để bỏ qua AC.
