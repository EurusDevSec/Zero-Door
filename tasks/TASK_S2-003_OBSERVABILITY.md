## 💡 Context

> **Task ID**: S2-003  
> **Phase**: Phase 1 - Setup & Research  
> **Sprint**: Sprint 2 - Architecture & Design  
> **Status**: ⬜ NOT STARTED  
> **Created**: 04/03/2026  
> **Target**: Sprint 2 (Tuần 3-4)  
> **Assignee**: 🔴 Hoàng (Lead) + 🟡 Teammate (Grafana dashboards)  
> **Blocked by**: S1-002 (cần K8s cluster)  
> **Blocks**: S3-002 (Gaia cần Prometheus data)

> Setup Prometheus + Grafana trên K8s để giám sát metrics.
> Đây là "mắt thần" của Agent Gaia — không có observability thì Gaia "mù".

---

## 🤖 AI Refined

> **User Story:**

> As an **SRE/DevOps Engineer**, I want to **deploy Prometheus and Grafana on Kubernetes** so that **Agent Gaia can scrape metrics from all services and the team can visualize system health in real-time.**

**Acceptance Criteria:**

- [ ] Prometheus server chạy trên K8s (`monitoring` namespace)
- [ ] Grafana chạy, accessible qua port-forward (`localhost:3000`)
- [ ] Prometheus scraping K8s node metrics (node-exporter)
- [ ] Grafana có ít nhất 1 dashboard: K8s Cluster Overview
- [ ] Alertmanager configured (basic alert rules)
- [ ] 🟡 Teammate: Customize Grafana dashboard với panels: CPU, Memory, Network, Pod status
- [ ] ServiceMonitor CRD ready (cho future custom metrics)

---

## 🛠️ Implementation

### Subtasks — 🔴 Hoàng

- [ ] 2.3.1 Install kube-prometheus-stack via Helm:
    ```bash
    helm install prometheus prometheus-community/kube-prometheus-stack \
      -n monitoring --create-namespace
    ```
- [ ] 2.3.2 Verify Prometheus server running: `kubectl port-forward svc/prometheus-server 9090:9090 -n monitoring`
- [ ] 2.3.3 Verify Grafana running: `kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring`
- [ ] 2.3.4 Configure basic alert rules (CPU > 80%, Memory > 85%, Pod restart)
- [ ] 2.3.5 Setup ServiceMonitor for future custom metrics

### Subtasks — 🟡 Teammate

- [ ] 2.3.6 Login Grafana (admin/prom-operator) → explore built-in dashboards
- [ ] 2.3.7 Create custom dashboard "ZERO DOOR Overview":
    - Panel 1: CPU Usage by namespace
    - Panel 2: Memory Usage by namespace
    - Panel 3: Pod count + status (Running/CrashLoop/Pending)
    - Panel 4: Network traffic
- [ ] 2.3.8 Export dashboard JSON → commit vào `infra/grafana/dashboards/`

### Branch & PR

- [ ] Branch: `infra/observability-stack`
- [ ] PR Created
- [ ] Prometheus Target page shows all targets UP
- [ ] Grafana dashboard screenshot attached

---

## 📝 Notes

> **Prometheus Query cho Gaia sẽ dùng sau:**
> ```promql
> # CPU usage per pod
> rate(container_cpu_usage_seconds_total{namespace="target-app"}[5m])
>
> # Memory usage per pod
> container_memory_working_set_bytes{namespace="target-app"}
>
> # HTTP request rate
> rate(http_server_requests_seconds_count{namespace="target-app"}[1m])
>
> # HTTP error rate (5xx)
> rate(http_server_requests_seconds_count{status=~"5.."}[1m])
> ```

> **Dashboard cho Teammate:**
>
> Grafana có built-in dashboards khi dùng kube-prometheus-stack:
> - Dashboard ID 15757: K8s Cluster Monitoring
> - Dashboard ID 6417: Kubernetes Pods
> - Teammate cần import + customize thêm cho ZERO DOOR branding

> **Tham khảo:**
>
> - [plan.md](../docs/plan.md) Section 5.1 — Observability Stack
> - Prometheus Operator: https://prometheus-operator.dev/
> - Grafana Getting Started: https://grafana.com/docs/grafana/latest/getting-started/
