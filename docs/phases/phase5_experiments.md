# Phase 5: War Game Experiments & Data Collection

> **Timeline:** Week 17-20 (Sprint 9-10)  
> **Owner:** EurusDevSec (Experiment Design & Execution) + hp8001 (Data Collection & Analysis)  
> **Milestone:** M6 (Full Loop validated)  
> **Prerequisite:** Phase 4 hoàn thành (Full Attack → Detect → Heal loop working)

---

## 1. Mục tiêu Phase

Chạy các kịch bản tấn công có hệ thống (War Game Experiments), thu thập dữ liệu định lượng (MTTD, MTTR, Uptime, False Positive Rate), và so sánh hiệu quả Self-Healing tự động với phản ứng thủ công. Dữ liệu từ Phase này là **nền tảng khoa học** cho báo cáo nghiên cứu (Phase 6).

---

## 2. Tasks

### 2.1. Thiết kế Thí nghiệm (Experiment Design)

- [ ] **T5.1** Định nghĩa **Steady-State Hypothesis** (trạng thái bình thường) cho Target App:

  | Metric | Steady-State Range | Prometheus Query |
  |---|---|---|
  | CPU Usage per pod | < 60% | `rate(container_cpu_usage_seconds_total{namespace="target-app"}[1m])` |
  | Memory Usage per pod | < 70% | `container_memory_working_set_bytes{namespace="target-app"}` |
  | HTTP Error Rate (5xx) | < 1% | `rate(http_server_requests_seconds_count{status=~"5.."}[1m])` |
  | P99 Latency | < 500ms | `histogram_quantile(0.99, rate(http_server_requests_seconds_bucket[1m]))` |
  | Kafka Consumer Lag | < 100 messages | Kafka JMX metrics |

- [ ] **T5.2** Thiết kế bảng **Experiment Matrix** — 4 kịch bản chính:

  | ID | Kịch bản | Attack Type | Expected Gaia Alert | Expected Hephaestus Action | Success Criteria |
  |---|---|---|---|---|---|
  | **E1** | CPU Stress trên cartservice | `CPU_STRESS` (60s) | `HIGH_CPU` CRITICAL | `SCALE_UP` hoặc `RESTART` | MTTD < 60s, MTTR < 180s, Error rate < 1% |
  | **E2** | HTTP Flood trên frontend | `HTTP_FLOOD` (30s, 500 rps) | `HIGH_ERROR_RATE` CRITICAL | `SCALE_UP` + `BLOCK_IP` | MTTD < 60s, MTTR < 180s, Latency < 500ms sau heal |
  | **E3** | Pod Kill 1 pod frontend | `POD_KILL` | `POD_CRASH` CRITICAL | `RESTART` (verify recreated) | MTTD < 30s, MTTR < 60s, Zero data loss |
  | **E4** | Combined: CPU Stress + HTTP Flood + Pod Kill | All 3 đồng thời | Multiple alerts | Priority-based healing | System stable < 3 phút, Uptime ≥ 95% |

- [ ] **T5.3** Thiết kế **Baseline Comparison** (So sánh với phản ứng thủ công):
  - Chạy cùng 4 kịch bản **KHÔNG** bật Hephaestus (chỉ có Gaia alert)
  - Đo thời gian phản ứng thủ công của EurusDevSec (ngồi xem Grafana + gõ `kubectl` bằng tay)
  - So sánh MTTD và MTTR giữa Manual vs. Automated

### 2.2. Execution Protocol (Quy trình chạy thí nghiệm)

- [ ] **T5.4** Viết script **Experiment Runner** (bash hoặc Go CLI):
  - Reset cluster state về steady-state trước mỗi experiment
  - Ghi timestamp `T0` (experiment start)
  - Trigger attack command qua Kafka
  - Thu thập timestamps từ Kafka topics:
    - `T1` = timestamp trong `attack.results` (attack executed)
    - `T2` = timestamp trong `monitoring.alerts` (Gaia detected)
    - `T3` = timestamp trong `healing.actions` (Hephaestus healed)
  - Tính toán: `MTTD = T2 - T1`, `MTTR = T3 - T2`
  - Export kết quả ra file CSV

- [ ] **T5.5** Chạy mỗi kịch bản (E1-E4) **tối thiểu 30 lần** (statistical significance):
  - 30 runs × 4 scenarios = 120 experiment runs
  - Chia thành: 15 runs với Automated Healing (Hephaestus ON) + 15 runs Manual (Hephaestus OFF)
- [ ] **T5.6** Ghi nhận các **edge cases** và **failures** trong quá trình thí nghiệm:
  - False Positives: Gaia alert nhưng không có attack thực sự
  - False Negatives: Attack xảy ra nhưng Gaia không detect được
  - Healing Failures: Hephaestus thực hiện action nhưng không giải quyết vấn đề

### 2.3. Data Collection & Export

- [ ] **T5.7** Thu thập dữ liệu từ các nguồn:

  | Nguồn dữ liệu | Format | Phương pháp thu thập |
  |---|---|---|
  | Kafka topics (`attack.results`, `monitoring.alerts`, `healing.actions`) | JSON → CSV | Kafka consumer script export ra CSV |
  | Prometheus metrics (CPU, Memory, Error Rate, Latency) | Time-series → CSV | Prometheus HTTP API `/api/v1/query_range` export |
  | Grafana Dashboard snapshots | PNG screenshots | Grafana Snapshot API hoặc manual screenshots |
  | Elasticsearch logs | JSON → filtered CSV | Elasticsearch `_search` API với time range filter |
  | K8s Events (pod restarts, scale events) | JSON → CSV | `kubectl get events --sort-by=.lastTimestamp -o json` |

- [ ] **T5.8** Tạo cấu trúc lưu trữ dữ liệu thí nghiệm:
  ```
  docs/experiments/
  ├── raw_data/
  │   ├── e1_cpu_stress/
  │   │   ├── run_01.csv
  │   │   ├── run_02.csv
  │   │   └── ...
  │   ├── e2_http_flood/
  │   ├── e3_pod_kill/
  │   └── e4_combined/
  ├── analysis/
  │   ├── summary_statistics.csv
  │   ├── mttd_comparison.png
  │   ├── mttr_comparison.png
  │   └── uptime_comparison.png
  └── screenshots/
      ├── grafana_e1_before.png
      ├── grafana_e1_during.png
      └── grafana_e1_after.png
  ```

### 2.4. Data Analysis & Visualization

- [ ] **T5.9** Tính toán **Summary Statistics** cho mỗi kịch bản:

  | Metric | Công thức |
  |---|---|
  | MTTD (Mean) | Trung bình cộng MTTD của 15 runs |
  | MTTD (Median) | Giá trị trung vị |
  | MTTD (P95) | Percentile 95 |
  | MTTR (Mean/Median/P95) | Tương tự |
  | Uptime (%) | `(1 - total_error_seconds / total_experiment_seconds) × 100` |
  | False Positive Rate (%) | `false_alerts / total_alerts × 100` |
  | Heal Success Rate (%) | `successful_heals / total_heal_attempts × 100` |

- [ ] **T5.10** Tạo **Comparison Charts** (dùng Python matplotlib, Excel, hoặc Google Sheets):
  - Bar chart: MTTD Manual vs. Automated (cho mỗi scenario E1-E4)
  - Bar chart: MTTR Manual vs. Automated
  - Line chart: Uptime % over time during combined attack (E4)
  - Box plot: Distribution of MTTD/MTTR across 15 runs

- [ ] **T5.11** Tạo bảng **Statistical Significance Test** (tùy chọn nâng cao):
  - Dùng Wilcoxon signed-rank test hoặc Mann-Whitney U test
  - So sánh MTTD(Manual) vs MTTD(Auto): p-value < 0.05?
  - Kết luận: Sự khác biệt có ý nghĩa thống kê hay không?

### 2.5. Unified Control Center Dashboard (Giao diện v2)

- [ ] **T5.12** Nâng cấp giao diện lên ngôn ngữ thiết kế **AWS Cloudscape Light Theme**:
  - Di chuyển hoàn toàn từ giao diện Dark Cyberpunk sang phong cách Light Theme tối giản của Amazon.
  - Áp dụng bố cục **cố định không cuộn trang (Fixed Viewport Grid Layout)**, giúp tất cả 4 panel chính nằm trọn trong 1 màn hình.
  - Tăng độ rộng cột bên trái lên **290px** và cấu hình danh sách Microservices Status hiển thị theo 1 cột thẳng đứng để không bị che khuất tên của các dịch vụ microservice dài (như `productcatalogservice`, `currencyservice`).
  - Thiết kế lại sơ đồ kiến trúc luồng tấn công/phục hồi (**2-Layer Topology Flow**):
    - Tầng trên (top row): Luồng chính `Nemesis ⚔️ → Kafka 🗳️ → Boutique App 🛍️ → Hephaestus 🛡️`.
    - Tầng dưới (bottom row): Các thành phần con `Gemini ✨ | Chaos Worker ⚡ | Gaia Agent 👁️` nối dọc trực quan.
  - Tăng thời gian hiệu ứng shimmer loading lên **2.8s** cho cảm giác tải tự nhiên và thiết lập Sidebar/Chat panel có khả năng thu gọn (collapsible).

---

## 3. Definition of Done (Tiêu chí hoàn thành Phase)

| # | Tiêu chí | Cách kiểm chứng |
|---|---|---|
| 1 | Chạy đủ 120 experiment runs (30 × 4 scenarios) | File CSV chứa ≥ 120 rows data |
| 2 | Baseline Manual data thu thập đủ | 15 runs manual × 4 scenarios = 60 rows |
| 3 | MTTD < 60s trong ≥ 70% automated runs | Summary statistics confirm |
| 4 | MTTR < 180s trong ≥ 70% automated runs | Summary statistics confirm |
| 5 | Uptime ≥ 99% cho E1, E2, E3 (single attacks) | Uptime calculation from metrics |
| 6 | Comparison charts đã tạo | PNG files trong `docs/experiments/analysis/` |
| 7 | Grafana screenshots cho mỗi scenario | PNG files trong `docs/experiments/screenshots/` |

---

## 4. Design Questions (Bạn cần tự trả lời)

### Q1: Bao nhiêu runs là đủ để có statistical significance cho MTTD/MTTR?
> Gợi ý: Trong nghiên cứu khoa học, thường cần n ≥ 30 cho Central Limit Theorem. Nhưng với thời gian giới hạn, 15 runs/scenario có chấp nhận được không?
> _Trả lời:_

### Q2: Làm sao đảm bảo cluster trở về steady-state giữa các runs?
> Nếu run trước gây OOM và run sau chạy trên cluster đang "bệnh" → dữ liệu bị bias.
> _Trả lời:_

### Q3: Khi chạy baseline manual (Hephaestus OFF), bạn có nên tính thời gian bạn mở terminal + gõ lệnh kubectl không? Hay chỉ tính từ lúc bạn nhìn thấy alert trên Grafana?
> Gợi ý: Xác định rõ ranh giới đo MTTD và MTTR cho cả hai trường hợp (auto vs manual) để so sánh công bằng.
> _Trả lời:_

---

## 5. Expected Output Data Format (CSV)

```csv
run_id,scenario,mode,attack_type,attack_start,attack_end,detect_time,heal_start,heal_end,mttd_seconds,mttr_seconds,uptime_percent,heal_status,false_positives,notes
1,E1,AUTO,CPU_STRESS,2026-03-01T10:00:00Z,2026-03-01T10:01:00Z,2026-03-01T10:00:15Z,2026-03-01T10:00:18Z,2026-03-01T10:01:30Z,15,72,99.2,SUCCESS,0,
2,E1,MANUAL,CPU_STRESS,2026-03-01T10:05:00Z,2026-03-01T10:06:00Z,2026-03-01T10:05:45Z,2026-03-01T10:06:10Z,2026-03-01T10:08:30Z,45,165,97.1,SUCCESS,0,Manual kubectl scale
```

---

## 6. References

| Resource | Link |
|---|---|
| Chaos Engineering Principles | https://principlesofchaos.org/ |
| Prometheus Query API | https://prometheus.io/docs/prometheus/latest/querying/api/ |
| Statistical Tests for Small Samples | https://statisticsbyjim.com/hypothesis-testing/nonparametric-tests/ |
| Google SRE — Monitoring | https://sre.google/sre-book/monitoring-distributed-systems/ |
