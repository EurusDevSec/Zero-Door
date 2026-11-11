# Issue — Chốt kỹ thuật và lưu hồ sơ R5

[Milestone R5](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R5-integration/README.md) · [Checkpoint](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/NOW.md)

**Issue Linear:** [ZER-25](https://linear.app/zero-door/issue/ZER-25/chot-ky-thuat-va-luu-ho-so-r5). Nguồn đối chiếu: `R5-T03`. Ghi chú này giữ yêu cầu kỹ thuật và lưu hồ sơ; AC/trạng thái/lịch hiện hành đọc issue Linear.

## Phạm vi kỹ thuật

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

## Đầu ra và cách chia issue

| Nguồn | Đầu ra / bước nghiệm thu | Liên kết Linear / checklist |
| --- | --- | --- |
| R5-T03-S01 | Sửa lỗi cốt lõi phát hiện trong pilot và chạy lại phép thử bị ảnh hưởng. | AC của [ZER-25](https://linear.app/zero-door/issue/ZER-25/chot-ky-thuat-va-luu-ho-so-r5) |
| R5-T03-S02 | Lưu snapshot, runbook và dataset mới, bảo toàn dữ liệu cũ. | [ZER-55](https://linear.app/zero-door/issue/ZER-55/djong-bang-ban-dung-runbook-va-dataset-manifest) |
| R5-T03-S03 | Lưu sơ đồ, protocol, câu hỏi/claim, bảng/plot và giới hạn kết quả trong hồ sơ kỹ thuật R5 để dùng khi viết báo cáo. | AC của [ZER-25](https://linear.app/zero-door/issue/ZER-25/chot-ky-thuat-va-luu-ho-so-r5) |

## Yêu cầu kiểm chứng từ kế hoạch nguồn

### R5-T03-S01

Danh sách lỗi, bản sửa và kết quả kiểm chứng; nếu chưa qua, gate G5 chưa đóng.

### R5-T03-S02

Phiên bản dựng lại được; dataset manifest có method version/hash/run IDs, legacy/pilot/formal tách riêng; analysis đọc danh sách dữ liệu đã khóa thay vì gộp mọi CSV. Run lỗi/loại khỏi phân tích có lý do theo protocol, vẫn được lưu và thống kê.

### R5-T03-S03

Ma trận RQ → cấu hình → metric → claim khớp log/code; source ledger/path tra được, phân biệt lịch sử với bằng chứng mới. Giữ vấn đề/KPI chưa đạt và ghi kết quả xử lý H01–H08 còn mở.

## Phụ thuộc cần đối chiếu

[R5-T02](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R5-integration/pilot-and-war-game.md).

Đây là prerequisite candidate; đọc contract/evidence trước khi tạo relation, không chặn theo thứ tự thư mục.

## Bàn giao kỹ thuật

### Gói ZER-25 / ZER-55 ngày 08/11/2026

- Codex đọc AC sống lúc 2026-11-08T06:17:53.850Z. Checkout riêng `codex/zer-25-handoff` bắt đầu sạch từ `90efe53f9a35f140f168166a5bd8b74a6cae2abb`. Checkout chính có thay đổi ngoài scope, giữ riêng. Codex ghi; Claude review chỉ đọc.
- Phạm vi ghi là [gói evidence ZER-25](../../../evidence/ZER-25/README.md), ghi chú này và checkpoint NOW. Hành động là đối chiếu byte nguồn/dữ liệu, replay pilot và kiểm hồi quy ngoại tuyến. Boundary vận hành của ZER-53 là FORMAL_HOLD.
- Manifest trước review dữ liệu gốc, SHA-256 `869e91fc7f45d2dd456e75e5ce95ab15385aac31845725793f8108e81da3c8e8`. Replay kiểm 265 pin nguồn, 4.549 tệp batch, tái lập 12 ca và giữ 6 batch dừng cùng một lần chưa claim. Legacy 8 CSV/40 dòng, formal 0 run. Bộ kiểm hồi quy 57/57 đạt. [Biên bản](../../../evidence/ZER-25/verification.json).
- Gói bàn giao có sơ đồ, ma trận RQ → cấu hình → metric → claim, bảng/biểu đồ, H01–H08 và runbook. Còn thiếu chứng cứ dựng image lại, nơi giữ raw cho Hòa, và readiness formal §5. Pilot tại 6 GiB, kiểm 5,5 GiB chỉ idle.
- Claude đã review bản manifest trước `8e3838917baa3f134d732417a202196be370b06bd0d84abafd61fcafbdc790f8` từ gói trích gọn. Kết luận còn hai P1 về dựng lại image pilot và lưu bền/quyền truy cập. Codex đã xử lý các finding về ledger, cache ID, ma trận và pin đính chính. Kiểm delta ngoại tuyến, không cập nhật trạng thái issue. Chờ quyết định cách kiểm dựng lại và vị trí chia sẻ cho Hòa.

### Delta sau review trực tiếp dữ liệu gốc ngày 08/11/2026

- **F7** — Checkout bàn giao có [quyết định SQLi-only 28/10](../../SCOPE.md) đã ghi ở workspace chính. Giữ cam kết đăng ký gốc và đánh dấu lựa chọn 17/10 là lịch sử.
- **F8** — [Đính chính SD](../../../evidence/ZER-25/protocol-erratum.md) nằm trong tệp riêng đã pin. Sửa thử note pilot trên bản sao vẫn replay được. Sửa thử đính chính bị từ chối do lệch hash. Protocol ZER-53 giữ đúng hash đã khóa.
- **F9** — [Runbook](../../../evidence/ZER-25/runbook.md#phạm-vi-phát-lại-và-kiểm-hồi-quy) ghi phạm vi của ZIP và đầu vào bổ sung để chạy đủ 57 test. ZIP giữ nguyên, kiểm lại 9.968 hash, phát lại 12 ca trên bản giải nén với manifest `e8a8ef96141c8051124a5017c15211a213c7beb37dab7d7f3cf2949aa04a59ab`. Chạy riêng bộ kiểm với đủ đầu vào cục bộ đạt 57/57. [Biên bản kiểm delta](../../../evidence/ZER-25/verification.json).
- Đối chiếu lại AC sống trên Linear. Còn F1 về dựng lại image hoặc quyết định của Hoàng về AC, và F2 về nơi lưu ngoài máy này/quyền của Hòa. G5 chưa đóng. Formal giữ HOLD với 0 run. Gói delta chỉ gồm thay đổi tài liệu, pin và kiểm ngoại tuyến.

### Kiểm dựng lại fixture ZER-55 ngày 11/11/2026

- 265/265 file nguồn Runtime07 khớp hash đã niêm phong. Fixture mới build từ bốn file đã pin, chạy safe trong một container cô lập và đạt HTTP 200 cho /health và /ready. Readback sau test xác nhận không còn container thử. [Biên bản dựng và kiểm](../../../evidence/ZER-25/rebuild-verification.json).
- Lượt kiểm này dựng fixture cục bộ. Kết luận nhận dạng worker ban đầu đã được đính chính bên dưới.

### Đính chính ID image và xác minh worker ZER-55

- ID host `d85043c0…` thuộc fixture. Cả 12 `worker-cache-admission.json` ghi worker host `250be486…` và node `b2c14377…`. Receipt build ZER-42 ghi đúng cả hai digest này, với exit 0. Toàn bộ build context của bản worker lịch sử chưa được chứng thực.
- [CI worker image](https://github.com/EurusDevSec/Zero-Door/actions/runs/42453718435/job/128648162818) đã dựng image và kiểm worker từ chối thiếu cấu hình mà không mở client. 30/30 tệp worker ở revision CI `90efe53f9a35f140f168166a5bd8b74a6cae2abb` khớp từng byte với snapshot Runtime07. Pilot dùng ba image tự build. Bằng chứng hiện có xác nhận dựng lại fixture và worker. Khả năng dựng lại Nemesis từ snapshot chưa được xác minh.
- Manifest mới `d4ffcb7f38e2e74c69537ccd0a399e93afa96a279500f8ef1ea95920b391cb40` sửa riêng metadata image và giới hạn rebuild. Replay đối chiếu cả hai loại receipt, tái lập đủ 12 ca và kết quả thống kê gốc. Hai bản manifest gán sai ID bị từ chối. ZIP pilot giữ nguyên hash. [Biên bản](../../../evidence/ZER-25/rebuild-verification.json).
- Còn review đính chính để nghiệm thu ZER-55. Nơi lưu đã chốt ở mục dưới. Hoàng hoãn bàn giao tài liệu và viết báo cáo đến sau các R. Formal giữ HOLD.

### Bản lưu ZER-55 trên laptop

- Hoàng chốt lưu riêng tại `local-evidence/ZER-55/`, ngoài scratch và được Git bỏ qua. Bản lưu gồm ZIP gốc, manifest đã đính chính, replay/analyzer, protocol, tám CSV legacy, runbook và biên bản.
- Kiểm trực tiếp từ bản lưu: 9.968/9.968 thành viên ZIP khớp SHA-256, replay PASS 12 ca pilot và 40 dòng legacy, 0 formal. Kết quả và hash bản lưu ghi trong `local-verification.json` tại đó. ZIP gốc giữ nguyên.
- Bàn giao tài liệu cho Hòa và viết báo cáo đã hoãn. Review đính chính độc lập và trạng thái Linear chưa cập nhật trong lượt lưu cục bộ.

## Gói chốt kỹ thuật R5 để Claude review — 11/11/2026

Checkout `codex/zer-25-handoff`, HEAD `90efe53f9a35f140f168166a5bd8b74a6cae2abb`. Review đợt đính chính này theo các tệp dưới đây và kết quả review trước. Hoàng chọn bản lưu riêng trên laptop và hoãn gửi tài liệu cho Hòa, viết báo cáo và tổng hợp số liệu cuối đến sau khi các R hoàn tất.

| Tiêu chí | Kết quả để Claude review | Bằng chứng |
| --- | --- | --- |
| ZER-25 AC-01 | Sửa và kiểm lại lỗi pilot đã có bằng chứng. Kết quả offline 57/57 thuộc lượt kiểm trước, với các đầu vào cục bộ trong runbook. | [Các lỗi và kiểm lại](../../../evidence/ZER-25/README.md#các-lỗi-phát-hiện-trong-pilot) · [Biên bản](../../../evidence/ZER-25/verification.json) |
| ZER-25 AC-02 và ZER-55 AC-01 | Có bằng chứng dựng fixture và worker. Biên bản pilot xác nhận Nemesis trong 12/12 ca. Khả năng dựng lại Nemesis từ snapshot chưa được xác minh. Kho riêng trên laptop đã phát lại đủ 12 ca và giữ riêng 40 dòng legacy, 0 formal. Bối cảnh build đầy đủ của image worker lịch sử chưa được chứng thực. | [Biên bản dựng](../../../evidence/ZER-25/rebuild-verification.json) · [Runbook](../../../evidence/ZER-25/runbook.md) · `local-evidence/ZER-55/local-verification.json` |
| ZER-25 AC-03 | Tài liệu đã chuẩn bị. Bàn giao thực tế và xác nhận của Hòa được hoãn theo quyết định của Hoàng, tiêu chí chưa nghiệm thu. | [Gói tài liệu](../../../evidence/ZER-25/README.md) |

### Ba điểm cần review

1. Đối chiếu trong 12 ca cả `cache-admission.json` và `worker-cache-admission.json`. ID host fixture và ID worker host/node phải đi đúng trường manifest. Xác nhận receipt build ZER-42 khớp hai digest của worker và [CI build/smoke](https://github.com/EurusDevSec/Zero-Door/actions/runs/42453718435/job/128648162818) khớp revision với 30/30 tệp worker. Giữ giới hạn đã ghi về provenance của binary lịch sử.
2. Kiểm diff manifest chỉ trong metadata bản dựng. Replay phải giữ kết quả 12 ca, nguyên trạng các batch dừng, và từ chối manifest hoán đổi ID hoặc gán sai worker node. ZIP gốc giữ SHA-256 `82406f6e27e3a6baba7442c3d438d5c361e4e1ac99ae0135e5a4aca8fca60bff`.
3. Đọc biên bản phục hồi cục bộ và xác nhận quyết định hoãn AC-03 được ghi chính xác. Phần thực nghiệm chính thức giữ `FORMAL_HOLD`. Review có thể đọc hoặc phát lại dữ liệu đã lưu ở chế độ offline.

| Tệp khóa cho review | SHA-256 |
| --- | --- |
| dataset-manifest.json | `d4ffcb7f38e2e74c69537ccd0a399e93afa96a279500f8ef1ea95920b391cb40` |
| replay-pilot.py | `c17c1ecba2c0302529e342f9ab87f6cf47e9ae9d617a904674cf8b092ae85bc7` |
| rebuild-verification.json | `e773acb089f6ef8b4b06cfbc5fbd2120467a1dc31e1ea20583df9e1e3f1bf36b` |
| protocol ZER-53 | `c9a6950de02a0d7e33417194da82afef317ee69a3e429e06653cc844b81ecfd8` |
| local-verification.json | `628184d7a1b0276fa5f262363324b224fd3c1fcd548bd09c6f58bac04cb78ee4` |
| SHA256SUMS của bản lưu | `cb46922fa1327788d0ec8e5c0bb89e7ce5b9093e9f2d03edde22f808f661f074` |

Sau review, Hoàng nghiệm thu phần kỹ thuật và quyết định cách ghi AC-03 đã hoãn khi chốt ZER-25 và G5.

Quyết định hoãn đã được ghi và đọc lại trên [ZER-25](https://linear.app/zero-door/issue/ZER-25/chot-ky-thuat-va-luu-ho-so-r5). Các tiêu chí và quan hệ phụ thuộc hiện hành giữ nguyên trong lúc chờ review.

## Delta ZER-55 sau review đính chính R5

Claude đã xác nhận ba điểm của gói trước. Bản delta này xử lý hai lỗi còn lại trong ZER-55 trên HEAD `90efe53f9a35f140f168166a5bd8b74a6cae2abb`. Chỉ kiểm và replay dữ liệu đã lưu ngoại tuyến.

1. Manifest ghi ID host/node của `zer42-nemesis:e80bc554b7ef`. Replay kiểm đúng một bản ghi Nemesis trong `worker-cache-admission.json` của từng ca. `pods-latest.json` xác nhận container `zer21-transport` của pod `zer46-source-a` dùng đúng node ID trong 12/12 ca. Hai manifest thử gán sai host ID hoặc node ID, với hash manifest đã tính lại, đều bị từ chối.
2. [Biên bản dựng lại](../../../evidence/ZER-25/rebuild-verification.json) pin ZER-42 runtime-01 raw/009–011 cho Nemesis và ZER-46 runtime-04 raw/0037 cho fixture. Snapshot thiếu Dockerfile và requirements.lock của Nemesis. ZER-42 dùng context `agent-orchestrator/nemesis`; CI dùng `./agent-orchestrator`. Kết luận dựng lại của cả gói là `PARTIAL_REBUILD_VERIFICATION`.
3. [Runbook](../../../evidence/ZER-25/runbook.md) và README bản lưu dùng `py -3.11 -B`. Replay từ dữ liệu gốc và từ bản lưu đều PASS với Python 3.11.9, đủ 12 ca pilot, 40 dòng legacy, 0 formal. Bản lưu xác minh 20 tệp checksum và 9.968 thành viên ZIP.
4. Nơi lưu là `R:/_Projects/Eurus_Workspace/zero_door/local-evidence/ZER-55/`. [README](../../../evidence/ZER-25/README.md) ghi rõ Hoàng đã hoãn bàn giao AC-03. ZER-55 chờ Claude kiểm delta và Hoàng nghiệm thu. Formal giữ HOLD.

| Tệp dùng cho review delta | SHA-256 |
| --- | --- |
| dataset-manifest.json | `710d9846209a13bd1d7553d2b332b6abd54dea0fd2a1464b53cc2836669ecabf` |
| replay-pilot.py | `ec736dc3e7a9de0b6f391a56647af325d3edd70ce6775342b4128b999c78a407` |
| rebuild-verification.json | `1e98bc9d00dd175e53f1a5063da2c8c3a29a6d50093362b68703b0213e72b2b6` |
| runbook.md | `cfce59c7d901dfc0ae75ccc3c7658996ae659c87f4d27088bd6c305562805b3f` |
| README.md của ZER-25 | `8be0ebbe07f9df56d3d3390fee1f566ba8501c8d657a10b32ca75392ac583b47` |
| README.md của bản lưu | `948d88055dfdf9ddb4b473a0255cf4f48e7c65b5ecb8b78c4ce515a7f18285e1` |
| verify-local.py | `fcb9c4355720db8c7acc1821a7cacfabbeec3ce1780c69717673c878404d8e45` |
| local-verification.json | `6f807e21978f2e1490dcf0a60893ca09f571041c1c7d36269f26c1e334f4b152` |
| SHA256SUMS | `36bdb71132b9dc5b0df558fd12999f349b630f62819ae016ec541af6c4151e6e` |
| ZIP gốc | `82406f6e27e3a6baba7442c3d438d5c361e4e1ac99ae0135e5a4aca8fca60bff` |
| Protocol ZER-53 | `c9a6950de02a0d7e33417194da82afef317ee69a3e429e06653cc844b81ecfd8` |

Claude kiểm lại các receipt, giới hạn dựng lại Nemesis và lệnh phát lại trên đúng các hash trên. Dùng bản lưu riêng tại chỗ để kiểm ngoại tuyến.

## Nghiệm thu ZER-55 với ngoại lệ Nemesis — 11/11/2026

Claude kiểm độc lập đúng các hash của delta. Cả 12/12 ca khớp hai ID Nemesis, chín manifest sai hoặc thiếu ID bị từ chối, và kết quả replay bằng Python 3.11.9 trùng giữa dữ liệu gốc và bản lưu. Phạm vi kiểm của Claude là delta ngoại tuyến.

Hoàng chấp nhận ngoại lệ dựng lại Nemesis cho ZER-55. Giữ kết luận `PARTIAL_REBUILD_VERIFICATION`. Biên bản xác nhận image lịch sử trong pilot và nguồn được niêm phong. Việc dựng lại Nemesis từ snapshot chưa được chứng minh và image Nemesis phải được pin lại trước formal. Bản ZIP riêng lưu tại laptop.

Hoàng duyệt commit, push và mở PR cho mã replay và hồ sơ chia sẻ. ZER-25 AC-03 vẫn hoãn, G5 còn mở và formal giữ `FORMAL_HOLD`.

## Kiểm chứng bổ sung bản dựng Nemesis từ nguồn Git

- Revision nguồn Runtime07 `7f806f13bc989934b7c880dcef5dfb6897c73695` và revision CI `90efe53f9a35f140f168166a5bd8b74a6cae2abb` có cùng cây Git `agent-orchestrator`. Đối chiếu khớp 13 tệp Nemesis, 14 tệp event_pipeline và SHA-256 của 16 tệp trong hai thư mục đã niêm phong. Hai đầu vào thiếu trong ZIP có trong Git đúng revision.
  - `agent-orchestrator/nemesis/Dockerfile` có SHA-256 `29ef8c59d2508a42fd21998a4bba9e8ab6f8ad2b44fb176ac6816cbe10d4e6eb`.
  - `agent-orchestrator/nemesis/requirements.lock` có SHA-256 `f7bccfb357471fe02404c8788071f9aa672bbca36bb51f823c7e228a1d5246a6`.
- [Job CI Nemesis](https://github.com/EurusDevSec/Zero-Door/actions/runs/42453718435/job/128648162817) xác nhận **Build nemesis** và **Import smoke test — nemesis** cùng SUCCESS. Đây là bằng chứng đã dựng và kiểm import Nemesis từ cây nguồn Git trùng revision pilot, với context `./agent-orchestrator`.
- Image cache dùng trong pilot được nhận dạng trong 12/12 ca. Biên bản ZER-42 raw/009 ghi một công thức khác với context `agent-orchestrator/nemesis`, trong đó bước COPY cuối là static và không có các bước COPY session, session_cli và event_pipeline của Dockerfile ở revision pilot. CI hiện có chứng minh được khả năng dựng từ Git theo công thức CI. Việc tái tạo image cache lịch sử bằng công thức gốc vẫn chưa được xác minh. Bằng chứng bổ sung nằm ngoài gói hash đã review.
- Phần công bố đang chờ xác nhận đích repo công khai. Formal giữ HOLD.

## Quyết định AC-03 — 11/11/2026

Hoàng bỏ yêu cầu gửi tài liệu cho Hòa và sẽ tự dùng hồ sơ R5 để viết báo cáo sau khi các R hoàn tất. AC-03 vẫn yêu cầu hồ sơ truy được về nguồn, giữ nguyên ma trận RQ → cấu hình → metric → claim, giới hạn KPI và theo dõi H01–H08. Quyết định này thay các ghi chú cũ về việc hoãn bàn giao trong hồ sơ đã review. AC-03 cần được đối chiếu với tiêu chí mới trước khi nghiệm thu. [ZER-25](https://linear.app/zero-door/issue/ZER-25/chot-ky-thuat-va-luu-ho-so-r5).

## Nghiệm thu hồ sơ theo AC-03 đã cập nhật — 11/11/2026

**Kết quả: AC-03 đạt.** Hồ sơ được lưu để Hoàng sử dụng khi viết báo cáo. Dùng mục này làm điểm vào hiện hành. Các mô tả bàn giao trong gói review trước là lịch sử.

| Yêu cầu AC-03 | Đối chiếu |
| --- | --- |
| Sơ đồ, protocol và giới hạn | [Luồng hệ thống và ma trận câu hỏi](../../../evidence/ZER-25/README.md#luồng-hệ-thống-và-ma-trận-câu-hỏi) tách B0/B1/B2, C0/C5, tín hiệu và claim. [Protocol ZER-53](../../../evidence/ZER-53/protocol.md) và [đính chính SD](../../../evidence/ZER-25/protocol-erratum.md) giữ hash đã review. RQ2/B3 ngoài phạm vi hiện hành. |
| RQ → cấu hình → metric → claim | [Bảng tái tính ZER-24](../../../evidence/ZER-24/README.md#ac-01--tái-tính-runtime07) khớp phân tích đã niêm phong. B1/B2 mỗi nhóm containment fixture 2/2 ca C5. C0 có 0/6 chặn nhầm, B2 có 2/2 ABSTAIN, benign fixture 12/12. Chênh workflow B2−B1 là +25,180 s C5 và +3,789 s C0. Cả 12 tọa độ của [biểu đồ](../../../evidence/ZER-25/pilot-workflow.svg) khớp `response_workflow_ms`. Kết quả là mô tả pilot với 2 ca mỗi ô. |
| Sổ nguồn và tách dữ liệu | Kiểm đủ 21 đường dẫn/anchor nội bộ trong README. [Manifest](../../../evidence/ZER-25/dataset-manifest.json) khóa 8 CSV legacy/40 dòng, 12 ca pilot, 6 batch dừng và 1 cửa sổ trước claim. Formal 0 ca. [Runbook](../../../evidence/ZER-25/runbook.md) dẫn bản lưu riêng trên laptop. Replay lần này bằng Python 3.11.9 đạt PASS sau khi kiểm 20 tệp và 9.968 thành viên ZIP. |
| KPI chưa đạt và H01–H08 | [Bảng KPI ZER-24](../../../evidence/ZER-24/README.md#ac-04--kết-quả-kpi-và-giới-hạn) giữ MTTD/reaction UNKNOWN, MTTR/TotalRecovery/M7/M8 NOT_EVALUABLE_BY_DESIGN, uptime NOT_MEASURED và các mục ngoài phạm vi. [Bảng H01–H08](../../../evidence/ZER-25/README.md#h01h08-và-sổ-nguồn) đủ tám mục, có nguồn hoặc việc còn mở. Giữ riêng các cam kết gốc chưa đáp ứng trong phạm vi thu hẹp. |

Bằng chứng này hoàn tất phần hồ sơ của AC-03. Phần công bố ZER-55 và các điều kiện còn lại của G5 được theo dõi riêng. Formal giữ HOLD.

## Gói chốt R5 để Claude review lần cuối — 11/11/2026

Đọc [README hồ sơ R5](../../../evidence/ZER-25/README.md) và [runbook](../../../evidence/ZER-25/runbook.md) cùng các kết quả dưới đây. Review ngoại tuyến trên đúng commit được bàn giao.

| AC hiện hành | Kết quả đối chiếu | Claude kiểm lại |
| --- | --- | --- |
| ZER-25 AC-01 | Bảng lỗi pilot nối hiện tượng, bản sửa và phép kiểm bị ảnh hưởng. Bộ hồi quy có đủ đầu vào cục bộ đạt 57/57 trong lượt chốt. Bản phân tích Runtime07 phát lại khớp seal. Các lần dừng, nguyên nhân tài nguyên UNKNOWN và B2/C0 chấm sai vẫn được giữ. | Đối chiếu bảng lỗi với nguồn và biên bản ZER-52. Kiểm log 57 test và phạm vi của driver. |
| ZER-25 AC-02 / ZER-55 AC-01 | Manifest khóa method, hash và run IDs. Replay giữ 12 ca pilot, 8 CSV legacy/40 dòng, 6 batch dừng, 1 cửa sổ trước claim và 0 formal. Có bằng chứng build fixture, worker và Nemesis từ các đầu vào đã đối chiếu. Ngoại lệ đã duyệt của Nemesis còn giới hạn ở tái tạo image cache lịch sử. | Đối chiếu ba build receipt và hai job CI. Kiểm Git source tree của Nemesis khớp revision pilot. Kiểm từ bản lưu và xác nhận ZIP, protocol, analyzer, manifest và replay driver giữ hash. |
| ZER-25 AC-03 | Linear đã đánh dấu hoàn tất. Sơ đồ, protocol, bảng/biểu đồ, sổ nguồn, KPI và H01–H08 dùng cho Hoàng tự viết báo cáo sau các R. Đã kiểm 12 tọa độ biểu đồ và 22 liên kết nội bộ trong README hiện hành. | Xác nhận AC-03 khớp nội dung Linear mới. Đối chiếu claim với bảng pilot và giới hạn. |

Báo kết quả theo từng AC. Ghi phát hiện chặn nghiệm thu cùng đường dẫn và đối chiếu cụ thể. Ghi riêng phần provenance lịch sử và cổng formal. Bản chốt cục bộ chờ review và duyệt công bố công khai. Hai issue vẫn mở. Formal giữ HOLD.

### Hash của bản chốt

| Artefact | SHA-256 |
| --- | --- |
| README ZER-25 | `1c68deb0654227d367a783d3868fbf3d83a15b78a509121013d55d1351dcb8ff` |
| Runbook | `506b205ef0149fbeffdf5f8a63f993d6f969b3263f1e99106ae3e3ee72a3eda1` |
| Biên bản dựng lại gốc | `1e98bc9d00dd175e53f1a5063da2c8c3a29a6d50093362b68703b0213e72b2b6` |
| Manifest | `710d9846209a13bd1d7553d2b332b6abd54dea0fd2a1464b53cc2836669ecabf` |
| Replay | `ec736dc3e7a9de0b6f391a56647af325d3edd70ce6775342b4128b999c78a407` |
| Analyzer | `8a0594ff6264867b91e9fc0dfd754e27480c41f4b6e334307c03be836ee013c9` |
| Protocol ZER-53 | `c9a6950de02a0d7e33417194da82afef317ee69a3e429e06653cc844b81ecfd8` |
| ZIP riêng trên laptop | `82406f6e27e3a6baba7442c3d438d5c361e4e1ac99ae0135e5a4aca8fca60bff` |
| SHA256SUMS bản lưu | `f1a96ae44071bbb20d3d72d5b8c5600abe602d7bfccd4555e935f3082cd6f785` |
| local-verification.json | `0513d68642bb59eaf4f4bdccbb6962db079fc62622d5993ec8c3fb4ca9b916c2` |
| Log 57 test ngoại tuyến | `cf19a0b7eac6958f052a502c6f4990e4de2b83b175189d28222de120d512f5f1` |

Log 57 test: `scratch/zer25-work/r5-final-candidate-offline.log`. Bản lưu: `local-evidence/ZER-55/`. Biên bản phát lại ghi 20 tệp kiểm checksum và 9.968 thành viên ZIP, PASS trên Python 3.11.9.
