# TÀI LIỆU THAM KHẢO - ZERO DOOR

## Các nghiên cứu liên quan đến đề tài Self-Healing Microservices, Chaos Engineering, và AIOps

---

## 1. NGHIÊN CỨU TRỰC TIẾP LIÊN QUAN (Highly Relevant)

### 1.1. Self-Healing + Chaos Engineering

| #   | Tên bài                                                                                                          | Tác giả                             | Năm  | Nguồn                         | Citations | Link                                                                |
| --- | ---------------------------------------------------------------------------------------------------------------- | ----------------------------------- | ---- | ----------------------------- | --------- | ------------------------------------------------------------------- |
| 1   | **On evaluating self-adaptive and self-healing systems using chaos engineering**                                 | Naqvi, M.A., Malik, S., Astekin, M. | 2022 | IEEE International Conference | 23        | [IEEE](https://ieeexplore.ieee.org/abstract/document/9935013/)      |
| 2   | **CHESS: A framework for evaluation of self-adaptive systems based on chaos engineering**                        | Malik, S., Naqvi, M.A., Moonen, L.  | 2023 | IEEE SEAMS                    | 14        | [IEEE](https://ieeexplore.ieee.org/abstract/document/10174151/)     |
| 3   | **Phoenix Stack: A Self-Healing Microservice Architecture for Real-Time Web Applications**                       | Tutuncuoglu, B.T.                   | 2025 | SSRN                          | -         | [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5343101) |
| 4   | **Architecting Resilient Cloud-Native APIs: Autonomous Fault Recovery in Event-Driven Microservices Ecosystems** | Tadi, S.                            | 2022 | ResearchGate                  | 18        | [PDF](https://www.researchgate.net/publication/390240674)           |

**Tại sao quan trọng:** Các bài này trực tiếp nghiên cứu về Self-Healing trong Microservices với Chaos Engineering - giống ZERO DOOR.

---

### 1.2. AIOps + Auto-Remediation (Closest to ZERO DOOR)

| #   | Tên bài                                                                                         | Tác giả                       | Năm  | Nguồn     | Citations | Link                                                             |
| --- | ----------------------------------------------------------------------------------------------- | ----------------------------- | ---- | --------- | --------- | ---------------------------------------------------------------- |
| 5   | **⭐ ADARMA: Auto-Detection and Auto-Remediation of Microservice Anomalies by Leveraging LLMs** | Sarda, K., Namrud, Z., et al. | 2023 | ACM ISSTA | 24        | [ACM](https://dl.acm.org/doi/abs/10.5555/3615924.3615949)        |
| 6   | **A Survey of AIOps for Failure Management in the Era of Large Language Models**                | Zhang, L., Jia, T., et al.    | 2024 | arXiv     | 35        | [arXiv](https://arxiv.org/abs/2406.11213)                        |
| 7   | **AI for IT Operations (AIOps) on Cloud Platforms: Reviews, Opportunities and Challenges**      | Cheng, Q., Sahoo, D., et al.  | 2023 | arXiv     | 69        | [arXiv](https://arxiv.org/abs/2304.04661)                        |
| 8   | **Leveraging AI and ML for Automated Incident Resolution in Cloud Infrastructure**              | Veluru, S.P.                  | 2021 | IJAIDSML  | 33        | [Link](https://ijaidsml.org/index.php/ijaidsml/article/view/143) |

**⭐ Bài #5 (ADARMA) rất giống ZERO DOOR:** Dùng LLM cho auto-detection và auto-remediation trong microservices!

---

### 1.3. Chaos Engineering cho Microservices

| #   | Tên bài                                                                                                   | Tác giả                             | Năm  | Nguồn                      | Citations | Link                                                      |
| --- | --------------------------------------------------------------------------------------------------------- | ----------------------------------- | ---- | -------------------------- | --------- | --------------------------------------------------------- |
| 9   | **Chaos Engineering for Microservices**                                                                   | Akuthota, A.                        | 2023 | St. Cloud State University | 4         | [PDF](https://repository.stcloudstate.edu/csit_etds/42/)  |
| 10  | **Resilience Engineering in DevOps: Fault Injection and Chaos Testing for Distributed Systems**           | Ramaswamy, Y.                       | 2020 | NeuroQuantology            | 2         | [PDF](https://www.researchgate.net/publication/393888322) |
| 11  | **Resilience Evaluation of Kubernetes in Cloud-Edge Environments via Failure Injection**                  | Chen, Z., Goudarzi, M., Toosi, A.N. | 2025 | arXiv                      | 1         | [arXiv](https://arxiv.org/abs/2507.16109)                 |
| 12  | **From Monolith to Microservices: Building Scalable Applications with K8s, CI/CD, and Chaos Engineering** | Mahgoub, A.                         | 2025 | Theseus                    | -         | [PDF](https://www.theseus.fi/handle/10024/887394)         |

---

## 2. NGHIÊN CỨU NỀN TẢNG (Foundational Papers)

### 2.1. Chaos Engineering - Gốc

| #   | Tên bài                                              | Tác giả                      | Năm  | Nguồn         | Citations | Ý nghĩa                        |
| --- | ---------------------------------------------------- | ---------------------------- | ---- | ------------- | --------- | ------------------------------ |
| 13  | **Chaos Engineering**                                | Basiri, A., et al. (Netflix) | 2016 | IEEE Software | 500+      | Paper gốc về Chaos Engineering |
| 14  | **The Netflix Simian Army**                          | Netflix Tech Blog            | 2011 | Netflix       | -         | Giới thiệu Chaos Monkey        |
| 15  | **Chaos Engineering: System Resiliency in Practice** | Casey Rosenthal, Nora Jones  | 2020 | O'Reilly Book | -         | Sách tổng hợp về CE            |

### 2.2. Site Reliability Engineering

| #   | Tên bài                                                              | Tác giả         | Năm  | Nguồn    | Citations | Ý nghĩa                    |
| --- | -------------------------------------------------------------------- | --------------- | ---- | -------- | --------- | -------------------------- |
| 16  | **Site Reliability Engineering: How Google Runs Production Systems** | Google SRE Team | 2016 | O'Reilly | 1000+     | Định nghĩa MTTD, MTTR, SLO |
| 17  | **The Site Reliability Workbook**                                    | Google SRE Team | 2018 | O'Reilly | -         | Practical SRE              |

### 2.3. Multi-Agent Systems

| #   | Tên bài                                                      | Tác giả        | Năm  | Nguồn     | Citations | Ý nghĩa               |
| --- | ------------------------------------------------------------ | -------------- | ---- | --------- | --------- | --------------------- |
| 18  | **An Introduction to MultiAgent Systems**                    | Wooldridge, M. | 2009 | Wiley     | 10000+    | Textbook chuẩn về MAS |
| 19  | **Multi-Agent Systems: A Modern Approach to Distributed AI** | Weiss, G.      | 1999 | MIT Press | -         | Classic MAS book      |

---

## 3. NGHIÊN CỨU BỔ SUNG (Supporting Research)

### 3.1. AIOps Platforms & Frameworks

| #   | Tên bài                                                                                 | Tác giả            | Năm  | Nguồn            | Link                                                                |
| --- | --------------------------------------------------------------------------------------- | ------------------ | ---- | ---------------- | ------------------------------------------------------------------- |
| 20  | **A Practical Approach to Defining a Framework for Developing an Agentic AIOps System** | Zota, R.D., et al. | 2025 | MDPI Electronics | [Link](https://www.mdpi.com/2079-9292/14/9/1775)                    |
| 21  | **Explainable AIOps: A Deep Survey on Trustworthy AI in Cloud-Scale DevOps**            | Sami, M.A., et al. | 2025 | Theses Journal   | [PDF](https://www.thesesjournal.com/index.php/1/article/view/607)   |
| 22  | **AIOps Evolution: From Reactive Monitoring to Predictive Service Management**          | Solanke, A.A.      | 2024 | ResearchGate     | [PDF](https://www.researchgate.net/publication/390585300)           |
| 23  | **Predictive Analytics and Auto-Remediation using AI/ML in Cloud Computing**            | Garg, S.           | 2019 | SSRN             | [Link](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5267117) |

### 3.2. Kubernetes & Cloud-Native Security

| #   | Tên bài                                                                             | Tác giả       | Năm  | Nguồn        | Link                                                                         |
| --- | ----------------------------------------------------------------------------------- | ------------- | ---- | ------------ | ---------------------------------------------------------------------------- |
| 24  | **Building Resilient Systems: The Role of Containers and Kubernetes**               | Perumal, A.P. | 2025 | IGI Global   | [Link](https://www.igi-global.com/chapter/building-resilient-systems/377003) |
| 25  | **Engineering Resilience: Cloud-Native Design Patterns for Fault-Tolerant Systems** | Oduri, S.     | 2024 | ResearchGate | [PDF](https://www.researchgate.net/publication/394980505)                    |
| 26  | **AIOps: How SRE Teams Can Leverage AI in IT-Operations**                           | Hansson, J.   | 2024 | DiVA Portal  | [PDF](https://www.diva-portal.org/smash/record.jsf?pid=diva2:1932231)        |

---

## 4. SO SÁNH VỚI ZERO DOOR

### 4.1. Bảng so sánh với các nghiên cứu tương tự

| Tiêu chí              | ADARMA (2023) | CHESS (2023)    | Phoenix Stack (2025) | **ZERO DOOR**   |
| --------------------- | ------------- | --------------- | -------------------- | --------------- |
| **LLM Integration**   | ✅ GPT-based  | ❌              | ❌                   | ✅ Spring AI    |
| **Chaos Engineering** | ❌            | ✅ ChaosToolkit | ❌                   | ✅ AI-generated |
| **Auto-Remediation**  | ✅            | ⚠️ Manual       | ✅                   | ✅ K8s API      |
| **Closed-Loop**       | ⚠️ Partial    | ❌              | ✅                   | ✅              |
| **Multi-Agent**       | ❌ Single     | ❌              | ❌                   | ✅ 3 Agents     |
| **Open-Source**       | ❌            | ⚠️ Partial      | ❌                   | ✅              |
| **Red Team AI**       | ❌            | ❌              | ❌                   | ✅ Nemesis      |

### 4.2. Khoảng trống ZERO DOOR lấp đầy

```
                    EXISTING RESEARCH
    ┌─────────────────────────────────────────────────┐
    │                                                 │
    │   ADARMA: LLM + Auto-remediation (no Chaos)     │
    │                     │                           │
    │   CHESS: Chaos + Self-adaptive (no AI)          │
    │                     │                           │
    │   Phoenix: Self-healing (no Chaos, no AI)       │
    │                     │                           │
    └─────────────────────┼───────────────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │      ZERO DOOR        │
              │                       │
              │  Chaos + AI + Multi-  │
              │  Agent + Closed-Loop  │
              │  + Open-Source        │
              │                       │
              └───────────────────────┘
```

---

## 5. CÁC BÀI NÊN ĐỌC KỸ (Must-Read)

### 5.1. Top 5 Papers Quan Trọng Nhất

| Priority | Paper                               | Lý do                                                            |
| -------- | ----------------------------------- | ---------------------------------------------------------------- |
| ⭐⭐⭐   | **ADARMA (2023)** - ACM             | Gần nhất với ZERO DOOR: LLM + auto-remediation cho microservices |
| ⭐⭐⭐   | **CHESS (2023)** - IEEE             | Framework đánh giá self-adaptive systems bằng chaos engineering  |
| ⭐⭐⭐   | **AIOps Survey (2024)** - arXiv     | Survey toàn diện về LLM trong AIOps                              |
| ⭐⭐     | **AIOps on Cloud (2023)** - arXiv   | Survey về AIOps với 69 citations                                 |
| ⭐⭐     | **Chaos Engineering (2016)** - IEEE | Paper gốc, foundational                                          |

### 5.2. Papers để Cite trong Báo cáo

**Cho phần Chaos Engineering:**

```
Basiri, A., et al. (2016). "Chaos Engineering." IEEE Software, 33(3), 35-41.
Malik, S., et al. (2023). "CHESS: A Framework for Evaluation of Self-Adaptive Systems." IEEE SEAMS.
```

**Cho phần AIOps & Auto-Remediation:**

```
Sarda, K., et al. (2023). "ADARMA: Auto-Detection and Auto-Remediation by Leveraging LLMs." ACM ISSTA.
Cheng, Q., et al. (2023). "AI for IT Operations on Cloud Platforms." arXiv:2304.04661.
Zhang, L., et al. (2024). "A Survey of AIOps for Failure Management in the Era of LLMs." arXiv:2406.11213.
```

**Cho phần Multi-Agent Systems:**

```
Wooldridge, M. (2009). An Introduction to MultiAgent Systems. Wiley.
```

**Cho phần SRE/Metrics:**

```
Google SRE Team. (2016). Site Reliability Engineering. O'Reilly Media.
```

---

## 6. HƯỚNG DẪN TÌM THÊM

### 6.1. Keywords để search

```
- "self-healing microservices" + "kubernetes"
- "chaos engineering" + "AI" + "machine learning"
- "AIOps" + "auto-remediation" + "LLM"
- "multi-agent systems" + "DevOps" OR "SRE"
- "anomaly detection" + "microservices" + "automated response"
- "proactive fault tolerance" + "cloud-native"
```

### 6.2. Nguồn tìm kiếm

| Nguồn          | URL                 | Ưu điểm                   |
| -------------- | ------------------- | ------------------------- |
| Google Scholar | scholar.google.com  | Đầy đủ, có citation count |
| IEEE Xplore    | ieeexplore.ieee.org | Papers chất lượng cao     |
| arXiv          | arxiv.org           | Pre-prints mới nhất       |
| ACM DL         | dl.acm.org          | Computer Science focus    |
| ResearchGate   | researchgate.net    | Có PDF free               |
| DBLP           | dblp.org            | Database papers CS        |

### 6.3. Conferences để theo dõi

- **ICSE** - International Conference on Software Engineering
- **ISSTA** - International Symposium on Software Testing and Analysis
- **SEAMS** - Software Engineering for Adaptive and Self-Managing Systems
- **SRE Con** - Site Reliability Engineering Conference
- **KubeCon** - Kubernetes Conference

---

## 7. LƯU Ý QUAN TRỌNG

### 7.1. Khi trình bày với Hội đồng

> **Không nói:** "Chưa ai làm cái này"
>
> **Nên nói:** "Các nghiên cứu hiện tại như ADARMA, CHESS đã giải quyết từng phần. ZERO DOOR đóng góp bằng cách **tích hợp hoàn chỉnh** Chaos Engineering + AI + Multi-Agent trong một platform open-source."

### 7.2. Cách cite đúng

```latex
@inproceedings{sarda2023adarma,
  title={ADARMA: Auto-Detection and Auto-Remediation of Microservice Anomalies by Leveraging Large Language Models},
  author={Sarda, Karan and Namrud, Zina and others},
  booktitle={Proceedings of ISSTA 2023},
  year={2023}
}
```

---

_Cập nhật: 26/01/2026_
