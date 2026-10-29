# ZER-19 — sửa blocker NetworkPolicy (POLICY_HOOK_MISSING)

Hoàng duyệt gói sửa ngày 29/10/2026: restart lần lượt server rồi agent, mỗi node kiểm IP/log/chain, tối đa 1 restart bù mỗi node, không gọi model, không chạy nghiệm thu. Kết quả: **sửa xong, không cần restart bù.** Đây là sửa hạ tầng, **không phải** nghiệm thu ZER-19; AC02/03 vẫn chưa đạt.

## Nguyên nhân (có bằng chứng)

- Lúc 2026-10-29T02:38:42Z cả hai container node k3d khởi động lại cùng lúc. Docker cấp lại IP: agent `.4→.3`, server `.5→.4`.
- Log k3s ngay sau lần khởi động đó ghi `Successfully retrieved node IP(s)`: agent `172.19.0.4`, server `172.19.0.5`, đều là IP cũ. Network policy controller (kube-router v2.2.1, k3s v1.31.5+k3s1) chỉ lập trình chain pod-firewall cho Pod có `hostIP` bằng IP đã nhận lúc khởi động, và không đọc lại IP.
- Hệ quả: agent lập trình 3 Pod của server và bỏ qua 19 Pod của chính nó (trong đó có fixture ở runtime-03); server có 0 chain. NetworkPolicy gần như không được thực thi từ 02:38Z đến lúc sửa. Gate của runner ở runtime-03 chặn đúng.
- Đối chứng: ở runtime-02 (28/10, agent = `.4`, chưa đổi IP), iptables của agent có chain cho mọi Pod trên agent, kể cả `sqli-fixture`.
- Chưa xác định nguồn cụ thể của giá trị IP cũ bên trong k3s; restart từng node một không lặp lại lỗi này.

## Thực hiện và kiểm

| Mốc (UTC) | Agent: IP / log IP / chain đúng / nhầm | Server: IP / log IP / chain đúng / nhầm |
| --- | --- | --- |
| [00-before](raw/00-before.json) 03:40:30 | .3 / .4 / 0 của 19 / 3 | .4 / .5 / 0 của 3 / 0 |
| [01-after-server](raw/01-after-server.json) 03:41:46 (Ready sau 39s) | không đổi | .4 / .4 / 3 của 3 / 0 |
| [02-after-agent](raw/02-after-agent.json) 03:43:18 (Ready sau 71s) | .3 / .3 / 19 của 19 / 0 | .4 / .4 / 3 của 3 / 0 |
| [03-stable](raw/03-stable.json) 03:43:35 | 19/19, 0 nhầm | 3/3, 0 nhầm |

"Chain đúng" là số Pod không-hostNetwork đang Running trên node đó có chain `KUBE-POD-FW` trong `iptables-save -t filter`. Script: [snap.sh](snap.sh) (chỉ đọc), [restart_node.sh](restart_node.sh).

## Tác động và cleanup

- IP của cả 4 container trên bridge `k3d-zero-door` không đổi qua hai lần restart. Node InternalIP vẫn là `.3` (agent) và `.4` (server).
- 3 PVC: UID không đổi, Bound. 26 Deployment/StatefulSet/DaemonSet: UID không đổi, không có object mới.
- 24 Pod đều Running/Ready. Riêng Pod Elasticsearch được tạo lại (`…-svvsz` → `…-gtrxw`, cùng ReplicaSet); các Pod khác chỉ tăng restartCount 1–2.
- Pod node-exporter (hostNetwork) trên agent trước đây báo `podIP=172.19.0.4` (giá trị cũ), nay báo `172.19.0.3`.
- Không gọi model, không gửi HTTP tới fixture, không build/import/pull, không đổi config hay manifest, không xóa object nào.

## Phòng ngừa

Sau mỗi lần Docker Desktop hoặc k3d khởi động lại các node, chạy `snap.sh` (chỉ đọc) trước mọi lượt runtime. Nếu `check.<node>.ok` sai thì restart riêng node đó một lần. Muốn IP node cố định thì phải tạo lại cluster với subnet/IP tĩnh — đó là thay đổi hạ tầng, ngoài phạm vi gói này.

## Còn lại cho ZER-19

Blocker POLICY_HOOK_MISSING đã gỡ. Bước tiếp theo là một proposal riêng cho đúng một lượt xác minh observation → model → executor → result, cần Hoàng duyệt. Chưa commit/push/PR.
