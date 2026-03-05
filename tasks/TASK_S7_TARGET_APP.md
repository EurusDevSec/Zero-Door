## 💡 Context

> **Task ID**: S7  
> **Phase**: Phase 2 - Target App + Gaia  
> **Sprint**: Sprint 3 - Deploy Target & Gaia Core  
> **Status**: ⬜ NOT STARTED  
> **Created**: 04/03/2026  
> **Target**: Sprint 3 (Tuần 5-6)  
> **Assignee**: 🔴 Hoàng (Lead)  
> **Blocked by**: S2 (K8s cluster), S6 (Prometheus)  
> **Blocks**: S8 (Gaia cần target app để monitor), S9 (Nemesis cần target để attack)

> Deploy Google Online Boutique (10+ microservices) lên K8s cluster.
> Đây là "mục tiêu" mà Nemesis tấn công và Gaia giám sát.

---

## 🤖 AI Refined

> **User Story:**

> As a **DevOps Engineer**, I want to **deploy Google Online Boutique e-commerce demo application on my K8s cluster** so that **I have a realistic microservices target for chaos engineering testing and monitoring.**

**Acceptance Criteria:**

- [ ] Google Online Boutique deployed thành công trên namespace `target-app`
- [ ] Tất cả 10+ pods Running (frontend, recommendation, product catalog, cart, checkout, etc.)
- [ ] Frontend accessible qua port-forward → shopping demo works
- [ ] Prometheus scraping metrics từ Online Boutique services
- [ ] Grafana dashboard hiển thị target app metrics
- [ ] ServiceMonitor configured cho custom metrics endpoints
- [ ] Load test cơ bản: `hey -n 100 -c 10 http://frontend` → verify app handles traffic

---

## 🛠️ Implementation

### Subtasks

- [ ] 3.1.1 Clone Google Online Boutique: `git clone https://github.com/GoogleCloudPlatform/microservices-demo`
- [ ] 3.1.2 Deploy vào K8s: `kubectl apply -f release/kubernetes-manifests.yaml -n target-app`
- [ ] 3.1.3 Wait for all pods Ready (12 services)
- [ ] 3.1.4 Port-forward frontend: `kubectl port-forward svc/frontend 8080:80 -n target-app`
- [ ] 3.1.5 Verify shopping flow (browse → add to cart → checkout)
- [ ] 3.1.6 Configure ServiceMonitor cho Prometheus scraping
- [ ] 3.1.7 Run basic load test: `hey -n 100 -c 10 http://localhost:8080`
- [ ] 3.1.8 Document pod list + service endpoints

### Branch & PR

- [ ] Branch: `feat/s3/target-app-deploy`
- [ ] PR Created
- [ ] All pods Running screenshot attached
- [ ] Shopping demo video/screenshot

---

## 📝 Notes

> **Google Online Boutique Services:**
>
> | Service | Language | Role |
> | --- | --- | --- |
> | frontend | Go | Web UI |
> | cartservice | C# | Shopping cart |
> | productcatalogservice | Go | Product listing |
> | currencyservice | Node.js | Currency conversion |
> | paymentservice | Node.js | Payment processing |
> | shippingservice | Go | Shipping calculation |
> | emailservice | Python | Email notifications |
> | checkoutservice | Go | Checkout flow |
> | recommendationservice | Python | Product recommendations |
> | adservice | Java | Advertisements |
> | loadgenerator | Python | Synthetic traffic |

> **Tại sao chọn Google Online Boutique:**
> - Polyglot: 5 ngôn ngữ → đa dạng attack surface
> - 10+ microservices → realistic target
> - K8s-native: đã có manifests sẵn
> - Well-documented: Google maintainer
> - Có loadgenerator built-in

> **Tham khảo:**
>
> - [plan.md](../docs/plan.md) Section 6.2 — Phase 2 Target App
> - Google Online Boutique: https://github.com/GoogleCloudPlatform/microservices-demo
