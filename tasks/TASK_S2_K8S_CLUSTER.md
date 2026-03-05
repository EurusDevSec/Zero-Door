## 💡 Context

> **Task ID**: S2  
> **Phase**: Phase 1 - Setup & Research  
> **Sprint**: Sprint 1 - Foundation  
> **Status**: ⬜ NOT STARTED  
> **Created**: 04/03/2026  
> **Target**: Sprint 1 (Tuần 1-2)  
> **Assignee**: 🔴 Hoàng (Lead)  
> **Blocked by**: S1 (cần repo trước)  
> **Blocks**: S6 (Prometheus cần K8s), S7 (Target app cần K8s), tất cả code deployments

> Setup Kubernetes cluster hoàn chỉnh cho toàn bộ dự án.
> Đây là nền tảng hạ tầng — không có K8s thì không deploy được gì cả.

---

## 🤖 AI Refined

> **User Story:**

> As a **DevOps Engineer**, I want to **set up a local Kubernetes cluster with essential tooling (kubectl, Helm, ingress)** so that **I can deploy and manage all microservices (target app, agents, monitoring stack) throughout the project.**

**Acceptance Criteria:**

- [ ] K3s hoặc Minikube cluster chạy ổn định trên local machine
- [ ] `kubectl get nodes` → node Ready
- [ ] Helm 3.x cài đặt, `helm version` thành công
- [ ] `kubectl` configured đúng context
- [ ] Tạo namespaces: `zero-door`, `monitoring`, `target-app`
- [ ] Ingress controller cài (Traefik hoặc Nginx)
- [ ] Chạy demo app (nginx) thành công trên cluster → verify cluster works
- [ ] Document lại cách setup (cho rebuild nếu cần)

---

## 🛠️ Implementation

### Subtasks

- [ ] 1.2.1 Cài đặt K3s (hoặc Minikube) trên Windows (Docker Desktop backend)
- [ ] 1.2.2 Cài đặt kubectl + cấu hình kubeconfig
- [ ] 1.2.3 Cài đặt Helm 3.x
- [ ] 1.2.4 Tạo 3 namespaces: `zero-door`, `monitoring`, `target-app`
- [ ] 1.2.5 Cài Ingress controller (Traefik/Nginx)
- [ ] 1.2.6 Deploy test pod (nginx) → verify cluster
- [ ] 1.2.7 Viết `docs/guides/GUIDE_K8S_SETUP.md`

### Branch & PR

- [ ] Branch: `infra/k8s-cluster-setup`
- [ ] PR Created
- [ ] `kubectl get nodes` screenshot attached
- [ ] Test pod accessible via port-forward

---

## 📝 Notes

> **Lựa chọn K8s distribution:**
>
> | Option   | Pros                          | Cons                    | Recommend      |
> | -------- | ----------------------------- | ----------------------- | -------------- |
> | K3s      | Nhẹ, nhanh, production-like   | Cần Docker Desktop      | ⭐ Recommended |
> | Minikube | Đơn giản, well-documented     | Chậm hơn K3s            | OK             |
> | Kind     | Nhẹ, dùng Docker containers   | Networking phức tạp hơn | Fallback       |

> **Resource requirements:**
>
> - K3s: min 1 CPU, 512MB RAM
> - Toàn bộ project (target + agents + monitoring): ~4-8GB RAM, 4 CPU cores
> - Recommend: 16GB RAM system, 8 CPU cores

> **Tham khảo:**
>
> - [plan.md](../docs/plan.md) Section 5.1 — Tech Stack
> - K3s Quick Start: https://docs.k3s.io/quick-start
> - Minikube Start: https://minikube.sigs.k8s.io/docs/start/
