# ZER-46 runtime-02 — API đã lên, cache và RAM chưa đạt

**NOT_MET / COMPONENT_NOT_STARTED / NOT_READY_FOR_PUBLICATION.** 28/10/2026,09:57:34+07.
Hoàng giải thích đã tắt container và tự bật lại; tiếp tục cùng envelope đã duyệt, giữ runtime-01 nguyên.

- Kubernetes API đọc được, đúng hai node k3d-zero-door-server-0/agent-0 và cả hai Ready. Chín Deployment
  Boutique đúng profile1replica/available1; shared agents giữ0. Namespace zd-sqli-lab absent.
- Gate cache thất bại tại pinned base
  gcr.io/distroless/python3-debian12:nonroot@sha256:0f8ca62dea61023c1fe02e445bd154ee02b2d97aec377f965ae3c641ec838e61:
  Docker trả `No such image`. Gói đã duyệt chỉ dùng cache, không cho pull. Chưa tới kiểm cache Traefik,
  không được suy proxy image cũng thiếu hoặc đã có. Không build từ một base khác để tránh gate.
- Cleanup đọc được inventory trước/sau: spec+UID và restart counts giữ nguyên; ba PVC UID/volume giữ nguyên.
  Không namespace/actor/rule/tunnel mới.0build/0mutation/0fixtureHTTP/0BoutiqueHTTP, không model/Kafka.
- Mẫu resource lúc09:57:34.735+07: hostAvailable455.815.168bytes≈434,70MiB, **<1GiB**; WSL available
  2.857.460KiB≈2,73GiB, memory PSI avg10=0,08. MEMORY_STOP thuộc RAM host, không phải WSL/PSI. Không hạ guard.
- Resource cleanup không có object mới; overall cleanup INCOMPLETE vì resource guard không đạt, chưa
  chạy business readback. Không báo Boutique healthy từ PodReady. Raw failure/cleanup/acceptance giữ nguyên.

Một lượt preflight mới được thực hiện sau steering của Hoàng, không có kỹ thuật/payload/target mới. Lượt
này kết thúc ở gate, không tự chạy vòng2 hoặc pull image. Cần RAM Windows ổn định trước; chuẩn bị cache
cần quyền tải đúng digest ngoài gói cache-only cũ. Xem [gói gộp tiếp theo](../runtime-prep/readiness-and-retry.md).
