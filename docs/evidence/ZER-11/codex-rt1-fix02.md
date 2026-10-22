# ZER-11 / ZER-39 — đóng FXRT1-01 offline

**PASS_FOCUSED_OFFLINE.** Hoàng giao Codex sửa trực tiếp phần còn lại. HEAD vẫn `169413303340fc01eea8597c121ce39455892af0`; không đổi nhánh. Phạm vi: hàm CTRL/caller, regression thời gian và đúng đoạn runbook; không sửa scorer/KPI, HPA, event pipeline hoặc CI.

## Sửa và bằng chứng

`controller_replacement(ev, t_rec)` đòi T_req/T_rec có dữ liệu và Event thỏa `T_req − 1000 < Event.t_ms`, `Event.t_ms + 1000 < T_rec`, đồng thời giữ các ràng buộc UID ReplicaSet/pod mới Ready/tên pod. Dung sai 1 giây nhất quán với nhánh HPA đã review. Thiếu thời gian hoặc thứ tự mơ hồ giữ claim `RECOVERED_CONTROLLER_EVIDENCE_MISSING`; nhãn scorer không đổi.

- Regression mới: một method gồm 12 ca biên (2 hợp lệ, 10 từ chối). Chạy **trước sửa production**: 10 subcase fail đúng lỗi nhận nhầm controller recovery; 2 đối chứng hợp lệ đạt. [Log fail-before](codex-rt1-fix02/fail-before.log).
- Sau sửa: method mới và method RT1-05 identity/HPA cũ đều đạt trên hai production pin Nemesis/Hephaestus (2 method mỗi pin). [Nemesis](codex-rt1-fix02/nemesis-focused.log), [Hephaestus](codex-rt1-fix02/hephaestus-focused.log).
- Chạy bản sao nguyên vẹn probe review độc lập: cả 4 ca đúng. Expected generic MISSING_OR_AMBIGUOUS của probe được so rõ với tên conservative thực tế MISSING, không sửa probe/bằng chứng cũ. [Output và assertion](codex-rt1-fix02/replay.log).
- Luồng fake end-to-end controller/HPA → seal/export → scorer → register → serve-results: 1/1 đạt trên Nemesis. [Log](codex-rt1-fix02/end-to-end.log). Bandit không issue; diff whitespace sạch.
- Snapshot trước sửa, runner, probe và checker nằm ở `scratch/zer11/codex-rt1-fix02/`; [hash source trước/sau](codex-rt1-fix02/source-hashes.json), [phạm vi intake](codex-rt1-fix02/scope.json).

Lệnh retest: `bash scratch/zer11/codex-rt1-fix02/run.sh` (hai production pin, replay có assert, một luồng fake liên quan và Bandit/diff-check), kết thúc OVERALL=0. Không chạy lại toàn bộ suite/clean checkout/mutant cho một thay đổi thuần diễn giải thời gian. Đã đọc lại diff so snapshot; caller production truyền t_rec, trường hợp thiếu event/identity giữ conservative.

## Kết luận và phần còn lại

FXRT1-01 khép ở mức offline; RT1-01…04 và các phần đã đạt giữ nguyên. Lượt fail timing Nemesis 26/27 của [retest trước](codex-rt1-retest01.md) cùng raw vẫn được giữ, **không** bị thay bằng kết luận toàn suite xanh. Lượt này không sửa cơ chế persistence/fake timing hoặc nới F-01.

Chưa Done: RT1 chưa chạy cluster thật. Những điểm managedFields scale, UID-delete stdin, Event thực và HPA activation vẫn cần xác minh theo runbook §5. Sau khi Hoàng cấp quyền RT1 mới chạy; kết quả thiếu effect, thiếu coverage, không kích hoạt HPA hoặc fail phải ghi đúng, không ép PASS. RT2/MANUAL runtime là phạm vi riêng đã ghi trong runbook. Chưa lab/Docker/model, commit/push/PR/merge hay đổi Linear.

Kiểm cuối: GitNexus local `--pdg --index-only` hoàn tất exit 0; không embeddings/wiki/publish. `git diff --check` sạch; danh sách Git status và staged trước/sau giống nhau (các file sửa vốn untracked/dirty). [Delta đúng ba file](codex-rt1-fix02/source.diff).
