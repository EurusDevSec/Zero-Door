# R1 — transport sự kiện và ranh giới evidence

Contract: [zd-event/1.0.0](../design/r1-event-contract.md). Issue:
[ZER-9](https://linear.app/zero-door/issue/ZER-9/thong-nhat-hop-djong-su-kien-va-luu-dau-vet).
Trạng thái triển khai/kiểm: [verification](../evidence/ZER-9/verification.md).

## Luồng và quyền

Harness cấp `run_id`, `trial_id`, slot `incident_id` trước onset, kể cả C0; War Game bỏ
`incident_id` khỏi O. Harness gửi RUN_CONTEXT rồi TRIAL_CONTEXT rỗng tới gateway O,
đợi receipt bền trước khi bắt đầu producer. Không đổi context sau đó. Factory sinh
event/alert/decision/action/call ID UUIDv4 và seq theo instance/stream; instance mới khi
restart. Giữ cùng envelope/event_id khi gửi lại, không dùng giờ ingest để sửa mốc thiếu.

Gaia hiện có → HTTP có source token → gateway O → Kafka topic O có HMAC → recorder
append/fsync → HTTP O-only → Hephaestus hiện có → DECISION giữ ID/cause → cùng recorder.
Kafka ack chưa là receipt bền: client đợi thấy đúng event_id trong archive. Consumer chỉ
commit offset sau fsync hoặc quarantine bền. Giao lại được lưu và khử trùng ở consumer;
cùng event_id khác nội dung là INTEGRITY_ERROR, không biến thành quyết định mới.

Mọi rejection đi qua một đường quarantine (HTTP, Kafka, sau seal). Lỗi dữ liệu của một message
(không phải UTF-8/JSON object, NaN/Infinity, JSON lồng quá 32 tầng, sai chữ ký, sai schema/nguồn/plane,
thiếu hoặc lệch context, INTEGRITY_ERROR, đến sau seal) được ghi+fsync rồi mới commit, recorder xử lý
tiếp message sau. Message chưa xác thực chỉ lưu bytes gốc ở phạm vi archive, không gán nguồn/run.
Giới hạn độ sâu (`MAX_DEPTH` 32 tầng container cả envelope; live-11 sâu 4) được kiểm lặp, không đệ
quy, trước validator/binding/audit; HTTP, Kafka và `Archive.ingest` trực tiếp cùng ra INVALID. Input đã
xác thực (token HTTP, HMAC Kafka) vẫn gán run/nguồn nhưng chỉ lưu bytes gốc và hash, không lưu bản
parse; JSON sâu tới mức decoder không đọc được là INVALID ở phạm vi archive. Lỗi I/O, archive
hỏng, lỗi Kafka/commit hoặc lỗi chương trình làm recorder dừng, không commit; `/readyz` trả 503.
Lỗi Kafka/commit được giao lại khi restart bridge; lỗi archive cần restart process (xem dưới).
Binding+append của mỗi event là một giao dịch dưới khóa archive.

Gateway H chạy process, UID, credential và PVC riêng. Nó không gửi vào broker legacy,
không có API đọc H. Gateway O không mount PVC/key H. O actor không truy cập trực tiếp
Kafka, Elasticsearch, Prometheus hoặc Kubernetes API. Chỉ gateway O có đường tới broker
và telemetry. PromQL được allowlist từ source Gaia đã đóng băng; log proxy luôn AND
namespace target-app, chỉ `_search` trên index cho phép, kiểm lại namespace của hits.
Không loại IP/request hoặc lịch sử vận hành tự nhiên bằng từ khóa.

Không dùng dashboard Nemesis legacy làm giao diện BM: nó chứa thông tin H. Gateway này
không cung cấp lịch, control log, scorer output, file browser hay query tùy ý. Mỗi O actor có
một Secret riêng: Gaia `detector`+`reader`, Hephaestus `decision_rules`+`reader`, operator
`operator_console`+`reader`, observer chỉ `reader`. Client từ chối file có role khác (kể cả
`harness`/`evaluator` hay role của actor khác). Key server O và key server H sinh riêng, không tái
sử dụng, và gateway từ chối file key có role ngoài plane của nó; giữ ngoài Git.

## Adapter hiện tại

`ZD_EVENT_URL` bật R1; cấu hình thiếu sẽ dừng, không tự quay về legacy. Cần có:

```bash
export ZD_EVENT_URL=http://events-o.zd-r1-events.svc.cluster.local:8000
export ZD_O_KEYS_FILE=/keys/keys.json   # file riêng của actor này, đúng {role của actor, reader}
export ZD_RUN_ID=run_UUIDV4_HEX
export ZD_TRIAL_ID=trl_UUIDV4_HEX
export ZD_PRODUCER_VERSION=REVISION_OR_IMAGE_DIGEST
export ZD_CLOCK_ID=NEUTRAL_CLOCK_ID
export ZD_CLOCK_SOURCE=UNKNOWN
```

Đây là ví dụ tên biến, phải điền ID UUIDv4 thật từ harness; không chạy nguyên placeholder.
Một process agent gắn đúng một trial: `ZD_RUN_ID`/`ZD_TRIAL_ID` cố định lúc khởi động, cooldown
Gaia và pending/refused của adapter nằm trong RAM. Harness phải khởi động process mới cho mỗi
trial và dừng process cũ trước TRIAL_CONTEXT kế tiếp; không tái dùng process giữa trial.

Gửi lại: timeout, lỗi kết nối, 5xx/429/408 hoặc ack Kafka chưa thấy receipt bền thì giữ và gửi lại
đúng envelope cũ. 4xx khác (422 rejection, 409 sau seal) là kết luận cho envelope đó: gateway đã
quarantine; adapter bỏ envelope, alert sau có ID/timestamp/giá trị mới, và không sinh lại DECISION.
Gaia dùng telemetry proxy theo URL R1, không kết nối broker trực tiếp. Hephaestus chỉ
phát RULES DECISION ở B1. B0/B2/B3/BM không tự fallback sang rules. B2/B3 cần adapter LLM
và fallback có provenance ở R4; BM cần operator console. R1 chặn `/heal/trigger` và
`/experiment/reset` legacy bằng 409 (không đổi replicas, không xóa state) và không init K8s executor. Không phát API_ACCEPTED, ACTION_COMPLETED hay recovery giả.
Guard/executor/probe/scorer thật vẫn thuộc các issue sở hữu; bật transport không bật heal.

`schema_version` và trường bắt buộc được kiểm khi nhận. Đây là validator transport,
không thay scorer về clock normalization, hồi phục, containment, quy công hay đủ coverage.
Các event H của probe/evaluator chỉ được nhận từ đúng source; chức năng đánh giá không
được triển khai trong ZER-9. Source hiện hành chưa bật R1 tiếp tục là legacy, không dùng
làm dataset R1. Template này phải được áp cùng ranh giới mạng khi bật profile, không chỉ
thêm biến môi trường vào pod legacy có quyền broker rộng.

## Kiểm offline

```bash
python -B tests/test_event_pipeline.py
python -B tests/test_event_pipeline_regressions.py
# Cần cả dependencies của hai agent; không truy cập lab:
scratch/zer9/venv/Scripts/python.exe -B tests/test_event_agents.py
bash tests/shell/run.sh
python -B tests/test_nemesis_consumer.py
bash infrastructure/scripts/verify-event-pipeline.sh --help
```

Gaia/Hephaestus Dockerfile dùng build context `agent-orchestrator/`, để copy module dùng
chung. Script Bash và CI đã chọn context/Dockerfile tương ứng. Nemesis không đổi context.

## Kiểm live có giới hạn

Chỉ chạy sau quyền vận hành cụ thể cho gói này. Script kiểm `k3d-zero-door`/
`desktop-linux`, tạo namespace mới `zd-zer9-<random>` từ [template](../../infrastructure/manifests/r1-event-pipeline.yaml),
hai PVC 64Mi, hai recorder (requests tổng 50m CPU/64Mi RAM, limits 300m/224Mi), và một
pod O (10m/16Mi requests, 100m/64Mi limits). Cleanup dùng thêm một pod ngắn hạn cùng ngân sách sau khi recorder O đã dừng. Không dùng PVC hay Deployment hiện hữu.

COPY-only image từ Gaia image local, không pull/cài package trong build; import image
vào cluster. Topic `zd.events.o.<random>` và consumer group riêng không đụng offset/topic
legacy. Gửi payload SYNTHETIC qua hàm `publish_alert` của source Gaia thật và decision
matrix của source Hephaestus thật, không khởi động loop auto-heal. Đây là bằng chứng
transport, không phải bằng chứng phát hiện fault hoặc KPI. Clock Windows ghi UNKNOWN.

```bash
# Python của môi trường kiểm cần dependencies đã khai báo của Gaia/Hephaestus và PyYAML.
# Có thể chọn venv cục bộ bằng ZD_PYTHON, không đổi Python toàn máy.
ZD_PYTHON=scratch/zer9/venv/Scripts/python.exe \
  bash infrastructure/scripts/verify-event-pipeline.sh --live --allow-temporary-es-ingress \
    --output scratch/zer9/live-NEW
```

Đường output phải mới; thay live-NEW bằng tên lượt chưa tồn tại. Cờ
`--allow-temporary-es-ingress` cần quyền riêng: tạo một NetworkPolicy mới trong monitoring,
chỉ namespace nonce mới + pod events-o được tới Elasticsearch TCP9200, rồi xóa đúng UID/nonce.
Policy monitoring hiện hữu không đổi. Nếu không được phép, không coi query log đã kiểm.

Profile local này khóa nodeSelector kubernetes.io/hostname=k3d-zero-door-server-0 cho
recorders và O actor. Chẩn đoán19/10: node agent có0 chain KUBE-POD-FW trong snapshot
iptables, node server có20; probe ở agent vẫn nối H/Kafka/Prom qua40 vòng, trong khi probe
trên server từng chặn được. Đây là enforcement khác nhau theo node, không chỉ startup.
Không sửa firewall/CNI toàn lab trong ZER-9. Không tự bỏ nodeSelector hoặc fallback sang
agent khi server thiếu chỗ. Rollout Gaia/Hephaestus/operator thật phải giữ cùng ràng buộc
placement và kiểm quyền trước trial; profile hiện tại chỉ chứng minh đúng node đã kiểm.

Readiness `/readyz` của recorder O chỉ Ready khi bridge Kafka còn sống và đã xử lý hết các offset
có trên topic lúc khởi động (event đã ack bởi process trước). H và O chỉ Ready khi archive mở được
và chưa gặp lỗi archive trong process (`ARCHIVE_FAILED:<lý do>`, xem mục Archive).
Liveness `/livez` chỉ phản ánh HTTP, không restart pod để che archive hỏng. Cả hai không chứng
minh quyền mạng: NetworkPolicy hội tụ bất đồng bộ trên node có enforcement; node không có
enforcement sẽ không hội tụ.
Không gắn dữ liệu nhạy cảm hoặc bắt đầu trial khi pod vừa Running. Verifier dùng dữ liệu
synthetic và cổng kiểm quyền trước mọi event trial: DNS phải phân giải, O API trả200,
bốn đường cấm phải bị chặn qua ba vòng liên tiếp, trần40 vòng; O API chưa sẵn sàng
cũng giữ gate đóng và được ghi lại. Lưu cả những vòng còn mở;
chưa đạt thì dừng, không suy cách ly từ YAML hoặc chờ một khoảng cố định. Mọi rollout
actor thật phải áp cổng kiểm quyền tương đương trước khi bắt đầu nghiên cứu; lượt tạm
không chứng minh không tồn tại cửa sổ hở ngay khi pod mới sinh. Không đưa harness key/raw
vào O pod ngay cả trong giai đoạn này.

Query thật có tối đa3 lượt kiểm, giữ kết quả lỗi từng lượt; hết trần phải FAIL. Không đổi
query hoặc trả dữ liệu thay thế để nhận PASS. Guard nguồn lực thiếu Metrics API dừng
trước build/deploy. Script kiểm quyền từ pod O thật, restart recorder, đối chiếu PVC/export,
rồi seal raw.
Chỉ sau khi cả hai export khớp hash mới xóa topic tạm và namespace mới mà UID/nonce đã
đối chiếu. Trước xóa topic phải dừng recorder subscriber; pod cleanup chỉ có client admin
cho đúng tên topic, đợi Kafka xác nhận topic vắng để tránh auto-create lại. Dừng các
port-forward do chính script tạo. Không có attack, heal, reset, LLM
hoặc sửa deployment lab hiện hành. Nếu FAIL, giữ namespace/PVC để chẩn đoán; không tự
xóa bằng wildcard. Không tự chạy lại khi lỗi quyền hoặc guard tài nguyên.

Ranh giới của profile này (ZR9-05): verifier import Gaia/Hephaestus vào chính process của nó trên
host, nối O qua port-forward, mỗi agent đọc file key riêng; process đó còn giữ key server và
context kube quản trị. Cổng kiểm quyền chỉ chứng minh cho pod observer, không cho process agent.
Receipt ghi `agent_execution`. Rollout actor thật theo [kế hoạch runtime](../evidence/ZER-9/fix-01/runtime-plan.md).
HARNESS_MANIFEST của verifier khai namespace/topic/image/nonce/pod/PVC/Secret/header do harness
tạo (NEUTRAL). Đối chứng rò có ca nhãn trong stream/target với ID hợp lệ, chỉ bắt được qua
LABEL_IN_METADATA; nhãn GROUND_TRUTH dùng cho đối chứng là synthetic trong RAM, không gửi lên H.
`/seal` trả 409 khi còn event đã ack chưa bền; verifier thử lại có giới hạn, hết lượt là FAIL.

Thư mục output chứa `private/` với token — KHÔNG commit/chia sẻ cả thư mục. Chỉ chọn
receipt đã soát và `export/H`, `export/O` sau run. Receipt/export giữ revision/hash,
transport offsets, timestamp, kết quả và giới hạn. `--help` không truy cập lab.

## Archive và audit sau trial

Raw giữ envelope không sửa trong bản ghi ingest. Kho ghi nối, một writer có OS file lock;
restart đọc lại hash/index. File đứt cuối dòng, dòng không đọc được hoặc hash sai làm dừng, không tự
truncate.

**Lỗi archive là sticky (fail closed).** Hai loại lỗi làm archive của process dừng hẳn, cho cả H và
O, có hay không có Kafka:
- ghi không chắc chắn: append raw/quarantine/late, fsync, tạo thư mục run, ghi seal;
- đọc nguồn archive thất bại: stat/lstat, open, read, hash hoặc copy-đọc trên file/thư mục của
  archive (raw, `rejections.jsonl` của run và ở gốc, `late.jsonl`, `manifest.json`, thư mục run) khi
  ingest/quarantine kiểm run đã seal chưa, `records()`/`GET /events`, seal hay export; dòng bị cắt,
  hỏng, hash lệch, symlink. File tùy chọn chưa tồn tại là trống; mọi lỗi khác (EIO, quyền) không bao
  giờ được coi là trống hay bị bỏ qua.

Sau đó: `/readyz` 503 `ARCHIVE_FAILED:<lý do>` (tên lỗi I/O, hoặc `INTEGRITY` cho dữ liệu hỏng),
`/livez` vẫn 200; mọi request ghi sau đó (kể cả input sai, vì không quarantine được) trả 503, không
201/202; `GET /events` trả 503 NOT_DURABLE; O với Kafka không publish thêm; recorder dừng, không
commit; `/seal`, `records()` và export từ chối; không thêm byte nào vào archive. Lỗi dữ liệu đã
quarantine thành công và lỗi chương trình xảy ra trước khi ghi không làm archive dừng. Lỗi ở thư mục
đích của export (tạo, ghi, fsync, chmod, bản sao đọc lại lệch hash) chỉ làm export đó thất bại
(OSError); archive nguồn vẫn Ready. Process không tự truncate, xóa lỗi, reset hay sửa file; restart
bridge trong cùng process không xóa được lỗi.

Phục hồi là restart process, việc của operator. Khi mở lại, archive kiểm lại mọi dòng:
- Dòng cuối bị cắt hoặc hỏng (ghi dở): archive không mở, pod không Ready. Operator giữ nguyên bytes
  (sao chép cả thư mục plane làm bằng chứng), quyết định cách xử lý và ghi lại; code không tự làm.
- Dòng đủ nhưng fsync báo lỗi: archive mở lại được và dòng đó có mặt dù producer nhận 503; producer
  gửi lại cùng envelope thành DUPLICATE (ít nhất một lần, không mất). Độ bền của dòng đó khi mất điện
  chưa được chứng minh; operator ghi run là nghi vấn nếu xảy ra trong trial.
- Lỗi không để lại byte nào: mở lại bình thường; Kafka giao lại message chưa commit.
- Lỗi đọc nguồn thoáng qua: mở lại bình thường nếu file đọc được và kiểm hash/dòng đạt. Nếu khi mở
  vẫn không đọc được, archive không mở, pod không Ready; operator kiểm đĩa/quyền, không sửa file.
Kiểm offline dùng fault injection (patch append/fsync, OSError EIO tại open/read/stat của file
nguồn), không phải thử đĩa hỏng hay mất điện thật.
Manifest ghi số dòng/bytes/hash, seq đầu/cuối và số seq phân biệt theo nguồn (SEQ_GAP khi số
nhỏ hơn last−first+1), khoảng ingest và schema version (`archive_format: 2`). Seal cũ (live-11)
không có trường mới vẫn mở, seal lại và export không đổi raw.

Bố cục một plane: `run_*/{plane}.jsonl` raw; `run_*/rejections.jsonl` quarantine trước seal (hash
nằm trong seal); `run_*/late.jsonl` mọi input của run đến sau seal (LATE_INGEST hoặc rejection,
ngoài hash đã seal); `rejections.jsonl` ở gốc cho input UNSCOPED hoặc chưa xác thực. Mỗi dòng
quarantine mang hash riêng (envelope hoặc bytes gốc); sửa một dòng làm archive không mở được.
Bản trùng nguyên văn của raw đã seal hoặc của bản late đã lưu không ghi thêm và không đổi export.
Run chỉ có rejection vẫn seal được, với raw rỗng.

O với Kafka: `/seal` dựng hàng rào, chờ các submit đang dở và chờ recorder xử lý đến offset đã ack
của run; chưa xong trong 10 s thì 409 SEAL_PENDING và run chưa seal. Submit đến khi đang seal
đợi hàng rào; sau seal thì vào `late.jsonl` và nhận 409.

Evaluator có thể dùng `Archive.export(run_id, destination)` khi writer đã dừng và giữ
quyền riêng đối với H/O. `/seal` chỉ nhận evaluator token; nó không cung cấp raw qua HTTP.
Export vào thư mục mới, giữ khóa archive khi chép, kiểm lại hash từng file và ghi `export.json`:
seal, raw, rejection, late, và quarantine phạm vi archive (`archive-scope/`, nhãn
ARCHIVE_GLOBAL_NOT_ATTRIBUTED_TO_RUN, không phải của run). Export chỉ hoàn tất khi lời gọi trả
về; export thất bại có thể để lại bản sao dở trong thư mục đích, bỏ thư mục đó và export lại vào thư
mục mới. Export là bản sao có hash/chmod readonly, không là WORM chống quản trị viên máy. Trên POSIX có fsync file và thư mục cha khi tạo;
Windows không fsync được thư mục. Chưa có bằng chứng mất điện/phục hồi ổ đĩa; kiểm restart process
không chứng minh điều đó.

`audit.audit` nhận H/O đúng trial và prompt/query đã lưu, kiểm canary, khóa cấm, nhãn trong
metadata, tài nguyên harness NEUTRAL/SECRET/OBSERVABLE và allowlist. Prompt phải khớp hash.
SECRET không gặp ở O và không `o_visible` là sạch; gặp hoặc `o_visible` là HARNESS_SECRET; lớp lạ vẫn UNKNOWN.
Tập nhãn gồm `case_class`/`variant_id`/`cause`, `attack_type` và `reveal_terms`, gom trước khi quét
ID/`stream`/`source_instance`/`target`. So khớp theo dãy token nguyên sau chuẩn hóa dấu nối mục 8.3,
không so chuỗi con, nên phần hex của ID không gây báo nhầm; quy tắc NEUTRAL dùng cùng cách so.
Thiếu manifest, prompt, audit lịch BM hoặc bằng chứng quyền thì UNKNOWN. Không suy CLEAN
từ việc payload nhìn sạch. Trạng thái access_complete chỉ được đặt sau phép kiểm runtime
đúng profile; không tái sử dụng kết quả namespace tạm cho một rollout khác.

Chỉ sau live/review/merge/Hoàng nghiệm thu mới được đề xuất Done. ZER-9 không đóng G1.
# Kiểm actor thật trong pod (ZER-9)

Entry point bổ sung: `bash infrastructure/scripts/verify-event-actors.sh --live --allow-temporary-es-ingress --output scratch/zer9/<thư-mục-mới>`; chỉ chạy sau khi có quyền vận hành đúng [phạm vi actor](../evidence/ZER-9/codex-fix03-review/runtime-scope.md). Không chạy đồng thời với verifier host. Dùng Docker `desktop-linux` và kube context `k3d-zero-door`; preflight thiếu metrics hoặc node memory trên 80% thì dừng trước build/deploy. Không sửa hay dựng lại cluster để vượt guard.

Verifier build ba Dockerfile production, import image tag nonce, tạo namespace/topic riêng, hai PVC64Mi và role Secret riêng. Overlay [r1-event-actors.yaml](../../infrastructure/manifests/r1-event-actors.yaml) chỉ cho hai actor vào gateway O và DNS. Init gate chạy trong từng pod với cùng labels/node/network; chỉ sau ba vòng liên tiếp O200 và H/Kafka/ES/Prometheus trực tiếp bị chặn mới khởi động actor. Các vòng hở do policy đang hội tụ vẫn được giữ trong receipt. Gaia tắt lifecycle polling trong profile transport này; query/publish dùng code production bên trong pod qua lệnh kiểm bounded. Hephaestus chạy FastAPI startup và consumer R1 bình thường. Không chứng minh phát hiện fault, KPI, healing hay LLM.

Phép kiểm gồm key theo vai trò, từ chối source giả/seal/reader POST, healer/reset409, Prometheus và Elasticsearch qua client Gaia thật, synthetic DETECTED → Kafka → RULES DECISION trong pod Hephaestus, redelivery, poison message và good-next, recorder restart, seal và late ingress. Sau khi dừng actor và recorder, evaluator riêng mở PVC bằng UID đúng plane và gọi `Archive.export` vào thư mục mới; từng file được kiểm hash trên host, quarantine/late được xuất cùng raw. Không có endpoint export/raw dành cho O actor. Exporter có quyền filesystem của evaluator; không phải quyền của Gaia/Hephaestus.

Cleanup chỉ sau khi đối chiếu export: dừng O subscriber, xóa đúng topic nonce và xác nhận vắng; kiểm UID/nonce namespace và rule ES trước khi xóa, đợi namespace/PVC tạm biến mất, dừng port-forward do verifier sở hữu. Lỗi giữ receipt và tài nguyên tạm để chẩn đoán, không tự chạy lại hoặc xóa bằng chứng. Private key chỉ ở thư mục `private` dưới scratch (gitignored), không chia sẻ/commit. Test offline của verifier: `python -B tests/test_event_actor_verifier.py`.
