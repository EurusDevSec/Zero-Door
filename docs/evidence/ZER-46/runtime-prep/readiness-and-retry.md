# ZER-46 — chuẩn bị cache còn thiếu và một lượt component sau khi RAM đủ

**PROPOSED / NOT_APPROVED / NOT_RUN.** 28/10/2026. Dựa raw runtime-02, không coi preflight là PASS.
Thay đổi duy nhất so với gói private trước: cho phép cache image pin nếu thiếu; không thay source image,
guard, topology, TTL hay tiêu chí. Người dùng tự bật container; không có quyền restart Docker Desktop/WSL.

## Trước thực thi

Hoàng giải phóng ứng dụng Windows không cần thiết để host Available RAM≥1GiB và ổn định qua preflight
120s. Không tự kill app/process, resize WSL, đổi swap, quotas, resources hoặc tắt dịch vụ dự án khác.
Giữ WSL available≥1GiB, memory PSI avg10≤5, capture mỗi5s. Nếu chưa đạt thì chưa pull/build/probe.

## Phần cần duyệt thêm, gom cùng lượt kiểm

- Chỉ context desktop-linux/k3d-zero-door đang Ready; vẫn cấm start/stop/restart cluster/node/shared app.
- Inspect cache read-only. Nếu thiếu, pull **tối đa một lần mỗi đúng hai digest** dưới đây; không login/
  đổi registry/auth/mirror/proxy, không tag latest, không pull image khác, không push. Mỗi pull≤120s và
  guard vẫn chạy; lỗi thì dừng, không thử mirror hay digest khác. Đây là tải dependency, không kiểm thử
  hoặc gửi traffic tấn công tới registry.
  - gcr.io/distroless/python3-debian12:nonroot@sha256:0f8ca62dea61023c1fe02e445bd154ee02b2d97aec377f965ae3c641ec838e61
  - docker.io/library/traefik@sha256:575fa15b135078fe5e50aa847987d96dbddd7b093c172429618404df73f3fa7c
- Xác minh digest/cache rồi một build fixture candidate như source-hashes.json, network=none/pull=false;
  import đúng cluster. Không sửa Dockerfile base hoặc thay source để dùng một image không tương đương.
- Sau đó **một attempt** component đúng [gói trước](next-run-proposal.md): safe private fixture/proxy/
  hai nguồn, trusted-IP/isolation controls; một rule TTL180s, một Pod fixture replacement, một writer
  process restart, probe sourceA/sourceB và cleanup độc lập. Không payload, load, model, Kafka hoặc shared
  DNS/CNI/Ingress/resource change. Production R1 executor vẫn disabled.
- **Một cửa sổ20phút cho cả cache prep + component, gồm5phút cleanup**,≤120fixture+32Boutique scriptHTTP,
  concurrency1/≤2RPS/timeout3s; giữ mọi trần khác. Cần thời gian cache quá lớn thì work dừng ở phút15,
  không kéo dài để kịp hết TTL hay tạo rule mới. Không tự attempt tiếp.

Xác minh/cleanup theo gói trước: API+mounted policy+request; namespace delete bằng UID; dừng child mình
tạo; shared spec/replica/restart/ba PVC và Boutique business readback. Không coi thiếu runtime proof là
PASS hay đổi tiêu chí vì deadline. Dữ liệu runtime-01/02 giữ nguyên; issue vẫn chưa Done/publication.
