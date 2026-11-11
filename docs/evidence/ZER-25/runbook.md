# Runbook R5 — Phát lại và chuẩn bị tái lập

## Phát lại dữ liệu trên máy của Hoàng

Replay yêu cầu Python 3.11 và thư viện chuẩn. Bản bàn giao được kiểm bằng Python 3.11.9. Python 3.12.4 cho sai khác số thực khoảng 2e-12 so với kết quả đã niêm phong. Dùng Windows Python Launcher với `py -3.11` để chọn đúng phiên bản. Mở Git Bash, chạy ở thư mục gốc của checkout chứa runbook này. Hai đối số là hash manifest từ biên bản bàn giao và đường dẫn Windows tới thư mục bằng chứng gốc. Trên máy hiện tại thư mục đó là `R:/_Projects/Eurus_Workspace/zero_door/scratch/zer52-checkout/docs/evidence/ZER-52`.

```bash
cd /r/_Projects/Eurus_Workspace/zero_door/scratch/zer25-checkout
export MSYS_NO_PATHCONV=1 PYTHONUTF8=1
py -3.11 -B docs/evidence/ZER-25/replay-pilot.py \
  --manifest-sha256 710d9846209a13bd1d7553d2b332b6abd54dea0fd2a1464b53cc2836669ecabf \
  --evidence-root R:/_Projects/Eurus_Workspace/zero_door/scratch/zer52-checkout/docs/evidence/ZER-52
```

Kỳ vọng PASS, 8 file legacy và 40 dòng, 12 ca pilot, 265 file nguồn, 4.549 file batch, 6 batch dừng và 1 cửa sổ dừng trước claim, 0 formal. Tùy chọn `--analysis-output` tạo JSON ở đường dẫn mới, từ chối ghi đè. Sai hash hoặc thiếu file dừng với mã 1. Chạy phát lại chỉ cần đọc file, không mở Docker/WSL.

Analyzer v4 được giữ nguyên byte và pin hash. Trình phát lại kiểm danh sách 12 trial và run ID khớp protocol, receipt và kết quả analyzer. Legacy kiểm theo từng CSV đã kê tên. Lượt dừng đối chiếu status, nhãn lỗi và guard từ acceptance gốc, run ID từ receipt đã pin khi có, verdict CLEAN và topic vắng mặt từ biên bản cleanup riêng. Không thêm file vào cohort bằng cách thả CSV vào thư mục. `infrastructure/scripts/analysis.py` là đường phân tích legacy.

## Bản dựng và nơi giữ bằng chứng

| Thành phần | Điểm khóa |
| --- | --- |
| Bản công bố dùng cho bàn giao | Git `90efe53f9a35f140f168166a5bd8b74a6cae2abb`, nguồn báo cáo ZER-24/52/53 và cấu hình code chính. |
| Nguồn thực thi pilot | Git base `7f806f13bc989934b7c880dcef5dfb6897c73695` cộng 265 file byte-exact trong `runtime-07/source/`. Manifest nguồn chứa các file runtime prep chưa có trong commit. Chỉ checkout commit sẽ thiếu các file này. Khi dựng lại nguồn để kiểm, dùng checkout riêng đúng base rồi đối chiếu/khôi phục đúng danh sách 265 file từ snapshot. |
| Cấu hình, runner và dependencies | Protocol Runtime07 và source manifest giữ tham số, renderer, runner, requirements và test đã pin. Manifest phân biệt ID của fixture/proxy trong 12 cache receipt với ID host/node của worker và Nemesis trong 12 worker cache receipt. ID fixture trên host thuộc fixture. Build receipt cũ ghi đúng ID worker, còn hồ sơ thiếu chứng thực toàn bộ đầu vào của lần build cũ. Launcher/profile quan sát lúc bàn giao có hash riêng, nằm ngoài seal nguồn batch. |
| Dữ liệu pilot | Root gốc ghi trong manifest, giữ seal cùng toàn bộ `runtime-07/`, raw report, analysis, terminal receipt và metadata cũ. Giữ riêng R01–R06, R02/R04 reconciliation và lần terminal lỗi trước claim. Các file gốc có thể chứa chi tiết vận hành. Hoàng giữ dữ liệu raw tại bản lưu riêng trên laptop để truy lại nguồn khi viết báo cáo. |
| Dữ liệu formal | 0 run. Bản thiết kế khóa ở ZER-53. Danh sách pin chưa đủ nằm trong manifest. Khi đã được duyệt, formal có manifest mới, giữ hash của protocol, runbook, config và lịch H niêm phong trước lượt đầu. |

Hoàng chọn `local-evidence/ZER-55/` làm nơi lưu riêng trên laptop. Thư mục giữ ZIP gốc, manifest đã đính chính, replay/analyzer, protocol, tám CSV legacy và biên bản xác minh. Mở README tại đó và chạy `py -3.11 -B verify-local.py` trong Git Bash để kiểm hash, giải nén tạm và phát lại từ chính bản lưu. Bản sao có phạm vi lưu cục bộ. Hồ sơ AC-03 dùng để Hoàng tự viết báo cáo.

Bản ghi đóng băng cho phép tái lập byte nguồn pilot và tính lại số liệu. [Biên bản 11/11](rebuild-verification.json) xác nhận dựng riêng fixture từ snapshot bằng base đã pin, chạy chế độ an toàn và kiểm /health cùng /ready. ID fixture mới được lưu riêng với ID pilot. [CI đã chạy](https://github.com/EurusDevSec/Zero-Door/actions/runs/42453718435/job/128648162818) xác nhận dựng image worker từ revision có 30/30 tệp worker trùng byte với snapshot và kiểm từ chối thiếu cấu hình khi khởi động. Receipt build lịch sử khớp cả ID worker trên host và node. Toàn bộ build context của worker lịch sử chưa được chứng thực. Biên bản ZER-46 runtime-04 raw/0037 ghi lần build fixture lịch sử. Nemesis được nhận dạng trong cả 12 ca qua biên bản cache và trạng thái container. Snapshot thiếu `agent-orchestrator/nemesis/Dockerfile` và `agent-orchestrator/nemesis/requirements.lock`. ZER-42 dùng build context `agent-orchestrator/nemesis`, còn CI dùng `./agent-orchestrator`. Cả hai tệp có trong Git đúng revision nguồn Runtime07. Cây Git `agent-orchestrator` trùng với cây [CI Nemesis](https://github.com/EurusDevSec/Zero-Door/actions/runs/42453718435/job/128648162817) đã dựng và kiểm import thành công. Biên bản ZER-42 ghi công thức khác cho image cache lịch sử. Khả năng tái tạo image cache đó chưa được xác minh. Đối chiếu provenance và pin trước khi dùng một image cho lần chạy khác. Các image cần dùng cho formal phải có digest và source/dependency tương ứng. Readiness phải xác minh cùng hồ sơ dự kiến dùng, tách khỏi dataset formal.

## Phạm vi phát lại và kiểm hồi quy

ZIP riêng tư là bản lưu **dữ liệu và snapshot pilot để phát lại**. Thư mục lưu riêng giữ kèm chương trình replay, manifest, protocol đã khóa, đính chính SD và tám CSV legacy. Kiểm trên bản giải nén đã tái tạo đủ 12 ca.

Kết quả **57/57** là lượt kiểm offline trên bản sao có đủ đầu vào. Claude xác minh chỉ chạy được 51/57 từ snapshot trong ZIP. Để chạy lại đủ, cần driver `scratch/zer25-work/retest.py`, cây kiểm trong `runtime-prep-07/` và `session-20261104/` của checkout pilot, các receipt bổ trợ mà bộ kiểm đọc, cùng `infrastructure/scripts/local_lab_profile.py` dùng cho hai case readiness. Driver hiện dùng đường dẫn của máy Hoàng. Trên máy này, từ thư mục gốc workspace chính chạy `bash scratch/zer25-work/retest.sh` để kiểm đủ bộ đầu vào cục bộ. [Biên bản kiểm](verification.json) ghi hash driver, phạm vi và danh sách case. Các đầu vào bổ sung của bộ 57 test vẫn ở checkout cục bộ đã nêu.

## Kiểm trước và sau vận hành khi được duyệt

1. Kiểm inventory máy hiện tại. Nếu cụm `k3d-zero-door` còn nguyên, dùng đường khởi động cụm có sẵn với Docker `desktop-linux`, explicit kube context và loopback. Nếu mất cụm hoặc sai UID/PVC/spec, dừng để đối chiếu [lab restoration](../ZER-35/lab-restoration.md), [Bash tooling](../../runbooks/bash-tooling.md) và image/config đã pin. Script rebuild Nemesis chỉ phục vụ một service.
2. Tại admission kiểm identity, baseline, HPA OFF, namespace/topic/policy/probe/actor sở hữu của lượt trước đã đóng, service Ready và profile đã duyệt. Đọc receipt cleanup gốc và đối soát riêng nếu có. Còn UNKNOWN hoặc drift thì HOLD. Không dùng lịch sử một lượt khác làm readback hiện tại.
3. Theo [ZER-53 §5](../ZER-53/protocol.md), pin source/image/renderer/dependency/resolver/detector/probe/scorer, kiểm năm seed, clock tổng sai số ≤0,5 s, H/O/S, lịch kín, BM và Hòa tách vai. Kiểm một vòng B2/C5 ở 5,5 GiB khi được duyệt riêng. Admission Windows ≥2.868 MiB suốt 25 mẫu/120 s và tại claim, giữ quiet 60 s và settle 30 s. Trong work/cleanup cả host và guest ≥1.024 MiB mỗi mẫu, PSI memory some avg10 ≤5. Giữ các guard khác của protocol.
4. Mỗi trial đã claim giữ receipt dù chưa gửi request. Giữ thời gian, actual status, lý do loại, coverage và tài nguyên. Tiếp tục theo lịch niêm phong và quy tắc dừng trong ZER-53. Mỗi ca phải đóng và thu hồi cây tiến trình, xác nhận namespace/UID và topic của đúng run đã vắng, spec và restart của tài nguyên dùng chung khớp. Hết deadline hoặc sai guard thì giữ bằng chứng và dừng. Cửa sổ tắt về offline theo kế hoạch.
5. Dùng đường phát lại chỉ cho pilot đã seal. Dùng scorer/manifest formal đã pin riêng khi có dữ liệu mới. Đưa failure/UNKNOWN/NOT_RUN cùng lý do vào ledger, tách ba tập legacy/pilot/formal.

Runtime07 đã kết thúc OFFLINE và grant đã dùng. Cấu hình 5,5 GiB chỉ đã kiểm idle. Các bước vận hành ở đây là quy trình chuẩn bị cho lượt được cấp quyền riêng.
