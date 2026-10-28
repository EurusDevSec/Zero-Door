# ZER-46 — một lượt kiểm component containment trong private lab

**PROPOSED / NOT_APPROVED / NOT_RUN.** 28/10/2026. Quyền sửa/kiểm offline hiện có không cấp quyền build,
apply, restart hay HTTP vào lab. Đọc scope SQLi-only và source-hashes.json; không tái sử dụng approval ZER-43.
Renderer/manifest đã kiểm offline; chưa có live inventory, dry-run admission, build hay probe.

## Outcome và ranh giới kết luận

Đo sourceA bị403 tại fixture, sourceB cùng proxy vẫn dùng catalog/CRUD, một TTL180s gỡ chặn đúng hạn,
trạng thái tồn tại qua đúng một lần thay Pod fixture và một lần khởi tạo lại writer process. Dùng request
catalog lành tính từ hai nguồn; SQLi effect đã có evidence ZER-41/42, không cần phát lại payload.
Đây là kiểm component BLOCK_IP, không chứng minh Gaia phát hiện, production healer tự hành, LLM hay KPI
end-to-end. Bằng chứng của lần này chỉ đóng được phần AC thật sự đo được; không tự Done/publication.

## Hành động được đề nghị

1. Chỉ Docker context desktop-linux, kubectl context k3d-zero-door và cluster hiện có. Nếu cluster không
   đang chạy/Ready, namespace zd-sqli-lab đã tồn tại, image pin chưa có cache, hay inventory khác baseline
   thì dừng; không start/stop/restart node, đổi context, xóa namespace cũ hoặc phục hồi hạ tầng.
2. Capture identity/spec/replicas/restarts, ba PVC UID/volume, node/controller args và route hiện có.
   Giữ guard host/WSL free RAM≥1GiB, memory PSI avg10≤5, kiểm mỗi5s. Preflight120s và baseline nghiệp vụ
   độc lập phải khỏe; failure giữ nguyên rồi dừng, không sửa DNS/CPU/Prometheus để tiếp tục.
3. Tối đa một build fixture candidate trong source-hashes.json, pinned base có sẵn, build network=none,
   pull=false; import vào đúng cluster, không push/pull image hay cài dependency. Traefik dùng cache digest
   docker.io/library/traefik@sha256:575fa15b135078fe5e50aa847987d96dbddd7b093c172429618404df73f3fa7c.
4. Tạo namespace zd-sqli-lab nếu vẫn absent bằng create, gắn owner scope duy nhất zer46-<12hex>, chụp UID.
   Dùng topology private đã nghiệm thu: một fixture safe, một proxy ClusterIP8000 và hai Pod nguồn. Không
   public Ingress/NodePort/hostPort; không endpoint/mục tiêu ngoài lab. Candidate review17resources ở
   review-only.safe.yaml là minh họa với IP giả, **không apply trực tiếp**. Render lại sau khi có proxy IP
   thật, pin đúng /32 và run/trial mới; giữ requests/limits accepted. Bootstrap proxy/source trước fixture.
5. Fixture giữ startup gate trong container Running; tối đa120s chờ đúng Pod hook/rule trên node thực tế,
   sau đó mới ghi /data/.policy-release. Rule missing thì dừng, không bỏ isolation. Xác minh direct TCP tới
   fixture bị từ chối, đường private proxy hoạt động, A/B được quan sát distinct và forged-leftmost XFF
   không thay IP. Các kiểm này không dùng IP lịch sử làm pin hiện hành.
6. Mount ConfigMap riêng zer46-sqli-containment read-only cả thư mục, không subPath; UID/scope/run/trial
   pin theo actual. Không bật R1_EXECUTOR hay production agent. Writer component dùng API client context
   explicit và joined source record mới≤60s, sourceA/sourceB/proxy được pin; không nhận IP từ model/body.
   Một rule TTL180s tính từ source observation. CAS≤3 lần, API timeout2s connect/3s read. Response chỉ là
   API_ACCEPTED. Poll≤90s tới khi mounted SHA và request403 chứng minh rule đã áp dụng; không lặp block
   bằng action ID mới để kéo dài TTL. Nếu projection quá chậm thì NOT_MET, không nới TTL/ngưỡng.
7. Trước restart hoàn tất delete/hậu kiểm mọi order probe đã tạo; DB emptyDir không bảo đảm order sống
   qua Pod replacement, không dùng lượt này để claim order durability. Trong TTL, thay đúng một Pod
   fixture bằng UID precondition, chờ rule hook rồi release gate của Pod mới.
   Giữ proxy và source Pods để IP không đổi. Readback ConfigMap UID/rule/expiry sau restart; writer tạo lại
   một process với cùng pins/action ID phải replay, không write/extend. Probe A403/B200/CRUD phải đúng;
   chưa kịp quan sát block sau restart trước expiry thì ghi thiếu proof, không PASS. Đây không là restart
   production Hephaestus Pod; không trình bày thành integration acceptance.
8. Chờ expiry gốc, không còn writer/timer tác động; A/B đều trở lại200 và CRUD có owned-delete hậu kiểm.
   So fixture probe với Boutique probe riêng, không coi unblock là sửa lỗ hổng. Sau đó cleanup owned rules
   bằng CAS, readback API+mounted SHA+rỗng, probe lại. Endpoint reset không được dùng để xóa policy.

## Trần và điều kiện dừng

- Một attempt, tối đa20phút gồm5phút cleanup; không tự thử lượt2. Work dừng ở phút15 dù chưa đủ AC.
- Script-originated: ≤120 HTTP fixture +≤32 HTTP Boutique, tổng≤152; concurrency1,≤2RPS, timeout mỗi
  request3s. ≤6 TCP isolation checks. Không load test, Kafka topic/message, SQLi payload, inference hoặc ES
  query mới. Kubelet health/readiness là nền riêng theo cadence trong manifest, thu logs/count riêng,
  không tuyên bố152 là mẫu số mọi network attempt của cluster.
- Tối đa một block rule, một TTL180s, một Pod fixture replacement, một writer process restart; không
  restart/scale shared agents, proxy, Boutique, node hay cluster. Không CoreDNS/Ingress/CNI/resource/quota/
  Prometheus/retention/model/cloud changes. Không động PVC hoặc command ledger dùng chung.
- Stop ngay nếu guard vượt, baseline fail, owner/UID/source/route sai, spoof/direct-access control sai,
  timeout, restart ngoài scope, drift source hoặc hết request/time budget. Không tiếp tục để lấy PASS.

## Cleanup và kiểm độc lập

Giữ5phút cuối: dừng actor do attempt sở hữu, xóa rule bằng CAS nếu ownership còn đúng; kiểm policy/file/
request thay vì chỉ nhìn API accepted. Lưu đầy đủ lỗi/missing/probe sau expiry. Chụp log trước xóa rồi
DELETE namespace bằng UID precondition và wait absent; không delete bằng tên nếu UID không khớp. Dừng
chỉ child tunnel/watcher đã tạo. Đối chiếu shared specs/replicas/restarts, ba PVC UID/volume và Boutique
business với baseline. Incomplete cleanup là INCOMPLETE, không sửa receipt thành CLEAN. Giữ image cache
và evidence; không có workload active từ cache. Không Git publication hoặc cập nhật Linear Done.

Một reconciler đọc raw requestID/status/source/policy-SHA, absolute expiry, trước/sau Pod UID và inventory;
không dùng chuỗi PASS của runner làm oracle. Cần review độc lập và integration đúng AC còn thiếu trước
nghiệm thu ZER-46/ZER-17; chạy component thành công không tự đóng chuỗi R3/R4/R5.
