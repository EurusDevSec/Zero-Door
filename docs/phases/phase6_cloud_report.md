# Phase 6: Cloud Transition & Final Scientific Report

> **Timeline:** Week 21-24 (Sprint 11-12)  
> **Owner:** EurusDevSec (Cloud Deploy & Demo) + hp8001 (Report Writing & Slides)  
> **Milestone:** M7 (Defense Ready)  
> **Prerequisite:** Phase 5 hoàn thành (Experiment data collected & analyzed)

---

## 1. Mục tiêu Phase

Hoàn thiện 2 deliverables cuối cùng: (1) Deploy hệ thống lên AWS Cloud để chứng minh tính khả thi ở môi trường production-like, và (2) Hoàn thành báo cáo nghiên cứu khoa học + demo video + bài thuyết trình để bảo vệ trước Hội đồng Khoa học Trường Đại học Thủ Dầu Một.

---

## 2. Tasks

### 2.1. Cloud Deployment — AWS (FinOps Strategy)

- [ ] **T6.1** Triển khai **1 EC2 Instance** chạy K3s:
  - Instance type: `t3.medium` hoặc `t3.large` (Spot Instance để tiết kiệm ~70%)
  - AMI: Ubuntu 22.04 LTS
  - Storage: 30GB GP3 EBS
  - Mục tiêu chi phí: < $15/tháng

- [ ] **T6.2** Cấu hình **VPC & Security Groups**:

  | Rule | Port | Source | Mục đích |
  |---|---|---|---|
  | SSH | 22 | IP cá nhân | Quản trị server |
  | HTTP | 80 | 0.0.0.0/0 | Frontend access |
  | HTTPS | 443 | 0.0.0.0/0 | Frontend access (TLS) |
  | Grafana | 3000 | IP cá nhân | Dashboard access |
  | K8s API | 6443 | IP cá nhân | kubectl remote access |

- [ ] **T6.3** Cài đặt **K3s** trên EC2 Instance:
  - Single-node mode (server + agent trên cùng 1 máy)
  - Disable Traefik, sử dụng Nginx Ingress
  - Configure kubectl context từ máy local để remote quản lý cluster

- [ ] **T6.4** Deploy full Helm stack lên K3s cloud:
  - 3 Namespaces (zero-door, target-app, monitoring)
  - Kafka, Prometheus, Grafana, Fluent Bit, Elasticsearch
  - 3 Agents (Nemesis, Gaia, Hephaestus) + Chaos Worker
  - Google Online Boutique (target-app)
  - Sử dụng Helm values file riêng cho cloud environment (cloud-values.yaml)

- [ ] **T6.5** Verify hệ thống hoạt động ổn định trên cloud:
  - Chạy lại ít nhất 5 experiment runs (E1-E3) trên cloud
  - So sánh MTTD/MTTR giữa local K3d và cloud K3s
  - Screenshot Grafana dashboards trên cloud

### 2.2. Domain & SSL (Tùy chọn)

- [ ] **T6.6** (Optional) Gắn domain cho Grafana dashboard và Frontend:
  - Mua domain (hoặc dùng free subdomain từ DuckDNS/nip.io)
  - Cấu hình Nginx Ingress + cert-manager cho Let's Encrypt TLS
  - Mục đích: Demo cho Hội đồng truy cập dashboard qua URL thay vì IP

### 2.3. Demo Video Production

- [ ] **T6.7** Chuẩn bị kịch bản Demo Video (5-10 phút):

  | Segment | Thời lượng | Nội dung |
  |---|---|---|
  | Intro | 30s | Giới thiệu đề tài, vấn đề nghiên cứu |
  | Architecture | 1 phút | Show sơ đồ kiến trúc, giải thích 3 Agents, Kafka, K8s |
  | Live Demo Setup | 1 phút | Show Grafana dashboard steady-state, show pods running |
  | Attack Phase | 2 phút | Trigger Nemesis attack, show CPU spike trên Grafana real-time |
  | Detect Phase | 1 phút | Show Gaia alert xuất hiện trên Kafka, Grafana alert firing |
  | Heal Phase | 2 phút | Show Hephaestus auto scale-up/restart, show system recovery |
  | Results | 1 phút | Show MTTD/MTTR numbers, so sánh bảng Manual vs Auto |
  | Conclusion | 30s | Tóm tắt đóng góp, hạn chế, hướng phát triển |

- [ ] **T6.8** Quay video demo:
  - Sử dụng OBS Studio hoặc tool record màn hình
  - Split screen: Terminal (kubectl) bên trái + Grafana Dashboard bên phải
  - Thêm subtitles/annotations giải thích từng bước
  - Export: MP4, 1080p

### 2.4. Báo cáo Nghiên cứu Khoa học

- [ ] **T6.9** Hoàn thiện cấu trúc báo cáo NCKH (tham khảo [plan_original_v3.md](file:///r:/_Projects/Eurus_Workspace/zero_door/docs/plan_original_v3.md)):

  | Chương | Nội dung | Người viết |
  |---|---|---|
  | **Chương 1** | Đặt vấn đề & Mục tiêu nghiên cứu | hp8001 |
  | **Chương 2** | Cơ sở lý thuyết (Multi-Agent, Chaos Engineering, K8s, Kafka) | hp8001 + EurusDevSec review |
  | **Chương 3** | Thiết kế hệ thống (Architecture, Tech Stack, Agent Design) | EurusDevSec |
  | **Chương 4** | Triển khai (Implementation Details, Docker, Helm, K8s configs) | EurusDevSec |
  | **Chương 5** | Thí nghiệm & Kết quả (Experiment Design, Data Analysis, Charts) | EurusDevSec + hp8001 |
  | **Chương 6** | Kết luận & Hướng phát triển | hp8001 + EurusDevSec |

- [ ] **T6.10** Đưa dữ liệu thí nghiệm (Phase 5) vào Chương 5:
  - Bảng MTTD/MTTR cho mỗi scenario (Mean, Median, P95)
  - Bảng so sánh Manual vs Automated
  - Biểu đồ bar chart, box plot
  - Grafana screenshots (before/during/after attack)
  - Phân tích và nhận xét cho từng kịch bản

- [ ] **T6.11** Viết phần **Giới hạn nghiên cứu** (thật thà với Hội đồng):
  - L1: Kết quả chỉ validate trên sandbox, chưa test production-scale
  - L2: Chỉ 3 loại tấn công (subset OWASP Top 10)
  - L3: Single K8s cluster, chưa test multi-cluster
  - L4: LLM payload quality phụ thuộc model và prompt engineering
  - L5: Chưa benchmark với commercial tools (Gremlin, PagerDuty AIOps)

- [ ] **T6.12** Viết phần **Hướng phát triển tương lai**:
  - Mở rộng thêm attack types (Network attacks, DNS poisoning)
  - Multi-cluster federation support
  - Reinforcement Learning thay cho rule-based healing
  - Integration với commercial SIEM/SOAR platforms
  - Benchmark với Gremlin, LitmusChaos, Harness

### 2.5. Bài Thuyết trình (Defense Presentation)

- [ ] **T6.13** Chuẩn bị slide thuyết trình (15-20 slides):

  | Slide | Nội dung |
  |---|---|
  | 1-2 | Title, Team, Timeline |
  | 3-4 | Vấn đề nghiên cứu, Case studies (AWS S3, Facebook outage) |
  | 5-6 | Research Questions & Objectives |
  | 7-8 | Architecture Diagram (High-level + Sequence Diagram) |
  | 9-10 | Tech Stack & Implementation highlights |
  | 11-12 | Experiment Design & Methodology |
  | 13-15 | Results: MTTD/MTTR charts, Uptime comparison |
  | 16-17 | Live Demo hoặc Demo Video |
  | 18-19 | Contributions, Limitations, Future Work |
  | 20 | Q&A |

- [ ] **T6.14** Chuẩn bị **câu hỏi phản biện thường gặp** từ Hội đồng và câu trả lời:

  | Câu hỏi có thể gặp | Hướng trả lời |
  |---|---|
  | "Tại sao dùng 3 agents riêng biệt thay vì 1 monolith agent?" | Separation of Concerns, fault isolation, scalability |
  | "30 runs có đủ statistical significance không?" | Central Limit Theorem, confidence interval, time constraints |
  | "Nemesis tấn công chính hệ thống mình — có nguy hiểm không?" | Blast radius control, RBAC, namespace isolation, kill switch |
  | "So với Gremlin/LitmusChaos thì Zero Door khác gì?" | Closed-loop (Attack+Detect+Heal), AI-driven, integrated platform |
  | "LLM sinh payload — độ tin cậy thế nào?" | Template+variation approach, validation layer, fallback rules |

---

## 3. Definition of Done (Tiêu chí hoàn thành Phase — Hoàn thành dự án)

| # | Tiêu chí | Cách kiểm chứng |
|---|---|---|
| 1 | Hệ thống chạy thành công trên AWS EC2/K3s | `kubectl get pods -A` trên cloud cluster → all Running |
| 2 | Cloud experiment runs cho MTTD/MTTR tương đương local | Bảng so sánh local vs cloud |
| 3 | Demo video hoàn thành (5-10 phút) | File MP4 trong repo/docs |
| 4 | Báo cáo NCKH hoàn thành đầy đủ 6 chương | File PDF/Word |
| 5 | Slide thuyết trình hoàn thành | File PowerPoint/PDF |
| 6 | Source code commit final trên GitHub | Git tag `v1.0.0` |
| 7 | README.md cập nhật instructions chạy lại hệ thống | Người khác có thể reproduce |

---

## 4. Design Questions (Bạn cần tự trả lời)

### Q1: EC2 Spot Instance có thể bị AWS thu hồi (terminate) bất kỳ lúc nào. Bạn xử lý tình huống này thế nào?
> Gợi ý: Spot Interruption Handling, data backup strategy.
> _Trả lời:_

### Q2: Khi deploy lên cloud, Helm values file cho cloud khác gì so với local?
> Ví dụ: Storage class, resource limits, ingress host, Kafka replication factor...
> _Trả lời:_

### Q3: Hội đồng hỏi "Tại sao không dùng EKS (Managed K8s)?". Bạn trả lời thế nào?
> _Trả lời:_

---

## 5. Budget Summary (FinOps Tổng kết)

| Hạng mục | Chi phí ước tính | Ghi chú |
|---|---|---|
| AWS EC2 Spot (t3.medium, 2 tháng) | ~$20-30 | Chỉ chạy khi cần demo/test |
| Domain (tùy chọn) | 0 - $10 | DuckDNS free hoặc mua domain rẻ |
| OpenAI API tokens | ~$10-20 | Giới hạn sử dụng, dùng Ollama local khi dev |
| **Tổng Phase 6** | **< $60** | Nằm trong budget 4.9M VNĐ ban đầu |

---

## 6. References

| Resource | Link |
|---|---|
| K3s Installation | https://docs.k3s.io/installation |
| AWS EC2 Spot Instances | https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-spot-instances.html |
| cert-manager (Let's Encrypt) | https://cert-manager.io/docs/ |
| OBS Studio | https://obsproject.com/ |
| Google SRE Book | https://sre.google/sre-book/table-of-contents/ |
