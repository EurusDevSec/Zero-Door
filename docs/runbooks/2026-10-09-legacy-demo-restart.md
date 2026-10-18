# Chạy lại demo ZERO DOOR bản cũ trên Windows

Hướng dẫn lệnh đã chuyển sang Bash ngày 18/10/2026. Phần quan sát/ngày/revision 09/10 bên dưới vẫn là lịch sử. Chức năng entry point mới, mặc định thực nghiệm và quản lý tunnel xem [Bash tooling](R:/_Projects/Eurus_Workspace/zero_door/docs/runbooks/bash-tooling.md).

Ngày hướng dẫn: 09/10/2026. Mục tiêu: mở lại bản trước recovery roadmap để quan sát chức năng hiện có. Hướng dẫn đã đối chiếu script/mã tại HEAD 6337b319b075bf389d484a6be13a4bc094f94a82; chưa chạy demo thành công trong lượt soạn này, chưa sửa mã hoặc khởi động cluster.

Snapshot chỉ đọc lúc khoảng 13:21 Asia/Saigon: context hiện tại là k3d-zero-door; API https://127.0.0.1:58117 từ chối kết nối. Truy vấn Docker có giới hạn 8 giây bị timeout, nên chưa kết luận cluster/container còn hay mất. Bắt đầu bằng kiểm tra bên dưới.

## Tài liệu cũ và cách sử dụng

- [demo_script.md](R:/_Projects/Eurus_Workspace/zero_door/docs/demo_script.md): bố cục trình diễn và thao tác dashboard. Các lời thoại về model sẵn sàng, MTTR 1,01s, downtime 1,34s và ưu thế nghiên cứu chưa đủ bằng chứng; dùng quan sát thực tế trong lần chạy mới.
- [start-demo.sh](R:/_Projects/Eurus_Workspace/zero_door/start-demo.sh): bản Bash từ 18/10 kiểm tra đúng context, quản lý các tunnel của chính nó trong một terminal và thoát lỗi khi kiểm tra thất bại. Không tạo cluster, deploy dịch vụ hay cấu hình ingress. Phần B cho phép chạy từng tunnel thủ công trong terminal riêng.
- [phase2_runbook.md](R:/_Projects/Eurus_Workspace/zero_door/docs/runbooks/phase2_runbook.md), [phase3_runbook.md](R:/_Projects/Eurus_Workspace/zero_door/docs/runbooks/phase3_runbook.md), [phase4_runbook.md](R:/_Projects/Eurus_Workspace/zero_door/docs/runbooks/phase4_runbook.md): tra thành phần. Một số URL có prefix /nemesis hoặc /hephaestus qua ingress; hướng dẫn này dùng port-forward trực tiếp với URL tương ứng.

## A. Kiểm tra và khởi động cluster cũ

Mở Docker Desktop, đợi engine hoạt động. Mở Git Bash trong project:

```bash
cd '/r/_Projects/Eurus_Workspace/zero_door'
docker context show
docker ps
k3d cluster list
docker ps -a --filter name=k3d-zero-door --format '{{.Names}} {{.Status}}'
```

Nếu docker ps lỗi hoặc treo, xử lý Docker Desktop trước; chưa chạy setup, delete hoặc prune. Kiểm tra Docker context đang trỏ engine local dùng cho lab, tránh hiểu context sai là cluster mất. Nếu Docker hoạt động nhưng danh sách không có cluster, kiểm tra inventory và chuyển phần E.

Nếu cluster zero-door tồn tại nhưng node chưa chạy, khởi động:

```bash
k3d cluster start zero-door
```

Nếu cluster đang chạy, bỏ qua lệnh start. Sau đó:

```bash
kubectl --context k3d-zero-door config use-context k3d-zero-door
kubectl --context k3d-zero-door get nodes --request-timeout=10s
kubectl --context k3d-zero-door get pods -n zero-door
kubectl --context k3d-zero-door get pods -n target-app
kubectl --context k3d-zero-door get pods -n monitoring
kubectl --context k3d-zero-door get svc -n zero-door
kubectl --context k3d-zero-door get svc -n monitoring
kubectl --context k3d-zero-door get ingress -n target-app
kubectl --context k3d-zero-door get pods -n kube-system -l app.kubernetes.io/name=ingress-nginx
```

Node phải Ready; pod phục vụ demo phải có đủ READY. Config repo hiện là 1 server + 1 agent, không bắt buộc 3 node như tài liệu cũ. zero-door cần Nemesis, Gaia, Hephaestus, Chaos Worker và Kafka; monitoring cần Prometheus và các dependency Gaia sử dụng. Running riêng lẻ không chứng minh pipeline hoạt động.

Nếu cluster list có zero-door nhưng context không tồn tại/endpoint đã cũ, lấy lại kubeconfig của chính cluster đó:

```bash
k3d kubeconfig merge zero-door --kubeconfig-switch-context
kubectl --context k3d-zero-door get nodes --request-timeout=10s
```

Nếu vẫn lỗi, giữ nguyên cluster/volume và lấy log lỗi để chẩn đoán. Không chạy recreate-cluster.sh: script đó xóa cluster hiện có, rồi chỉ dựng Phase 1.

## B. Mở dashboard và dịch vụ

Mỗi lệnh dưới đây chạy trong một tab Bash riêng, giữ tab mở. Ctrl+C chỉ dừng port-forward ở tab đó. Dùng context tường minh để không trỏ nhầm cluster.

Tab 1 — Nemesis/dashboard:

```bash
kubectl --context k3d-zero-door -n zero-door port-forward svc/nemesis 9092:8000
```

Tab 2 — Hephaestus:

```bash
kubectl --context k3d-zero-door -n zero-door port-forward svc/hephaestus 9091:8000
```

Tab 3 — Prometheus, nếu service này có trong inventory phần A:

```bash
kubectl --context k3d-zero-door -n monitoring port-forward svc/prometheus-kube-prometheus-prometheus 9090:9090
```

Nếu deployment cũ chỉ có prometheus-operated, dùng service đó với cùng 9090:9090. Grafana là tab bổ sung khi cần, dùng service có thật trong inventory:

```bash
kubectl --context k3d-zero-door -n monitoring port-forward svc/prometheus-grafana 3000:80
```

Mở:

- Dashboard: http://localhost:9092/dashboard/
- Boutique qua ingress: http://localhost:8080/
- Prometheus: http://localhost:9090/
- Grafana, nếu đã mở: http://localhost:3000/

Nếu cổng bận, xem ứng dụng đang giữ cổng rồi chọn cổng khác hoặc dừng đúng terminal port-forward cũ. Không dừng tất cả kubectl của các project khác.

Nếu Boutique trên 8080 không mở, kiểm tra ingress/controller/service trước. Có thể mở tab bổ sung qua cổng 8088 để kiểm tra frontend:

```bash
kubectl --context k3d-zero-door -n target-app port-forward svc/frontend 8088:80
```

Mở http://localhost:8088/. Đây là đường đi trực tiếp tới pod frontend; khi pod bị kill, tunnel có thể mất và phải mở lại. Dùng ingress 8080 cho demo PodKill nếu muốn quan sát website phục hồi mà không cần dựng lại tunnel.

Tab kiểm tra API:

```bash
curl --fail --show-error --max-time 10 "http://localhost:9092/healthz"
curl --fail --show-error --max-time 10 "http://localhost:9091/healthz"
```

Nemesis cần kafka_connected=true; Hephaestus cần Kafka/K8s kết nối đúng. HTTP 200 hoặc llm_provider=gemini chỉ là status/cấu hình, không chứng minh model gọi được. Mở Boutique, thử xem sản phẩm và giỏ hàng; ghi thao tác nào thành công thật. Nếu định demo checkout, phải thử checkout trước, không suy từ trang chủ mở được.

## C. Demo bản cũ bằng PodKill trước, rồi thử HTTP Flood

Ưu tiên kích hoạt thủ công để kiểm tra executor/pipeline khi chưa xác minh LLM. Không cần API key cho đường /attack/trigger. Nút Trigger Gemini Attack gọi /attack/llm-plan, tạo kế hoạch rồi thực thi ngay; chỉ dùng sau khi backend được kiểm chứng và sẵn sàng chịu một lượt attack.

1. Chờ lab ổn định, không còn attack đang chạy. Ghi trạng thái pod/replica trước khi reset. Nút RESET SYSTEM xóa history/cooldown và đưa danh sách deployment về 1 replica; lưu log cần giữ trước khi bấm. Nó không phải nút stop attack, không bảo đảm cleanup stress pod, và HPA có thể đổi replicas tiếp.
2. Mở Boutique 8080 và dashboard. Giữ một tab theo dõi frontend:

```bash
kubectl --context k3d-zero-door -n target-app get pods -l app=frontend -w
```

3. Trên dashboard chọn Attack Type=Pod Kill, Service=frontend, Intensity=Low; bấm Inject Failure Script một lần. Hoặc dùng API tương đương trong tab khác:

```bash
curl --fail --show-error --max-time 15 -X POST 'http://localhost:9092/attack/trigger' \
  -H 'Content-Type: application/json' \
  --data '{"attackType":"POD_KILL","targetService":"frontend","targetNamespace":"target-app","durationSec":90,"intensity":"LOW","concurrency":1}'
```

4. Quan sát pod cũ bị xóa, pod thay thế Ready và refresh Boutique. Có thể thấy lỗi tạm thời hoặc không thấy lỗi nếu vẫn có replica phục vụ. PodKill xóa pod rồi kết thúc, không liên tục kill trong 90s. Pod được tạo lại trước hết là hành vi Deployment controller Kubernetes; chỉ quy cho Hephaestus nếu có log action tương ứng.
5. Kiểm tra log và lịch sử, không dùng animation/chat làm bằng chứng thay thế:

```bash
kubectl --context k3d-zero-door -n zero-door logs deployment/chaos-worker --tail=60
kubectl --context k3d-zero-door -n zero-door logs deployment/gaia --tail=60
kubectl --context k3d-zero-door -n zero-door logs deployment/hephaestus --tail=60
curl --fail --show-error --max-time 10 "http://localhost:9091/heal/history"
kubectl --context k3d-zero-door -n target-app get deployments
```

6. Sau khi mọi tác động trước đã kết thúc, thử HTTP Flood: chọn frontend, Low, Inject Failure Script. UI Low gửi concurrency=5 và durationSec=90; High yêu cầu 80, worker có thể cap theo config. Chạy một lượt, theo dõi website/Network tab và log. Không hứa độ trễ sẽ tăng hoặc sẽ auto-scale: tải Low có thể chưa qua ngưỡng.

Frontend service dùng port 80, container dùng 8080. Để tránh URL default sai trong những request API khác, URL cho HTTP Flood trên frontend có thể ghi tường minh http://frontend.target-app.svc.cluster.local:80/. Flood đi nội bộ trực tiếp tới service, không qua ingress host; metric ingress có thể không thấy tải này. Đây là hạn chế bản cũ cần nói rõ, không phải lý do để tăng tải liên tục khi chưa hiểu đường đo.

CPU Stress là lượt bổ sung sau khi lab ổn định: chọn service có thật và Low, theo dõi quota/pod. Mã hiện tại tạo pod stress riêng, không chứng minh CPU của chính app bị gây cạn. SQLi chưa có executor trong registry bản này; block IP và rollback chưa được kiểm chứng đúng như yêu cầu. Không đưa các phần đó vào danh sách demo đã hoàn thiện.

## D. Kiểm tra riêng healer nếu full loop chưa phát alert

Chỉ thực hiện khi muốn demo chức năng scale của Hephaestus, phân biệt rõ với phát hiện tự động. Chờ attack kết thúc, lưu log, reset nếu cần và xem replicas frontend trước:

```bash
curl --fail --show-error --max-time 15 -X POST 'http://localhost:9091/heal/trigger' \
  -H 'Content-Type: application/json' \
  --data '{"alertType":"HIGH_CPU","severity":"WARNING","affectedService":"frontend"}'
kubectl --context k3d-zero-door -n target-app get deployment frontend
kubectl --context k3d-zero-door -n target-app get pods -l app=frontend
```

Đây là inject alert trực tiếp, bỏ qua Gaia/Kafka detector. Nếu replicas đã ở max hoặc cooldown còn thì có thể không scale. Log API chấp nhận, action thành công và pod Ready là các quan sát riêng; chưa phải MTTR hoặc bằng chứng nghiệp vụ phục hồi.

## E. Nếu đã xác nhận cluster cũ không còn

Nhánh này dựng lab mới bằng code cũ, không phải sửa theo roadmap. Nó tải chart/image, build image và apply cấu hình; thời gian/khả năng chạy phụ thuộc Docker, mạng, image/chart cũ và quota. Không thể bảo đảm dựng kịp trước buổi gặp thầy. Chỉ dùng sau khi Docker/context/inventory đã được kiểm tra, dữ liệu cần giữ đã được xác định; không dùng lệnh delete/prune.

Từ thư mục gốc project, chạy từng nhóm và dừng nếu có lỗi; không tiếp tục chỉ vì script in Complete:

1. Hạ tầng Phase 1:

```bash
bash ./infrastructure/scripts/setup-phase1.sh
kubectl --context k3d-zero-door config use-context k3d-zero-door
kubectl --context k3d-zero-door get nodes --request-timeout=10s
kubectl --context k3d-zero-door get pods -n zero-door
kubectl --context k3d-zero-door get pods -n monitoring
```

Nếu setup thất bại, giữ lỗi đầu tiên để xử lý. Các script cũ không khóa mọi chart version; image/chart có thể không còn tải được. Chưa kiểm chứng một lượt dựng mới tại ngày hướng dẫn.

2. Target và Gaia: repo không có setup-phase2.sh; dùng các file đang tồn tại. Tag Gaia phải khớp image zero-door/gaia:latest trong manifest:

```bash
kubectl --context k3d-zero-door apply -f ./infrastructure/manifests/target-app.yaml
kubectl --context k3d-zero-door apply -f ./infrastructure/manifests/target-app-addons.yaml
kubectl --context k3d-zero-door apply -f ./infrastructure/manifests/target-app-ingress.yaml
# Frontend không có /metrics; dùng ServiceMonitor của Traefik theo bash-tooling.md.
kubectl --context k3d-zero-door apply -f ./infrastructure/manifests/prometheus-rules.yaml
docker build -t zero-door/gaia:latest ./agent-orchestrator/gaia
k3d image import zero-door/gaia:latest -c zero-door
kubectl --context k3d-zero-door apply -f ./infrastructure/manifests/gaia-deployment.yaml
kubectl --context k3d-zero-door rollout status deployment/gaia -n zero-door --timeout=120s
kubectl --context k3d-zero-door get pods -n target-app
```

Chỉ tiếp tục khi các lệnh thành công và pod mục tiêu Ready. ServiceMonitor /metrics tồn tại không chứng minh endpoint trả metric hợp lệ. Addons bổ sung dependency Boutique trong repo, vẫn cần thử từng luồng nghiệp vụ.

3. Nemesis/Chaos Worker, rồi Hephaestus:

```bash
bash ./infrastructure/scripts/setup-phase3.sh
kubectl --context k3d-zero-door get pods -n zero-door
bash ./infrastructure/scripts/setup-phase4.sh
kubectl --context k3d-zero-door get pods -n zero-door
```

Script setup-phase3.sh tạo Secret mẫu rỗng trên lab mới và giữ Secret đã tồn tại. Không apply nguyên manifest Nemesis thủ công đè key cũ chỉ để mở dashboard; không in Secret ra màn hình. Demo manual không cần LLM. setup-phase5.sh mặc định chỉ kiểm tra HTTP/mở tunnel; cờ `--run-smoke` và các runner vẫn gây lỗi/thay đổi dữ liệu, không dùng như health check.

4. Quay lại B và kiểm tra health/website/log trước khi làm C. Nếu thiếu tài nguyên, ErrImagePull, CrashLoop hoặc API lỗi, xử lý lỗi đó trước; chưa thể gọi demo sẵn sàng.

## F. Kết thúc và lỗi thường gặp

- Port-forward không mở: xem lỗi ở tab đó, kiểm tra service/pod; CTRL+C rồi mở lại tunnel đúng dịch vụ. Đóng các tab port-forward khi kết thúc; cluster vẫn chạy.
- Quota/scheduling lỗi: xem kubectl get events -n target-app --sort-by=.metadata.creationTimestamp và kubectl describe resourcequota -n target-app; reset không dừng attack hoặc tự gỡ mọi tài nguyên.
- Cần dừng HTTP Flood khẩn cấp trong lab này: kubectl --context k3d-zero-door -n zero-door scale deployment/chaos-worker --replicas=0 để dừng worker hiện tại; khi cần chạy lại, scale về replica count đã ghi trước đó. Ghi run bị ngắt, không coi hoàn tất.
- Pod stress còn lại: xem kubectl --context k3d-zero-door -n target-app get pods -l chaos-worker=true. Chỉ xóa tên pod stress đã xác nhận thuộc lượt demo bằng kubectl --context k3d-zero-door -n target-app delete pod <ten-pod-stress>; không xóa namespace/volume hoặc mọi pod app. Dừng worker không tự dọn stress pod đã tạo.
- RESET SYSTEM mất history: lưu log cần dùng trước khi reset. Lượt HTTP Flood tự có duration/worker cap, nhưng nút reset không hủy lượt đang chạy.
- Nếu thầy hỏi tốc độ/AI: báo những gì vừa quan sát được; số KPI dashboard có thành phần ngẫu nhiên, chat Gaia/Hephaestus có diễn giải theo template. Chưa dùng chúng như kết quả nghiên cứu hoặc bằng chứng ba tác tử cùng suy luận LLM.

Buổi demo bản cũ phù hợp để trình bày các thành phần đã chạy và phần còn thiếu. Để kết luận đúng vòng tự phục hồi và KPI nghiên cứu, vẫn cần thực hiện roadmap.
