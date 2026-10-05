# Oracle Database Copilot — Tài Liệu Tổng Hợp

> **Phiên bản:** 0.1 · **Ngày cập nhật:** 2026-09-17 · **Tổng số tài liệu gộp:** 15 files

---

## Mục Lục

| # | Nhóm | Tài liệu |
|---|---|---|
| 1 | Product | Business Requirements Document (BRD) |
| 2 | Product | Problem Statement |
| 3 | Product | Product Requirements Document (PRD) |
| 4 | Architecture | High-Level Design (HLD) |
| 5 | Architecture | Low-Level Design (LLD) |
| 6 | Technical | Oracle MCP Server Design |
| 7 | Technical | AI Engine Design |
| 8 | Technical | Correlation Engine Design |
| 9 | Technical | Evidence Engine Design |
| 10 | Technical | Investigation Engine Design |
| 11 | Tasks | Task Breakdown: Evidence Collection (Phase 1) |
| 12 | Tasks | Task Breakdown: Correlation & Health Engine (Phase 2) |
| 13 | Tasks | Task Breakdown: AI & Investigation Engine (Phase 3) |
| 14 | Implementation | Implementation Plan |
| 15 | Implementation | Test Plan |

---



<!-- ======================================================
     FILE: docs/01-product/brd.md
     ====================================================== -->

# BRD — Business Requirements Document
# Tài Liệu Yêu Cầu Nghiệp Vụ

**Sản phẩm / Product:** DB Copilot  
**Phiên bản / Version:** 0.1  
**Trạng thái / Status:** Draft  
**Ngày / Date:** 2026-09-08

---

> 🇻🇳 **Phần tiếng Việt / Vietnamese Section** — Sections 1–14  
> 🇬🇧 **English Section** — Sections 15–28 (mirror content)

---

# 🇻🇳 PHẦN TIẾNG VIỆT

---

## 1. Tóm Tắt Điều Hành (Executive Summary)

**DB Copilot** là hệ thống AI hỗ trợ DBA/Developer giám sát, điều tra và chẩn đoán vấn đề hiệu năng của Oracle Database.

DB Copilot **không phải** chatbot Oracle thông thường. Thay vì trả lời câu hỏi lý thuyết, hệ thống tập trung vào câu hỏi thực tế từ môi trường production:

> "Database sáng nay có vấn đề gì?"

> "SQL nào hôm qua bị regression?"

> "Tại sao procedure `PROC_SETTLEMENT` lúc 14:32 chạy 18 phút trong khi bình thường chỉ mất 2 phút?"

> "SQL này chậm do index, execution plan, statistics hay database đang bị quá tải?"

**Định vị sản phẩm:**
> **AI-powered Database Observability and Investigation Platform**

---

## 2. Vision & Tầm Nhìn

Xây dựng một **"AI Database Engineer"** có khả năng quan sát Oracle Database liên tục và hỗ trợ con người trả lời:

1. Database đang có vấn đề gì?
2. Vấn đề xảy ra khi nào?
3. SQL / session / job nào liên quan?
4. Nguyên nhân có khả năng là gì?
5. Evidence nào chứng minh điều đó?
6. Nên kiểm tra hoặc xử lý gì tiếp theo?

### Ba năng lực cốt lõi

```
             DB COPILOT

        ┌────────┼─────────┐
        │        │         │
        ▼        ▼         ▼
     QUAN SÁT  ĐIỀU TRA  GIẢI THÍCH
        │        │         │
        ▼        ▼         ▼
     Phát hiện  Tại sao?  Chẩn đoán
     Giám sát   Liên kết  Đề xuất
     Cảnh báo   Evidence  Độ tin cậy
```

---

## 3. Nguyên Tắc Sản Phẩm

### 3.1 AI không trực tiếp điều khiển Database

> **AI có thể quan sát. AI có thể suy luận. AI có thể đề xuất. Con người kiểm soát database.**

**AI được phép:**
- Đọc dữ liệu từ Oracle (read-only)
- Phân tích evidence
- Đưa ra hypothesis
- Đề xuất SQL / action cho DBA

**AI tuyệt đối không được:**
- INSERT / UPDATE / DELETE
- ALTER / DROP / CREATE
- EXECUTE procedure bất kỳ
- Chạy remediation tự động

Ngay cả khi AI đề xuất một lệnh SQL, hệ thống **chỉ hiển thị recommendation** — không có nút "Execute" tự động.

### 3.2 Vòng kiểm soát

```
QUAN SÁT → THU THẬP → LIÊN KẾT
→ ĐIỀU TRA → SUY LUẬN → GIẢI THÍCH
→ ĐỀ XUẤT → CON NGƯỜI QUYẾT ĐỊNH
```

---

## 4. Phát Biểu Vấn Đề (Problem Statement)

### 4.1 Hiện trạng

Khi sự cố Oracle xảy ra, DBA/Developer phải thủ công kiểm tra nhiều nguồn rời rạc:

```
AWR / ASH / V$SQL / V$SESSION / Execution Plan
Wait Events / Tablespace / Jobs / Alert Log
PL/SQL Source / Statistics / Indexes
Application Logs / Deployment History
```

### 4.2 Pain point cốt lõi

Dữ liệu nằm **rời rạc**. Con người phải tự liên kết toàn bộ chuỗi:

```
SQL_ID → Execution Plan → Wait Event
→ Table → Statistics → Procedure → Source Code
```

Việc này tốn thời gian, phụ thuộc kinh nghiệm cá nhân, dễ bỏ sót.

### 4.3 Giải pháp

DB Copilot xây dựng lớp **Evidence Correlation** tự động liên kết toàn bộ chuỗi này, giúp DBA có bức tranh đầy đủ nhanh hơn và chính xác hơn.

---

## 5. Mục Tiêu Kinh Doanh (Business Objectives)

| # | Mục tiêu | Đo lường thành công |
|---|---|---|
| BO-1 | Rút ngắn thời gian chẩn đoán sự cố Oracle | Thời gian điều tra giảm ≥ 50% |
| BO-2 | Proactive phát hiện sự cố trước khi ảnh hưởng production | Phát hiện trước khi user báo cáo |
| BO-3 | Cung cấp Daily Health Report tự động | DBA có báo cáo mỗi sáng, không cần manual check |
| BO-4 | Chuẩn hóa quy trình điều tra DB | Mỗi investigation đều có evidence cụ thể, không phụ thuộc kinh nghiệm cá nhân |
| BO-5 | Hỗ trợ developer không chuyên Oracle | Developer tự hiểu nguyên nhân mà không cần DBA giải thích |

---

## 6. Các Bên Liên Quan (Stakeholders)

| Vai trò | Nhu cầu chính |
|---|---|
| **DBA** | Báo cáo hàng ngày, điều tra sự cố nhanh, có evidence rõ ràng |
| **Database Developer** | Hiểu tại sao procedure / SQL chậm |
| **Backend Developer** | Explanation đơn giản về vấn đề DB liên quan code |
| **System Engineer** | Giám sát resource, storage, jobs |
| **Management / CTO** | Health score tổng quan, risk visibility |

---

## 7. Các Trường Hợp Sử Dụng Cấp Cao (High-level Use Cases)

| UC # | Tên | Mô tả |
|---|---|---|
| UC-01 | Xem báo cáo sức khỏe hàng ngày | DBA mở dashboard mỗi sáng, xem health score và danh sách sự cố |
| UC-02 | Điều tra SQL chậm | User hỏi "SQL nào chạy chậm hôm qua?" hệ thống tự phân tích |
| UC-03 | Điều tra Procedure chậm | User hỏi "Tại sao PROC_X chậm lúc 14:32?" hệ thống tự điều tra |
| UC-04 | Xem evidence của sự cố | User xem danh sách evidence và confidence level |
| UC-05 | Nhận cảnh báo real-time | Hệ thống gửi alert khi phát hiện blocking / SQL regression |
| UC-06 | Tra cứu source code | Xem source code PL/SQL và truy vết SQL đến dòng code cụ thể |

---

## 8. Yêu Cầu Chức Năng Cấp Cao (High-level Functional Requirements)

| FR # | Tên | Mô tả ngắn |
|---|---|---|
| FR-001 | Database Health Monitoring | Giám sát CPU, memory, IO, sessions, tablespace, jobs, errors |
| FR-002 | SQL Performance Monitoring | Phát hiện SQL chậm, regression, plan thay đổi, cardinality mismatch |
| FR-003 | Procedure Investigation | Điều tra tại sao procedure chậm tại thời điểm cụ thể |
| FR-004 | PL/SQL Source Intelligence | Đọc và truy vết source code từ SQL_ID đến dòng code |
| FR-005 | Daily Health Report | Tự động tạo báo cáo sáng: health score, CRITICAL/WARNING/INFO items |
| FR-006 | Evidence-based Diagnosis | Mỗi diagnosis có: Observation, Diagnosis, Confidence %, Evidence, Recommendation |

---

## 9. Yêu Cầu Phi Chức Năng Cấp Cao (High-level Non-functional Requirements)

| NFR # | Tên | Mô tả |
|---|---|---|
| NFR-001 | Security | Oracle credentials không được expose lên AI/LLM |
| NFR-002 | Least Privilege | Oracle account chỉ có quyền đọc, không có DML/DDL |
| NFR-003 | Auditability | Mọi MCP tool call đều được audit log đầy đủ |

---

## 10. Chiến Lược MVP & Phân Kỳ (MVP Strategy & Phasing)

Hệ thống chia thành **4 MVP**, build từng bước tránh over-engineering:

| MVP | Tên | Mục tiêu |
|---|---|---|
| **MVP-1** | Oracle Health Collector | Kết nối Oracle read-only, thu thập evidence an toàn. Deliverable: MCP Server với 15 tools |
| **MVP-2** | Database Health Engine | Tự động phát hiện sự cố không cần LLM (deterministic rules) |
| **MVP-3** | AI Daily DBA Report | Biến raw evidence thành daily report qua LLM |
| **MVP-4** | Investigation Copilot | User hỏi câu hỏi tự nhiên, hệ thống tự điều tra và cho diagnosis |

### Feature Priority

| Feature | Priority |
|---|---|
| Oracle MCP Server | P0 |
| Read-only security | P0 |
| SQL monitoring | P0 |
| AWR/ASH | P0 |
| Execution plan | P0 |
| Tablespace | P0 |
| Rule engine | P0 |
| Jobs | P1 |
| Source code | P1 |
| Evidence store | P1 |
| Daily report | P1 |
| AI diagnosis | P1 |
| Investigation engine | P1 |
| Git correlation | P2 |
| Knowledge graph | P2 |
| Autonomous remediation | ❌ NOT MVP |

---

## 11. Tiêu Chí Thành Công (Success Criteria)

MVP thành công khi thực hiện được end-to-end 3 scenarios:

**Scenario 1 — Auto Detection:**
```
SQL regression trong DB → Collector phát hiện → Rule engine tạo incident
→ MCP lấy evidence → AI phân tích → Daily report gửi đến DBA
```

**Scenario 2 — SQL Investigation:**
```
User: "Why was SQL_ID 8f3abc slow yesterday?"
→ Investigation Engine → Plan comparison + ASH + Wait + CPU + IO + Statistics
→ Evidence-based Diagnosis
```

**Scenario 3 — Procedure Investigation ⭐ (Quan trọng nhất):**
```
User: "Why was PROC_SETTLEMENT slow at 14:32?"
→ Procedure → SQL → Plan → ASH → Wait → Source code → Diagnosis
```

---

## 12. Ngoài Phạm Vi MVP (Out of Scope)

| Tính năng | Lý do loại trừ |
|---|---|
| Autonomous DBA | Vi phạm nguyên tắc Human-in-control |
| Automatic SQL tuning / index / statistics | Ngoài scope MVP |
| Full knowledge graph | Phức tạp, để phase 2+ |
| Multi-cloud / Multi-database | Tập trung Oracle trước |
| Complex frontend | MVP ưu tiên backend/engine |
| Tự động thực thi bất kỳ lệnh DB nào | Vi phạm nguyên tắc security |

---

## 13. Roadmap Kinh Doanh (Business Roadmap)

| Phase | Thời gian | Deliverable |
|---|---|---|
| Phase 0 — Foundation | 1–2 tuần | Python project setup, Oracle connection, MCP framework, Docker |
| Phase 1 — Oracle MCP | 2–3 tuần | 15 MCP tools, read-only account, audit, structured responses |
| Phase 2 — Health Engine | 2 tuần | Deterministic rules phát hiện SQL regression, blocking, tablespace, jobs |
| Phase 3 — Evidence Store | 1–2 tuần | PostgreSQL evidence store với historical data |
| Phase 4 — AI Diagnosis | 1–2 tuần | LLM diagnosis với structured output |
| Phase 5 — Investigation Engine | 2–4 tuần | Natural language investigation với full evidence correlation |

**Tổng ước tính:** 10–15 tuần

---

## 14. Định Vị Sản Phẩm (Product Differentiation)

**Chatbot Oracle thông thường:**
```
User → Question → LLM → Answer (từ kiến thức chung)
```

**DB Copilot:**
```
User → Question → Investigation Engine → Oracle MCP
→ Real Database Evidence → Correlation → Hypothesis
→ Validation → AI → Evidence-based Diagnosis
```

**Điểm khác biệt:** Mọi kết luận đều được chứng minh bằng evidence thực từ database production, không phải kiến thức lý thuyết của LLM.

---

---

# 🇬🇧 ENGLISH SECTION

---

## 15. Executive Summary

**DB Copilot** is an AI system that helps DBAs and Developers monitor, investigate, and diagnose Oracle Database performance issues.

DB Copilot is **not** a generic Oracle chatbot. Instead of answering theoretical questions, it focuses on real production questions:

> "What issues does the database have this morning?"

> "Which SQL queries regressed yesterday?"

> "Why did procedure `PROC_SETTLEMENT` run for 18 minutes at 14:32 when it normally takes 2 minutes?"

> "Is this SQL slow because of an index, execution plan, stale statistics, or database overload?"

**Product Positioning:**
> **AI-powered Database Observability and Investigation Platform**

---

## 16. Vision

Build an **"AI Database Engineer"** capable of continuously observing Oracle Database and helping humans answer:

1. What issues does the database currently have?
2. When did the problem occur?
3. Which SQL / session / job is involved?
4. What is the likely root cause?
5. What evidence supports that conclusion?
6. What should be checked or done next?

### Three Core Capabilities

```
             DB COPILOT

        ┌────────┼─────────┐
        │        │         │
        ▼        ▼         ▼
     OBSERVE  INVESTIGATE  EXPLAIN
        │        │         │
        ▼        ▼         ▼
     Detect     Why?      Diagnosis
     Monitor    Correlate Recommendation
     Alert      Evidence  Confidence
```

---

## 17. Product Principles

### 17.1 AI Does Not Directly Control the Database

> **AI can observe. AI can reason. AI can recommend. Human controls the database.**

**AI is permitted to:**
- Read data from Oracle (read-only)
- Analyze evidence
- Generate hypotheses
- Suggest SQL / actions to DBA

**AI is strictly prohibited from:**
- INSERT / UPDATE / DELETE
- ALTER / DROP / CREATE
- EXECUTE any procedure
- Running any automatic remediation

Even when AI suggests a SQL statement, the system **only displays it as a recommendation** — there is no "Execute" button for automatic execution.

### 17.2 Control Loop

```
OBSERVE → COLLECT → CORRELATE
→ INVESTIGATE → REASON → EXPLAIN
→ RECOMMEND → HUMAN DECIDES
```

---

## 18. Problem Statement

### 18.1 Current State

When an Oracle issue occurs, DBAs/Developers must manually check multiple disconnected data sources:

```
AWR / ASH / V$SQL / V$SESSION / Execution Plan
Wait Events / Tablespace / Jobs / Alert Log
PL/SQL Source / Statistics / Indexes
Application Logs / Deployment History
```

### 18.2 Core Pain Point

Data is **fragmented**. Humans must manually trace the entire chain:

```
SQL_ID → Execution Plan → Wait Event
→ Table → Statistics → Procedure → Source Code
```

This is time-consuming, depends on individual expertise, and is prone to gaps.

### 18.3 Solution

DB Copilot builds an **Evidence Correlation** layer that automatically links all of this data, giving DBAs a complete picture faster and more accurately.

---

## 19. Business Objectives

| # | Objective | Success Metric |
|---|---|---|
| BO-1 | Reduce Oracle incident diagnosis time | Mean investigation time reduced by ≥ 50% |
| BO-2 | Proactively detect issues before production impact | Issues detected before user reports |
| BO-3 | Deliver automated Daily Health Reports | DBAs receive morning report with no manual effort |
| BO-4 | Standardize database investigation workflows | Every investigation has concrete evidence, not gut feeling |
| BO-5 | Enable non-Oracle developers to understand DB issues | Developers self-diagnose without requiring DBA intervention |

---

## 20. Stakeholders

| Role | Primary Need |
|---|---|
| **DBA** | Daily reports, fast incident investigation, clear evidence |
| **Database Developer** | Understand why a procedure / SQL is slow |
| **Backend Developer** | Simple explanation of DB issues related to their code |
| **System Engineer** | Resource, storage, and job monitoring |
| **Management / CTO** | Health score overview, risk visibility |

---

## 21. High-level Use Cases

| UC # | Name | Description |
|---|---|---|
| UC-01 | View Daily Health Report | DBA opens dashboard each morning, sees health score and incident list |
| UC-02 | Investigate slow SQL | User asks "Which SQL was slow yesterday?" — system auto-analyzes |
| UC-03 | Investigate slow Procedure | User asks "Why was PROC_X slow at 14:32?" — system auto-investigates |
| UC-04 | View incident evidence | User views evidence list and confidence levels |
| UC-05 | Receive real-time alerts | System sends alerts on blocking / SQL regression |
| UC-06 | Source code lookup | View PL/SQL source and trace SQL to specific code lines |

---

## 22. High-level Functional Requirements

| FR # | Name | Short Description |
|---|---|---|
| FR-001 | Database Health Monitoring | Monitor CPU, memory, IO, sessions, tablespace, jobs, errors |
| FR-002 | SQL Performance Monitoring | Detect slow SQL, regression, plan changes, cardinality mismatch |
| FR-003 | Procedure Investigation | Investigate why a procedure was slow at a specific time |
| FR-004 | PL/SQL Source Intelligence | Read and trace source code from SQL_ID to specific code line |
| FR-005 | Daily Health Report | Auto-generate morning report: health score, CRITICAL/WARNING/INFO items |
| FR-006 | Evidence-based Diagnosis | Every diagnosis: Observation, Diagnosis, Confidence %, Evidence, Recommendation |

---

## 23. High-level Non-functional Requirements

| NFR # | Name | Description |
|---|---|---|
| NFR-001 | Security | Oracle credentials must never be exposed to AI/LLM |
| NFR-002 | Least Privilege | Oracle account has read-only access, no DML/DDL |
| NFR-003 | Auditability | Every MCP tool call must be fully audit-logged |

---

## 24. MVP Strategy & Phasing

| MVP | Name | Objective |
|---|---|---|
| **MVP-1** | Oracle Health Collector | Read-only Oracle connection, safe evidence collection. Deliverable: MCP Server with 15 tools |
| **MVP-2** | Database Health Engine | Auto-detect issues without LLM (deterministic rules) |
| **MVP-3** | AI Daily DBA Report | Transform raw evidence into daily report via LLM |
| **MVP-4** | Investigation Copilot | Natural language questions, self-directed investigation, diagnosis |

---

## 25. Success Criteria

MVP is successful when all 3 scenarios work end-to-end:

**Scenario 1 — Auto Detection:**
SQL regression → Collector detects → Rule engine raises incident → MCP collects evidence → AI analyzes → Daily report sent to DBA

**Scenario 2 — SQL Investigation:**
User: *"Why was SQL_ID 8f3abc slow yesterday?"* → Investigation Engine → Plan comparison, ASH, Wait events, CPU, IO, Statistics → Evidence-based Diagnosis

**Scenario 3 — Procedure Investigation ⭐ (Most Important):**
User: *"Why was PROC_SETTLEMENT slow at 14:32?"* → Procedure → SQL → Plan → ASH → Wait → Source code → Diagnosis

---

## 26. Out of Scope

| Feature | Reason |
|---|---|
| Autonomous DBA | Violates Human-in-control principle |
| Automatic SQL tuning / index / statistics | Out of MVP scope |
| Full knowledge graph | Complex, deferred to Phase 2+ |
| Multi-cloud / Multi-database | Focus on Oracle first |
| Complex frontend | MVP prioritizes backend/engine |
| Auto-execute any DB commands | Violates security principles |

---

## 27. Business Roadmap

| Phase | Duration | Deliverable |
|---|---|---|
| Phase 0 — Foundation | 1–2 weeks | Python setup, Oracle connection, MCP framework, Docker |
| Phase 1 — Oracle MCP | 2–3 weeks | 15 MCP tools, read-only account, audit, structured responses |
| Phase 2 — Health Engine | 2 weeks | Deterministic rules: SQL regression, blocking, tablespace, jobs |
| Phase 3 — Evidence Store | 1–2 weeks | PostgreSQL evidence store with historical data |
| Phase 4 — AI Diagnosis | 1–2 weeks | LLM diagnosis with structured output |
| Phase 5 — Investigation Engine | 2–4 weeks | Natural language investigation with full evidence correlation |

**Total Estimate:** 10–15 weeks

---

## 28. Product Differentiation

**Typical Oracle Chatbot:**
```
User → Question → LLM → Answer (from general knowledge)
```

**DB Copilot:**
```
User → Question → Investigation Engine → Oracle MCP
→ Real Database Evidence → Correlation → Hypothesis
→ Validation → AI → Evidence-based Diagnosis
```

**Core Differentiator:** Every conclusion is backed by real evidence from the production database — not LLM general knowledge.

---


<!-- ======================================================
     FILE: docs/01-product/problem-statement.md
     ====================================================== -->

# Problem Statement
# Phát Biểu Vấn Đề

**Sản phẩm / Product:** DB Copilot  
**Phiên bản / Version:** 0.1  
**Ngày / Date:** 2026-09-08

---

# 🇻🇳 PHẦN TIẾNG VIỆT

---

## 1. Bối Cảnh (Context)

Oracle Database là hệ thống cơ sở dữ liệu trung tâm trong nhiều doanh nghiệp lớn. Khi có sự cố hiệu năng xảy ra — một procedure chạy chậm đột ngột, một SQL bị regression, một tablespace gần đầy — DBA và Developer phải điều tra để tìm nguyên nhân.

Quá trình điều tra hiện tại hoàn toàn **thủ công** và **phụ thuộc hoàn toàn vào kinh nghiệm cá nhân**.

---

## 2. Vấn Đề Cốt Lõi (Core Problem)

### 2.1 Dữ liệu rời rạc, không có Evidence Correlation

Khi sự cố xảy ra, DBA phải tự mình kiểm tra hàng chục nguồn dữ liệu rời rạc:

```
AWR Snapshots          → Hiệu năng lịch sử
ASH (Active Session)   → Session activity
V$SQL                  → SQL đang chạy
V$SESSION              → Sessions hiện tại
Execution Plan         → Kế hoạch thực thi
Wait Events            → Sự kiện chờ
Tablespace             → Không gian lưu trữ
Scheduler Jobs         → Các jobs đã chạy
Alert Log              → Lỗi Oracle
PL/SQL Source          → Source code
Statistics             → Thống kê object
Indexes                → Chỉ mục
Deployment History     → Lịch sử triển khai
```

Không có công cụ nào **tự động liên kết** các nguồn này thành một bức tranh hoàn chỉnh.

### 2.2 Chuỗi điều tra phức tạp, dễ bỏ sót

Để chẩn đoán một sự cố đơn giản, DBA phải tự truy vết toàn bộ chuỗi:

```
SQL_ID
   ↓ Tìm execution plan
Execution Plan
   ↓ Xác định wait event
Wait Event (I/O)
   ↓ Tìm table/index bị ảnh hưởng
Table
   ↓ Kiểm tra statistics
Statistics (stale?)
   ↓ Tìm procedure gọi SQL này
Procedure
   ↓ Đọc source code
Source Code (line 247)
```

Mỗi bước là một query thủ công. Dễ bỏ sót, dễ nhầm.

### 2.3 Không có baseline — không biết "nhanh" hay "chậm" so với gì

Khi SQL chạy 10 giây, DBA phải tự hỏi:
- 10 giây có phải là bất thường không?
- Bình thường SQL này chạy bao lâu?
- Vào giờ cao điểm thì khác gì giờ thấp điểm?

Không có historical baseline tự động → DBA phải nhớ hoặc đoán.

### 2.4 Chẩn đoán phụ thuộc hoàn toàn vào kinh nghiệm cá nhân

Junior DBA và Senior DBA nhìn cùng một vấn đề, có thể đưa ra kết luận khác nhau — hoặc Junior DBA không biết phải nhìn vào đâu.

Không có quy trình chuẩn hóa. Không có checklist. Không có evidence trail để review lại.

---

## 3. Ví Dụ Thực Tế (Real-world Example)

### Tình huống

Lúc 14:32, procedure `PROC_SETTLEMENT` chạy mất **18 phút 24 giây**.  
Bình thường procedure này chỉ mất **1 phút 40 giây**.

### Điều tra thủ công hiện tại

DBA phải:

1. Kiểm tra ASH để tìm SQL nào chiếm nhiều time nhất trong PROC_SETTLEMENT
2. Lấy SQL_ID từ ASH → `8f3abc`
3. Query `V$SQL` để xem statistics → elapsed time tăng 20x
4. Query `DBA_HIST_SQL_PLAN` để so sánh plan hash → thay đổi từ `18473291` → `98237412`
5. Query plan detail để xem thay đổi gì → Full Table Scan thay vì Index Range Scan
6. Query `DBA_TAB_STATISTICS` → statistics của `ACCOUNT_POSITION` cập nhật cách đây 18 ngày
7. Query `ALL_SOURCE` để tìm dòng code → line 247: `UPDATE ACCOUNT_POSITION`
8. Kiểm tra blocking → không có
9. Kiểm tra CPU → bình thường
10. Kết luận: Statistics stale → Cardinality mismatch → Bad plan → Performance degradation

**Tổng thời gian điều tra:** 45–90 phút tùy kinh nghiệm DBA.

### DB Copilot

User hỏi: _"Why was PROC_SETTLEMENT slow at 14:32?"_

Hệ thống tự động thực hiện 10 bước trên trong **< 60 giây** và trả về:

```
Diagnosis: Execution plan regression
Confidence: 91%

Evidence:
✓ SQL_ID 8f3abc: 91% of total DB time
✓ Plan changed: 18473291 → 98237412
✓ Physical reads: +920%
✓ Cardinality mismatch: estimated 120, actual 4,320
✓ Statistics: stale (18 days ago)
✗ Blocking: None
✗ CPU: Normal

Recommendation: Gather statistics for ACCOUNT_POSITION
```

---

## 4. Khoảng Trống Thị Trường (Market Gap)

| Tool | Giới hạn |
|---|---|
| **Oracle Enterprise Manager (OEM)** | Dashboard monitoring nhưng không có AI investigation. DBA vẫn phải tự điều tra. |
| **Generic SQL AI tools** | Chỉ trả lời câu hỏi dựa trên kiến thức LLM chung, không kết nối vào database thực |
| **AWR/ASH Reports** | Raw data, không có correlation tự động |
| **DataDog / Grafana** | Infrastructure monitoring, không chuyên sâu Oracle, không có investigation |

**Khoảng trống:** Không có công cụ nào kết hợp được **Oracle-specific deep data access** + **AI evidence correlation** + **Evidence-based diagnosis** thành một hệ thống thống nhất.

---

## 5. Tuyên Bố Vấn Đề Cô Đọng (Problem Statement)

> Khi Oracle Database có sự cố hiệu năng, DBA và Developer phải điều tra thủ công qua hàng chục nguồn dữ liệu rời rạc mà không có công cụ nào tự động liên kết chúng — dẫn đến thời gian điều tra kéo dài 45–90 phút, phụ thuộc hoàn toàn vào kinh nghiệm cá nhân, và thiếu evidence trail để review và chuẩn hóa quy trình.

---

## 6. Giải Pháp Đề Xuất (Proposed Solution)

DB Copilot giải quyết bằng 3 năng lực:

| Năng lực | Mô tả |
|---|---|
| **OBSERVE** | Thu thập và lưu trữ liên tục evidence từ Oracle (SQL, sessions, storage, jobs, source code) |
| **INVESTIGATE** | Khi có câu hỏi, tự động tạo investigation plan và execute qua MCP protocol |
| **EXPLAIN** | Liên kết evidence, đưa ra hypothesis có confidence score, trình bày diagnosis có căn cứ |

**Nguyên tắc bất di bất dịch:**
> AI quan sát, suy luận, đề xuất. Con người quyết định và thực thi.

---

---

# 🇬🇧 ENGLISH SECTION

---

## 7. Context

Oracle Database is the central data system for many large enterprises. When performance incidents occur — a procedure suddenly slows down, SQL regresses, a tablespace nears capacity — DBAs and Developers must investigate the root cause.

The current investigation process is entirely **manual** and **entirely dependent on individual expertise**.

---

## 8. Core Problem

### 8.1 Fragmented Data — No Evidence Correlation

When an incident occurs, DBAs must manually check dozens of disconnected data sources:

```
AWR Snapshots          → Historical performance
ASH (Active Session)   → Session activity
V$SQL                  → Running SQL
V$SESSION              → Current sessions
Execution Plan         → Query execution plan
Wait Events            → Wait events
Tablespace             → Storage space
Scheduler Jobs         → Job runs
Alert Log              → Oracle errors
PL/SQL Source          → Source code
Statistics             → Object statistics
Indexes                → Index definitions
Deployment History     → Release history
```

No tool **automatically links** these sources into a complete picture.

### 8.2 Complex Investigation Chain — Prone to Gaps

To diagnose a single incident, a DBA must manually trace the entire chain:

```
SQL_ID → Execution Plan → Wait Event → Table → Statistics → Procedure → Source Code
```

Each step is a manual query. Easy to miss steps, easy to make mistakes.

### 8.3 No Baseline — No Reference for "Fast" vs "Slow"

When SQL runs for 10 seconds, the DBA must ask:
- Is 10 seconds abnormal?
- What was the normal execution time?
- How does peak hours compare to off-peak?

No automatic historical baseline → DBAs must rely on memory or guesswork.

### 8.4 Diagnosis Entirely Dependent on Individual Expertise

A Junior DBA and a Senior DBA looking at the same problem may reach different conclusions — or a Junior DBA may not even know where to look.

No standardized process. No checklist. No evidence trail for review.

---

## 9. Real-world Example

### Situation

At 14:32, procedure `PROC_SETTLEMENT` ran for **18 minutes 24 seconds**.  
Normally this procedure takes **1 minute 40 seconds**.

### Current Manual Investigation

The DBA must manually:

1. Check ASH to find which SQL consumed the most time in PROC_SETTLEMENT
2. Get SQL_ID: `8f3abc`
3. Query V$SQL for statistics → elapsed time 20x higher
4. Query DBA_HIST_SQL_PLAN for plan hash → changed from `18473291` → `98237412`
5. Query plan detail → Full Table Scan replaced Index Range Scan
6. Query DBA_TAB_STATISTICS → ACCOUNT_POSITION statistics 18 days old
7. Query ALL_SOURCE → line 247: `UPDATE ACCOUNT_POSITION`
8. Check blocking → none
9. Check CPU → normal
10. Conclude: Stale statistics → Cardinality mismatch → Bad plan → Performance degradation

**Total investigation time:** 45–90 minutes depending on DBA experience.

### With DB Copilot

User asks: _"Why was PROC_SETTLEMENT slow at 14:32?"_

System automatically executes all 10 steps in **< 60 seconds** and returns a structured, evidence-backed diagnosis.

---

## 10. Market Gap

| Tool | Limitation |
|---|---|
| **Oracle Enterprise Manager (OEM)** | Dashboard monitoring but no AI investigation. DBA still investigates manually. |
| **Generic AI SQL tools** | Answer questions from LLM general knowledge only — no real database connection |
| **AWR/ASH Reports** | Raw data, no automatic correlation |
| **DataDog / Grafana** | Infrastructure monitoring, not Oracle-deep, no investigation |

**Gap:** No tool combines **Oracle-specific deep data access** + **AI evidence correlation** + **Evidence-based diagnosis** into a unified system.

---

## 11. Problem Statement (Concise)

> When Oracle Database has a performance incident, DBAs and Developers must manually investigate across dozens of disconnected data sources with no tool to automatically correlate them — resulting in 45–90 minute investigation times, total dependence on individual expertise, and no evidence trail to review or standardize the process.

---

## 12. Proposed Solution

DB Copilot addresses this with three capabilities:

| Capability | Description |
|---|---|
| **OBSERVE** | Continuously collect and store evidence from Oracle (SQL, sessions, storage, jobs, source code) |
| **INVESTIGATE** | On demand, auto-generate investigation plan and execute via MCP protocol |
| **EXPLAIN** | Correlate evidence, generate ranked hypotheses with confidence scores, present grounded diagnosis |

**Core principle:**
> AI observes, reasons, and recommends. Humans decide and execute.

---


<!-- ======================================================
     FILE: docs/01-product/prd.md
     ====================================================== -->

# PRD — Product Requirements Document
# Tài Liệu Yêu Cầu Sản Phẩm

**Sản phẩm / Product:** DB Copilot  
**Phiên bản / Version:** 0.1  
**Trạng thái / Status:** Draft  
**Ngày / Date:** 2026-09-08

---

> 🇻🇳 **Phần tiếng Việt** — Sections 1–12  
> 🇬🇧 **English Section** — Sections 13–24

---

# 🇻🇳 PHẦN TIẾNG VIỆT

---

## 1. Tổng Quan Sản Phẩm

DB Copilot là **AI Database Observability and Investigation Platform** cho Oracle Database.

### 1.1 Vấn đề cần giải quyết

DBA/Developer tốn nhiều thời gian điều tra sự cố vì dữ liệu nằm rời rạc ở nhiều nguồn. Không có công cụ nào tự động liên kết AWR, ASH, execution plan, session, source code thành một bức tranh hoàn chỉnh.

### 1.2 Giải pháp

DB Copilot tự động thu thập, liên kết evidence và sử dụng AI để đưa ra diagnosis có근거cụ thể — giúp DBA trả lời câu hỏi "tại sao" trong vài phút thay vì vài giờ.

---

## 2. Người Dùng & User Stories

### 2.1 DBA (Database Administrator)

| ID | User Story | Acceptance Criteria |
|---|---|---|
| US-DBA-01 | Là DBA, tôi muốn nhận báo cáo sức khỏe database mỗi sáng để biết có vấn đề gì cần xử lý | Báo cáo tự động gửi lúc 7:00 sáng, có health score, danh sách CRITICAL/WARNING items |
| US-DBA-02 | Là DBA, tôi muốn được cảnh báo ngay khi có blocking session để xử lý kịp thời | Alert được gửi trong vòng 60 giây kể từ khi phát hiện blocking |
| US-DBA-03 | Là DBA, tôi muốn xem đầy đủ evidence của một sự cố để có cơ sở ra quyết định | Mỗi incident hiển thị đủ: observation, evidence list, confidence %, recommendation |
| US-DBA-04 | Là DBA, tôi muốn hỏi tại sao một procedure cụ thể bị chậm và nhận được phân tích | Hệ thống tự điều tra và trả về diagnosis trong <60 giây |

### 2.2 Database Developer

| ID | User Story | Acceptance Criteria |
|---|---|---|
| US-DEV-01 | Là DB Developer, tôi muốn biết SQL nào đang chạy chậm nhất hôm nay | Dashboard hiển thị top SQL by elapsed time, CPU, IO |
| US-DEV-02 | Là DB Developer, tôi muốn xem execution plan của một SQL_ID cụ thể | Hệ thống hiển thị plan hiện tại và lịch sử plan thay đổi |
| US-DEV-03 | Là DB Developer, tôi muốn truy vết SQL_ID về đến dòng code PL/SQL cụ thể | Source mapping hiển thị package/procedure/line number |

### 2.3 Backend Developer

| ID | User Story | Acceptance Criteria |
|---|---|---|
| US-BE-01 | Là Backend Developer, tôi muốn hiểu tại sao API của tôi bị chậm do DB | Hệ thống cho biết SQL nào liên quan và vấn đề là gì |
| US-BE-02 | Là Backend Developer, tôi muốn nhận explanation đơn giản không cần hiểu sâu Oracle | Diagnosis được trình bày bằng ngôn ngữ đơn giản, không jargon |

---

## 3. Yêu Cầu Chức Năng Chi Tiết

### FR-001 — Database Health Monitoring

**Mô tả:** Hệ thống liên tục thu thập và giám sát các chỉ số sức khỏe Oracle Database.

**Các metrics cần theo dõi:**

| Loại | Metrics |
|---|---|
| **Compute** | CPU utilization, memory usage, IO rate |
| **Connections** | Active sessions, processes count, blocking sessions, long-running sessions |
| **Storage** | Tablespace usage %, TEMP usage, UNDO usage, datafile status |
| **Redo** | Redo log generation rate, log switch frequency |
| **SQL** | Top SQL by various dimensions |
| **Jobs** | Scheduler job status, failed jobs |
| **Code** | Invalid objects count |
| **Errors** | Oracle errors in alert log |

**Acceptance Criteria:**
- [ ] Hệ thống thu thập metrics mỗi 5 phút (configurable)
- [ ] Lưu trữ historical data tối thiểu 30 ngày
- [ ] Phát hiện anomaly khi metric vượt ngưỡng đã cấu hình
- [ ] Tạo incident record cho mỗi anomaly phát hiện

---

### FR-002 — SQL Performance Monitoring

**Mô tả:** Tự động phát hiện SQL có vấn đề hiệu năng.

**Phát hiện các loại vấn đề:**

| Loại | Điều kiện phát hiện |
|---|---|
| SQL Regression | `current_elapsed > historical_avg × 3` |
| CPU Spike | CPU của SQL tăng > 200% so với baseline |
| Physical Read Increase | Disk reads tăng > 500% |
| Execution Count Spike | Số lần chạy tăng đột biến |
| Plan Change | `plan_hash_value` thay đổi so với lần chạy trước |
| Cardinality Mismatch | `actual_rows / estimated_rows > 10` hoặc `< 0.1` |

**Ví dụ output:**
```
SQL_ID: 8f3abc
Normal execution time: 210 ms
Current:               4.2 sec (20x increase)
Plan hash: 18473291 → 98237412 (CHANGED)
Physical reads: +920%
Cardinality: estimated 120, actual 4,320 (36x mismatch)
Likely cause: Statistics / execution plan regression
```

**Acceptance Criteria:**
- [ ] Phát hiện regression trong vòng 1 chu kỳ thu thập (5 phút)
- [ ] So sánh với baseline được tính từ 7 ngày lịch sử
- [ ] Liên kết SQL_ID với plan history trong AWR
- [ ] Bao gồm cardinality mismatch detection

---

### FR-003 — Procedure / Function Investigation

**Mô tả:** User có thể hỏi tại sao một procedure cụ thể bị chậm, hệ thống tự điều tra.

**Investigation pipeline:**
```
Procedure name + timestamp
    ↓ Tìm executions trong ASH
    ↓ Tìm SQL được execute bởi procedure
    ↓ Xác định SQL tốn nhiều time nhất
    ↓ So sánh performance lịch sử
    ↓ Kiểm tra plan change
    ↓ Kiểm tra wait events
    ↓ Kiểm tra blocking
    ↓ Kiểm tra resource (CPU, IO)
    ↓ Kiểm tra statistics
    ↓ Đọc source code
    ↓ Correlate evidence
    ↓ Generate diagnosis
```

**Acceptance Criteria:**
- [ ] Hoàn thành investigation trong < 60 giây
- [ ] Trả về structured diagnosis với evidence list
- [ ] Bao gồm confidence score cho diagnosis
- [ ] Include source code fragment nếu map được

---

### FR-004 — PL/SQL Source Intelligence

**Mô tả:** Đọc và phân tích source code PL/SQL để hỗ trợ investigation.

**Khả năng cần có:**
- Đọc: Procedure, Function, Package spec, Package body, Trigger, View
- Extract: SQL statements từ source
- Build: Dependency graph giữa các objects
- Map: SQL_ID → Procedure → Package → Line number

**Mapping states:**

| State | Ý nghĩa |
|---|---|
| `exact` | SQL_ID được map chính xác đến source line |
| `inferred` | Map dựa trên heuristics (có thể không chính xác) |
| `unavailable` | Không thể xác định mapping |

**Acceptance Criteria:**
- [ ] Đọc được toàn bộ 7 loại PL/SQL object
- [ ] Build dependency graph cho object
- [ ] Map SQL_ID về procedure/package với mapping state rõ ràng
- [ ] Parser extract SQL statements từ source (không gửi toàn bộ source cho LLM)

---

### FR-005 — Daily Health Report

**Mô tả:** Hệ thống tự động tạo báo cáo sức khỏe database mỗi ngày.

**Cấu trúc báo cáo:**

```
# DB Morning Briefing
Ngày: 2026-09-08
Health Score: 82/100

## CRITICAL
### SQL Regression
SQL_ID: 8f3abc
Runtime: 210ms → 4.2s (20x)
Confidence: 91%
Evidence: [Plan changed, Physical reads +920%, Stale statistics]
Recommendation: Review execution plan và statistics

## WARNING
### Tablespace
APP_DATA: 87% used
Trend: +2.1%/ngày
Ước tính đầy: 6 ngày

## JOBS
3 jobs thất bại: [JOB_SETTLEMENT, JOB_REPORT, JOB_CLEANUP]

## Recommendations
1. Review SQL execution plan cho SQL_ID 8f3abc
2. Validate statistics cho table ACCOUNT_POSITION
3. Kiểm tra lý do 3 jobs thất bại

Không có thay đổi tự động nào được thực hiện.
```

**Delivery channels:**
- Dashboard (trong app)
- Email (configurable)
- Slack / Teams webhook (configurable)

**Acceptance Criteria:**
- [ ] Report được tạo tự động theo schedule (default 6:00 AM)
- [ ] Mỗi issue có evidence cụ thể, không phải chung chung
- [ ] Có health score với breakdown
- [ ] Có recommendations rõ ràng
- [ ] Cuối report luôn có disclaimer: "Không có thay đổi tự động nào được thực hiện"

---

### FR-006 — Evidence-based Diagnosis

**Mô tả:** Mỗi diagnosis phải có đầy đủ thành phần, không được đưa ra kết luận thiếu evidence.

**Cấu trúc bắt buộc:**

```json
{
  "observation": "PROC_SETTLEMENT took 18m24s at 14:32 (normal: 2m)",
  "diagnosis": "Likely SQL execution plan regression",
  "confidence": 0.91,
  "evidence": [
    "SQL_ID 8f3abc consumed 91% of total DB time",
    "Plan hash changed: 18473291 → 98237412",
    "Physical reads increased 920%",
    "Estimated rows: 120, Actual rows: 4,320",
    "Statistics last updated 18 days ago",
    "No blocking detected",
    "CPU remained normal"
  ],
  "recommendations": [
    "Review execution plan for SQL_ID 8f3abc",
    "Consider gathering statistics for ACCOUNT_POSITION",
    "Compare plans with: SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY_AWR('8f3abc', ...))"
  ],
  "hypothesis_ranking": [
    {"hypothesis": "Statistics issue", "confidence": 0.87},
    {"hypothesis": "Execution plan regression", "confidence": 0.72},
    {"hypothesis": "Data volume increase", "confidence": 0.61}
  ]
}
```

**Acceptance Criteria:**
- [ ] Không được đưa ra diagnosis khi không có evidence
- [ ] Confidence score phải có kèm lý giải
- [ ] Recommendations phải actionable (có thể thực hiện được ngay)
- [ ] Không bao giờ suggest AI tự execute bất kỳ thứ gì

---

## 4. Yêu Cầu UI/UX

### 4.1 Dashboard Chính

**Các thành phần:**

| Component | Mô tả |
|---|---|
| Health Score Card | Số điểm lớn (0-100), màu theo severity, breakdown theo category |
| Incident Feed | Danh sách incidents theo severity, click để xem chi tiết |
| SQL Performance Panel | Top SQL by elapsed time / CPU / IO, sparkline trend |
| Active Sessions Counter | Số sessions đang active, highlight nếu có blocking |
| Storage Usage | Progress bars cho tablespace, cảnh báo khi > 80% |
| Job Status | Số jobs success/failed hôm nay |

**UX Requirements:**
- Auto-refresh mỗi 60 giây
- Click vào bất kỳ item nào để drill-down xem evidence
- Severity color: 🔴 CRITICAL / 🟡 WARNING / 🟢 INFO

### 4.2 Trang Investigation (Chat Interface)

**Layout:**
```
┌─────────────────────────────────────┐
│ Why was PROC_SETTLEMENT slow?       │  ← Input
└─────────────────────────────────────┘

Timeline
─────────────────────────────────────
14:20  Normal
14:30  CPU normal
14:31  SQL plan changed         [!]
14:32  Runtime increased        [!!]
14:33  Physical reads increased [!!]
14:40  Procedure completed

Root Cause
─────────────────────────────────────
Likely execution plan regression
Confidence: 91%

Evidence
─────────────────────────────────────
✓ Plan hash changed
✓ Physical reads +920%
✓ Cardinality mismatch 36x
✓ Statistics stale (18 days)
✓ No blocking detected
✓ CPU normal

Source Code
─────────────────────────────────────
PROC_SETTLEMENT — Line 247
UPDATE ACCOUNT_POSITION ...

Recommendations
─────────────────────────────────────
1. Review execution plan
2. Gather statistics
3. [Copy SQL commands]
```

**UX Requirements:**
- Timeline phải có visual timeline chart
- Evidence items có icon ✓ (supporting) / ✗ (contradicting)
- Source code có syntax highlight
- Recommendations có "Copy" button cho SQL commands
- Không có "Execute" button

### 4.3 Trang SQL Detail

- SQL text với syntax highlighting
- Execution plan tree (visual)
- Plan history timeline (khi nào plan thay đổi)
- Performance metrics chart (elapsed, CPU, IO over time)
- Session context (module, action, program)
- Source code mapping (nếu available)

### 4.4 Daily Report Page

- Xem report của ngày hôm nay và lịch sử
- Download PDF / Markdown
- Share link
- Configure delivery (email, Slack)

---

## 5. Yêu Cầu Phi Chức Năng

### 5.1 Performance

| Requirement | Target |
|---|---|
| Investigation response time | < 60 giây |
| Dashboard load time | < 3 giây |
| MCP tool response | < 5 giây per tool call |
| Data freshness | < 5 phút |

### 5.2 Security

- Oracle credentials không bao giờ được gửi cho LLM
- Mọi MCP call được audit log với timestamp, user, tool, duration, status
- Oracle account chỉ có SELECT privileges trên các views được xác định trước

### 5.3 Reliability

- Evidence Store (PostgreSQL) giữ data tối thiểu 90 ngày
- MCP Server phải có health check endpoint
- Audit log không được mất dù có lỗi

---

## 6. MVP Phasing & Acceptance

### MVP-1: Oracle Health Collector

**Done when:**
- [ ] MCP Server start thành công và kết nối được Oracle
- [ ] 15 tools hoạt động và trả về structured JSON
- [ ] CLI test client có thể gọi tất cả tools
- [ ] Audit log ghi nhận mọi tool call
- [ ] Oracle account không có DML/DDL privileges

### MVP-2: Database Health Engine

**Done when:**
- [ ] Hệ thống tự phát hiện SQL regression không cần LLM
- [ ] Hệ thống phát hiện blocking sessions
- [ ] Hệ thống phát hiện tablespace > 85%
- [ ] Hệ thống phát hiện failed jobs
- [ ] Incident record được tạo tự động

### MVP-3: AI Daily DBA Report

**Done when:**
- [ ] Report được tạo tự động theo schedule
- [ ] Report có health score với breakdown
- [ ] Mỗi incident trong report có evidence cụ thể
- [ ] Report có disclaimer về không tự execute

### MVP-4: Investigation Copilot

**Done when:**
- [ ] User có thể hỏi câu tự nhiên bằng tiếng Anh
- [ ] Hệ thống tự tạo investigation plan và execute
- [ ] Diagnosis có structured evidence list
- [ ] Confidence score hợp lý (không phải luôn 99%)
- [ ] Source code mapping hoạt động (kể cả khi unavailable)

---

## 7. Feature Flags & Configuration

| Config | Default | Mô tả |
|---|---|---|
| `collection_interval_minutes` | 5 | Tần suất thu thập metrics |
| `report_schedule` | `"0 6 * * *"` | Cron schedule cho daily report |
| `tablespace_warning_threshold` | 80 | % tablespace trigger warning |
| `tablespace_critical_threshold` | 90 | % tablespace trigger critical |
| `sql_regression_multiplier` | 3.0 | Ngưỡng detect SQL regression |
| `baseline_days` | 7 | Số ngày dùng để tính baseline |
| `evidence_retention_days` | 90 | Số ngày giữ evidence |
| `llm_provider` | `"openai"` | LLM provider (openai/claude/gemini) |
| `alert_channels` | `[]` | Danh sách kênh alert (email, slack, teams) |

---

## 8. Những Thứ Không Làm (Non-goals)

- Không tự động thực thi bất kỳ lệnh SQL nào lên Oracle
- Không hỗ trợ non-Oracle databases trong MVP
- Không build complex BI/analytics dashboard
- Không thay thế Oracle Enterprise Manager (OEM)
- Không là generic SQL client

---

---

# 🇬🇧 ENGLISH SECTION

---

## 13. Product Overview

DB Copilot is an **AI Database Observability and Investigation Platform** for Oracle Database.

### 13.1 Problem

DBAs/Developers waste hours during incidents because data is fragmented across multiple sources. No tool automatically links AWR, ASH, execution plan, sessions, and source code into one complete picture.

### 13.2 Solution

DB Copilot auto-collects, correlates evidence, and uses AI to provide grounded diagnosis — helping DBAs answer "why" in minutes instead of hours.

---

## 14. Users & User Stories

### 14.1 DBA (Database Administrator)

| ID | User Story | Acceptance Criteria |
|---|---|---|
| US-DBA-01 | As a DBA, I want to receive a database health report every morning to know what needs attention | Report auto-sent at 7:00 AM with health score and CRITICAL/WARNING items |
| US-DBA-02 | As a DBA, I want to be alerted immediately when blocking sessions occur | Alert sent within 60 seconds of detecting blocking |
| US-DBA-03 | As a DBA, I want to see full evidence for each incident to make informed decisions | Each incident shows: observation, evidence list, confidence %, recommendation |
| US-DBA-04 | As a DBA, I want to ask why a specific procedure was slow and receive an analysis | System self-investigates and returns diagnosis in < 60 seconds |

### 14.2 Database Developer

| ID | User Story | Acceptance Criteria |
|---|---|---|
| US-DEV-01 | As a DB Developer, I want to know which SQL is slowest today | Dashboard shows top SQL by elapsed time, CPU, IO |
| US-DEV-02 | As a DB Developer, I want to see the execution plan for a specific SQL_ID | System shows current plan and plan change history |
| US-DEV-03 | As a DB Developer, I want to trace a SQL_ID back to a specific PL/SQL code line | Source mapping shows package/procedure/line number |

### 14.3 Backend Developer

| ID | User Story | Acceptance Criteria |
|---|---|---|
| US-BE-01 | As a Backend Developer, I want to understand why my API is slow due to DB | System identifies relevant SQL and explains the problem |
| US-BE-02 | As a Backend Developer, I want a simple explanation without deep Oracle knowledge | Diagnosis presented in plain language, minimal jargon |

---

## 15. Detailed Functional Requirements

### FR-001 — Database Health Monitoring

**Description:** Continuously collect and monitor Oracle Database health metrics.

**Metrics to Monitor:**

| Type | Metrics |
|---|---|
| **Compute** | CPU utilization, memory usage, IO rate |
| **Connections** | Active sessions, process count, blocking sessions, long-running sessions |
| **Storage** | Tablespace usage %, TEMP usage, UNDO usage, datafile status |
| **Redo** | Redo log generation rate, log switch frequency |
| **SQL** | Top SQL by various dimensions |
| **Jobs** | Scheduler job status, failed jobs |
| **Code** | Invalid object count |
| **Errors** | Oracle errors in alert log |

**Acceptance Criteria:**
- [ ] System collects metrics every 5 minutes (configurable)
- [ ] Historical data stored for minimum 30 days
- [ ] Anomaly detected when metric exceeds configured threshold
- [ ] Incident record created for each detected anomaly

---

### FR-002 — SQL Performance Monitoring

**Description:** Automatically detect SQL with performance issues.

**Detection Types:**

| Type | Detection Condition |
|---|---|
| SQL Regression | `current_elapsed > historical_avg × 3` |
| CPU Spike | SQL CPU increased > 200% vs baseline |
| Physical Read Increase | Disk reads increased > 500% |
| Execution Count Spike | Execution count anomalous spike |
| Plan Change | `plan_hash_value` changed vs previous execution |
| Cardinality Mismatch | `actual_rows / estimated_rows > 10` or `< 0.1` |

**Acceptance Criteria:**
- [ ] Detect regression within 1 collection cycle (5 minutes)
- [ ] Compare against baseline calculated from 7 days of history
- [ ] Link SQL_ID to plan history in AWR
- [ ] Include cardinality mismatch detection

---

### FR-003 — Procedure / Function Investigation

**Description:** User can ask why a specific procedure was slow; system self-investigates.

**Acceptance Criteria:**
- [ ] Complete investigation in < 60 seconds
- [ ] Return structured diagnosis with evidence list
- [ ] Include confidence score for diagnosis
- [ ] Include source code fragment when mappable

---

### FR-004 — PL/SQL Source Intelligence

**Description:** Read and analyze PL/SQL source code to support investigation.

**Mapping States:**

| State | Meaning |
|---|---|
| `exact` | SQL_ID precisely mapped to source line |
| `inferred` | Mapped via heuristics (may not be accurate) |
| `unavailable` | Cannot determine mapping |

**Acceptance Criteria:**
- [ ] Read all 7 PL/SQL object types
- [ ] Build dependency graph for objects
- [ ] Map SQL_ID to procedure/package with explicit mapping state
- [ ] Parser extracts SQL statements (does not send full source to LLM)

---

### FR-005 — Daily Health Report

**Description:** System auto-generates database health report every day.

**Report Structure:**
```
# DB Morning Briefing
Date: 2026-09-08
Health Score: 82/100

## CRITICAL
### SQL Regression
SQL_ID: 8f3abc | Runtime: 210ms → 4.2s (20x) | Confidence: 91%
Evidence: Plan changed, Physical reads +920%, Stale statistics
Recommendation: Review execution plan and statistics

## WARNING
### Tablespace
APP_DATA: 87% | Trend: +2.1%/day | Estimated full: 6 days

## Recommendations
1. Review SQL execution plan for SQL_ID 8f3abc
2. Validate statistics for ACCOUNT_POSITION

No automatic database changes were executed.
```

**Acceptance Criteria:**
- [ ] Report auto-generated on schedule (default 6:00 AM)
- [ ] Each issue has specific evidence, not vague descriptions
- [ ] Includes health score with category breakdown
- [ ] Clear, actionable recommendations
- [ ] Always ends with disclaimer: "No automatic database changes were executed"

---

### FR-006 — Evidence-based Diagnosis

**Description:** Every diagnosis must include full structured evidence; no unsupported conclusions.

**Required Structure:**

```json
{
  "observation": "...",
  "diagnosis": "...",
  "confidence": 0.91,
  "evidence": [],
  "recommendations": [],
  "hypothesis_ranking": []
}
```

**Acceptance Criteria:**
- [ ] No diagnosis without evidence
- [ ] Confidence score with justification
- [ ] Recommendations must be actionable
- [ ] Never suggest AI execute anything automatically

---

## 16. UI/UX Requirements

### 16.1 Main Dashboard

**Components:**

| Component | Description |
|---|---|
| Health Score Card | Large score (0-100), severity-colored, category breakdown |
| Incident Feed | Sorted by severity, click to drill down to evidence |
| SQL Performance Panel | Top SQL by elapsed/CPU/IO, sparkline trend |
| Active Sessions Counter | Active count, highlighted if blocking exists |
| Storage Usage | Progress bars per tablespace, warning at > 80% |
| Job Status | Today's success/failed job count |

**UX Requirements:**
- Auto-refresh every 60 seconds
- Click any item to drill down and view evidence
- Severity colors: 🔴 CRITICAL / 🟡 WARNING / 🟢 INFO

### 16.2 Investigation Page (Chat Interface)

**Layout:**
```
┌─────────────────────────────────────┐
│ Why was PROC_SETTLEMENT slow?       │  ← Natural language input
└─────────────────────────────────────┘

Timeline
─────────────────────────────────────
14:20  Normal
14:31  SQL plan changed         [!]
14:32  Runtime increased        [!!]
14:33  Physical reads increased [!!]

Root Cause
─────────────────────────────────────
Likely execution plan regression
Confidence: 91%

Evidence
─────────────────────────────────────
✓ Plan hash changed
✓ Physical reads +920%
✓ Cardinality mismatch 36x
✗ Blocking: None detected
✗ CPU: Normal

Source Code
─────────────────────────────────────
PROC_SETTLEMENT — Line 247
UPDATE ACCOUNT_POSITION ...

Recommendations
─────────────────────────────────────
1. Review execution plan
2. Gather statistics
[Copy SQL]
```

**UX Requirements:**
- Visual timeline chart
- Evidence items have ✓ (supporting) / ✗ (contradicting) icons
- Source code with syntax highlighting
- "Copy" button for SQL commands in recommendations
- **No "Execute" button — ever**

### 16.3 SQL Detail Page

- SQL text with syntax highlighting
- Visual execution plan tree
- Plan history timeline (when plan changed)
- Performance metrics chart over time (elapsed, CPU, IO)
- Session context (module, action, program)
- Source code mapping (if available)

### 16.4 Daily Report Page

- View today's report and history
- Download PDF / Markdown
- Share link
- Configure delivery (email, Slack, Teams)

---

## 17. Non-functional Requirements

### 17.1 Performance

| Requirement | Target |
|---|---|
| Investigation response time | < 60 seconds |
| Dashboard load time | < 3 seconds |
| MCP tool response | < 5 seconds per tool call |
| Data freshness | < 5 minutes |

### 17.2 Security

- Oracle credentials never sent to LLM
- All MCP calls audit-logged: timestamp, user, tool, duration, status
- Oracle account with SELECT-only privileges on pre-approved views

---

## 18. MVP Phasing & Acceptance

### MVP-1: Oracle Health Collector
- [ ] MCP Server starts and connects to Oracle
- [ ] All 15 tools return structured JSON
- [ ] CLI test client works for all tools
- [ ] Audit log records all tool calls
- [ ] Oracle account has no DML/DDL privileges

### MVP-2: Database Health Engine
- [ ] System detects SQL regression without LLM
- [ ] Detects blocking sessions
- [ ] Detects tablespace > 85%
- [ ] Detects failed jobs
- [ ] Incident records auto-created

### MVP-3: AI Daily DBA Report
- [ ] Report auto-generated on schedule
- [ ] Health score with breakdown
- [ ] Each incident has specific evidence
- [ ] No-execution disclaimer present

### MVP-4: Investigation Copilot
- [ ] Natural language questions accepted
- [ ] System auto-plans and executes investigation
- [ ] Structured evidence list in diagnosis
- [ ] Confidence scores reasonable (not always 99%)
- [ ] Source code mapping works (even when unavailable)

---

## 19. Configuration

| Config | Default | Description |
|---|---|---|
| `collection_interval_minutes` | 5 | Metric collection frequency |
| `report_schedule` | `"0 6 * * *"` | Daily report cron schedule |
| `tablespace_warning_threshold` | 80 | Tablespace % for warning |
| `tablespace_critical_threshold` | 90 | Tablespace % for critical |
| `sql_regression_multiplier` | 3.0 | Regression detection multiplier |
| `baseline_days` | 7 | Days used to calculate baseline |
| `evidence_retention_days` | 90 | Days to retain evidence data |
| `llm_provider` | `"openai"` | LLM provider (openai/claude/gemini) |
| `alert_channels` | `[]` | Alert channels (email, slack, teams) |

---

## 20. Non-goals

- Never auto-execute any SQL command against Oracle
- No non-Oracle database support in MVP
- No complex BI/analytics dashboard
- Not a replacement for Oracle Enterprise Manager (OEM)
- Not a generic SQL client

---


<!-- ======================================================
     FILE: docs/02-architecture/hld.md
     ====================================================== -->

# HLD — High-Level Design
# Thiết Kế Cấp Cao

**Sản phẩm / Product:** DB Copilot  
**Phiên bản / Version:** 0.1  
**Ngày / Date:** 2026-09-08

---

# 🇻🇳 PHẦN TIẾNG VIỆT

---

## 1. Tổng Quan Hệ Thống

DB Copilot là **AI Database Observability and Investigation Platform** cho Oracle Database, được xây dựng theo kiến trúc **hai project riêng biệt**:

| Project | Vai trò |
|---|---|
| `oracle-mcp-server` | Oracle Evidence Gateway — kết nối Oracle, expose tools qua MCP protocol |
| `db-copilot` | AI Application — Investigation Engine, Health Engine, Report Engine, FastAPI |

### Nguyên tắc kiến trúc cốt lõi

> **AI quan sát. AI suy luận. AI đề xuất. Con người kiểm soát database.**

---

## 2. Sơ Đồ Kiến Trúc Tổng Thể

```
┌───────────────────────────────────────────────────────────┐
│                       DB COPILOT APP                      │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐  │
│  │                    React UI                         │  │
│  │                                                     │  │
│  │ Dashboard | Incidents | SQL | Investigation | Chat  │  │
│  └──────────────────────┬──────────────────────────────┘  │
│                         │                                 │
│                         ▼                                 │
│  ┌─────────────────────────────────────────────────────┐  │
│  │                  FastAPI (Python)                    │  │
│  └──────────────────────┬──────────────────────────────┘  │
│                         │                                 │
│                         ▼                                 │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              Application Layer                       │  │
│  │                                                     │  │
│  │  Investigation Engine                               │  │
│  │  Incident Engine                                    │  │
│  │  Report Engine                                      │  │
│  └──────────────────────┬──────────────────────────────┘  │
│                         │                                 │
│              ┌──────────┴──────────┐                      │
│              ▼                     ▼                      │
│  ┌─────────────────────┐  ┌───────────────────────────┐  │
│  │ Correlation Engine   │  │ AI / LLM Service          │  │
│  └──────────┬──────────┘  └───────────────────────────┘  │
│             │                                             │
│             ▼                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              Oracle Evidence Layer                   │  │
│  │                                                     │  │
│  │ Data Access → Normalization → Evidence Builder      │  │
│  └──────────────────────┬──────────────────────────────┘  │
│                         │                                 │
│                   MCP Protocol                            │
│                         │                                 │
└─────────────────────────┼────────────────────────────────┘
                          │
          ┌───────────────▼──────────────────┐
          │        ORACLE MCP SERVER          │
          │       (Separate Project)          │
          │                                  │
          │  server.py                        │
          │  tools/ (sql, ash, awr, session,  │
          │          plan, object, storage)   │
          │  oracle/ (connection, repos,      │
          │           queries)               │
          │  security/ | models/ | config/   │
          └───────────────┬──────────────────┘
                          │
                    Read-only User
                          │
                          ▼
                   ┌─────────────┐
                   │   Oracle    │
                   │  Database   │
                   └─────────────┘

          ┌─────────────────────────┐
          │       PostgreSQL        │
          │     Evidence Store      │
          │                         │
          │ snapshots | sql_metrics │
          │ incidents | evidence    │
          │ baselines | audit_logs  │
          └─────────────────────────┘
```

---

## 3. Hai Project Riêng Biệt

### 3.1 oracle-mcp-server

**Mục đích:** Oracle Evidence Gateway — cung cấp công cụ đọc Oracle qua MCP protocol.

**Đặc điểm:**
- Toàn bộ kết nối Oracle nằm ở đây
- Chỉ có SELECT privileges
- Có audit logging riêng
- Có thể deploy độc lập
- Stateless (không có database riêng)

**Tools:** 7 groups, ~35 tools (sql, ash, awr, session, plan, object, storage)

**Giao tiếp:** MCP protocol (Stdio hoặc SSE)

### 3.2 db-copilot

**Mục đích:** AI Application — Investigation, Health, Report.

**Đặc điểm:**
- Không có kết nối Oracle trực tiếp
- Gọi oracle-mcp-server qua MCP protocol
- Có PostgreSQL Evidence Store riêng
- Stateful (lưu evidence, baselines, incidents, audit logs)

**Components:**
- FastAPI REST API
- Investigation Engine
- Correlation/Detection Engine
- AI/LLM Service
- Evidence Store (PostgreSQL)

---

## 4. Data Flow Tổng Thể

### 4.1 Collection Flow (Background, mỗi 5 phút)

```
APScheduler (db-copilot)
    ↓
Evidence Collector
    ↓ [MCP call]
oracle-mcp-server tools
    ↓ [read-only query]
Oracle Database
    ↓ [structured JSON response]
Evidence Builder
    ↓
PostgreSQL Evidence Store
    ↓
Correlation Engine (detection rules)
    ↓
Incident Records
```

### 4.2 Investigation Flow (On-demand)

```
User Question (natural language)
    ↓
FastAPI POST /investigate
    ↓
Intent Parser
    ↓
Investigation Planner
    ↓
[Dynamic MCP calls via oracle-mcp-server]
    ↓
Evidence Collection
    ↓
Evidence Normalization
    ↓
Correlation Engine
    ↓
Hypothesis Engine
    ↓
AI / LLM Service
    ↓
Evidence-based Diagnosis
    ↓
REST API Response
```

### 4.3 Daily Report Flow (Scheduled, 6:00 AM)

```
APScheduler
    ↓
Health Service
    ↓ [reads from PostgreSQL]
Evidence Store (last 24h)
    ↓
AI / LLM Service
    ↓
Report Generator
    ↓
Dashboard | Email | Slack | Teams
```

---

## 5. Giao Tiếp Giữa Các Components

| Từ | Đến | Protocol | Ghi chú |
|---|---|---|---|
| React UI | FastAPI | HTTP/REST + WebSocket | REST cho queries, WS cho streaming investigation |
| FastAPI | Evidence Store | SQL (asyncpg) | Via SQLAlchemy async |
| FastAPI | oracle-mcp-server | MCP (Stdio/SSE) | Evidence collection & investigation |
| oracle-mcp-server | Oracle Database | `python-oracledb` thin mode | Read-only connection pool |
| FastAPI | LLM Provider | HTTP (OpenAI/Anthropic/Google APIs) | Structured JSON output |
| APScheduler | Evidence Collector | In-process | Background job |

---

## 6. Security Boundaries

```
┌─────────────────────────────────────────────┐
│              PUBLIC ZONE                    │
│  React UI ←→ FastAPI                        │
└──────────────────────┬──────────────────────┘
                       │ (internal only)
┌──────────────────────▼──────────────────────┐
│              INTERNAL ZONE                  │
│  FastAPI ←→ oracle-mcp-server               │
│  FastAPI ←→ PostgreSQL                      │
│  FastAPI ←→ LLM APIs                        │
└──────────────────────┬──────────────────────┘
                       │ (read-only, audited)
┌──────────────────────▼──────────────────────┐
│              DATABASE ZONE                  │
│  oracle-mcp-server ←→ Oracle DB             │
│  (read-only Oracle account, least privilege) │
└─────────────────────────────────────────────┘
```

**Oracle credentials** chỉ tồn tại trong `oracle-mcp-server`. Không bao giờ được gửi lên `db-copilot` app hoặc LLM.

---

## 7. Tech Stack Summary

| Layer | Technology |
|---|---|
| API | FastAPI (Python 3.12) |
| UI | React |
| Oracle Access | `python-oracledb` (thin mode) — chỉ trong oracle-mcp-server |
| MCP Protocol | MCP SDK (Python) |
| Evidence Store | PostgreSQL 16 |
| Scheduler | APScheduler |
| AI/LLM | Python abstraction: OpenAI / Claude / Gemini |
| Containerization | Docker / Docker Compose |
| Package Management | `pyproject.toml` (Poetry hoặc uv) |

---

---

# 🇬🇧 ENGLISH SECTION

---

## 8. System Overview

DB Copilot is an **AI Database Observability and Investigation Platform** for Oracle Database, built as **two separate projects**:

| Project | Role |
|---|---|
| `oracle-mcp-server` | Oracle Evidence Gateway — connects to Oracle, exposes tools via MCP protocol |
| `db-copilot` | AI Application — Investigation Engine, Health Engine, Report Engine, FastAPI |

### Core Architecture Principle

> **AI observes. AI reasons. AI recommends. Human controls the database.**

---

## 9. High-Level Architecture Diagram

_(See Section 2 — same diagram)_

Key architectural decision: **MCP Server is a completely separate, independently deployable project.** The main `db-copilot` app has no direct Oracle connection — it only communicates with `oracle-mcp-server` via MCP protocol.

---

## 10. Two Separate Projects

### 10.1 oracle-mcp-server

**Purpose:** Oracle Evidence Gateway — provides Oracle read tools via MCP protocol.

**Characteristics:**
- All Oracle connectivity lives here
- SELECT-only privileges
- Has its own audit logging
- Can be deployed independently
- Stateless (no database of its own)

**Tools:** 7 groups, ~35 tools (sql, ash, awr, session, plan, object, storage)

**Communication:** MCP protocol (Stdio or SSE)

### 10.2 db-copilot

**Purpose:** AI Application — Investigation, Health, Report.

**Characteristics:**
- No direct Oracle connection
- Calls oracle-mcp-server via MCP protocol
- Has its own PostgreSQL Evidence Store
- Stateful (stores evidence, baselines, incidents, audit logs)

**Components:**
- FastAPI REST API
- Investigation Engine
- Correlation/Detection Engine
- AI/LLM Service
- Evidence Store (PostgreSQL)

---

## 11. Data Flows

### 11.1 Collection Flow (Background, every 5 minutes)

APScheduler → Evidence Collector → [MCP call] → oracle-mcp-server → Oracle DB → Evidence Builder → PostgreSQL → Correlation Engine → Incidents

### 11.2 Investigation Flow (On-demand)

User Question → FastAPI → Intent Parser → Planner → [MCP calls] → Evidence → Correlation → Hypotheses → LLM → Diagnosis

### 11.3 Daily Report Flow (6:00 AM scheduled)

APScheduler → Health Service → PostgreSQL (last 24h) → LLM → Report → Dashboard/Email/Slack

---

## 12. Security Boundaries

- **Oracle credentials**: Only exist in `oracle-mcp-server`. Never sent to `db-copilot` app or LLM.
- **Public zone**: React UI ↔ FastAPI
- **Internal zone**: FastAPI ↔ oracle-mcp-server, FastAPI ↔ PostgreSQL, FastAPI ↔ LLM APIs
- **Database zone**: oracle-mcp-server ↔ Oracle DB (read-only, audited)

---

## 13. Tech Stack Summary

| Layer | Technology |
|---|---|
| API | FastAPI (Python 3.12) |
| UI | React |
| Oracle Access | `python-oracledb` (thin mode) — oracle-mcp-server only |
| MCP Protocol | MCP SDK (Python) |
| Evidence Store | PostgreSQL 16 |
| Scheduler | APScheduler |
| AI/LLM | OpenAI / Claude / Gemini (abstracted) |
| Containers | Docker / Docker Compose |
| Packaging | `pyproject.toml` (Poetry or uv) |

---


<!-- ======================================================
     FILE: docs/02-architecture/lld.md
     ====================================================== -->

# LLD — Low-Level Design
# Thiết Kế Cấp Thấp

**Sản phẩm / Product:** DB Copilot  
**Phiên bản / Version:** 0.1  
**Ngày / Date:** 2026-09-08

---

# 🇻🇳 PHẦN TIẾNG VIỆT

---

## 1. Project Structure Chi Tiết

### 1.1 oracle-mcp-server

```
oracle-mcp-server/
│
├── src/
│   └── oracle_mcp/
│       ├── server.py              # MCP server entry point (Stdio/SSE)
│       │
│       ├── tools/                 # MCP tool implementations
│       │   ├── sql.py             # get_top_sql, get_sql_statistics, get_sql_plan
│       │   ├── ash.py             # get_ash_sample, get_ash_sql_activity
│       │   ├── awr.py             # get_awr_snapshot, get_awr_sql_stats, get_awr_sql_plan
│       │   ├── session.py         # get_active_sessions, get_blocking_sessions, get_long_running_sessions
│       │   ├── plan.py            # get_sql_plan_history, get_sql_execution_context
│       │   ├── object.py          # get_object_source, get_object_metadata, get_object_dependencies
│       │   └── storage.py         # get_tablespace_usage, get_temp_usage, get_undo_usage, get_segment_growth
│       │
│       ├── oracle/
│       │   ├── connection.py      # python-oracledb async connection pool
│       │   ├── repositories/
│       │   │   ├── sql_repo.py
│       │   │   ├── ash_repo.py
│       │   │   ├── awr_repo.py
│       │   │   ├── session_repo.py
│       │   │   ├── plan_repo.py
│       │   │   ├── object_repo.py
│       │   │   └── storage_repo.py
│       │   └── queries/
│       │       ├── sql_queries.py
│       │       ├── ash_queries.py
│       │       ├── awr_queries.py
│       │       ├── session_queries.py
│       │       └── object_queries.py
│       │
│       ├── models/                # Pydantic response models
│       │   ├── sql_models.py
│       │   ├── session_models.py
│       │   ├── storage_models.py
│       │   └── object_models.py
│       │
│       ├── security/
│       │   ├── audit.py           # Audit logging (mọi MCP call)
│       │   └── sanitizer.py       # Sanitize args trước khi log
│       │
│       └── config/
│           └── settings.py        # Oracle DSN, credentials từ env vars
│
├── tests/
│   ├── unit/
│   └── integration/               # Cần Oracle test instance
│
├── docs/
├── Dockerfile
├── pyproject.toml
└── README.md
```

### 1.2 db-copilot

```
db-copilot/
│
├── src/
│   └── db_copilot/
│       │
│       ├── api/                   # FastAPI application
│       │   ├── routes/
│       │   │   ├── health.py      # GET /health, GET /database/status
│       │   │   ├── incidents.py   # GET /incidents, GET /incidents/{id}
│       │   │   ├── investigation.py # POST /investigate, GET /investigate/{id}
│       │   │   ├── sql.py         # GET /sql/top, GET /sql/{sql_id}
│       │   │   └── reports.py     # GET /reports/daily, GET /reports/daily/{date}
│       │   ├── dependencies.py    # FastAPI Depends (settings, services)
│       │   └── app.py             # FastAPI factory, lifespan, middleware
│       │
│       ├── domain/                # Pure domain models — no infrastructure deps
│       │   ├── models/
│       │   │   ├── incident.py
│       │   │   ├── evidence.py
│       │   │   ├── diagnosis.py
│       │   │   ├── sql_metric.py
│       │   │   └── baseline.py
│       │   ├── enums/
│       │   │   ├── severity.py
│       │   │   ├── incident_category.py
│       │   │   └── evidence_type.py
│       │   └── interfaces/
│       │       ├── llm_provider.py
│       │       └── evidence_repo.py
│       │
│       ├── application/           # Use cases & orchestration
│       │   ├── services/
│       │   │   ├── investigation_service.py
│       │   │   ├── health_service.py
│       │   │   └── report_service.py
│       │   ├── commands/          # Write operations
│       │   └── queries/           # Read operations
│       │
│       ├── evidence/              # Oracle Evidence Layer
│       │   ├── collectors/
│       │   │   ├── sql_collector.py
│       │   │   ├── session_collector.py
│       │   │   └── storage_collector.py
│       │   ├── normalizers/
│       │   │   └── evidence_normalizer.py
│       │   ├── builders/
│       │   │   └── evidence_builder.py
│       │   └── repository.py      # PostgreSQL evidence store
│       │
│       ├── correlation/           # Detection & Correlation
│       │   ├── rules/
│       │   │   ├── sql_rules.py   # SQL regression, plan change
│       │   │   ├── session_rules.py # Blocking, long running
│       │   │   └── storage_rules.py # Tablespace threshold
│       │   ├── graph.py           # Evidence graph builder
│       │   └── engine.py          # Correlation orchestrator
│       │
│       ├── investigation/         # Investigation Engine
│       │   ├── planner.py         # Intent → Investigation plan
│       │   ├── executor.py        # Execute plan steps via MCP
│       │   └── context.py         # Investigation context state
│       │
│       ├── ai/                    # AI / LLM Service
│       │   ├── providers/
│       │   │   ├── openai_provider.py
│       │   │   ├── claude_provider.py
│       │   │   └── gemini_provider.py
│       │   ├── prompts/
│       │   │   ├── diagnosis_prompt.py
│       │   │   └── report_prompt.py
│       │   └── service.py
│       │
│       └── config/
│           ├── settings.py        # Pydantic Settings (env vars)
│           └── logging.py
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── scenarios/                 # End-to-end investigation scenarios
│
├── docs/
├── pyproject.toml
└── README.md
```

---

## 2. API Endpoints Chi Tiết

### FastAPI Routes

| Method | Path | Request | Response | Mô tả |
|---|---|---|---|---|
| `GET` | `/api/v1/health` | — | `HealthStatus` | System health check |
| `GET` | `/api/v1/database/status` | — | `DatabaseStatus` | DB health score + summary |
| `GET` | `/api/v1/incidents` | `?severity=&status=&limit=` | `List[IncidentSummary]` | List incidents |
| `GET` | `/api/v1/incidents/{id}` | — | `IncidentDetail` | Incident + evidence |
| `POST` | `/api/v1/investigate` | `{question: str}` | `{id: str, status: "queued"}` | Start investigation |
| `GET` | `/api/v1/investigate/{id}` | — | `InvestigationResult` | Get investigation result |
| `GET` | `/api/v1/sql/top` | `?metric=elapsed&limit=20` | `List[SqlSummary]` | Top SQL |
| `GET` | `/api/v1/sql/{sql_id}` | — | `SqlDetail` | SQL detail + plan + history |
| `GET` | `/api/v1/reports/daily` | — | `DailyReport` | Latest daily report |
| `GET` | `/api/v1/reports/daily/{date}` | — | `DailyReport` | Report cho ngày cụ thể |

---

## 3. Domain Models Chi Tiết

### 3.1 Evidence

```python
@dataclass
class Evidence:
    id: UUID
    incident_id: UUID
    type: EvidenceType       # sql_plan_change, sql_regression, stale_statistics, ...
    source: str              # "DBA_HIST_SQLSTAT", "V$SESSION", etc.
    timestamp: datetime
    entity_type: str         # "SQL", "SESSION", "TABLE", "PROCEDURE"
    entity_id: str           # sql_id, session_id, object_name
    severity: Severity       # HIGH, MEDIUM, LOW, INFO
    data: dict               # Raw evidence payload
    supports_hypothesis: list[str]
```

### 3.2 Incident

```python
@dataclass
class Incident:
    id: UUID
    database_id: UUID
    detected_at: datetime
    resolved_at: datetime | None
    severity: Severity       # CRITICAL, HIGH, MEDIUM, LOW
    category: IncidentCategory  # SQL_REGRESSION, BLOCKING, TABLESPACE, JOB_FAILURE
    title: str
    description: str
    evidence: list[Evidence]
    diagnosis: Diagnosis | None
    status: IncidentStatus   # OPEN, INVESTIGATING, RESOLVED
```

### 3.3 DiagnosisResult

```python
@dataclass
class DiagnosisResult:
    diagnosis: str
    confidence: float        # 0.0 – 1.0
    primary_cause: str
    evidence_used: list[str]
    evidence_against: list[str]
    recommendations: list[Recommendation]
    confidence_explanation: str
    hypothesis_ranking: list[Hypothesis]
```

---

## 4. PostgreSQL Schema

### Core Tables

```sql
-- Databases being monitored
CREATE TABLE databases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(64) UNIQUE NOT NULL,
    host VARCHAR(256) NOT NULL,
    service_name VARCHAR(64) NOT NULL,
    version VARCHAR(32),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Periodic health snapshots (every 5 min)
CREATE TABLE snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    database_id UUID REFERENCES databases(id),
    captured_at TIMESTAMPTZ NOT NULL,
    active_sessions INT,
    blocking_sessions INT,
    cpu_pct DECIMAL(5,2),
    health_score INT,
    raw_data JSONB
);
CREATE INDEX idx_snapshots_db_time ON snapshots(database_id, captured_at DESC);

-- SQL performance metrics per snapshot
CREATE TABLE sql_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    database_id UUID REFERENCES databases(id),
    snapshot_id UUID REFERENCES snapshots(id),
    sql_id VARCHAR(13) NOT NULL,
    captured_at TIMESTAMPTZ NOT NULL,
    executions BIGINT,
    elapsed_time_ms BIGINT,
    cpu_time_ms BIGINT,
    buffer_gets BIGINT,
    disk_reads BIGINT,
    rows_processed BIGINT,
    plan_hash_value BIGINT
);
CREATE INDEX idx_sql_metrics_id_time ON sql_metrics(database_id, sql_id, captured_at DESC);

-- SQL baselines (recalculated hourly)
CREATE TABLE sql_baselines (
    database_id UUID REFERENCES databases(id),
    sql_id VARCHAR(13) NOT NULL,
    hour_of_day INT NOT NULL,    -- 0-23
    day_of_week INT NOT NULL,    -- 0-6 (Mon-Sun)
    sample_count INT,
    mean_elapsed_ms DECIMAL(15,2),
    stddev_elapsed_ms DECIMAL(15,2),
    p50_elapsed_ms DECIMAL(15,2),
    p95_elapsed_ms DECIMAL(15,2),
    is_reliable BOOLEAN DEFAULT FALSE,  -- True khi sample_count >= 5
    calculated_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (database_id, sql_id, hour_of_day, day_of_week)
);

-- Incidents
CREATE TABLE incidents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    database_id UUID REFERENCES databases(id),
    detected_at TIMESTAMPTZ NOT NULL,
    resolved_at TIMESTAMPTZ,
    severity VARCHAR(16),       -- CRITICAL, HIGH, MEDIUM, LOW
    category VARCHAR(64),       -- SQL_REGRESSION, BLOCKING, TABLESPACE, JOB_FAILURE
    title TEXT NOT NULL,
    description TEXT,
    status VARCHAR(32) DEFAULT 'OPEN',
    diagnosis JSONB
);
CREATE INDEX idx_incidents_db_sev ON incidents(database_id, severity, detected_at DESC);

-- Evidence items
CREATE TABLE evidence_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id UUID REFERENCES incidents(id),
    type VARCHAR(64),
    source VARCHAR(128),
    timestamp TIMESTAMPTZ,
    entity_type VARCHAR(32),
    entity_id VARCHAR(128),
    severity VARCHAR(16),
    data JSONB
);

-- MCP audit log (from db-copilot perspective — calls to oracle-mcp-server)
CREATE TABLE mcp_audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    database_id UUID REFERENCES databases(id),
    tool_name VARCHAR(128) NOT NULL,
    input_args JSONB,           -- Sanitized, no credentials
    duration_ms INT,
    rows_returned INT,
    status VARCHAR(16),         -- success | error | timeout
    error_message TEXT
);
CREATE INDEX idx_audit_time ON mcp_audit_log(occurred_at DESC);

-- Daily reports
CREATE TABLE daily_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    database_id UUID REFERENCES databases(id),
    report_date DATE NOT NULL,
    generated_at TIMESTAMPTZ NOT NULL,
    health_score INT,
    content_markdown TEXT,
    content_json JSONB,
    UNIQUE(database_id, report_date)
);
```

## 5. MCP Client trong db-copilot

Để đáp ứng SLA điều tra sự cố (< 60s cho chuỗi 9 bước investigation) và tuân thủ nguyên tắc an ninh bảo mật dữ liệu, `db-copilot` kết nối với `oracle-mcp-server` qua **SSE Transport với Persistent Connection** ([LLD-01], [LLD-02]).

### 5.1 Kiến trúc kết nối Persistent SSE
- **oracle-mcp-server** chạy độc lập dưới dạng microservice/daemon (Docker container hoặc systemd), quản lý Oracle Connection Pool và lưu giữ an toàn credentials nội bộ.
- **db-copilot** là SSE client, kết nối qua HTTP/SSE (`MCP_SERVER_URL`). `db-copilot` hoàn toàn **không lưu trữ hoặc chuyển tiếp** tài khoản Oracle (`ORACLE_USER`/`ORACLE_PASSWORD`).
- **Tái sử dụng Connection/Session**: `OracleMcpClient` khởi tạo `ClientSession` một lần trong vòng đời ứng dụng (hoặc phiên điều tra), loại bỏ hoàn toàn chi phí khởi động tiến trình Python (~1.5s) và bắt tay kết nối Oracle (~1s) ở mỗi tool call. Thời gian thực thi mỗi tool call giảm từ ~2-3s xuống còn ~30-100ms.

### 5.2 Implementation Pattern (`OracleMcpClient`)

```python
# src/db_copilot/mcp/client.py

import json
import logging
import time
from typing import Any
from mcp import ClientSession
from mcp.client.sse import sse_client
from db_copilot.config.settings import get_settings

logger = logging.getLogger(__name__)

class McpClientError(Exception):
    """Ngoại lệ khi gọi MCP tool thất bại."""
    def __init__(self, tool_name: str, message: str, duration_ms: int = 0):
        super().__init__(f"MCP tool '{tool_name}' error: {message}")
        self.tool_name = tool_name
        self.message = message
        self.duration_ms = duration_ms

class OracleMcpClient:
    """
    Persistent SSE MCP Client kết nối tới oracle-mcp-server.
    db-copilot hoàn toàn không lưu giữ credentials của Oracle DB.
    """

    def __init__(self, server_url: str | None = None, auth_token: str | None = None):
        settings = get_settings()
        self.server_url = server_url or settings.mcp_server_url
        self.auth_token = auth_token or settings.mcp_server_auth_token
        self._session: ClientSession | None = None
        self._sse_ctx = None
        self._session_ctx = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()

    async def connect(self) -> None:
        """Khởi tạo persistent connection một lần duy nhất."""
        if self._session is not None:
            return

        headers = {}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"

        self._sse_ctx = sse_client(self.server_url, headers=headers)
        read_stream, write_stream = await self._sse_ctx.__aenter__()

        self._session_ctx = ClientSession(read_stream, write_stream)
        self._session = await self._session_ctx.__aenter__()
        await self._session.initialize()
        logger.info(f"Connected persistent MCP SSE session to {self.server_url}")

    async def disconnect(self) -> None:
        """Đóng session và giải phóng kết nối SSE khi shutdown."""
        if self._session_ctx:
            await self._session_ctx.__aexit__(None, None, None)
            self._session_ctx = None
            self._session = None
        if self._sse_ctx:
            await self._sse_ctx.__aexit__(None, None, None)
            self._sse_ctx = None
        logger.info("Closed persistent MCP SSE session")

    async def call_tool(self, tool_name: str, arguments: dict[str, Any] | None = None) -> Any:
        """Gọi MCP tool trên session đã mở sẵn, tái sử dụng cho toàn bộ investigation."""
        if self._session is None:
            await self.connect()

        start_time = time.monotonic()
        arguments = arguments or {}

        try:
            result = await self._session.call_tool(tool_name, arguments=arguments)
            duration_ms = int((time.monotonic() - start_time) * 1000)

            if getattr(result, "isError", False):
                err_msg = self._extract_text(result.content)
                raise McpClientError(tool_name, err_msg, duration_ms=duration_ms)

            content_text = self._extract_text(result.content)
            logger.debug(f"Tool {tool_name} executed via SSE in {duration_ms}ms")
            
            try:
                return json.loads(content_text)
            except (json.JSONDecodeError, TypeError):
                return content_text

        except Exception as e:
            duration_ms = int((time.monotonic() - start_time) * 1000)
            logger.error(f"MCP tool {tool_name} failed ({duration_ms}ms): {e}")
            raise McpClientError(tool_name, str(e), duration_ms=duration_ms) from e

    def _extract_text(self, content: Any) -> str:
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for item in content:
                if hasattr(item, "text"):
                    parts.append(item.text)
                elif isinstance(item, dict) and "text" in item:
                    parts.append(item["text"])
            return "\n".join(parts)
        return str(content) if content else ""
```

---

## 6. Configuration Schema & Trade-offs

### 6.1 oracle-mcp-server `.env`
*(Chứa toàn bộ cấu hình kết nối Oracle và bảo mật transport)*

```env
# Oracle Connection (Chỉ duy nhất oracle-mcp-server nắm giữ credentials)
ORACLE_USER=db_copilot_readonly
ORACLE_PASSWORD=<secret>
ORACLE_DSN=prod-oracle-host:1521/ORCL
ORACLE_POOL_MIN=2
ORACLE_POOL_MAX=10

# MCP Transport Mode
MCP_TRANSPORT=sse
MCP_SSE_HOST=0.0.0.0
MCP_SSE_PORT=8080
MCP_SERVER_AUTH_TOKEN=<secret-internal-bearer-token>

# Audit Logging
AUDIT_LOG_LEVEL=INFO
AUDIT_RETENTION_DAYS=365
```

### 6.2 db-copilot `.env`
*(Tuyệt đối KHÔNG chứa Oracle credentials — giải quyết [LLD-02])*

```env
# MCP Server Connection (SSE Persistent Transport)
MCP_TRANSPORT=sse
MCP_SERVER_URL=http://oracle-mcp-server:8080/sse
MCP_SERVER_AUTH_TOKEN=<secret-internal-bearer-token>

# PostgreSQL Evidence Store
POSTGRES_URL=postgresql+asyncpg://dbcopilot:secret@localhost/dbcopilot

# LLM Provider Configuration
LLM_PROVIDER=openai  # openai | claude | gemini
OPENAI_API_KEY=<secret>
OPENAI_MODEL=gpt-4o

# Fallback LLM Provider (Optional)
FALLBACK_LLM_PROVIDER=gemini
GEMINI_API_KEY=<secret>
GEMINI_MODEL=gemini-2.0-flash

# Collection & Baselines
COLLECTION_INTERVAL_MINUTES=5
BASELINE_DAYS=7
SQL_REGRESSION_MULTIPLIER=3.0
TABLESPACE_WARNING_THRESHOLD=80
TABLESPACE_CRITICAL_THRESHOLD=90

# Daily Report
REPORT_SCHEDULE=0 6 * * *

# Alerts
SLACK_WEBHOOK_URL=<optional>
TEAMS_WEBHOOK_URL=<optional>
```

### 6.3 So Sánh & Trade-offs Các LLM Provider ([LLD-03])

Để hỗ trợ khách hàng doanh nghiệp (commercial customers) lựa chọn cấu hình phù hợp giữa **Chi phí (Cost)**, **Tốc độ (Latency)** và **Độ tin cậy JSON (Structured Output Reliability)**, hệ thống cung cấp ma trận đánh giá chi tiết:

| Tiêu chí | OpenAI `gpt-4o` *(Mặc định)* | Anthropic `claude-3-5-sonnet` | Google `gemini-2.0-flash` | OpenAI `gpt-4o-mini` | Google `gemini-1.5-pro` |
|---|---|---|---|---|---|
| **Chi phí Input (1M tokens)** | \$2.50 | \$3.00 | **\$0.10** | \$0.15 | \$1.25 |
| **Chi phí Output (1M tokens)** | \$10.00 | \$15.00 | **\$0.40** | \$0.60 | \$5.00 |
| **Độ trễ Latency (p50 / p95)** | ~1.2s / 2.5s | ~1.8s / 3.8s | **~0.6s / 1.2s** | ~0.5s / 1.0s | ~2.0s / 4.5s |
| **Độ tin cậy JSON Output** | ⭐⭐⭐⭐⭐ (Strict Mode) | ⭐⭐⭐⭐ (Cần parse markdown) | ⭐⭐⭐⭐⭐ (Structured Schema) | ⭐⭐⭐⭐⭐ (Strict Mode) | ⭐⭐⭐⭐⭐ (Structured Schema) |
| **Khả năng suy luận Oracle DB** | ⭐⭐⭐⭐⭐ (Rất chuẩn xác) | ⭐⭐⭐⭐⭐ (RCA xuất sắc nhất) | ⭐⭐⭐⭐ (Tốt) | ⭐⭐⭐ (Cơ bản) | ⭐⭐⭐⭐⭐ (Rất sâu) |
| **Context Window** | 128K tokens | 200K tokens | **1,048K tokens (1M)** | 128K tokens | **2,097K tokens (2M)** |
| **Phù hợp sử dụng** | **Production Tiêu chuẩn** | **Sự cố P1 / RCA Phức tạp** | **Chi phí tối ưu / High-traffic** | **Tóm tắt đơn giản / Dev** | **Phân tích AWR Dump lớn** |

#### Hướng Dẫn Lựa Chọn Kiến Trúc Cho Khách Hàng Doanh Nghiệp:
1. **Môi trường Production tiêu chuẩn (Khuyến nghị):** Chọn `LLM_PROVIDER=openai` với model `gpt-4o`. Lý do: Hỗ trợ Native Structured Outputs đảm bảo 100% schema JSON không bao giờ bị lỗi format khi parse vào `DiagnosisResult`.
2. **Tối ưu chi phí vận hành & Báo cáo định kỳ:** Chọn `LLM_PROVIDER=gemini` với model `gemini-2.0-flash`. Chi phí thấp hơn **25 lần** so với GPT-4o, tốc độ xử lý dưới 1 giây, context window 1M tokens cho phép nạp lượng lớn snapshot metric.
3. **Phân tích sự cố nghiêm trọng (Severity CRITICAL):** Cấu hình fallback hoặc định tuyến chuyên biệt sang `claude-3-5-sonnet`. Claude thể hiện khả năng liên kết nguyên nhân gốc rễ (Root Cause Analysis) tốt nhất trên execution plan phức tạp và chuỗi lock contention.

---

---

# 🇬🇧 ENGLISH SECTION

---

## 7. Project Structure Detail

_(See Sections 1.1 and 1.2 — same content)_

Key points:
- **oracle-mcp-server**: All Oracle connectivity. Stateless daemon. Runs independently with internal credentials.
- **db-copilot**: AI Application. Connects to MCP server via SSE transport. Zero direct Oracle credentials. Has PostgreSQL for evidence persistence.

---

## 8. API Endpoints

_(See Section 2 — same table)_

All endpoints return structured JSON. Investigation uses async pattern: POST returns ID, GET polls for result.

---

## 9. Domain Models

_(See Section 3 — same models)_

All domain models are pure Python dataclasses with no infrastructure dependencies, following clean architecture principles.

---

## 10. PostgreSQL Schema

_(See Section 4 — same DDL)_

Key design decisions:
- `sql_baselines` uses composite PK on `(database_id, sql_id, hour_of_day, day_of_week)` for time-bucketed baseline queries
- `evidence_items.data` is JSONB for flexibility across different evidence types
- All audit logs stored in `mcp_audit_log` — retained minimum 1 year

---

## 11. MCP Client Pattern

db-copilot acts as **MCP client** to oracle-mcp-server:
- **SSE Persistent Transport ([LLD-01])**: Reuses long-lived HTTP/SSE connection (`ClientSession`) across all tool calls in an investigation session, avoiding process spawn and connection pool overhead (~2-3s per call dropped to ~30-100ms), guaranteeing SLA < 60s.
- **Security Boundary ([LLD-02])**: Oracle credentials reside exclusively inside `oracle-mcp-server`. `db-copilot` only knows `MCP_SERVER_URL` (and bearer auth token), completely eliminating credential leakage into the AI application.
- All tool calls go through `OracleMcpClient.call_tool()`.

---

## 12. Configuration & LLM Provider Trade-offs

### 12.1 Configuration Isolation
Two separate `.env` files:
1. `oracle-mcp-server/.env`: Oracle connection (`ORACLE_USER`, `ORACLE_PASSWORD`, `ORACLE_DSN`) + MCP SSE server settings.
2. `db-copilot/.env`: `MCP_SERVER_URL` + PostgreSQL + LLM API keys + scheduling (No Oracle credentials).

### 12.2 LLM Provider Comparison ([LLD-03])
- **OpenAI `gpt-4o` (Default)**: Best balance of Oracle SQL reasoning and guaranteed structured JSON outputs via Strict Mode.
- **Google `gemini-2.0-flash`**: Highest throughput, ultra-low latency (<1s), lowest cost (~25x cheaper), 1M token context for massive AWR/ASH dumps.
- **Anthropic `claude-3-5-sonnet`**: Superior root cause analysis for complex execution plan regressions and locking graphs. Recommended for Critical incidents.

---


<!-- ======================================================
     FILE: docs/03-technical/oracle-mcp-design.md
     ====================================================== -->

# Oracle MCP Server Design
# Thiết Kế Oracle MCP Server

**Project:** `oracle-mcp-server`  
**Phiên bản / Version:** 0.1  
**Ngày / Date:** 2026-09-08

---

# 🇻🇳 PHẦN TIẾNG VIỆT

---

## 1. Tổng Quan

`oracle-mcp-server` là một **project độc lập** đóng vai trò **Oracle Observability & Evidence Gateway**.

Nó implement **Model Context Protocol (MCP)** để cung cấp các Oracle read-only tools cho AI agents hoặc bất kỳ MCP client nào (bao gồm `db-copilot`).

### 1.1 Nguyên tắc thiết kế

| Nguyên tắc | Giải thích |
|---|---|
| **Semantic tools, không phải generic SQL** | Mỗi tool có ngữ nghĩa rõ ràng, không có `execute_sql()` |
| **Read-only tuyệt đối** | Oracle account chỉ có SELECT privileges |
| **Structured output** | Mọi tool trả về Pydantic model, không phải raw rows |
| **Audit mọi call** | Mọi tool call đều được log với timestamp, args, duration |
| **Stateless** | Không có database riêng, không lưu state |
| **Fail-safe** | Lỗi query → trả về error có cấu trúc, không crash server |

---

## 2. MCP Protocol

### 2.1 Transport Modes

| Mode | Cách dùng |
|---|---|
| **Stdio** | `db-copilot` spawn `oracle-mcp-server` process, giao tiếp qua stdin/stdout |
| **SSE** | `oracle-mcp-server` chạy như HTTP server, client kết nối qua Server-Sent Events |

**MVP:** Stdio mode (đơn giản hơn, không cần network config)

### 2.2 MCP Server Entry Point

```python
# src/oracle_mcp/server.py

import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from oracle_mcp.tools import sql, ash, awr, session, plan, object_, storage
from oracle_mcp.config.settings import Settings

settings = Settings()
app = Server("oracle-mcp-server")

# Register all tools
for tool_fn in [
    *sql.get_tools(),
    *ash.get_tools(),
    *awr.get_tools(),
    *session.get_tools(),
    *plan.get_tools(),
    *object_.get_tools(),
    *storage.get_tools(),
]:
    app.add_tool(tool_fn)

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 3. Tool Catalog Đầy Đủ

### Group 1: SQL Tools (`tools/sql.py`)

| Tool | Input | Oracle Source | Output |
|---|---|---|---|
| `get_top_sql` | `metric, limit, hours` | `V$SQL`, `V$SQLSTATS` | `List[SqlSummary]` |
| `get_sql_statistics` | `sql_id` | `V$SQL`, `DBA_HIST_SQLSTAT` | `SqlStatistics` |
| `get_sql_wait_events` | `sql_id, hours` | `V$SESSION_WAIT`, `ASH` | `List[WaitEvent]` |
| `get_sql_execution_context` | `sql_id` | `V$SQL.MODULE/ACTION` | `ExecutionContext` |

### Group 2: ASH Tools (`tools/ash.py`)

| Tool | Input | Oracle Source | Output |
|---|---|---|---|
| `get_ash_sample` | `begin_time, end_time` | `V$ACTIVE_SESSION_HISTORY` | `List[AshSample]` |
| `get_ash_sql_activity` | `sql_id, begin_time, end_time` | `DBA_HIST_ACTIVE_SESS_HISTORY` | `AshActivity` |

### Group 3: AWR Tools (`tools/awr.py`)

| Tool | Input | Oracle Source | Output |
|---|---|---|---|
| `get_awr_snapshot` | `hours` | `DBA_HIST_SNAPSHOT` | `List[AwrSnapshot]` |
| `get_awr_sql_stats` | `sql_id, begin_snap, end_snap` | `DBA_HIST_SQLSTAT` | `AwrSqlStats` |

### Group 4: Session Tools (`tools/session.py`)

| Tool | Input | Oracle Source | Output |
|---|---|---|---|
| `get_active_sessions` | `min_elapsed_sec` | `V$SESSION` | `List[Session]` |
| `get_session` | `session_id, serial` | `V$SESSION` | `SessionDetail` |
| `get_session_waits` | `session_id` | `V$SESSION_WAIT` | `List[SessionWait]` |
| `get_blocking_sessions` | — | `V$SESSION` (self-join) | `List[BlockingChain]` |
| `get_long_running_sessions` | `min_minutes` | `V$SESSION.LAST_CALL_ET` | `List[Session]` |

### Group 5: Plan Tools (`tools/plan.py`)

| Tool | Input | Oracle Source | Output |
|---|---|---|---|
| `get_sql_plan` | `sql_id` | `V$SQL_PLAN` | `ExecutionPlan` |
| `get_sql_plan_history` | `sql_id, days` | `DBA_HIST_SQL_PLAN`, `DBA_HIST_SQLSTAT` | `List[PlanHistory]` |

### Group 6: Object/Code Tools (`tools/object.py`)

| Tool | Input | Oracle Source | Output |
|---|---|---|---|
| `get_object_source` | `owner, name, type` | `ALL_SOURCE` | `ObjectSource` |
| `get_object_metadata` | `owner, name, type` | `DBA_OBJECTS`, `DBA_TAB_STATISTICS` | `ObjectMetadata` |
| `get_object_arguments` | `owner, name` | `ALL_ARGUMENTS` | `List[Argument]` |
| `get_object_dependencies` | `owner, name, type` | `ALL_DEPENDENCIES` | `List[Dependency]` |
| `get_dependency_graph` | `owner, name, type, depth` | `ALL_DEPENDENCIES` (recursive) | `DependencyGraph` |
| `get_invalid_objects` | — | `DBA_OBJECTS` | `List[InvalidObject]` |

### Group 7: Storage Tools (`tools/storage.py`)

| Tool | Input | Oracle Source | Output |
|---|---|---|---|
| `get_tablespace_usage` | — | `DBA_DATA_FILES`, `DBA_FREE_SPACE` | `List[TablespaceUsage]` |
| `get_datafile_usage` | `tablespace_name` | `DBA_DATA_FILES` | `List[DatafileUsage]` |
| `get_segment_growth` | `owner, name, days` | `DBA_SEGMENTS` | `SegmentGrowth` |
| `get_temp_usage` | — | `V$TEMPSTAT`, `DBA_TEMP_FILES` | `TempUsage` |
| `get_undo_usage` | — | `V$UNDOSTAT` | `UndoUsage` |
| `get_database_info` | — | `V$DATABASE`, `V$INSTANCE`, `V$PARAMETER` | `DatabaseInfo` |
| `get_resource_usage` | — | `V$SYSSTAT`, `V$SYSEVENT` | `ResourceUsage` |
| `get_redo_statistics` | `hours` | `V$LOG`, `V$ARCHIVED_LOG` | `RedoStatistics` |
| `get_alert_events` | `hours` | `V$DIAG_ALERT_EXT` | `List[AlertEvent]` |
| `get_scheduler_jobs` | — | `DBA_SCHEDULER_JOBS` | `List[JobStatus]` |
| `get_scheduler_job_history` | `job_name, days` | `DBA_SCHEDULER_JOB_RUN_DETAILS` | `List[JobRun]` |
| `get_failed_jobs` | `hours` | `DBA_SCHEDULER_JOB_RUN_DETAILS` | `List[JobRun]` |

---

## 4. Tool Implementation Pattern

```python
# src/oracle_mcp/tools/sql.py

from mcp.types import Tool
from oracle_mcp.oracle.repositories.sql_repo import SqlRepository
from oracle_mcp.security.audit import AuditContext
from oracle_mcp.models.sql_models import SqlStatistics

async def get_sql_statistics(sql_id: str) -> dict:
    """
    Lấy cumulative execution statistics cho một SQL_ID.
    Source: V$SQL (real-time) và DBA_HIST_SQLSTAT (historical).
    """
    async with AuditContext(tool="get_sql_statistics", args={"sql_id": sql_id}):
        repo = SqlRepository()
        stats: SqlStatistics = await repo.get_sql_statistics(sql_id)
        return stats.model_dump()

def get_tools() -> list[Tool]:
    return [
        Tool(
            name="get_sql_statistics",
            description=(
                "Get cumulative execution statistics for a specific SQL_ID. "
                "Includes executions, elapsed time, CPU time, buffer gets, "
                "disk reads, rows processed, and current plan hash."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "sql_id": {
                        "type": "string",
                        "description": "Oracle SQL_ID (13-character identifier)"
                    }
                },
                "required": ["sql_id"]
            },
            fn=get_sql_statistics
        ),
        # ... other tools
    ]
```

---

## 5. Oracle Connection

```python
# src/oracle_mcp/oracle/connection.py

import oracledb
from oracle_mcp.config.settings import Settings

class OracleConnectionPool:
    """
    Singleton async connection pool.
    python-oracledb thin mode (không cần Oracle Client).
    """
    _pool: oracledb.AsyncConnectionPool | None = None

    @classmethod
    async def initialize(cls):
        s = Settings()
        cls._pool = await oracledb.create_pool_async(
            user=s.oracle_user,
            password=s.oracle_password,
            dsn=s.oracle_dsn,
            min=2,
            max=10,
            increment=1
        )

    @classmethod
    async def acquire(cls) -> oracledb.AsyncConnection:
        if cls._pool is None:
            await cls.initialize()
        return await cls._pool.acquire()
```

---

## 6. Audit System

```python
# src/oracle_mcp/security/audit.py

import time
import json
import logging
from logging.handlers import RotatingFileHandler
from contextlib import asynccontextmanager
from oracle_mcp.security.sanitizer import sanitize_args

# [MCP-03] Audit logging hỗ trợ cả Stderr và Rotating File Log cho Enterprise SOC2 Compliance
audit_logger = logging.getLogger("oracle_mcp.audit")
audit_logger.setLevel(logging.INFO)
file_handler = RotatingFileHandler("logs/mcp_audit.log", maxBytes=10*1024*1024, backupCount=5)
audit_logger.addHandler(file_handler)

@asynccontextmanager
async def AuditContext(tool: str, args: dict):
    """
    Context manager: log mọi MCP tool call.
    Ghi log TRƯỚC khi trả kết quả (vào cả rotating file và stderr).
    """
    start = time.time()
    sanitized = sanitize_args(args)

    try:
        yield
        duration_ms = int((time.time() - start) * 1000)
        _write_audit_log(tool, sanitized, duration_ms, status="success")
    except Exception as e:
        duration_ms = int((time.time() - start) * 1000)
        _write_audit_log(tool, sanitized, duration_ms, status="error", error=str(e))
        raise

def _write_audit_log(tool, args, duration_ms, status, error=None):
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "tool": tool,
        "args": args,
        "duration_ms": duration_ms,
        "status": status,
        "error": error
    }
    line = json.dumps(record, ensure_ascii=False)
    # 1. Ghi ra stderr (stdout dành riêng cho MCP JSON-RPC protocol)
    print(line, file=sys.stderr, flush=True)
    # 2. Ghi ra rotating file bảo vệ log không bị mất khi chạy Stdio mode mà parent không capture
    audit_logger.info(line)
```

---

## 7. Security: Oracle Permissions

```sql
-- Tạo read-only user
CREATE USER db_copilot_readonly IDENTIFIED BY "<password>";

-- AWR / ASH
GRANT SELECT ON SYS.DBA_HIST_SQLSTAT TO db_copilot_readonly;
GRANT SELECT ON SYS.DBA_HIST_SQL_PLAN TO db_copilot_readonly;
GRANT SELECT ON SYS.DBA_HIST_SNAPSHOT TO db_copilot_readonly;
GRANT SELECT ON SYS.DBA_HIST_SQLTEXT TO db_copilot_readonly;
GRANT SELECT ON SYS.DBA_HIST_ACTIVE_SESS_HISTORY TO db_copilot_readonly;

-- V$ Dynamic Views
GRANT SELECT ON SYS.V_$SQL TO db_copilot_readonly;
GRANT SELECT ON SYS.V_$SQLSTATS TO db_copilot_readonly;
GRANT SELECT ON SYS.V_$SESSION TO db_copilot_readonly;
GRANT SELECT ON SYS.V_$SESSION_WAIT TO db_copilot_readonly;
GRANT SELECT ON SYS.V_$SQL_PLAN TO db_copilot_readonly;
GRANT SELECT ON SYS.V_$SQL_PLAN_STATISTICS_ALL TO db_copilot_readonly;
GRANT SELECT ON SYS.V_$ACTIVE_SESSION_HISTORY TO db_copilot_readonly;
GRANT SELECT ON SYS.V_$UNDOSTAT TO db_copilot_readonly;
GRANT SELECT ON SYS.V_$TEMPSTAT TO db_copilot_readonly;
GRANT SELECT ON SYS.V_$DATABASE TO db_copilot_readonly;
GRANT SELECT ON SYS.V_$INSTANCE TO db_copilot_readonly;
GRANT SELECT ON SYS.V_$PARAMETER TO db_copilot_readonly;
GRANT SELECT ON SYS.V_$SYSSTAT TO db_copilot_readonly;
GRANT SELECT ON SYS.V_$SYSEVENT TO db_copilot_readonly;
GRANT SELECT ON SYS.V_$LOG TO db_copilot_readonly;
GRANT SELECT ON SYS.V_$ARCHIVED_LOG TO db_copilot_readonly;  -- [MCP-02] get_redo_statistics

-- Diagnostics / Alert Log
GRANT SELECT ON SYS.V_$DIAG_ALERT_EXT TO db_copilot_readonly; -- [MCP-01] get_alert_events

-- Storage
GRANT SELECT ON SYS.DBA_DATA_FILES TO db_copilot_readonly;
GRANT SELECT ON SYS.DBA_FREE_SPACE TO db_copilot_readonly;
GRANT SELECT ON SYS.DBA_SEGMENTS TO db_copilot_readonly;
GRANT SELECT ON SYS.DBA_TABLESPACES TO db_copilot_readonly;
GRANT SELECT ON SYS.DBA_TEMP_FILES TO db_copilot_readonly;

-- Jobs
GRANT SELECT ON SYS.DBA_SCHEDULER_JOBS TO db_copilot_readonly;
GRANT SELECT ON SYS.DBA_SCHEDULER_JOB_RUN_DETAILS TO db_copilot_readonly;
GRANT SELECT ON SYS.DBA_SCHEDULER_RUNNING_JOBS TO db_copilot_readonly;

-- Code / Objects
GRANT SELECT ON SYS.ALL_SOURCE TO db_copilot_readonly;
GRANT SELECT ON SYS.ALL_OBJECTS TO db_copilot_readonly;
GRANT SELECT ON SYS.DBA_OBJECTS TO db_copilot_readonly;
GRANT SELECT ON SYS.ALL_DEPENDENCIES TO db_copilot_readonly;
GRANT SELECT ON SYS.ALL_ARGUMENTS TO db_copilot_readonly;
GRANT SELECT ON SYS.DBA_TAB_STATISTICS TO db_copilot_readonly;
GRANT SELECT ON SYS.DBA_IND_STATISTICS TO db_copilot_readonly;
GRANT SELECT ON SYS.DBA_INDEXES TO db_copilot_readonly;

-- Không cấp: DML, DDL, EXECUTE, DBA role
```

---

## 8. Tool Output Contracts

### get_sql_statistics

```json
{
  "sql_id": "8f3abc",
  "sql_text_fragment": "SELECT * FROM ACCOUNT_POSITION WHERE ...",
  "executions": 12450,
  "elapsed_time_ms": 52300000,
  "cpu_time_ms": 21300000,
  "buffer_gets": 182000000,
  "disk_reads": 9300000,
  "rows_processed": 4200000,
  "last_active_time": "2026-09-08T14:32:00Z",
  "plan_hash_value": 98237412,
  "module": "PROC_SETTLEMENT",
  "action": "UPDATE_PHASE"
}
```

### get_blocking_sessions

```json
{
  "blocking_chains": [
    {
      "blocker": {
        "session_id": 142, "serial": 1023,
        "user": "APP", "sql_id": "abc123",
        "wait_event": "enq: TX - row lock contention",
        "elapsed_seconds": 423
      },
      "blocked": [
        {"session_id": 156, "serial": 2011, "sql_id": "def456"}
      ]
    }
  ],
  "total_blocked": 1,
  "max_wait_seconds": 423
}
```

### get_object_source

```json
{
  "owner": "APP",
  "object_name": "PROC_SETTLEMENT",
  "object_type": "PROCEDURE",
  "status": "VALID",
  "last_ddl_time": "2026-09-01T10:00:00Z",
  "source_hash": "sha256:abc123...",
  "source_lines": 312,
  "source": "CREATE OR REPLACE PROCEDURE PROC_SETTLEMENT ...",
  "sql_statements": [
    {"line": 247, "type": "UPDATE", "table": "ACCOUNT_POSITION"}
  ],
  "dependencies": [
    {"owner": "APP", "name": "ACCOUNT_POSITION", "type": "TABLE"},
    {"owner": "APP", "name": "PROC_CALCULATE", "type": "PROCEDURE"}
  ]
}
```

> **[MCP-04] Lưu ý kỹ thuật về trích xuất `sql_statements`:**
> PL/SQL full AST parsing là bài toán phức tạp. Trong phạm vi MVP, hệ thống sử dụng **heuristic regex-based parser** nhận diện các câu lệnh DML tĩnh (`SELECT`, `INSERT`, `UPDATE`, `DELETE`, `MERGE`).
> - **Đặc điểm:** Approximate (xấp xỉ), tập trung định vị nhanh dòng code nghi vấn.
> - **Giới hạn:** Không hỗ trợ Dynamic SQL phức tạp (`EXECUTE IMMEDIATE`, `DBMS_SQL`).

---

---

# 🇬🇧 ENGLISH SECTION

---

## 9. Overview

`oracle-mcp-server` is a **standalone project** acting as the **Oracle Observability & Evidence Gateway**.

It implements the **Model Context Protocol (MCP)** to expose Oracle read-only tools to AI agents or any MCP client (including `db-copilot`).

### 9.1 Design Principles

| Principle | Explanation |
|---|---|
| **Semantic tools, not generic SQL** | Each tool has clear semantics, no `execute_sql()` |
| **Absolutely read-only** | Oracle account has SELECT privileges only |
| **Structured output** | All tools return Pydantic models, not raw rows |
| **Audit every call** | Every tool call logged: timestamp, args, duration |
| **Stateless** | No own database, no stored state |
| **Fail-safe** | Query error → structured error response, no server crash |

---

## 10. Tool Groups Summary

- **sql.py** (4 tools): `get_top_sql`, `get_sql_statistics`, `get_sql_wait_events`, `get_sql_execution_context`
- **ash.py** (2 tools): `get_ash_sample`, `get_ash_sql_activity`
- **awr.py** (2 tools): `get_awr_snapshot`, `get_awr_sql_stats`
- **session.py** (5 tools): `get_active_sessions`, `get_session`, `get_session_waits`, `get_blocking_sessions`, `get_long_running_sessions`
- **plan.py** (2 tools): `get_sql_plan`, `get_sql_plan_history`
- **object.py** (6 tools): `get_object_source`, `get_object_metadata`, `get_object_arguments`, `get_object_dependencies`, `get_dependency_graph`, `get_invalid_objects`
- **storage.py** (11 tools): tablespace, temp, undo, segments, redo, jobs, db info, alerts, resources

**Total: ~32 tools**

---

## 11. Security

- Oracle credentials only in `oracle-mcp-server` — read from environment variables
- Never logged (sanitizer removes credentials from audit args)
- Never passed to `db-copilot` or LLM
- SELECT-only grants on ~35 pre-approved views/tables (including `V$DIAG_ALERT_EXT` and `V$ARCHIVED_LOG`)
- No DML, DDL, EXECUTE, or DBA role granted

---

## 12. Audit

Every MCP tool call is audit-logged to both stderr (for console monitoring) and a dedicated rotating log file (`logs/mcp_audit.log`):

```json
{
  "timestamp": "2026-09-08T14:32:01Z",
  "tool": "get_sql_statistics",
  "args": {"sql_id": "8f3abc"},
  "duration_ms": 132,
  "status": "success"
}
```

Audit log entries are **always written**, even on errors, ensuring enterprise SOC2 compliance. The `AuditContext` context manager guarantees this.

---


<!-- ======================================================
     FILE: docs/03-technical/ai-engine-design.md
     ====================================================== -->

# AI Engine Design
# Thiết Kế AI Engine

**Project:** `db-copilot` — `ai/`  
**Phiên bản / Version:** 0.1  
**Ngày / Date:** 2026-09-08

---

# 🇻🇳 PHẦN TIẾNG VIỆT

---

## 1. Tổng Quan

AI Engine là layer duy nhất trong `db-copilot` giao tiếp với LLM. Nó nhận **structured evidence** từ Investigation Engine và trả về **structured diagnosis** — không bao giờ nhận raw Oracle data và không bao giờ trả về free-form text.

### Nguyên tắc

| Nguyên tắc | Giải thích |
|---|---|
| **Evidence-first** | LLM chỉ được gọi sau khi có đủ evidence từ deterministic rules |
| **Structured I/O** | Input: EvidencePackage, Output: DiagnosisResult (JSON) |
| **Multi-provider** | Không lock-in một LLM, có thể switch OpenAI/Claude/Gemini |
| **No credentials leak** | LLM không bao giờ nhận Oracle credentials hoặc PII |
| **No auto-execute** | LLM chỉ được recommend, không được suggest execute |

---

## 2. Component Overview

```
db-copilot/ai/
│
├── providers/
│   ├── openai_provider.py    # OpenAI GPT-4o
│   ├── claude_provider.py    # Anthropic Claude
│   └── gemini_provider.py    # Google Gemini
│
├── prompts/
│   ├── diagnosis_prompt.py   # System prompt cho diagnosis
│   └── report_prompt.py      # System prompt cho daily report
│
└── service.py                # AI service orchestrator
```

---

## 3. LLM Provider Interface

```python
# src/db_copilot/domain/interfaces/llm_provider.py

from abc import ABC, abstractmethod

class LLMProvider(ABC):

    @abstractmethod
    async def diagnose(self, package: EvidencePackage) -> DiagnosisResult:
        """
        Nhận evidence package, trả về structured diagnosis.
        Output PHẢI là DiagnosisResult — không trả free-form text.
        Raise LLMDiagnosisError nếu không thể tạo structured output.
        """
        pass

    @abstractmethod
    async def generate_report_section(
        self,
        incidents: list[Incident],
        section_type: str
    ) -> str:
        """
        Tạo một section hoặc toàn bộ markdown daily report.
        section_type: "critical", "warning", "info", "summary", hoặc "full_report"
        """
        pass

    @abstractmethod
    async def parse_intent(self, question: str, current_time: datetime) -> dict:
        """
        Parse natural language question thành InvestigationIntent dict.
        Separate, nhỏ call — không cần full evidence context.
        """
        pass
```

---

## 4. Evidence Package Schema

```python
# src/db_copilot/domain/models/diagnosis.py

@dataclass
class EvidencePackage:
    # Core
    question: str
    intent: InvestigationIntent

    # Evidence
    evidence: list[Evidence]          # All collected evidence
    hypotheses: list[Hypothesis]      # Pre-ranked by Hypothesis Engine

    # Context
    database_name: str
    investigation_timestamp: datetime
    investigation_duration_seconds: float

    # Additional data (filtered, not raw Oracle data)
    sql_details: dict | None = None   # SQL text, plan summary
    source_fragment: str | None = None # PL/SQL source fragment (NOT full source)
    baseline_data: dict | None = None  # Baseline comparison

    # What LLM should NOT know
    # oracle_credentials: ← NEVER included
    # raw_oracle_rows: ← NEVER included (only processed evidence)
```

---

## 5. Structured Output Schema

LLM **bắt buộc** trả về JSON theo schema sau:

```python
@dataclass
class Recommendation:
    action: str           # "Gather statistics for ACCOUNT_POSITION"
    sql: str | None       # SQL command (display only, never auto-execute)
    priority: str         # "HIGH", "MEDIUM", "LOW"
    note: str             # "DBA must review and execute manually"

@dataclass
class DiagnosisResult:
    diagnosis: str                    # Tóm tắt chẩn đoán
    confidence: float                 # 0.0 – 1.0
    primary_cause: str                # Root cause chính
    evidence_used: list[str]          # Evidence hỗ trợ kết luận
    evidence_against: list[str]       # Evidence mâu thuẫn
    recommendations: list[Recommendation]
    confidence_explanation: str       # Giải thích tại sao confidence = X%
    alternative_causes: list[str]     # Các nguyên nhân khác ít khả năng hơn
```

---

## 6. Diagnosis Prompt Design

```python
# src/db_copilot/ai/prompts/diagnosis_prompt.py

DIAGNOSIS_SYSTEM_PROMPT = """
You are an expert Oracle Database Performance Engineer.

TASK: Analyze the provided database investigation evidence and provide a structured diagnosis.

RULES:
1. Base ALL conclusions ONLY on the provided evidence — never use general knowledge as primary evidence.
2. If evidence is insufficient, say so explicitly and lower confidence.
3. Do NOT suggest any automatic execution. All recommendations must be prefixed with "DBA must review and execute manually."
4. Confidence must reflect actual evidence quality:
   - < 0.5: Insufficient evidence
   - 0.5 – 0.7: Partial evidence, possible cause
   - 0.7 – 0.9: Strong evidence, likely cause
   - > 0.9: Very strong evidence, highly probable cause
5. Always include contradicting evidence (what rules out other causes).
6. SQL in recommendations is for human review only — clearly state this.

OUTPUT FORMAT: Return ONLY valid JSON matching the DiagnosisResult schema. No markdown, no explanation outside JSON.
"""

DIAGNOSIS_USER_TEMPLATE = """
QUESTION: {question}

DATABASE: {database_name}
INVESTIGATION TIME: {timestamp}

PRE-RANKED HYPOTHESES (from deterministic analysis):
{hypotheses_json}

EVIDENCE COLLECTED:
{evidence_json}

ADDITIONAL CONTEXT:
{context_json}
"""
```

---

## 7. Provider Implementations

### 7.1 OpenAI Provider

```python
# src/db_copilot/ai/providers/openai_provider.py

import json
from openai import AsyncOpenAI
from db_copilot.domain.interfaces.llm_provider import LLMProvider
from db_copilot.domain.models.diagnosis import EvidencePackage, DiagnosisResult
from db_copilot.domain.models.incident import Incident
from db_copilot.ai.prompts.diagnosis_prompt import DIAGNOSIS_SYSTEM_PROMPT, DIAGNOSIS_USER_TEMPLATE

class OpenAIProvider(LLMProvider):

    def __init__(self, model: str = "gpt-4o"):
        self.client = AsyncOpenAI()
        self.model = model

    async def diagnose(self, package: EvidencePackage) -> DiagnosisResult:
        user_prompt = DIAGNOSIS_USER_TEMPLATE.format(
            question=package.question,
            database_name=package.database_name,
            timestamp=package.investigation_timestamp.isoformat(),
            hypotheses_json=json.dumps(
                [h.__dict__ for h in package.hypotheses], indent=2
            ),
            evidence_json=json.dumps(
                [self._serialize_evidence(e) for e in self._filter_evidence(package.evidence)], indent=2
            ),
            context_json=json.dumps({
                "sql_details": package.sql_details,
                "source_fragment": package.source_fragment
            }, indent=2)
        )

        # Retry logic nếu JSON parse error
        messages = [
            {"role": "system", "content": DIAGNOSIS_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]

        for attempt in range(2):
            response = await self.client.chat.completions.create(
                model=self.model,
                temperature=0.1,          # Low temperature for consistent structured output
                max_tokens=4096,          # [AI-06] Tránh truncate JSON kết quả phức tạp
                response_format={"type": "json_object"},
                messages=messages
            )
            raw_json = response.choices[0].message.content
            try:
                data = json.loads(raw_json)
                return DiagnosisResult(**data)
            except Exception as err:
                if attempt == 0:
                    messages.append({"role": "assistant", "content": raw_json})
                    messages.append({"role": "user", "content": f"Invalid JSON format: {err}. Please return STRICT valid JSON matching DiagnosisResult schema."})
                else:
                    raise err

    async def generate_report_section(
        self,
        incidents: list[Incident],
        section_type: str = "full_report"
    ) -> str:
        prompt = f"Generate a {section_type} section for these incidents: {json.dumps([i.__dict__ for i in incidents], default=str)}"
        response = await self.client.chat.completions.create(
            model=self.model,
            temperature=0.2,
            messages=[
                {"role": "system", "content": "You are a senior Oracle DBA generating a clean markdown daily health report."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

    async def parse_intent(self, question: str, current_time: datetime) -> dict:
        # [AI-05] Implement parse_intent
        prompt = f"Parse the user question into an investigation intent: '{question}'. Current time is {current_time.isoformat()}."
        response = await self.client.chat.completions.create(
            model=self.model,
            temperature=0.0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "Parse database troubleshooting questions into JSON with keys: intent_type, entity_type, entity_id, time_range (start_time, end_time), focus_metric."},
                {"role": "user", "content": prompt}
            ]
        )
        return json.loads(response.choices[0].message.content)

    def _filter_evidence(self, evidence_list: list[Evidence]) -> list[Evidence]:
        # [AI-08] Filter chỉ HIGH + MEDIUM severity để tối ưu context & privacy
        filtered = [e for e in evidence_list if e.severity in (Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM)]
        return filtered if filtered else evidence_list[:15]

    def _serialize_evidence(self, e: Evidence) -> dict:
        """Serialize evidence, removing any sensitive fields."""
        return {
            "type": e.type.value,
            "entity": f"{e.entity_type}:{e.entity_id}",
            "severity": e.severity.value,
            "data": e.data  # Already sanitized by collector
        }
```

### 7.2 Claude Provider

```python
# src/db_copilot/ai/providers/claude_provider.py

import anthropic
import json
from db_copilot.domain.interfaces.llm_provider import LLMProvider
from db_copilot.domain.models.diagnosis import EvidencePackage, DiagnosisResult
from db_copilot.domain.models.incident import Incident
from db_copilot.ai.prompts.diagnosis_prompt import DIAGNOSIS_SYSTEM_PROMPT

class ClaudeProvider(LLMProvider):

    def __init__(self, model: str = "claude-sonnet-4-6"):  # [AI-03] Update model ID mới nhất
        self.client = anthropic.AsyncAnthropic()
        self.model = model

    async def diagnose(self, package: EvidencePackage) -> DiagnosisResult:
        # [AI-01] Dùng Claude tool_use để force structured output (không sợ thiếu _extract_json)
        # [AI-04] Sử dụng prompt caching với cache_control ephemeral
        system_content = [
            {
                "type": "text",
                "text": DIAGNOSIS_SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"}  # Cache 5 phút
            }
        ]

        diagnosis_tool = {
            "name": "submit_diagnosis",
            "description": "Submit structured Oracle DB diagnosis result",
            "input_schema": DiagnosisResult.model_json_schema()
        }

        user_content = self._build_user_prompt(package)

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=4096,  # [AI-06] Tăng max_tokens lên 4096
            temperature=0.1,  # [AI-07] Bổ sung temperature 0.1 cho đồng nhất output
            system=system_content,
            tools=[diagnosis_tool],
            tool_choice={"type": "tool", "name": "submit_diagnosis"},
            messages=[
                {"role": "user", "content": user_content}
            ]
        )

        for content_block in response.content:
            if content_block.type == "tool_use" and content_block.name == "submit_diagnosis":
                return DiagnosisResult(**content_block.input)

        raise ValueError("Claude did not call submit_diagnosis tool")

    async def generate_report_section(
        self,
        incidents: list[Incident],
        section_type: str = "full_report"
    ) -> str:
        prompt = f"Generate {section_type} section for daily report from incidents: {json.dumps([i.__dict__ for i in incidents], default=str)}"
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            temperature=0.2,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

    async def parse_intent(self, question: str, current_time: datetime) -> dict:
        # [AI-05] Implement parse_intent qua tool_use
        intent_tool = {
            "name": "submit_intent",
            "description": "Submit parsed question intent",
            "input_schema": {
                "type": "object",
                "properties": {
                    "intent_type": {"type": "string"},
                    "entity_type": {"type": "string"},
                    "entity_id": {"type": "string"},
                    "start_time": {"type": "string"},
                    "end_time": {"type": "string"},
                    "focus_metric": {"type": "string"}
                },
                "required": ["intent_type"]
            }
        }
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            temperature=0.0,
            tools=[intent_tool],
            tool_choice={"type": "tool", "name": "submit_intent"},
            messages=[{"role": "user", "content": f"Parse question: '{question}'. Current time: {current_time.isoformat()}."}]
        )
        for block in response.content:
            if block.type == "tool_use" and block.name == "submit_intent":
                return block.input
        return {"intent_type": "UNKNOWN"}

    def _build_user_prompt(self, package: EvidencePackage) -> str:
        # [AI-08] Filter evidence
        filtered_evidence = [e for e in package.evidence if e.severity in (Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM)]
        if not filtered_evidence:
            filtered_evidence = package.evidence[:15]

        return f"""
QUESTION: {package.question}
DATABASE: {package.database_name}
TIMESTAMP: {package.investigation_timestamp.isoformat()}

HYPOTHESES: {json.dumps([h.__dict__ for h in package.hypotheses], default=str)}
EVIDENCE: {json.dumps([e.data for e in filtered_evidence], default=str)}
CONTEXT: sql_details={package.sql_details}, source_fragment={package.source_fragment}
"""
```

### 7.3 Gemini Provider

```python
# src/db_copilot/ai/providers/gemini_provider.py

import json
from google import genai
from google.genai import types
from db_copilot.domain.interfaces.llm_provider import LLMProvider
from db_copilot.domain.models.diagnosis import EvidencePackage, DiagnosisResult
from db_copilot.domain.models.incident import Incident
from db_copilot.ai.prompts.diagnosis_prompt import DIAGNOSIS_SYSTEM_PROMPT

class GeminiProvider(LLMProvider):

    def __init__(self, model: str = "gemini-2.0-flash"):
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = model

    async def diagnose(self, package: EvidencePackage) -> DiagnosisResult:
        user_prompt = self._build_user_prompt(package)
        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=DIAGNOSIS_SYSTEM_PROMPT,
                response_mime_type="application/json",
                response_schema=DiagnosisResult,
                temperature=0.1,
                max_output_tokens=4096
            )
        )
        return DiagnosisResult(**json.loads(response.text))

    async def generate_report_section(
        self,
        incidents: list[Incident],
        section_type: str = "full_report"
    ) -> str:
        prompt = f"Generate {section_type} section for daily report from: {json.dumps([i.__dict__ for i in incidents], default=str)}"
        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction="You are a senior Oracle DBA writing daily report in markdown.",
                temperature=0.2
            )
        )
        return response.text

    async def parse_intent(self, question: str, current_time: datetime) -> dict:
        prompt = f"Parse question: '{question}'. Current time: {current_time.isoformat()}."
        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction="Parse user question into JSON with keys: intent_type, entity_type, entity_id, start_time, end_time, focus_metric.",
                response_mime_type="application/json",
                temperature=0.0
            )
        )
        return json.loads(response.text)

    def _build_user_prompt(self, package: EvidencePackage) -> str:
        filtered = [e for e in package.evidence if e.severity in (Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM)] or package.evidence[:15]
        return f"QUESTION: {package.question}\nDATABASE: {package.database_name}\nEVIDENCE: {json.dumps([e.data for e in filtered], default=str)}"
```

---

## 8. AI Service Orchestrator

```python
# src/db_copilot/ai/service.py
# [AI-02] Merge toàn bộ chức năng vào 1 class AIService duy nhất (diagnose + generate_daily_report)

import asyncio
import logging
from datetime import date
from db_copilot.domain.interfaces.llm_provider import LLMProvider
from db_copilot.domain.models.diagnosis import EvidencePackage, DiagnosisResult, Recommendation
from db_copilot.domain.models.incident import Incident, Severity
from db_copilot.config.settings import Settings
from db_copilot.ai.providers.openai_provider import OpenAIProvider
from db_copilot.ai.providers.claude_provider import ClaudeProvider
from db_copilot.ai.providers.gemini_provider import GeminiProvider

logger = logging.getLogger(__name__)

class AIService:
    """
    Orchestrates LLM calls.
    Handles: provider selection, retry, fallback, error handling, daily reports.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.primary = self._create_provider(settings.llm_provider)
        self.fallback = self._create_provider(settings.llm_fallback_provider)

    async def diagnose(self, package: EvidencePackage) -> DiagnosisResult:
        try:
            return await asyncio.wait_for(
                self.primary.diagnose(package),
                timeout=30.0  # 30s timeout cho LLM call
            )
        except (asyncio.TimeoutError, Exception) as e:
            logger.warning(f"Primary LLM failed ({e}), trying fallback provider")
            try:
                return await asyncio.wait_for(
                    self.fallback.diagnose(package),
                    timeout=30.0
                )
            except Exception as fallback_err:
                logger.error(f"Fallback LLM failed ({fallback_err}), using rule-based fallback")
                return self._fallback_diagnosis(package)

    async def generate_daily_report(
        self,
        incidents: list[Incident],
        health_score: int,
        database_name: str,
        report_date: date
    ) -> str:
        """
        Generate markdown daily report from incidents.
        """
        try:
            # [AI-10] Sử dụng section_type='full_report' đồng nhất
            return await self.primary.generate_report_section(
                incidents=incidents,
                section_type="full_report"
            )
        except Exception as e:
            logger.warning(f"Primary failed to generate report ({e}), trying fallback")
            return await self.fallback.generate_report_section(
                incidents=incidents,
                section_type="full_report"
            )

    def _fallback_diagnosis(self, package: EvidencePackage) -> DiagnosisResult:
        """
        Khi LLM fail hoàn toàn, tạo diagnosis từ Hypothesis Engine output.
        Không dùng LLM, chỉ dùng hypotheses đã có.
        """
        top_hypothesis = package.hypotheses[0] if package.hypotheses else None
        return DiagnosisResult(
            diagnosis=top_hypothesis.name if top_hypothesis else "Unable to diagnose",
            confidence=top_hypothesis.confidence if top_hypothesis else 0.0,
            primary_cause=top_hypothesis.name if top_hypothesis else "Unknown",
            evidence_used=[e.type.value for e in package.evidence[:5]],
            evidence_against=[],
            recommendations=[
                Recommendation(
                    action="Review the evidence manually",
                    sql=None,
                    priority="HIGH",
                    note="DBA must review and execute manually."
                )
            ],
            confidence_explanation="Diagnosis based on rule engine only (AI unavailable)",
            alternative_causes=[]
        )

    def _create_provider(self, provider_name: str) -> LLMProvider:
        match provider_name:
            case "openai":
                return OpenAIProvider(model=self.settings.openai_model)
            case "claude":
                return ClaudeProvider(model=self.settings.claude_model)
            case "gemini":
                return GeminiProvider(model=self.settings.gemini_model)
            case _:
                raise ValueError(f"Unknown LLM provider: {provider_name}")
```

---

## 9. Report Generation Prompts

```python
# src/db_copilot/ai/prompts/report_prompt.py

REPORT_SYSTEM_PROMPT = """
You are an Oracle Database monitoring system generating a daily health report for DBAs.

RULES:
1. Be concise and actionable — DBAs are busy.
2. Group issues by severity: CRITICAL > WARNING > INFO.
3. For each issue, provide: what happened, evidence summary, specific recommendation.
4. Use plain language — avoid jargon where possible.
5. Always end with: "No automatic database changes were executed."
6. Never recommend automatic execution of any database commands.

FORMAT: Clean markdown. Use headings, bullet points, and code blocks for SQL.
"""
```

---

---

# 🇬🇧 ENGLISH SECTION

---

## 10. Overview

AI Engine is the only layer in `db-copilot` that communicates with LLMs. It receives **structured evidence** from Investigation Engine and returns **structured diagnosis** — never raw Oracle data in, never free-form text out.

---

## 11. Multi-Provider Architecture

```
AIService (orchestrator)
    │
    ├── Primary Provider  (configured via LLM_PROVIDER env)
    │   ├── OpenAIProvider (GPT-4o)
    │   ├── ClaudeProvider (Claude Sonnet 4.6)
    │   └── GeminiProvider (Gemini 2.0 Flash)
    │
    └── Fallback Provider (LLM_FALLBACK_PROVIDER env)
        └── Falls back to rule-engine diagnosis if both fail
```

---

## 12. Provider Selection

```python
# .env
LLM_PROVIDER=openai
LLM_FALLBACK_PROVIDER=claude
OPENAI_MODEL=gpt-4o
CLAUDE_MODEL=claude-sonnet-4-6
GEMINI_MODEL=gemini-2.0-flash
```

---

## 13. Evidence Sanitization

Before sending to LLM, evidence is:
1. **Serialized** from typed objects to JSON
2. **Filtered**: Oracle credentials, connection strings, PII → removed
3. **Summarized**: Large objects (SQL plans) → summary only
4. **Truncated**: Source code → only relevant fragment (±20 lines around matching line)

---

## 14. Fail-Safe Behavior

| Failure Mode | Response |
|---|---|
| LLM timeout (> 30s) | Try fallback provider |
| Both providers fail | Return rule-engine based diagnosis (lower confidence) |
| JSON parse error | Retry with stricter JSON formatting instruction |
| Invalid schema | Return error with partial results |

**The system always returns some diagnosis.** Even if LLM is completely unavailable, the Hypothesis Engine provides a fallback diagnosis based on deterministic scoring.

---

## 15. Prompt Design Principles

1. **Low temperature** (0.1): Consistent, deterministic output
2. **JSON mode enabled**: Where supported (OpenAI), forces JSON output
3. **Evidence-first instructions**: LLM explicitly told to base conclusions on evidence, not general knowledge
4. **No-execute clause**: Explicitly instructed that recommendations are for human review only
5. **Confidence calibration**: Clear guidance on what different confidence levels mean

---


<!-- ======================================================
     FILE: docs/03-technical/correlation-engine-design.md
     ====================================================== -->

# Correlation Engine Design
# Thiết Kế Correlation Engine

**Project:** `db-copilot` — `correlation/`  
**Phiên bản / Version:** 0.1  
**Ngày / Date:** 2026-09-08

---

# 🇻🇳 PHẦN TIẾNG VIỆT

---

## 1. Tổng Quan

Correlation Engine là layer phân tích evidence để:

1. **Phát hiện anomaly** (Detection Rules) — deterministic, không dùng AI
2. **Liên kết evidence** (Evidence Graph) — build graph quan hệ giữa entities
3. **Tạo Incident** — khi phát hiện vấn đề thực sự
4. **Cung cấp hypothesis** (Hypothesis Engine) — xếp hạng các nguyên nhân có thể

### Nguyên tắc quan trọng

> **Detection Rules chạy trước AI.** AI chỉ được gọi sau khi đã có đủ evidence từ deterministic rules.

---

## 2. Component Overview

```
db-copilot/correlation/
│
├── rules/
│   ├── sql_rules.py      # SQL regression, plan change, cardinality
│   ├── session_rules.py  # Blocking sessions, long running
│   └── storage_rules.py  # Tablespace threshold, temp, undo
│
├── graph.py              # Evidence graph builder
└── engine.py             # Orchestrator: chạy rules → incidents → hypotheses
```

---

## 3. Detection Rules (Deterministic)

### 3.1 SQL Regression Rule

```python
# src/db_copilot/correlation/rules/sql_rules.py

class SqlRegressionRule:
    """
    Phát hiện SQL có elapsed time tăng so với historical baseline.

    Thresholds:
    - multiplier >= 3.0  → Trigger (configurable)
    - sample_count >= 5  → Baseline reliable

    Baseline: 7-day rolling window, same hour_of_day + day_of_week bucket.
    """

    async def evaluate(
        self,
        metric: SqlMetric,
        baseline: SqlBaseline | None
    ) -> Incident | None:

        if baseline is None or not baseline.is_reliable:
            return None

        ratio = metric.elapsed_time_ms / baseline.mean_elapsed_ms

        if ratio < settings.sql_regression_multiplier:
            return None

        # Kiểm tra plan change từ PostgreSQL metrics history (KHÔNG gọi MCP trực tiếp trong rule)
        plan_changed = False
        previous_metric = await self.repo.get_previous_sql_metric(metric.sql_id)
        if previous_metric and previous_metric.plan_hash_value != metric.plan_hash_value:
            plan_changed = True

        evidence_list = [
            Evidence(
                type=EvidenceType.SQL_REGRESSION,
                entity_type="SQL",
                entity_id=metric.sql_id,
                severity=self._severity(ratio),
                data={
                    "sql_id": metric.sql_id,
                    "current_elapsed_ms": metric.elapsed_time_ms,
                    "baseline_avg_ms": baseline.mean_elapsed_ms,
                    "ratio": ratio,
                    "plan_hash_value": metric.plan_hash_value,
                }
            )
        ]

        if plan_changed and previous_metric:
            evidence_list.append(Evidence(
                type=EvidenceType.SQL_PLAN_CHANGE,
                entity_type="SQL",
                entity_id=metric.sql_id,
                severity=Severity.HIGH,
                data={
                    "old_plan": previous_metric.plan_hash_value,
                    "new_plan": metric.plan_hash_value,
                    "previous_timestamp": str(previous_metric.timestamp),
                }
            ))

        return Incident(
            severity=Severity.HIGH if ratio >= 5 else Severity.MEDIUM,
            category=IncidentCategory.SQL_REGRESSION,
            title=f"SQL Regression: {metric.sql_id} ({ratio:.1f}x slower)",
            description=f"SQL {metric.sql_id} elapsed time increased {ratio:.1f}x vs baseline",
            evidence=evidence_list
        )

    def _severity(self, ratio: float) -> Severity:
        if ratio >= 10: return Severity.CRITICAL
        if ratio >= 5:  return Severity.HIGH
        return Severity.MEDIUM
```

### 3.2 Blocking Session Rule

```python
class BlockingSessionRule:
    """
    Phát hiện blocking session chains.
    Severity phân tầng theo thời gian chờ và số session bị block (tránh Alert Fatigue):
    - Wait < 30s VÀ <= 2 sessions  → MEDIUM
    - Wait 30s-300s HOẶC 3-9 sessions → HIGH
    - Wait > 300s HOẶC >= 10 sessions → CRITICAL
    """

    async def evaluate(self, blocking_data: dict) -> Incident | None:
        total_blocked = blocking_data.get("total_blocked", 0)
        max_wait = blocking_data.get("max_wait_seconds", 0)

        if total_blocked == 0:
            return None

        # Severity scaling
        if max_wait > 300 or total_blocked >= 10:
            sev = Severity.CRITICAL
        elif max_wait >= 30 or total_blocked >= 3:
            sev = Severity.HIGH
        else:
            sev = Severity.MEDIUM

        return Incident(
            severity=sev,
            category=IncidentCategory.BLOCKING,
            title=f"Blocking detected: {total_blocked} sessions blocked",
            description=f"Max wait: {max_wait}s (Severity: {sev.value})",
            evidence=[Evidence(
                type=EvidenceType.BLOCKING_SESSION,
                severity=sev,
                data=blocking_data
            )]
        )
```

### 3.3 Tablespace Threshold Rule

```python
class TablespaceThresholdRule:
    """
    WARNING: > 80% used
    CRITICAL: > 90% used
    Include: growth trend (bytes/day), estimated_days_until_full
    """

    async def evaluate(self, usage_list: list[dict]) -> list[Incident]:
        incidents = []

        for ts in usage_list:
            if ts["used_pct"] >= settings.tablespace_critical_threshold:
                sev = Severity.CRITICAL
            elif ts["used_pct"] >= settings.tablespace_warning_threshold:
                sev = Severity.MEDIUM
            else:
                continue

            # Tính growth trend từ 7 ngày lịch sử trong PostgreSQL
            trend = await self._calculate_growth_trend(ts["name"])

            incidents.append(Incident(
                severity=sev,
                category=IncidentCategory.TABLESPACE,
                title=f"Tablespace {ts['name']}: {ts['used_pct']:.1f}% used",
                evidence=[Evidence(
                    type=EvidenceType.TABLESPACE_THRESHOLD,
                    severity=sev,
                    data={
                        "tablespace_name": ts["name"],
                        "used_pct": ts["used_pct"],
                        "used_bytes": ts["used_bytes"],
                        "free_bytes": ts["free_bytes"],
                        "growth_bytes_per_day": trend.bytes_per_day,
                        "estimated_days_until_full": trend.days_until_full
                    }
                )]
            ))

        return incidents
```

### 3.4 Job Failure Rule

```python
class JobFailureRule:
    """
    Phát hiện scheduler jobs thất bại trong 24h qua.
    """

    async def evaluate(self, failed_jobs: list[dict]) -> list[Incident]:
        incidents = []

        for job in failed_jobs:
            incidents.append(Incident(
                severity=Severity.HIGH,
                category=IncidentCategory.JOB_FAILURE,
                title=f"Job Failed: {job['job_name']}",
                evidence=[Evidence(
                    type=EvidenceType.JOB_FAILURE,
                    severity=Severity.HIGH,
                    data={
                        "job_name": job["job_name"],
                        "error_message": job["error_message"],
                        "run_duration": job["run_duration"],
                        "last_successful_run": job["last_successful_run"]
                    }
                )]
            ))

        return incidents
```

### 3.5 Long Running Session Rule

```python
class LongRunningSessionRule:
    """
    Phát hiện session chạy lâu vượt quá ngưỡng cho phép (mặc định > 1800s / 30 phút).
    Severity:
    - >= 7200s (2h) → CRITICAL
    - >= 3600s (1h) → HIGH
    - >= 1800s (30m) → MEDIUM
    """

    async def evaluate(self, sessions: list[dict]) -> list[Incident]:
        incidents = []
        threshold_sec = settings.long_running_threshold_sec

        for s in sessions:
            elapsed_sec = s.get("elapsed_seconds", 0)
            if elapsed_sec < threshold_sec:
                continue

            if elapsed_sec >= 7200:
                sev = Severity.CRITICAL
            elif elapsed_sec >= 3600:
                sev = Severity.HIGH
            else:
                sev = Severity.MEDIUM

            minutes = elapsed_sec // 60
            incidents.append(Incident(
                severity=sev,
                category=IncidentCategory.LONG_RUNNING_SESSION,
                title=f"Long Running Session: SID {s.get('sid')} ({minutes}m)",
                description=f"Session SID {s.get('sid')} active for {minutes}m running SQL {s.get('sql_id')}",
                evidence=[Evidence(
                    type=EvidenceType.LONG_RUNNING_SESSION,
                    severity=sev,
                    data=s
                )]
            ))

        return incidents
```

### 3.6 Invalid Object Rule

```python
class InvalidObjectRule:
    """
    Phát hiện schema objects chuyển sang trạng thái INVALID.
    Severity:
    - PACKAGE BODY, PROCEDURE, FUNCTION, TRIGGER quan trọng → MEDIUM / HIGH
    - Các đối tượng khác → LOW
    """

    async def evaluate(self, invalid_objects: list[dict]) -> list[Incident]:
        incidents = []

        for obj in invalid_objects:
            obj_type = obj.get("object_type", "UNKNOWN")
            sev = Severity.HIGH if obj_type in ("PACKAGE BODY", "PROCEDURE", "TRIGGER") else Severity.LOW

            incidents.append(Incident(
                severity=sev,
                category=IncidentCategory.INVALID_OBJECT,
                title=f"Invalid Object: {obj.get('object_name')} ({obj_type})",
                description=f"Object {obj.get('object_name')} owned by {obj.get('owner')} is INVALID",
                evidence=[Evidence(
                    type=EvidenceType.INVALID_OBJECT,
                    severity=sev,
                    data=obj
                )]
            ))

        return incidents
```

---

## 4. Evidence Graph & Relationship Modeling

> [!NOTE]
> **Phạm vi áp dụng (Scope Clarity):**
> Trong chu kỳ đánh giá Anomaly định kỳ (MVP Correlation Cycle), hệ thống sử dụng **flat evidence list** để tạo Incident và xếp hạng Hypothesis nhằm đảm bảo hiệu năng và tính đơn giản.
> `EvidenceGraph` cùng thuật toán duyệt đồ thị BFS (`get_causal_chain`, `get_most_impactful_entity`) được sử dụng trong **Investigation Engine (Phase 3)** khi người dùng yêu cầu điều tra chuyên sâu đa tầng (Multi-hop Causal Tracing: Procedure → SQL → Plan → Table → Statistics).

```python
# src/db_copilot/correlation/graph.py

from dataclasses import dataclass, field
from typing import Optional

@dataclass
class GraphNode:
    entity_type: str    # "SQL", "PROCEDURE", "TABLE", "SESSION"
    entity_id: str
    evidence: list[Evidence] = field(default_factory=list)

@dataclass
class GraphEdge:
    source: GraphNode
    target: GraphNode
    relationship: str   # "executes", "uses", "accesses", "blocks", "depends_on"
    weight: float       # 0.0 – 1.0 (temporal proximity + causal likelihood)

class EvidenceGraph:
    """
    Build directed evidence graph từ evidence collection.
    Chuyên biệt phục vụ Investigation Engine để tìm causal chain đa tầng.
    """

    def __init__(self):
        self.nodes: dict[str, GraphNode] = {}
        self.edges: list[GraphEdge] = []

    def add_evidence(self, evidence: Evidence) -> GraphNode:
        key = f"{evidence.entity_type}:{evidence.entity_id}"
        if key not in self.nodes:
            self.nodes[key] = GraphNode(evidence.entity_type, evidence.entity_id)
        self.nodes[key].evidence.append(evidence)
        return self.nodes[key]

    def add_relationship(
        self,
        source_type: str, source_id: str,
        relationship: str,
        target_type: str, target_id: str,
        weight: float = 0.5
    ):
        source_key = f"{source_type}:{source_id}"
        target_key = f"{target_type}:{target_id}"

        source = self.nodes.get(source_key)
        target = self.nodes.get(target_key)

        if source and target:
            self.edges.append(GraphEdge(source, target, relationship, weight))

    def get_causal_chain(self, root_entity: str) -> list[GraphEdge]:
        """BFS từ root entity, trả về ordered causal chain."""
        visited = set()
        queue = [root_entity]
        chain = []

        while queue:
            curr = queue.pop(0)
            if curr in visited:
                continue
            visited.add(curr)

            for edge in self.edges:
                curr_key = f"{edge.source.entity_type}:{edge.source.entity_id}"
                if curr_key == curr:
                    target_key = f"{edge.target.entity_type}:{edge.target.entity_id}"
                    if target_key not in visited:
                        chain.append(edge)
                        queue.append(target_key)
        return chain

    def get_most_impactful_entity(self) -> GraphNode | None:
        """Entity có nhiều evidence nhất với highest severity."""
        if not self.nodes:
            return None
        return max(
            self.nodes.values(),
            key=lambda n: (
                max((e.severity.value for e in n.evidence), default="LOW"),
                len(n.evidence)
            )
        )
```

### 4.1 Ví dụ Evidence Graph trong Investigation Engine

```
PROC_SETTLEMENT (PROCEDURE)
      │
      │ executes [via ASH MODULE]
      ▼
SQL_ID 8f3abc (SQL)
      │
      │ plan_changed [DBA_HIST_SQLSTAT]
      ▼
PLAN 98237412 (PLAN)
      │
      │ accesses [from plan operations]
      ▼
ACCOUNT_POSITION (TABLE)
      │
      │ stale_statistics [DBA_TAB_STATISTICS]
      ▼
LAST_ANALYZED: 18 days ago (STATISTICS)
```

---

## 5. Hypothesis Engine

```python
# src/db_copilot/correlation/engine.py

HYPOTHESIS_DEFINITIONS = [
    {
        "name": "Statistics Issue",
        "required_evidence": [EvidenceType.STALE_STATISTICS],
        "supporting_evidence": [
            EvidenceType.CARDINALITY_MISMATCH,
            EvidenceType.SQL_REGRESSION,
            EvidenceType.HIGH_PHYSICAL_READS
        ],
        "base_confidence": 0.70,
        "confidence_boost_per_supporting": 0.08,
        "contradicted_by": [EvidenceType.BLOCKING_SESSION]
    },
    {
        "name": "Execution Plan Regression",
        "required_evidence": [EvidenceType.SQL_PLAN_CHANGE],
        "supporting_evidence": [
            EvidenceType.SQL_REGRESSION,
            EvidenceType.HIGH_PHYSICAL_READS,
            EvidenceType.CARDINALITY_MISMATCH
        ],
        "base_confidence": 0.65,
        "confidence_boost_per_supporting": 0.08,
        "contradicted_by": []
    },
    {
        "name": "Blocking / Concurrency Issue",
        "required_evidence": [EvidenceType.BLOCKING_SESSION],
        "supporting_evidence": [EvidenceType.LONG_RUNNING_SESSION],
        "base_confidence": 0.90,
        "confidence_boost_per_supporting": 0.05,
        "contradicted_by": []
    },
    {
        "name": "IO Contention",
        "required_evidence": [EvidenceType.WAIT_EVENT_ANOMALY],  # db file sequential read
        "supporting_evidence": [EvidenceType.HIGH_PHYSICAL_READS],
        "base_confidence": 0.55,
        "confidence_boost_per_supporting": 0.10,
        "contradicted_by": []
    },
    {
        "name": "Data Volume Increase",
        # [CE-04]: Phải có CARDINALITY_MISMATCH thì mới kích hoạt hypothesis này, tránh noise
        "required_evidence": [EvidenceType.CARDINALITY_MISMATCH],
        "supporting_evidence": [
            EvidenceType.HIGH_PHYSICAL_READS,
        ],
        "base_confidence": 0.40,
        "confidence_boost_per_supporting": 0.12,
        "contradicted_by": [EvidenceType.SQL_PLAN_CHANGE, EvidenceType.STALE_STATISTICS]
    }
]

class HypothesisEngine:
    def rank_hypotheses(self, evidence_list: list[Evidence]) -> list[Hypothesis]:
        """
        Với mỗi hypothesis definition:
        1. Kiểm tra required_evidence có đủ không (nếu thiếu -> skip hoàn toàn)
        2. Đếm supporting_evidence
        3. Kiểm tra contradicting_evidence
        4. Tính confidence score
        5. Sort by confidence DESC
        """
        results = []
        evidence_types = {e.type for e in evidence_list}

        for defn in HYPOTHESIS_DEFINITIONS:
            # Check required
            required = set(defn["required_evidence"])
            if required and not required.issubset(evidence_types):
                # Có required evidence không tồn tại → skip
                continue

            # Count supporting
            supporting_count = sum(
                1 for et in defn["supporting_evidence"]
                if et in evidence_types
            )

            # Check contradicting
            is_contradicted = any(
                et in evidence_types
                for et in defn.get("contradicted_by", [])
            )

            # Calculate confidence
            confidence = defn["base_confidence"]
            confidence += supporting_count * defn["confidence_boost_per_supporting"]
            if is_contradicted:
                confidence *= 0.4  # Giảm mạnh confidence

            confidence = min(0.98, confidence)  # Cap at 98%

            results.append(Hypothesis(
                name=defn["name"],
                confidence=confidence,
                supporting_evidence=[
                    e for e in evidence_list if e.type in defn["supporting_evidence"]
                ],
                contradicting_evidence=[
                    e for e in evidence_list if e.type in defn.get("contradicted_by", [])
                ]
            ))

        return sorted(results, key=lambda h: h.confidence, reverse=True)
```

---

## 6. Correlation Engine Orchestrator & Incident Deduplication

### 6.1 Chiến lược Deduplication (Chống bão Alert)
- **Vấn đề [CE-05]:** Khi SQL bị chậm kéo dài 30 phút, nếu mỗi cycle 5 phút sinh 1 incident mới thì DBA sẽ nhận 6 incidents duplicate rác.
- **Giải pháp:**
  - Kiểm tra xem trong database đã có Incident nào cùng `(database_id, category, entity_id)` đang ở trạng thái `OPEN` hoặc `INVESTIGATING` trong vòng **60 phút** vừa qua không.
  - Nếu đã tồn tại: Cập nhật incident cũ (`last_seen_at = now()`, cập nhật severity nếu cao hơn, append evidence mới vào incident hiện có).
  - Nếu chưa có: Tạo mới incident.
  - Tầng PostgreSQL hỗ trợ index: `CREATE INDEX idx_incidents_dedup ON incidents (database_id, category, status, detected_at);`

```python
# src/db_copilot/correlation/engine.py

class CorrelationEngine:
    """
    Orchestrator chính:
    1. Chạy tất cả detection rules sau mỗi collection cycle
    2. Gom flat evidence list
    3. Generate hypotheses
    4. Deduplicate và Lưu/Cập nhật incidents trong PostgreSQL
    """

    def __init__(self, incident_repo: IncidentRepository):
        self.incident_repo = incident_repo
        self.rules = [
            SqlRegressionRule(),
            BlockingSessionRule(),
            TablespaceThresholdRule(),
            JobFailureRule(),
            LongRunningSessionRule(),
            InvalidObjectRule()
        ]
        self.hypothesis_engine = HypothesisEngine()

    async def evaluate_all(self, collected_data: dict, context: dict):
        all_incidents = []

        # 1. Chạy tất cả detection rules trên dữ liệu đã thu thập
        for rule in self.rules:
            incidents = await rule.evaluate(collected_data.get(rule.name), context)
            if isinstance(incidents, list):
                all_incidents.extend(incidents)
            elif incidents:
                all_incidents.append(incidents)

        # 2. Deduplicate và lưu trữ Incident
        for incident in all_incidents:
            # Generate hypotheses trên flat evidence list
            incident.hypotheses = self.hypothesis_engine.rank_hypotheses(
                incident.evidence
            )

            # Deduplication: kiểm tra incident tương tự đang OPEN trong 60 phút
            existing = await self.incident_repo.find_open_incident(
                database_id=incident.database_id,
                category=incident.category,
                entity_id=incident.evidence[0].entity_id if incident.evidence else None,
                within_minutes=60
            )

            if existing:
                # Merge evidence và nâng severity nếu cần
                await self.incident_repo.append_evidence(existing.id, incident.evidence)
                if incident.severity > existing.severity:
                    await self.incident_repo.update_severity(existing.id, incident.severity)
            else:
                await self.incident_repo.create_incident(incident)

    async def evaluate_for_investigation(
        self,
        evidence_list: list[Evidence]
    ) -> list[Hypothesis]:
        """
        Được gọi bởi Investigation Engine để generate hypotheses
        cho một investigation cụ thể.
        """
        return self.hypothesis_engine.rank_hypotheses(evidence_list)
```

---

---

# 🇬🇧 ENGLISH SECTION

---

## 7. Overview

Correlation Engine is the layer that analyzes evidence to:

1. **Detect anomalies** (Detection Rules) — deterministic, no AI
2. **Link evidence** (Evidence Graph) — build relationship graph between entities
3. **Create Incidents** — when real issues are detected
4. **Generate Hypotheses** — rank possible root causes

### Core Principle

> **Detection Rules run before AI.** AI is only called after deterministic rules have collected sufficient evidence.

---

## 8. Detection Rules Summary

| Rule | Trigger | Severity | Extra Evidence Collected | Architecture Note |
|---|---|---|---|---|
| `SqlRegressionRule` | `elapsed > baseline × 3.0` | MEDIUM–CRITICAL | `plan_hash_value` change | Compare with historical metrics in DB; **no MCP call inside rule** |
| `BlockingSessionRule` | Total blocked > 0 | MEDIUM–CRITICAL | Full blocking tree | Scaled by wait time & blocked count to prevent alert fatigue |
| `TablespaceThresholdRule` | usage > 80% or > 90% | MEDIUM–CRITICAL | Growth trend | From 7-day snapshot metrics |
| `JobFailureRule` | Any failed job in 24h | HIGH | Error message, last success | Filtered by run history |
| `LongRunningSessionRule` | Active session > 1800s | MEDIUM–CRITICAL | Session context | Scaled: 30m (MEDIUM), 1h (HIGH), 2h (CRITICAL) |
| `InvalidObjectRule` | Any INVALID object | LOW–HIGH | Object metadata | HIGH for packages/procedures/triggers |

---

## 9. Evidence Graph & Investigation Engine

> [!NOTE]
> **Scope & MVP Execution:**
> In the scheduled correlation cycle (MVP), a **flat evidence list** is processed to create Incidents and rank Hypotheses with high speed and deterministic guarantees.
> The `EvidenceGraph` and its BFS causal chain algorithms (`get_causal_chain`, `get_most_impactful_entity`) are dedicated to the **Investigation Engine (Phase 3)** for deep interactive multi-hop root-cause tracing.

---

## 10. Hypothesis Engine

Scores hypotheses based on:
- **Required evidence**: Must be present in the evidence list (if missing → skip hypothesis entirely)
- **Supporting evidence**: Each adds `confidence_boost_per_supporting`
- **Contradicting evidence**: Multiplies confidence by 0.4
- **Deduplication & Noise Filter**: All hypotheses require relevant evidence to trigger (e.g. Data Volume Increase requires `cardinality_mismatch`).

Output: Sorted list of hypotheses with confidence scores (capped at 98%).

---

## 11. Hypothesis Definitions

| Hypothesis | Required Evidence | Primary Supporting Evidence | Contradicted By |
|---|---|---|---|
| Statistics Issue | `stale_statistics` | `cardinality_mismatch`, `sql_regression` | `blocking_session` |
| Execution Plan Regression | `sql_plan_change` | `sql_regression`, `high_physical_reads` | _(none)_ |
| Blocking / Concurrency | `blocking_session` | `long_running_session` | _(none)_ |
| IO Contention | `wait_event_anomaly` | `high_physical_reads` | _(none)_ |
| Data Volume Increase | `cardinality_mismatch` | `high_physical_reads` | `sql_plan_change`, `stale_statistics` |

---

## 12. Incident Deduplication Strategy

To prevent alert fatigue and notification storms when an issue persists over multiple 5-minute cycles:
1. When a rule triggers an incident for an entity, query the repository for an existing `OPEN` or `INVESTIGATING` incident matching `(database_id, category, entity_id)` within a **60-minute deduplication window**.
2. If an open incident exists:
   - Update `last_seen_at = now()`.
   - Upgrade `severity` if the new occurrence is more severe.
   - Append new evidence to the existing incident's evidence collection.
3. If no open incident exists: Create a new incident.
4. Database level: Deduplication index on `(database_id, category, status, detected_at)`.

---


<!-- ======================================================
     FILE: docs/03-technical/evidence-engine-design.md
     ====================================================== -->

# Evidence Engine Design
# Thiết Kế Evidence Engine

**Project:** `db-copilot` — `evidence/`  
**Phiên bản / Version:** 0.1  
**Ngày / Date:** 2026-09-08

---

# 🇻🇳 PHẦN TIẾNG VIỆT

---

## 1. Tổng Quan

Evidence Engine là layer trong `db-copilot` chịu trách nhiệm:

1. **Thu thập** (Collect): Gọi oracle-mcp-server định kỳ để lấy dữ liệu
2. **Chuẩn hóa** (Normalize): Convert raw data thành Evidence objects có type rõ ràng
3. **Lưu trữ** (Store): Persist vào PostgreSQL Evidence Store
4. **Cung cấp** (Serve): Cung cấp evidence cho Correlation Engine và Investigation Engine

Evidence Engine **không phân tích** và **không quyết định** — đó là nhiệm vụ của Correlation Engine và AI Service.

---

## 2. Component Overview

```
db-copilot/evidence/
│
├── collectors/
│   ├── sql_collector.py      # Thu thập SQL metrics mỗi 5 phút
│   ├── session_collector.py  # Thu thập session data
│   └── storage_collector.py  # Thu thập storage metrics
│
├── normalizers/
│   └── evidence_normalizer.py # Raw data → Evidence objects
│
├── builders/
│   └── evidence_builder.py   # Build EvidencePackage cho investigation
│
└── repository.py             # PostgreSQL read/write
```

---

## 3. Evidence Types

| Type | Nguồn MCP Tool | Mô tả |
|---|---|---|
| `sql_regression` | `get_sql_statistics` | Elapsed time tăng so với baseline |
| `sql_plan_change` | `get_sql_plan_history` | Plan hash thay đổi |
| `cardinality_mismatch` | `get_sql_plan` | Estimated rows ≠ actual rows |
| `high_physical_reads` | `get_sql_statistics` | Disk reads tăng đột biến |
| `stale_statistics` | `get_object_metadata` | Statistics quá cũ (> N ngày) |
| `blocking_session` | `get_blocking_sessions` | Có session bị block |
| `long_running_session` | `get_long_running_sessions` | Session chạy quá lâu |
| `tablespace_threshold` | `get_tablespace_usage` | Tablespace vượt ngưỡng % |
| `temp_usage_high` | `get_temp_usage` | TEMP usage cao |
| `job_failure` | `get_failed_jobs` | Scheduler job thất bại |
| `invalid_object` | `get_invalid_objects` | Object bị INVALID |
| `wait_event_anomaly` | `get_sql_wait_events` | Wait event bất thường |

---

## 4. Evidence Schema

```python
# src/db_copilot/domain/models/evidence.py

from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from uuid import UUID

class EvidenceType(str, Enum):
    SQL_REGRESSION = "sql_regression"
    SQL_PLAN_CHANGE = "sql_plan_change"
    CARDINALITY_MISMATCH = "cardinality_mismatch"
    HIGH_PHYSICAL_READS = "high_physical_reads"
    STALE_STATISTICS = "stale_statistics"
    BLOCKING_SESSION = "blocking_session"
    LONG_RUNNING_SESSION = "long_running_session"
    TABLESPACE_THRESHOLD = "tablespace_threshold"
    JOB_FAILURE = "job_failure"
    INVALID_OBJECT = "invalid_object"
    WAIT_EVENT_ANOMALY = "wait_event_anomaly"

class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

@dataclass
class Evidence:
    id: UUID
    incident_id: UUID | None        # None nếu chưa gán incident
    type: EvidenceType
    source: str                      # Oracle view/tool name
    timestamp: datetime
    entity_type: str                 # "SQL", "SESSION", "TABLE", "PROCEDURE", "JOB"
    entity_id: str                   # sql_id, session_id, object_name
    severity: Severity
    data: dict                       # Raw evidence payload (JSONB in DB)
    supports_hypothesis: list[str] = field(default_factory=list)
    contradicts_hypothesis: list[str] = field(default_factory=list)
```

---

## 5. Collection Flow

### 5.1 APScheduler Setup

```python
# src/db_copilot/api/app.py (lifespan)

from apscheduler.schedulers.asyncio import AsyncIOScheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = AsyncIOScheduler()

    # Evidence collection — mỗi 5 phút
    scheduler.add_job(SqlCollector().collect, "interval", minutes=5, id="sql_collector")
    scheduler.add_job(SessionCollector().collect, "interval", minutes=5, id="session_collector")
    scheduler.add_job(StorageCollector().collect, "interval", minutes=5, id="storage_collector")

    # Baseline recalculation — mỗi giờ
    scheduler.add_job(BaselineEngine().recalculate, "interval", hours=1, id="baseline")

    # Daily report — 6:00 AM
    scheduler.add_job(ReportService().generate_daily, "cron", hour=6, id="daily_report")

    scheduler.start()
    yield
    scheduler.shutdown()
```

### 5.2 SQL Collector

```python
# src/db_copilot/evidence/collectors/sql_collector.py

class SqlCollector:
    def __init__(self, mcp_client: OracleMcpClient, repo: EvidenceRepository):
        self.mcp = mcp_client
        self.repo = repo

    async def collect(self):
        """
        Chu kỳ: mỗi 5 phút
        1. Gọi get_top_sql đa chiều (elapsed_time, cpu_time, disk_reads) để phát hiện
           cả latency spikes, CPU hogs và IO hogs ([EE-04]).
        2. Deduplicate theo sql_id và normalize thành SqlMetric objects.
        3. Lưu snapshot và metrics vào PostgreSQL (ON CONFLICT explicit key).
        4. Trigger correlation detection rules.
        """
        metrics_by_sql_id: dict[str, SqlMetric] = {}

        # Thu thập theo 3 chiều đo lường cốt lõi ([EE-04])
        for sort_metric in ["elapsed_time", "cpu_time", "disk_reads"]:
            raw = await self.mcp.call_tool("get_top_sql", {
                "metric": sort_metric,
                "limit": 50,
                "hours": 1
            })
            for item in raw:
                metric = SqlMetric.from_mcp_response(item)
                # Giữ lại hoặc merge metric mới nhất
                metrics_by_sql_id[metric.sql_id] = metric

        metrics = list(metrics_by_sql_id.values())

        async with self.repo.session() as session:
            snapshot = await session.create_snapshot()
            for metric in metrics:
                await session.upsert_sql_metric(metric, snapshot_id=snapshot.id)

        # Trigger detection rules
        await CorrelationEngine().evaluate_sql_metrics(metrics)
```

### 5.3 Session Collector

```python
class SessionCollector:
    async def collect(self):
        """
        Thu thập:
        - Active sessions (get_active_sessions)
        - Blocking chains (get_blocking_sessions)
        - Long running sessions (get_long_running_sessions)
        """
        blocking = await self.mcp.call_tool("get_blocking_sessions", {})
        if blocking.get("total_blocked", 0) > 0:
            # Immediate: tạo evidence với đầy đủ required fields ([EE-01])
            evidence = Evidence(
                id=uuid4(),
                incident_id=None,
                type=EvidenceType.BLOCKING_SESSION,
                source="V$SESSION / get_blocking_sessions",
                timestamp=datetime.utcnow(),
                entity_type="SESSION",
                entity_id=str(blocking.get("root_blocker_sid", "UNKNOWN")),
                severity=Severity.HIGH,
                data=blocking
            )
            await CorrelationEngine().raise_incident(evidence)
```

---

## 6. Evidence Normalization

```python
# src/db_copilot/evidence/normalizers/evidence_normalizer.py

from uuid import uuid4
from datetime import datetime

class EvidenceNormalizer:
    """
    Convert raw MCP tool response thành typed Evidence objects.
    Áp dụng business logic (thresholds, severity mapping).
    """

    def normalize_sql_regression(
        self,
        current: SqlMetric,
        baseline: SqlBaseline,
        multiplier: float
    ) -> Evidence | None:
        if not baseline.is_reliable:
            return None  # Không đủ data

        ratio = current.elapsed_time_ms / baseline.mean_elapsed_ms
        if ratio < multiplier:
            return None  # Không regression

        # Cung cấp đầy đủ required fields để tránh TypeError/Runtime Crash ([EE-01])
        return Evidence(
            id=uuid4(),
            incident_id=None,
            type=EvidenceType.SQL_REGRESSION,
            source="sql_metrics + sql_baselines",
            timestamp=datetime.utcnow(),
            entity_type="SQL",
            entity_id=current.sql_id,
            severity=self._severity_from_ratio(ratio),
            data={
                "sql_id": current.sql_id,
                "current_elapsed_ms": current.elapsed_time_ms,
                "baseline_avg_ms": baseline.mean_elapsed_ms,
                "regression_ratio": ratio,
                "baseline_sample_count": baseline.sample_count
            }
        )

    def _severity_from_ratio(self, ratio: float) -> Severity:
        if ratio >= 10:
            return Severity.CRITICAL
        elif ratio >= 5:
            return Severity.HIGH
        elif ratio >= 3:
            return Severity.MEDIUM
        return Severity.LOW
```

---

## 7. Evidence Repository (PostgreSQL)

```python
# src/db_copilot/evidence/repository.py

class EvidenceRepository:
    async def upsert_sql_metric(self, metric: SqlMetric, snapshot_id: UUID):
        # Bắt buộc khai báo explicit conflict target (database_id, sql_id, captured_at)
        # để tuân thủ cú pháp PostgreSQL ([EE-05])
        await db.execute(
            """
            INSERT INTO sql_metrics (database_id, snapshot_id, sql_id, captured_at,
                executions, elapsed_time_ms, cpu_time_ms, buffer_gets,
                disk_reads, rows_processed, plan_hash_value)
            VALUES (:database_id, :snapshot_id, :sql_id, :captured_at,
                :executions, :elapsed_time_ms, :cpu_time_ms, :buffer_gets,
                :disk_reads, :rows_processed, :plan_hash_value)
            ON CONFLICT (database_id, sql_id, captured_at) DO NOTHING
            """,
            metric.dict()
        )

    async def get_baseline(self, sql_id: str, hour: int, dow: int) -> SqlBaseline | None:
        row = await db.fetch_one(
            """
            SELECT * FROM sql_baselines
            WHERE database_id = :db_id AND sql_id = :sql_id
              AND hour_of_day = :hour AND day_of_week = :dow
            """,
            {"db_id": current_db_id, "sql_id": sql_id, "hour": hour, "dow": dow}
        )
        return SqlBaseline(**row) if row else None

    async def get_evidence_for_incident(self, incident_id: UUID) -> list[Evidence]:
        rows = await db.fetch_all(
            "SELECT * FROM evidence_items WHERE incident_id = :id",
            {"id": incident_id}
        )
        return [Evidence(**row) for row in rows]
```

---

## 8. Baseline Calculation

### 8.1 Vấn đề N+1 Query & Giải pháp Aggregation SQL ([EE-03])
Thay vì lặp 3 vòng lồng nhau `N SQL IDs × 24 giờ × 7 ngày = 16,800 DB queries/giờ` làm quá tải kết nối và I/O, hệ thống sử dụng **1 single SQL aggregation query** trực tiếp trong PostgreSQL kết hợp hàm window thống kê `PERCENTILE_CONT`:

```sql
-- Query tính toán toàn bộ baseline 7 ngày chỉ với 1 lượt quét ([EE-03])
SELECT 
    sql_id,
    EXTRACT(HOUR FROM captured_at)::INT AS hour_of_day,
    EXTRACT(DOW  FROM captured_at)::INT AS day_of_week,
    COUNT(*) AS sample_count,
    AVG(elapsed_time_ms)::DECIMAL(15,2) AS mean_elapsed_ms,
    COALESCE(STDDEV(elapsed_time_ms), 0)::DECIMAL(15,2) AS stddev_elapsed_ms,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY elapsed_time_ms)::DECIMAL(15,2) AS p50_elapsed_ms,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY elapsed_time_ms)::DECIMAL(15,2) AS p95_elapsed_ms
FROM sql_metrics
WHERE database_id = :db_id 
  AND captured_at >= NOW() - INTERVAL '7 days'
GROUP BY sql_id, hour_of_day, day_of_week
```

### 8.2 BaselineEngine Implementation

```python
# src/db_copilot/evidence/baseline.py

import statistics
from datetime import datetime
from db_copilot.domain.models.sql_metric import SqlMetric
from db_copilot.domain.models.baseline import SqlBaseline

class BaselineEngine:
    """
    Tính toán baseline hiệu năng SQL từ dữ liệu 7 ngày gần nhất.
    Chạy định kỳ mỗi 1 giờ.
    """

    def __init__(self, repo: EvidenceRepository):
        self.repo = repo

    def _remove_outliers(self, samples: list[SqlMetric]) -> list[SqlMetric]:
        """
        Loại bỏ các điểm đo dị biệt (> 2 độ lệch chuẩn stddev) ([EE-02]).
        Nếu mẫu < 3 thì giữ nguyên để tránh bias thống kê.
        """
        if len(samples) < 3:
            return samples
        mean = statistics.mean(s.elapsed_time_ms for s in samples)
        stddev = statistics.stdev(s.elapsed_time_ms for s in samples)
        return [s for s in samples if abs(s.elapsed_time_ms - mean) <= 2 * stddev]

    async def recalculate(self, database_id: str):
        """
        Thực thi tính toán baseline:
        - Sử dụng aggregation query duy nhất để lấy thống kê ([EE-03])
        - Batch upsert vào bảng sql_baselines với conflict target rõ ràng
        """
        rows = await self.repo.calculate_aggregated_baselines(database_id, days=7)

        baselines_to_upsert = []
        for r in rows:
            sample_count = r["sample_count"]
            is_reliable = sample_count >= 5

            baselines_to_upsert.append(SqlBaseline(
                database_id=database_id,
                sql_id=r["sql_id"],
                hour_of_day=r["hour_of_day"],
                day_of_week=r["day_of_week"],
                sample_count=sample_count,
                mean_elapsed_ms=float(r["mean_elapsed_ms"]),
                stddev_elapsed_ms=float(r["stddev_elapsed_ms"]),
                p50_elapsed_ms=float(r["p50_elapsed_ms"]),
                p95_elapsed_ms=float(r["p95_elapsed_ms"]),
                is_reliable=is_reliable,
                calculated_at=datetime.utcnow()
            ))

        await self.repo.batch_upsert_baselines(baselines_to_upsert)
```

---

---

# 🇬🇧 ENGLISH SECTION

---

## 9. Overview

Evidence Engine is the layer in `db-copilot` responsible for:

1. **Collect**: Call oracle-mcp-server periodically to fetch data
2. **Normalize**: Convert raw data into typed Evidence objects
3. **Store**: Persist to PostgreSQL Evidence Store
4. **Serve**: Provide evidence to Correlation Engine and Investigation Engine

The Evidence Engine does **not analyze** and does **not make decisions** — that is the job of Correlation Engine and AI Service.

---

## 10. Collection Schedule

| Collector | Interval | What it collects |
|---|---|---|
| `SqlCollector` | Every 5 min | Multi-dimensional Top SQL (elapsed_time, cpu_time, disk_reads) to detect latency spikes, CPU hogs, and IO hogs ([EE-04]) |
| `SessionCollector` | Every 5 min | Active sessions, blocking chains, long-running (full `id`, `timestamp` fields [EE-01]) |
| `StorageCollector` | Every 5 min | Tablespace usage, temp, undo |
| `BaselineEngine` | Every 1 hour | Recalculate SQL baselines using single PostgreSQL aggregation query ([EE-03]) |
| `ReportService` | Daily 6:00 AM | Generate daily health report |

---

## 11. Evidence Types

_(See Section 3 — same table)_

12 evidence types covering SQL performance, sessions, storage, jobs, and objects.

---

## 12. Normalization & Reliability Rules

- **Full Constructor Fields ([EE-01])**: All `Evidence` instantiations include required `id: UUID`, `incident_id: UUID | None`, and `timestamp: datetime` to avoid runtime TypeErrors.
- **SQL Regression**: `current_elapsed > baseline_mean × multiplier` (default 3.0)
- **Severity mapping**: ratio ≥ 10 → CRITICAL, ≥ 5 → HIGH, ≥ 3 → MEDIUM
- **Minimum baseline samples**: 5 required for reliable baseline
- **Outlier removal ([EE-02])**: `_remove_outliers()` filters samples > 2 standard deviations when sample size ≥ 3.
- **Single Aggregation Query ([EE-03])**: Eliminates 16,800 DB queries/hour by executing 1 analytical query using `PERCENTILE_CONT(0.5)` and `PERCENTILE_CONT(0.95)` with `GROUP BY sql_id, hour_of_day, day_of_week`.

---

## 13. Evidence Store

PostgreSQL tables: `snapshots`, `sql_metrics`, `sql_baselines`, `incidents`, `evidence_items`

Key design:
- `sql_metrics` enforces `UNIQUE(database_id, sql_id, captured_at)` to support explicit `ON CONFLICT (database_id, sql_id, captured_at) DO NOTHING` ([EE-05]).
- `sql_baselines` keyed on `(database_id, sql_id, hour_of_day, day_of_week)` — time-bucketed.
- `evidence_items.data` as JSONB — flexible schema per evidence type.
- Evidence is retained for 90 days (configurable).

---


<!-- ======================================================
     FILE: docs/03-technical/investigation-engine-design.md
     ====================================================== -->

# Investigation Engine Design
# Thiết Kế Investigation Engine

**Project:** `db-copilot` — `investigation/`  
**Phiên bản / Version:** 0.1  
**Ngày / Date:** 2026-09-08

---

# 🇻🇳 PHẦN TIẾNG VIỆT

---

## 1. Tổng Quan

Investigation Engine là "bộ não" của hệ thống — xử lý câu hỏi tự nhiên từ người dùng và tự động thực hiện toàn bộ quy trình điều tra.

**Input:** Câu hỏi tiếng Anh từ user (vd: _"Why was PROC_SETTLEMENT slow at 14:32?"_)

**Output:** Structured `InvestigationResult` với evidence, hypotheses và diagnosis.

---

## 2. Component Overview

```
db-copilot/investigation/
│
├── planner.py    # Intent Parser + Investigation Planner
├── executor.py   # Execute investigation steps via oracle-mcp-server
└── context.py    # Investigation state (kết quả từng step)
```

---

## 3. Full Pipeline

```
User Question
      │
      ▼
┌─────────────────┐
│  Intent Parser   │
│                  │
│ Parse: type,     │
│ entities,        │
│ time_range,      │
│ focus_metric     │
└────────┬─────────┘
         │
         ▼
┌─────────────────┐
│   Planner        │
│                  │
│ Intent →         │
│ Ordered steps    │
│ (with deps)      │
└────────┬─────────┘
         │
         ▼
┌─────────────────┐
│   Executor       │
│                  │
│ Execute steps    │
│ via MCP calls    │
│ Dynamic deps     │
│ Timeout: 10s/call│
│ Continue on err  │
└────────┬─────────┘
         │
         ▼
┌─────────────────┐
│  Evidence Build  │
│                  │
│ Raw results →    │
│ Evidence objects │
│ Evidence graph   │
└────────┬─────────┘
         │
         ▼
┌─────────────────┐
│  Hypothesis Eng. │
│                  │
│ Rank hypotheses  │
│ with confidence  │
└────────┬─────────┘
         │
         ▼
┌─────────────────┐
│  AI Diagnosis    │
│                  │
│ Evidence pkg →   │
│ LLM →            │
│ Structured JSON  │
└────────┬─────────┘
         │
         ▼
   InvestigationResult
```

---

## 4. Intent Types & Parsing

### 4.1 Supported Intent Types

| IntentType | Ví dụ câu hỏi | Plan xử lý |
|---|---|---|
| `PROCEDURE_SLOW` | "Why was PROC_SETTLEMENT slow at 14:32?" | 9 steps (có fallback dependency) |
| `SQL_SLOW` | "Why was SQL_ID 8f3abc slow yesterday?" | 8 steps (kèm statistics check) |
| `SQL_TOP` | "Which SQL is slowest today?" | 3 steps (top sql, statistics, plan) |
| `HEALTH_CHECK` | "What issues does the database have?" | 7 steps tổng quát |
| `BLOCKING_CHECK` | "Is there any blocking?" | 4 steps (blocking chains, sessions) |
| `TABLESPACE_CHECK` | "How is the storage looking?" | 3 steps (tablespaces, datafiles) |
| `JOB_CHECK` | "Did any jobs fail today?" | 3 steps (scheduler jobs, failed jobs) |
| `GENERAL_INCIDENT` | "What happened to the database last night?" | **[IE-07] Tự động map sang `HEALTH_CHECK` plan** |

### 4.2 Intent Schema

```python
@dataclass
class InvestigationIntent:
    type: IntentType
    entities: list[Entity]      # {"type": "PROCEDURE", "name": "PROC_SETTLEMENT"}
    time_range: TimeRange       # {begin: datetime, end: datetime}
    focus_metric: str | None    # "elapsed_time", "cpu", "io", "blocking"
    question_text: str          # Original question

@dataclass
class Entity:
    type: str    # "PROCEDURE", "SQL", "TABLE", "SESSION", "JOB"
    name: str
    owner: str | None = None

@dataclass
class TimeRange:
    begin: datetime
    end: datetime
    is_approximate: bool = True  # True nếu LLM suy ra từ "at 14:32"
```

### 4.3 Intent Parsing (LLM + Heuristic Regex Fallback)

```python
# src/db_copilot/investigation/planner.py
import re

class IntentParser:
    """
    Parse natural language thành InvestigationIntent.
    Ưu tiên LLM call nhỏ, tự động fallback sang Regex Patterns khi LLM offline/timeout.
    """

    SYSTEM_PROMPT = """
    You are an Oracle Database investigation assistant.
    Parse the user's question and extract: intent type, entities, time range, focus metric.
    Return JSON only. Current time: {current_time}
    """

    # [IE-06] Regex Fallback Patterns
    _PATTERNS = {
        IntentType.BLOCKING_CHECK: r"\b(block|blocking|lock|deadlock|contention)\b",
        IntentType.PROCEDURE_SLOW: r"\b(proc|procedure|package)\b.{0,30}\b(slow|latency|hang)\b",
        IntentType.SQL_SLOW: r"\b(sql_id|sql|query)\b.{0,30}\b(slow|regression)\b|\b[a-z0-9]{13}\b",
        IntentType.TABLESPACE_CHECK: r"\b(tablespace|disk|storage|full)\b",
        IntentType.JOB_CHECK: r"\b(job|scheduler|failed job)\b",
    }

    async def parse(self, question: str) -> InvestigationIntent:
        try:
            response = await asyncio.wait_for(
                self.llm.complete(
                    system=self.SYSTEM_PROMPT.format(current_time=datetime.utcnow()),
                    user=question,
                    response_format="json"
                ),
                timeout=5.0
            )
            data = json.loads(response)
            # [IE-07] Map GENERAL_INCIDENT sang HEALTH_CHECK
            if data.get("type") == "GENERAL_INCIDENT":
                data["type"] = "HEALTH_CHECK"
            return InvestigationIntent(**data)
        except Exception as err:
            logger.warning(f"LLM intent parsing failed ({err}), falling back to regex heuristic parser.")
            return self._regex_fallback(question)

    def _regex_fallback(self, question: str) -> InvestigationIntent:
        q = question.lower()
        for intent_type, pattern in self._PATTERNS.items():
            if re.search(pattern, q):
                return InvestigationIntent(
                    type=intent_type,
                    entities=[Entity(type="UNKNOWN", name="")],
                    time_range=TimeRange(begin=datetime.utcnow()-timedelta(hours=1), end=datetime.utcnow()),
                    focus_metric="general",
                    question_text=question
                )
        return InvestigationIntent(
            type=IntentType.HEALTH_CHECK,
            entities=[],
            time_range=TimeRange(begin=datetime.utcnow()-timedelta(hours=1), end=datetime.utcnow()),
            focus_metric="general",
            question_text=question
        )
```

---

## 5. Investigation Plans Per Intent Type

### 5.1 PROCEDURE_SLOW Plan

```python
def plan_procedure_slow(intent: InvestigationIntent) -> InvestigationPlan:
    proc_name = intent.entities[0].name
    t_begin = intent.time_range.begin - timedelta(minutes=15)
    t_end = intent.time_range.end + timedelta(minutes=15)

    return InvestigationPlan(steps=[
        Step("get_object_metadata",
             args={"name": proc_name, "type": "PROCEDURE", "owner": intent.entities[0].owner},
             produces="proc_metadata"),

        # [IE-02] Fallback: Lấy dependencies của procedure để cross-reference với ASH/V$SQL
        # Tránh trường hợp hệ thống bận không lọc được top_sql_id thực sự thuộc về procedure
        Step("get_object_dependencies",
             args={"name": proc_name, "type": "PROCEDURE", "owner": intent.entities[0].owner},
             produces="proc_dependencies",
             optional=True),

        Step("get_ash_sql_activity",
             args={"begin_time": t_begin, "end_time": t_end},
             produces="ash_activity"),

        Step("get_sql_statistics",
             args={"sql_id": DependsOn("ash_activity", extract="top_sql_id")},
             produces="sql_stats"),

        Step("get_sql_plan_history",
             args={"sql_id": DependsOn("sql_stats", extract="sql_id"), "days": 3},
             produces="plan_history"),

        Step("get_sql_wait_events",
             args={"sql_id": DependsOn("sql_stats", extract="sql_id"), "hours": 4},
             produces="wait_events"),

        # [IE-03] Sử dụng đúng tham số snapshot IDs đã được resolve
        Step("get_awr_sql_stats",
             args={
                 "sql_id": DependsOn("sql_stats", extract="sql_id"),
                 "begin_snap": DependsOn("ash_activity", extract="nearest_snapshot_begin"),
                 "end_snap": DependsOn("ash_activity", extract="nearest_snapshot_end")
             },
             produces="awr_stats"),

        Step("get_blocking_sessions",
             args={},
             produces="blocking"),

        Step("get_resource_usage",
             args={},
             produces="resource"),

        Step("get_object_source",
             args={"name": proc_name, "type": "PROCEDURE",
                   "owner": DependsOn("proc_metadata", extract="owner")},
             produces="source_code",
             optional=True),
    ])
```

### 5.2 SQL_SLOW Plan

```python
def plan_sql_slow(intent: InvestigationIntent) -> InvestigationPlan:
    sql_id = intent.entities[0].name  # SQL_ID

    return InvestigationPlan(steps=[
        Step("get_sql_statistics", args={"sql_id": sql_id}, produces="sql_stats"),
        Step("get_sql_plan_history", args={"sql_id": sql_id, "days": 7}, produces="plan_history"),
        Step("get_sql_wait_events", args={"sql_id": sql_id, "hours": 24}, produces="wait_events"),
        # [IE-03] AWR stats thống nhất truyền snapshot range hoặc days được hỗ trợ
        Step("get_awr_sql_stats", args={"sql_id": sql_id, "days": 1}, produces="awr_stats"),
        Step("get_sql_execution_context", args={"sql_id": sql_id}, produces="context"),
        # [IE-08] Kiểm tra statistics freshness cho các tables tham chiếu trong SQL
        Step("get_object_metadata",
             args={"name": DependsOn("context", extract="referenced_table"), "type": "TABLE"},
             produces="table_stats",
             optional=True),
        Step("get_blocking_sessions", args={}, produces="blocking"),
        Step("get_resource_usage", args={}, produces="resource"),
    ])
```

### 5.3 HEALTH_CHECK Plan

```python
def plan_health_check(intent: InvestigationIntent) -> InvestigationPlan:
    return InvestigationPlan(steps=[
        Step("get_top_sql", args={"metric": "elapsed_time", "limit": 10, "hours": 24}),
        Step("get_blocking_sessions", args={}),
        Step("get_tablespace_usage", args={}),
        Step("get_failed_jobs", args={"hours": 24}),
        Step("get_invalid_objects", args={}),
        Step("get_resource_usage", args={}),
        Step("get_long_running_sessions", args={"min_minutes": 30}),
    ])
```

---

## 6. Investigation Executor

```python
# src/db_copilot/investigation/executor.py

class InvestigationExecutor:

    async def execute(self, question: str) -> InvestigationResult:
        # 1. Parse intent
        intent = await self.intent_parser.parse(question)

        # 2. Create plan
        plan = self.planner.create_plan(intent)

        # 3. Execute steps (Hỗ trợ dependency wave để chạy song song các tool độc lập)
        context = InvestigationContext()

        # [IE-05] Phân nhóm các steps thành từng wave:
        # Wave 1 (Độc lập): metadata, dependencies, ash_activity, blocking, resource
        # Wave 2 (Phụ thuộc vào Wave 1): sql_stats, table_stats
        # Wave 3 (Phụ thuộc vào sql_stats): plan_history, wait_events, awr_stats, source_code
        step_waves = self._group_into_waves(plan.steps)

        for wave in step_waves:
            tasks = [self._execute_single_step(step, context) for step in wave]
            await asyncio.gather(*tasks)

        # 4. Build evidence
        evidence_list = self.evidence_builder.build_from_context(context, intent)
        graph = self._build_evidence_graph(evidence_list, context)

        # 5. Generate hypotheses
        hypotheses = self.correlation_engine.rank_hypotheses(evidence_list)

        # 6. AI diagnosis — [IE-01] Align chuẩn 100% với schema EvidencePackage
        package = EvidencePackage(
            question=question,
            intent=intent.__dict__,
            evidence=evidence_list,
            hypotheses=hypotheses,
            context={"graph": graph, **context.to_dict()}
        )
        diagnosis = await self.ai_service.diagnose(package)

        return InvestigationResult(
            id=uuid4(),
            question=question,
            intent=intent,
            evidence=evidence_list,
            hypotheses=hypotheses,
            diagnosis=diagnosis,
            duration_seconds=context.elapsed_seconds
        )

    async def _execute_single_step(self, step: Step, context: InvestigationContext):
        try:
            # [IE-04] Resolve dynamic dependencies với kiểm tra None an toàn
            resolved_args, has_missing_dep = self._resolve_args(step.args, context)
            if has_missing_dep:
                msg = f"Skipping step {step.tool}: required upstream dependency evaluated to None"
                context.add_error(step.produces, msg)
                logger.warning(msg)
                return

            # Call oracle-mcp-server với 10s timeout
            result = await asyncio.wait_for(
                self.mcp_client.call_tool(step.tool, resolved_args),
                timeout=10.0
            )
            context.add_result(step.produces, result)

        except asyncio.TimeoutError:
            context.add_error(step.produces, "timeout")
            logger.warning(f"Step {step.tool} timed out")

        except Exception as e:
            context.add_error(step.produces, str(e))
            logger.error(f"Step {step.tool} failed: {e}")

    def _resolve_args(self, args: dict, context: InvestigationContext) -> tuple[dict, bool]:
        """
        [IE-04] Resolve DependsOn references.
        Trả về (resolved_args, has_missing_dep). Nếu dependency bắt buộc bị None -> báo cờ để skip.
        """
        resolved = {}
        has_missing_dep = False
        for key, value in args.items():
            if isinstance(value, DependsOn):
                extracted = context.extract(value.source, value.path)
                if extracted is None:
                    has_missing_dep = True
                resolved[key] = extracted
            else:
                resolved[key] = value
        return resolved, has_missing_dep
```

---

## 7. Investigation Context

```python
# src/db_copilot/investigation/context.py

class InvestigationContext:
    """
    Holds all results from investigation steps.
    Allows dynamic dependency resolution.
    """

    def __init__(self):
        self.results: dict[str, Any] = {}
        self.errors: dict[str, str] = {}
        self.start_time = time.time()

    def add_result(self, key: str, value: Any):
        self.results[key] = value

    def add_error(self, key: str, error: str):
        self.errors[key] = error

    def extract(self, source: str, path: str) -> Any:
        """
        Extract value from a previous step result.
        path: "top_sql_id" → result["top_sql"][0]["sql_id"]
        """
        data = self.results.get(source)
        if data is None:
            return None
        return self._get_by_path(data, path)

    @property
    def elapsed_seconds(self) -> float:
        return time.time() - self.start_time

    def to_dict(self) -> dict:
        return {"results": self.results, "errors": self.errors}
```

---

## 8. InvestigationResult Schema

```python
@dataclass
class InvestigationResult:
    id: UUID
    question: str
    intent: InvestigationIntent
    evidence: list[Evidence]
    hypotheses: list[Hypothesis]
    diagnosis: DiagnosisResult
    duration_seconds: float
    created_at: datetime = field(default_factory=datetime.utcnow)
```

---

---

# 🇬🇧 ENGLISH SECTION

---

## 9. Overview

Investigation Engine is the "brain" of the system — processes natural language questions and automatically performs the full investigation workflow.

**Input:** Natural language question (e.g., _"Why was PROC_SETTLEMENT slow at 14:32?"_)

**Output:** Structured `InvestigationResult` with evidence, hypotheses, and diagnosis.

---

## 10. Pipeline Summary

1. **Intent Parser** (LLM): Parse natural language → structured intent (type, entities, time range, metric)
2. **Planner**: Intent → Ordered investigation steps with dynamic dependencies
3. **Executor**: Execute steps via oracle-mcp-server MCP calls (10s timeout, continue on error)
4. **Evidence Builder**: Raw results → typed Evidence objects + Evidence graph
5. **Hypothesis Engine**: Rank hypotheses by confidence (deterministic scoring)
6. **AI Diagnosis**: EvidencePackage → LLM → Structured DiagnosisResult

---

## 11. Investigation Plans

| Intent Type | Steps Count | Key MCP Tools Used |
|---|---|---|
| `PROCEDURE_SLOW` | 9 steps | ash_activity, sql_statistics, plan_history, wait_events, awr_stats, blocking, resource, object_source |
| `SQL_SLOW` | 7 steps | sql_statistics, plan_history, wait_events, awr_stats, execution_context, blocking, resource |
| `HEALTH_CHECK` | 7 steps | top_sql, blocking, tablespace, failed_jobs, invalid_objects, resource, long_running |

---

## 12. Dynamic Dependencies

Steps can depend on previous step results:

```python
Step("get_sql_statistics",
     args={"sql_id": DependsOn("ash_activity", extract="top_sql_id")})
```

This means: _"The sql_id argument comes from the result of the 'ash_activity' step, extracted via the 'top_sql_id' path."_

If a dependency fails, the dependent step is skipped (for optional steps) or logs a warning and continues.

---

## 13. Performance Target

- Total investigation time: **< 60 seconds**
- Per MCP tool call timeout: **10 seconds**
- Continue on individual step failures — partial results are still valuable
- Minimum viable result: Can provide diagnosis even with incomplete evidence (lower confidence)

---


<!-- ======================================================
     FILE: docs/03-technical/task_evidence.md
     ====================================================== -->

# 📋 Task Breakdown: Mục 4.2 — db-copilot MCP Client & Evidence Collection

Tài liệu chi tiết phân tách **Mục 4.2** thành các task nhỏ nhất (atomic tasks), có tiêu chí nghiệm thu rõ ràng, dễ dàng triển khai và kiểm thử từng bước.

---

## 📌 Tổng Quan Phạm Vi Mục 4.2

- **Mục tiêu:** Xây dựng tầng MCP Client Gateway kết nối với `oracle-mcp-server` và bộ máy thu thập bằng chứng (`Evidence Engine`) lưu vào PostgreSQL của `db-copilot`.
- **Thư mục tác động chính:** `db-copilot/src/db_copilot/` (`mcp/`, `evidence/`, `config/`, `api/`) và `db-copilot/tests/unit/evidence/`.

---

## 📑 Danh Sách Task Chi Tiết

### GIAI ĐOẠN 1: MÔI TRƯỜNG & CẤU HÌNH (Phase 1.1)

- [x] **Task 1.1: Bổ sung Dependencies**
  - **File:** `db-copilot/pyproject.toml`
  - **Nội dung:** Thêm `mcp>=1.0.0` và `apscheduler>=3.10.0,<4.0.0` vào danh sách `dependencies`.
  - **Tiêu chuẩn hoàn thành:** Chạy `uv pip install --system -e ".[dev]"` thành công không xung đột package.

- [x] **Task 1.2: Mở rộng Settings**
  - **File:** `db-copilot/src/db_copilot/config/settings.py`
  - **Nội dung:** Bổ sung các biến cấu hình:
    - `mcp_server_command: str = "python"`
    - `mcp_server_args: list[str] = ["-m", "oracle_mcp.server"]`
    - `mcp_server_cwd: str | None = None`
    - `oracle_user: str = "db_copilot_readonly"`
    - `oracle_password: str = ""`
    - `oracle_dsn: str = "localhost:1521/ORCL"`
    - `collection_interval_minutes: int = 5`
    - `baseline_recalc_interval_hours: int = 1`
    - `enable_scheduler: bool = True`
  - **Tiêu chuẩn hoàn thành:** `Settings()` khởi tạo đầy đủ các giá trị mặc định và đọc được từ `.env`.

- [x] **Task 1.3: Cập nhật File Mẫu Biến Môi Trường**
  - **File:** `db-copilot/.env.example`
  - **Nội dung:** Bổ sung phần cấu hình MCP Server và Oracle target credentials.
  - **Tiêu chuẩn hoàn thành:** File `.env.example` đầy đủ ghi chú cho từng biến mới.

---

### GIAI ĐOẠN 2: TẦNG MCP CLIENT GATEWAY (Phase 1.2)

- [x] **Task 2.1: Khởi tạo Module MCP Client**
  - **File:** `db-copilot/src/db_copilot/mcp/__init__.py`, `db-copilot/src/db_copilot/mcp/client.py`
  - **Nội dung:** Tạo class `OracleMcpClient` nhận cấu hình server command, args, env và cwd.

- [x] **Task 2.2: Triển khai Hàm `call_tool` qua Stdio Transport**
  - **File:** `db-copilot/src/db_copilot/mcp/client.py`
  - **Nội dung:** Sử dụng `mcp.client.stdio.stdio_client` và `ClientSession` để kết nối, khởi tạo session, gọi tool theo tên và arguments, trích xuất dữ liệu TextContent / JSON.
  - **Tiêu chuẩn hoàn thành:** Trả về Python dict/list chuẩn sau khi parse JSON từ output của MCP tool.

- [x] **Task 2.3: Đo lường và Xử lý Lỗi Cuộc gọi MCP**
  - **File:** `db-copilot/src/db_copilot/mcp/client.py`
  - **Nội dung:** Bổ sung đo thời gian thực thi `duration_ms`, bắt ngoại lệ timeout/connection error, trả về kết quả hoặc throw MCPClientError có cấu trúc.

- [x] **Task 2.4: Unit Tests cho `OracleMcpClient`**
  - **File:** `db-copilot/tests/unit/evidence/test_mcp_client.py`
  - **Nội dung:** Test `call_tool` thành công với mock session, test khi server trả về lỗi, test khi JSON parse lỗi.
  - **Tiêu chuẩn hoàn thành:** Pytest xanh 100%, không cần chạy server thật.

---

### GIAI ĐOẠN 3: EVIDENCE REPOSITORY (Phase 1.3)

- [x] **Task 3.1: Khởi tạo Module Evidence Repository**
  - **File:** `db-copilot/src/db_copilot/evidence/__init__.py`, `db-copilot/src/db_copilot/evidence/repository.py`
  - **Nội dung:** Khởi tạo class `EvidenceRepository` nhận SQLAlchemy `AsyncSession` hoặc `async_sessionmaker`.

- [x] **Task 3.2: CRUD Database Instance**
  - **File:** `db-copilot/src/db_copilot/evidence/repository.py`
  - **Nội dung:** Hàm `get_or_create_default_database(name, host, service_name, version) -> Database`.

- [x] **Task 3.3: Ghi nhận Snapshot Định kỳ**
  - **File:** `db-copilot/src/db_copilot/evidence/repository.py`
  - **Nội dung:** Hàm `create_snapshot(database_id, captured_at, active_sessions, blocking_sessions, cpu_pct, health_score, raw_data) -> Snapshot`.

- [x] **Task 3.4: Lưu trữ SQL Metrics Hàng loạt**
  - **File:** `db-copilot/src/db_copilot/evidence/repository.py`
  - **Nội dung:** Hàm `save_sql_metrics(metrics: list[dict], database_id: UUID, snapshot_id: UUID | None)` bulk insert vào bảng `sql_metrics`.

- [x] **Task 3.5: Truy vấn Dữ liệu Lịch sử SQL (7 ngày)**
  - **File:** `db-copilot/src/db_copilot/evidence/repository.py`
  - **Nội dung:**
    - `get_active_sql_ids(database_id: UUID, days: int = 7) -> list[str]`
    - `get_sql_metrics_history(database_id: UUID, sql_id: str, days: int = 7) -> list[SqlMetric]`

- [x] **Task 3.6: Quản lý SQL Baseline**
  - **File:** `db-copilot/src/db_copilot/evidence/repository.py`
  - **Nội dung:**
    - `upsert_baseline(baseline: SqlBaseline)`: Cập nhật hoặc thêm mới baseline theo primary key `(database_id, sql_id, hour_of_day, day_of_week)`.
    - `get_baseline(database_id: UUID, sql_id: str, hour: int, dow: int) -> SqlBaseline | None`.

- [x] **Task 3.7: Lưu trữ Evidence Items**
  - **File:** `db-copilot/src/db_copilot/evidence/repository.py`
  - **Nội dung:** Hàm `save_evidence(evidence: Evidence, incident_id: UUID | None = None) -> EvidenceItem`.

- [x] **Task 3.8: Ghi Log Audit MCP Phía Client**
  - **File:** `db-copilot/src/db_copilot/evidence/repository.py`
  - **Nội dung:** Hàm `log_mcp_audit(tool_name, input_args, duration_ms, rows_returned, status, error_message, database_id)` ghi vào bảng `mcp_audit_log`.

- [x] **Task 3.9: Unit Tests cho `EvidenceRepository`**
  - **File:** `db-copilot/tests/unit/evidence/test_repository.py`
  - **Nội dung:** Test các phương thức của repository bằng mock session hoặc SQLite in-memory.

---

### GIAI ĐOẠN 4: EVIDENCE NORMALIZER (Phase 1.4)

- [x] **Task 4.1: Khởi tạo Class EvidenceNormalizer**
  - **File:** `db-copilot/src/db_copilot/evidence/normalizers/__init__.py`, `db-copilot/src/db_copilot/evidence/normalizers/evidence_normalizer.py`

- [x] **Task 4.2: Chuẩn hóa SQL Regression**
  - **File:** `db-copilot/src/db_copilot/evidence/normalizers/evidence_normalizer.py`
  - **Nội dung:** Hàm `normalize_sql_regression(current_elapsed_ms, baseline, multiplier=3.0) -> Evidence | None`.
    - Bỏ qua nếu `baseline.is_reliable == False`.
    - Bỏ qua nếu `ratio < multiplier`.
    - Gán Severity: ratio >= 10 -> `CRITICAL`, >= 5 -> `HIGH`, >= 3 -> `MEDIUM`.

- [x] **Task 4.3: Chuẩn hóa Blocking Sessions**
  - **File:** `db-copilot/src/db_copilot/evidence/normalizers/evidence_normalizer.py`
  - **Nội dung:** Hàm `normalize_blocking_chain(blocking_data: dict) -> list[Evidence]`:
    - Tạo `EvidenceType.BLOCKING_SESSION` với thông tin root blocker, blocked sessions, wait event.

- [x] **Task 4.4: Chuẩn hóa Tablespace Usage**
  - **File:** `db-copilot/src/db_copilot/evidence/normalizers/evidence_normalizer.py`
  - **Nội dung:** Hàm `normalize_tablespace_usage(tablespaces: list[dict], warning_pct=80.0, critical_pct=90.0) -> list[Evidence]`.
    - Tạo `EvidenceType.TABLESPACE_FULL` với Severity `CRITICAL` (> 90%) hoặc `HIGH` (> 80%).

- [x] **Task 4.5: Chuẩn hóa Failed Jobs**
  - **File:** `db-copilot/src/db_copilot/evidence/normalizers/evidence_normalizer.py`
  - **Nội dung:** Hàm `normalize_failed_jobs(failed_jobs: list[dict]) -> list[Evidence]`.
    - Tạo `EvidenceType.JOB_FAILURE` cho từng job lỗi kèm error code và message.

- [x] **Task 4.6: Chuẩn hóa Long Running Sessions & Invalid Objects**
  - **File:** `db-copilot/src/db_copilot/evidence/normalizers/evidence_normalizer.py`
  - **Nội dung:**
    - `normalize_long_running_sessions(sessions: list[dict], threshold_sec=1800) -> list[Evidence]`
    - `normalize_invalid_objects(invalid_objects: list[dict]) -> list[Evidence]`

- [x] **Task 4.7: Unit Tests cho `EvidenceNormalizer`**
  - **File:** `db-copilot/tests/unit/evidence/test_normalizer.py`
  - **Nội dung:** Kiểm tra đầy đủ mọi nhánh logic, tỷ lệ ngưỡng, mức độ nghiêm trọng và bỏ qua khi dữ liệu không đủ.

---

### GIAI ĐOẠN 5: COLLECTORS (Phase 1.5)

- [x] **Task 5.1: Xây dựng BaseCollector**
  - **File:** `db-copilot/src/db_copilot/evidence/collectors/__init__.py`, `db-copilot/src/db_copilot/evidence/collectors/base.py`
  - **Nội dung:** Base class nhận `OracleMcpClient`, `EvidenceRepository`, `EvidenceNormalizer` và `database_id`.

- [x] **Task 5.2: Triển khai SqlCollector**
  - **File:** `db-copilot/src/db_copilot/evidence/collectors/sql_collector.py`
  - **Nội dung:**
    1. Gọi tool `get_top_sql` (metric="elapsed_time", limit=100, hours=1).
    2. Tạo `Snapshot` và lưu metrics vào `sql_metrics`.
    3. Đối chiếu nhanh với baseline để sinh `EvidenceType.SQL_REGRESSION` (nếu có).

- [x] **Task 5.3: Triển khai SessionCollector**
  - **File:** `db-copilot/src/db_copilot/evidence/collectors/session_collector.py`
  - **Nội dung:**
    1. Gọi `get_active_sessions`, `get_blocking_sessions`, `get_long_running_sessions`.
    2. Cập nhật số active & blocking sessions vào `Snapshot`.
    3. Chuẩn hóa và lưu trữ các `Evidence` blocking/long-running.

- [x] **Task 5.4: Triển khai StorageCollector**
  - **File:** `db-copilot/src/db_copilot/evidence/collectors/storage_collector.py`
  - **Nội dung:**
    1. Gọi `get_tablespace_usage`, `get_failed_jobs`, `get_invalid_objects`.
    2. Chuẩn hóa và lưu trữ các `Evidence` cảnh báo dung lượng và lỗi job.

- [x] **Task 5.5: Unit Tests cho Collectors**
  - **File:** `db-copilot/tests/unit/evidence/test_collectors.py`
  - **Nội dung:** Mock MCP client responses và mock repository để kiểm tra logic điều phối thu thập của cả 3 collectors.

---

### GIAI ĐOẠN 6: BASELINE ENGINE (Phase 1.6)

- [x] **Task 6.1: Khởi tạo Class BaselineEngine**
  - **File:** `db-copilot/src/db_copilot/evidence/baseline_engine.py`
  - **Nội dung:** Nhận `EvidenceRepository` và cấu hình số ngày cửa sổ trượt (mặc định 7 ngày).

- [x] **Task 6.2: Thuật toán Lọc Outliers**
  - **File:** `db-copilot/src/db_copilot/evidence/baseline_engine.py`
  - **Nội dung:** Hàm `_remove_outliers(samples: list[float]) -> list[float]`: Loại bỏ giá trị ngoài khoảng `mean ± 2 * stddev`.

- [x] **Task 6.3: Thuật toán Tính toán Chỉ số Thống kê**
  - **File:** `db-copilot/src/db_copilot/evidence/baseline_engine.py`
  - **Nội dung:** Tính `mean`, `stddev`, `p50` (median), `p95` (95th percentile) bằng thư viện `statistics` hoặc thuật toán mảng.

- [x] **Task 6.4: Cơ chế Đánh giá Độ tin cậy (Reliability)**
  - **File:** `db-copilot/src/db_copilot/evidence/baseline_engine.py`
  - **Nội dung:** Nếu số mẫu sau khi lọc `>= 5` -> `is_reliable = True`; nếu `< 5` -> `is_reliable = False`.

- [x] **Task 6.5: Triển khai Hàm `recalculate`**
  - **File:** `db-copilot/src/db_copilot/evidence/baseline_engine.py`
  - **Nội dung:**
    - Lấy danh sách `sql_id` hoạt động trong 7 ngày.
    - Lặp qua 24 giờ x 7 ngày trong tuần.
    - Tính baseline và gọi `repo.upsert_baseline`.

- [x] **Task 6.6: Unit Tests cho `BaselineEngine`**
  - **File:** `db-copilot/tests/unit/evidence/test_baseline_engine.py`
  - **Nội dung:** Test lọc nhiễu, test tính đúng p50/p95/mean/stddev, test gắn cờ `is_reliable` chính xác.

---

### GIAI ĐOẠN 7: SCHEDULER & APP INTEGRATION (Phase 1.7)

- [x] **Task 7.1: Quản lý AsyncIOScheduler**
  - **File:** `db-copilot/src/db_copilot/evidence/scheduler.py`
  - **Nội dung:** Class `EvidenceScheduler` đóng gói `AsyncIOScheduler`, định nghĩa các hàm wrapper chạy an toàn (bắt ngoại lệ không để crash scheduler).

- [x] **Task 7.2: Đăng ký Định kỳ Các Jobs**
  - **File:** `db-copilot/src/db_copilot/evidence/scheduler.py`
  - **Nội dung:**
    - Job `collect_sql`: interval 5 phút.
    - Job `collect_sessions`: interval 5 phút.
    - Job `collect_storage`: interval 5 phút.
    - Job `recalculate_baselines`: interval 1 giờ.

- [x] **Task 7.3: Tích hợp vào FastAPI Lifespan**
  - **File:** `db-copilot/src/db_copilot/api/app.py`
  - **Nội dung:**
    - Khi startup: Nếu `settings.enable_scheduler` là `True`, khởi động `scheduler.start()`.
    - Khi shutdown: Gọi `scheduler.shutdown()` để kết thúc các task ngầm an toàn.

- [x] **Task 7.4: Unit Tests cho Scheduler Lifecycle**
  - **File:** `db-copilot/tests/unit/evidence/test_scheduler.py`
  - **Nội dung:** Test start/stop scheduler, test cờ enable/disable scheduler.

---

### GIAI ĐOẠN 8: KIỂM THỬ TỔNG HỢP & HOÀN THIỆN (Phase 1.8)

- [x] **Task 8.1: Kiểm tra Linting và Định dạng Mã Nguồn**
  - **Lệnh:** `ruff check .`
  - **Yêu cầu:** Không có bất kỳ lỗi syntax, import, hay typing cảnh báo nào.

- [x] **Task 8.2: Chạy Toàn Bộ Test Suite**
  - **Lệnh:** `pytest -v tests/`
  - **Yêu cầu:** 100% test cases của cả Mục 3.2 và Mục 4.2 đều passed.

- [x] **Task 8.3: Cập nhật Trạng thái Dự án**
  - **File:** `SESSION_STATE.md` và `docs/04-implementation/implementation-plan.md`
  - **Nội dung:** Đánh dấu hoàn thành Mục 4.2 và chuẩn bị bước vào Phase 2 (Correlation Engine).

---


<!-- ======================================================
     FILE: docs/03-technical/task_correlation.md
     ====================================================== -->

# 📋 Task Breakdown: Phase 2 — Correlation & Health Engine

Tài liệu chi tiết phân tách **Phase 2 (Correlation & Health Engine)** thành các task nhỏ nhất (atomic tasks), có tiêu chuẩn nghiệm thu và file tác động cụ thể.

---

## 📌 Tổng Quan Phạm Vi Phase 2

- **Mục tiêu:** Xây dựng hệ thống phát hiện sự cố (Deterministic Detection Rules), liên kết các bằng chứng thành đồ thị (`EvidenceGraph`), gom nhóm thành `Incident`, và xếp hạng các giả thuyết chẩn đoán ban đầu (`HypothesisEngine`).
- **Nguyên tắc cốt lõi:** *Detection Rules chạy trước AI*. Toàn bộ việc phát hiện và liên kết là tất định (deterministic), không dùng LLM.
- **Thư mục tác động chính:** `db-copilot/src/db_copilot/correlation/`, `db-copilot/src/db_copilot/api/routes/incidents.py`, `db-copilot/tests/unit/correlation/`.

---

## 📑 Danh Sách Task Chi Tiết

### GIAI ĐOẠN 1: INCIDENT REPOSITORY & DOMAIN EXTENSIONS (Phase 2.1)

- [x] **Task 1.1: Khởi tạo Module Correlation**
  - **File:** `db-copilot/src/db_copilot/correlation/__init__.py`, `db-copilot/src/db_copilot/correlation/repository.py`
  - **Nội dung:** Tạo class `IncidentRepository` tương tác với PostgreSQL qua `AsyncSession`.

- [x] **Task 1.2: CRUD Quản lý Vòng đời Incident**
  - **File:** `db-copilot/src/db_copilot/correlation/repository.py`
  - **Nội dung:**
    - `create_incident(incident: Incident) -> Incident`
    - `get_incident_by_id(incident_id: UUID) -> IncidentDetail | None`
    - `list_incidents(severity=None, status=None, category=None, limit=50, offset=0) -> list[IncidentSummary]`
    - `update_incident_status(incident_id: UUID, status: IncidentStatus, resolved_at: datetime | None = None)`
    - `attach_evidence_to_incident(incident_id: UUID, evidence_id: UUID)`

- [x] **Task 1.3: Cơ chế Chống Trùng lặp Sự cố (Deduplication)**
  - **File:** `db-copilot/src/db_copilot/correlation/repository.py`
  - **Nội dung:** Hàm `find_open_incident(category: IncidentCategory, entity_id: str, within_minutes: int = 60) -> Incident | None`: Tránh tạo nhiều incident lặp lại cho cùng 1 SQL hoặc 1 tablespace đang bị lỗi.

- [x] **Task 1.4: Unit Tests cho `IncidentRepository`**
  - **File:** `db-copilot/tests/unit/correlation/test_repository.py`
  - **Nội dung:** Test tạo incident, filter theo status/severity, test chống duplicate incident.

---

### GIAI ĐOẠN 2: BỘ QUY TẮC PHÁT HIỆN TẤT ĐỊNH (Detection Rules) (Phase 2.2)

- [x] **Task 2.1: Tạo BaseRule Interface**
  - **File:** `db-copilot/src/db_copilot/correlation/rules/__init__.py`, `db-copilot/src/db_copilot/correlation/rules/base.py`
  - **Nội dung:** Lớp trừu tượng `BaseRule` có phương thức `evaluate(...)` và chứa tham chiếu tới `OracleMcpClient`.

- [x] **Task 2.2: Quy tắc Suy thoái SQL (`SqlRegressionRule`)**
  - **File:** `db-copilot/src/db_copilot/correlation/rules/sql_rules.py`
  - **Nội dung:**
    - So sánh `metric.elapsed_time_ms` với `baseline.mean_elapsed_ms`.
    - Bỏ qua nếu baseline unreliable hoặc ratio < `settings.sql_regression_multiplier` (3.0x).
    - Tự động gọi tool `get_sql_plan_history` từ MCP để phát hiện `plan_hash` thay đổi.
    - Sinh `Incident` loại `SQL_REGRESSION` kèm 2 bằng chứng: `SQL_REGRESSION` và `SQL_PLAN_CHANGE` (nếu plan đổi).
    - Gán severity: ratio >= 10x -> `CRITICAL`, >= 5x -> `HIGH`, >= 3x -> `MEDIUM`.

- [x] **Task 2.3: Quy tắc Tắc nghẽn Khóa (`BlockingSessionRule`)**
  - **File:** `db-copilot/src/db_copilot/correlation/rules/session_rules.py`
  - **Nội dung:**
    - Đánh giá từ dữ liệu `get_blocking_sessions`.
    - Nếu `total_blocked > 0`: Sinh `Incident` loại `BLOCKING`, severity `HIGH`.
    - Ghi nhận root blocker SID, wait event, danh sách session bị chặn, max wait time.

- [x] **Task 2.4: Quy tắc Session Chạy Quá Lâu (`LongRunningSessionRule`)**
  - **File:** `db-copilot/src/db_copilot/correlation/rules/session_rules.py`
  - **Nội dung:**
    - Đánh giá các session active có `elapsed_seconds >= settings.long_running_threshold_sec` (mặc định 1800s / 30 phút).
    - Sinh `Incident` loại `LONG_RUNNING_SESSION`.

- [x] **Task 2.5: Quy tắc Ngưỡng Dung Lượng Tablespace (`TablespaceThresholdRule`)**
  - **File:** `db-copilot/src/db_copilot/correlation/rules/storage_rules.py`
  - **Nội dung:**
    - Kiểm tra `used_pct`: `>= 90%` -> `CRITICAL`, `>= 80%` -> `MEDIUM`.
    - Tính xu hướng tăng trưởng: `bytes_per_day` và ước tính số ngày còn lại `days_until_full`.
    - Sinh `Incident` loại `TABLESPACE`.

- [x] **Task 2.6: Quy tắc Lỗi Scheduler Job (`JobFailureRule`)**
  - **File:** `db-copilot/src/db_copilot/correlation/rules/storage_rules.py`
  - **Nội dung:**
    - Quét danh sách job lỗi trong 24 giờ qua (`get_failed_jobs`).
    - Sinh `Incident` loại `JOB_FAILURE` với mã lỗi Oracle và tên job.

- [x] **Task 2.7: Quy tắc Đối Tượng Không Hợp Lệ (`InvalidObjectRule`)**
  - **File:** `db-copilot/src/db_copilot/correlation/rules/storage_rules.py`
  - **Nội dung:**
    - Quét các package/procedure/trigger/view bị `STATUS = 'INVALID'`.
    - Sinh incident cảnh báo cho DBA nếu có object core bị hỏng.

- [x] **Task 2.8: Unit Tests cho Tất Cả Detection Rules**
  - **File:** `db-copilot/tests/unit/correlation/test_rules.py`
  - **Nội dung:** Test độc lập từng rule với các mock data đầu vào, kiểm tra đúng điều kiện kích hoạt, không kích hoạt khi chưa vượt ngưỡng.

---

### GIAI ĐOẠN 3: ĐỒ THỊ QUAN HỆ BẰNG CHỨNG (Evidence Graph) (Phase 2.3)

- [x] **Task 3.1: Định nghĩa GraphNode và GraphEdge**
  - **File:** `db-copilot/src/db_copilot/correlation/graph.py`
  - **Nội dung:**
    - `GraphNode`: `entity_type` ("SQL", "PROCEDURE", "TABLE", "SESSION", "PLAN"), `entity_id`, danh sách `evidence`.
    - `GraphEdge`: `source: GraphNode`, `target: GraphNode`, `relationship` ("executes", "uses", "accesses", "blocks", "depends_on"), `weight: float`.

- [x] **Task 3.2: Xây dựng Class `EvidenceGraph`**
  - **File:** `db-copilot/src/db_copilot/correlation/graph.py`
  - **Nội dung:**
    - `add_evidence(evidence: Evidence) -> GraphNode`
    - `add_relationship(source_type, source_id, rel, target_type, target_id, weight=0.5)`
    - `to_dict() -> dict`: Chuyển đồ thị thành format JSON để frontend render hoặc LLM đọc.

- [x] **Task 3.3: Thuật toán Tìm Chuỗi Nguyên Nhân (`get_causal_chain`)**
  - **File:** `db-copilot/src/db_copilot/correlation/graph.py`
  - **Nội dung:** Dùng Breadth-First Search (BFS) duyệt từ root entity để truy vết chuỗi: `Procedure -> SQL -> Plan -> Table -> Stale Stats`.

- [x] **Task 3.4: Thuật toán Xác định Thực thể Ảnh hưởng Lớn nhất (`get_most_impactful_entity`)**
  - **File:** `db-copilot/src/db_copilot/correlation/graph.py`
  - **Nội dung:** Tính tổng điểm severity và bậc vào/ra của nodes để tìm bottleneck lớn nhất.

- [x] **Task 3.5: Unit Tests cho `EvidenceGraph`**
  - **File:** `db-copilot/tests/unit/correlation/test_graph.py`
  - **Nội dung:** Test thêm nodes/edges, test BFS causal chain, test serialize ra JSON.

---

### GIAI ĐOẠN 4: BỘ SUY LUẬN GIẢ THUYẾT (Hypothesis Engine) (Phase 2.4)

- [x] **Task 4.1: Định nghĩa 5 Giả Thuyết Gốc**
  - **File:** `db-copilot/src/db_copilot/correlation/hypothesis_engine.py`
  - **Nội dung:** Cấu hình 5 ma trận giả thuyết:
    1. `Statistics Issue` (Required: `stale_statistics`; Supporting: `cardinality_mismatch`, `sql_regression`; Contradicted: `blocking_session`)
    2. `Execution Plan Regression` (Required: `sql_plan_change`; Supporting: `sql_regression`, `high_physical_reads`)
    3. `Blocking / Concurrency Issue` (Required: `blocking_session`; Supporting: `long_running_session`)
    4. `Tablespace / Storage Issue` (Required: `tablespace_threshold`)
    5. `Background Job Failure` (Required: `job_failure`)

- [x] **Task 4.2: Thuật toán Tính Điểm Tự Động (`rank_hypotheses`)**
  - **File:** `db-copilot/src/db_copilot/correlation/hypothesis_engine.py`
  - **Nội dung:**
    - Kiểm tra `required_evidence`: Nếu thiếu -> loại bỏ giả thuyết (confidence = 0).
    - Cộng điểm cơ bản `base_confidence`.
    - Với mỗi `supporting_evidence` xuất hiện: cộng `+0.08` confidence.
    - Nếu có `contradicted_by`: giảm `-0.30` hoặc hạ điểm.
    - Giới hạn confidence trong `[0.0, 1.0]`, sắp xếp giảm dần theo điểm.

- [x] **Task 4.3: Unit Tests cho `HypothesisEngine`**
  - **File:** `db-copilot/tests/unit/correlation/test_hypothesis_engine.py`
  - **Nội dung:** Test confidence tăng khi có supporting evidence, test bị loại bỏ khi thiếu required evidence, test xếp hạng đúng thứ tự.

---

### GIAI ĐOẠN 5: CORRELATION ENGINE ORCHESTRATOR (Phase 2.5)

- [x] **Task 5.1: Xây dựng Bộ Điều Phối `CorrelationEngine`**
  - **File:** `db-copilot/src/db_copilot/correlation/engine.py`
  - **Nội dung:**
    - Khởi tạo cùng `OracleMcpClient`, `IncidentRepository`, `HypothesisEngine`, và danh sách các Rules.
    - Hàm `evaluate_sql_metrics(metrics: list[SqlMetric]) -> list[Incident]`
    - Hàm `evaluate_session_state(session_data: dict) -> list[Incident]`
    - Hàm `evaluate_storage_state(storage_data: dict) -> list[Incident]`
    - Tự động gắn EvidenceGraph và danh sách giả thuyết vào mỗi Incident trước khi lưu.

- [x] **Task 5.2: Tích hợp với Collectors trong Evidence Engine**
  - **File:** `db-copilot/src/db_copilot/evidence/collectors/`
  - **Nội dung:** Sau khi Collectors kéo xong dữ liệu định kỳ mỗi 5 phút, gọi sang `CorrelationEngine` để đánh giá ngay lập tức.

- [x] **Task 5.3: Unit Tests cho `CorrelationEngine`**
  - **File:** `db-copilot/tests/unit/correlation/test_engine.py`
  - **Nội dung:** Kiểm tra toàn bộ luồng từ metric đầu vào -> kích hoạt rule -> build graph -> rank hypothesis -> lưu incident.

---

### GIAI ĐOẠN 6: REST API CHO INCIDENTS (Phase 2.6)

- [x] **Task 6.1: Định nghĩa Pydantic Schemas cho Incidents**
  - **File:** `db-copilot/src/db_copilot/api/routes/incidents.py`
  - **Nội dung:** Schema response `IncidentSummaryResponse`, `IncidentDetailResponse`, `IncidentResolveRequest`.

- [x] **Task 6.2: Triển khai Endpoint `GET /api/v1/incidents`**
  - **File:** `db-copilot/src/db_copilot/api/routes/incidents.py`
  - **Nội dung:** Lấy danh sách incident hỗ trợ query params: `severity`, `status`, `category`, `limit`, `offset`.

- [x] **Task 6.3: Triển khai Endpoint `GET /api/v1/incidents/{id}`**
  - **File:** `db-copilot/src/db_copilot/api/routes/incidents.py`
  - **Nội dung:** Trả về chi tiết sự cố, danh sách evidence đính kèm, hypothesis ranking và đồ thị quan hệ.

- [x] **Task 6.4: Triển khai Endpoint `PATCH /api/v1/incidents/{id}/resolve`**
  - **File:** `db-copilot/src/db_copilot/api/routes/incidents.py`
  - **Nội dung:** Cho phép DBA cập nhật trạng thái `RESOLVED` cho sự cố.

- [x] **Task 6.5: Đăng ký Router trong FastAPI App**
  - **File:** `db-copilot/src/db_copilot/api/app.py`
  - **Nội dung:** Include router incidents vào ứng dụng chính.

- [x] **Task 6.6: Unit Tests cho Incident API Endpoints**
  - **File:** `db-copilot/tests/unit/api/test_incidents.py`
  - **Nội dung:** Test HTTP status 200, 404 khi không tìm thấy, lọc dữ liệu chính xác.

---

### GIAI ĐOẠN 7: KIỂM THỬ TỔNG HỢP (Phase 2.7)

- [x] **Task 7.1: Kiểm tra Linting**
  - **Lệnh:** `ruff check .`
  - **Yêu cầu:** 0 lỗi linting.

- [x] **Task 7.2: Chạy Toàn Bộ Test Suite**
  - **Lệnh:** `pytest -v tests/`
  - **Yêu cầu:** 100% tests passed.

- [x] **Task 7.3: Cập nhật Trạng thái Dự án**
  - **File:** `SESSION_STATE.md` và `docs/04-implementation/implementation-plan.md`.

---


<!-- ======================================================
     FILE: docs/03-technical/task_investigation_ai.md
     ====================================================== -->

# 📋 Task Breakdown: Phase 3 — AI & Investigation Engine

Tài liệu chi tiết phân tách **Phase 3 (AI & Investigation Engine)** thành các task nhỏ nhất (atomic tasks), có tiêu chuẩn nghiệm thu và file tác động cụ thể.

---

## 📌 Tổng Quan Phạm Vi Phase 3

- **Mục tiêu:** Xây dựng "bộ não" thông minh của hệ thống:
  1. Tiếp nhận câu hỏi tự nhiên từ DBA bằng tiếng Anh/Việt.
  2. Tự động lập kế hoạch điều tra (`InvestigationPlanner`) và gọi các MCP tools để thu thập chứng cứ chuyên sâu (`InvestigationExecutor`).
  3. Tích hợp AI (LLM: Gemini / Claude / OpenAI) để chẩn đoán nguyên nhân gốc rễ và đưa ra khuyến nghị chuẩn cấu trúc (`DiagnosisResult`).
  4. Tự động sinh báo cáo sức khỏe cơ sở dữ liệu hàng ngày (`DailyReport`).
  5. Cung cấp REST/WebSocket API và giao diện người dùng (Frontend Web Dashboard).
- **Nguyên tắc cốt lõi:**
  - **Evidence-first:** LLM chỉ được gọi khi đã tập hợp đủ chứng cứ.
  - **Structured I/O:** LLM chỉ trả về structured JSON, không trả free-form text.
  - **Human-in-control:** Mọi khuyến nghị của AI chỉ mang tính tham khảo cho DBA, không bao giờ tự động thực thi lên Oracle.
- **Thư mục tác động chính:** `db-copilot/src/db_copilot/ai/`, `db-copilot/src/db_copilot/investigation/`, `db-copilot/src/db_copilot/api/routes/investigate.py`, `frontend/`.

---

## 📑 Danh Sách Task Chi Tiết

### GIAI ĐOẠN 1: TẦNG LLM PROVIDER & MULTI-ADAPTER (Phase 3.1)

- [ ] **Task 1.1: Khởi tạo Interface LLMProvider**
  - **File:** `db-copilot/src/db_copilot/domain/interfaces/__init__.py`, `db-copilot/src/db_copilot/domain/interfaces/llm_provider.py`
  - **Nội dung:** Abstract Base Class `LLMProvider` với các hàm trừu tượng:
    - `diagnose(package: EvidencePackage) -> DiagnosisResult`
    - `parse_intent(question: str, current_time: datetime) -> dict`
    - `generate_report_narrative(incidents: list[Incident], metrics: dict) -> str`

- [ ] **Task 1.2: Triển khai Google Gemini Provider**
  - **File:** `db-copilot/src/db_copilot/ai/providers/gemini_provider.py`
  - **Nội dung:**
    - Sử dụng Google Gemini API (model `gemini-1.5-pro` hoặc `gemini-2.0-flash`).
    - Bật chế độ `response_mime_type="application/json"` với JSON schema của `DiagnosisResult`.
    - Xử lý rate limit, retry và parse kết quả trả về `DiagnosisResult`.

- [ ] **Task 1.3: Triển khai Anthropic Claude / OpenAI Provider**
  - **File:** `db-copilot/src/db_copilot/ai/providers/claude_provider.py`, `db-copilot/src/db_copilot/ai/providers/openai_provider.py`
  - **Nội dung:** Hỗ trợ linh hoạt chuyển đổi provider qua biến cấu hình `LLM_PROVIDER=gemini|claude|openai`.

- [ ] **Task 1.4: Unit Tests cho LLM Providers (với Mock SDK)**
  - **File:** `db-copilot/tests/unit/ai/test_providers.py`
  - **Nội dung:** Mock API response, kiểm tra parsing chính xác vào Pydantic model `DiagnosisResult`, xử lý khi API trả JSON sai định dạng.

---

### GIAI ĐOẠN 2: PROMPT ENGINEERING & AI DIAGNOSIS SERVICE (Phase 3.2)

- [ ] **Task 2.1: Thiết kế System Prompt Chẩn Đoán (`DIAGNOSIS_SYSTEM_PROMPT`)**
  - **File:** `db-copilot/src/db_copilot/ai/prompts/diagnosis_prompt.py`
  - **Nội dung:**
    - Định nghĩa vai trò Senior Oracle Performance DBA.
    - Ép buộc tuân thủ 5 nguyên tắc: Chỉ dựa trên evidence cung cấp, không leak credentials, giải thích confidence, luôn đính kèm note *"DBA must review and execute manually"*, trả về 100% valid JSON.

- [ ] **Task 2.2: Thiết kế System Prompt Báo Cáo Hàng Ngày (`REPORT_SYSTEM_PROMPT`)**
  - **File:** `db-copilot/src/db_copilot/ai/prompts/report_prompt.py`
  - **Nội dung:** Prompt hướng dẫn tóm tắt các sự cố trong ngày, chỉ ra các SQL ngốn tài nguyên nhất, xu hướng tablespace và khuyến nghị hành động cho ca trực tiếp theo.

- [ ] **Task 2.3: Xây dựng AIService Orchestrator**
  - **File:** `db-copilot/src/db_copilot/ai/service.py`
  - **Nội dung:**
    - Kiểm tra tính hợp lệ của `EvidencePackage`.
    - Gọi LLM Provider để chẩn đoán.
    - **Cơ chế Fallback an toàn:** Nếu LLM gặp lỗi timeout hoặc không thể phân tích JSON, tự động sinh `DiagnosisResult` từ kết quả của `HypothesisEngine` (không làm gián đoạn hệ thống).

- [ ] **Task 2.4: Unit Tests cho `AIService`**
  - **File:** `db-copilot/tests/unit/ai/test_ai_service.py`
  - **Nội dung:** Test luồng thành công, test fallback sang rule-based khi LLM offline.

---

### GIAI ĐOẠN 3: ĐIỀU TRA TỰ ĐỘNG — INTENT PARSER & PLANNER (Phase 3.3)

- [ ] **Task 3.1: Phân Tích Ý Định Người Dùng (`IntentParser`)**
  - **File:** `db-copilot/src/db_copilot/investigation/planner.py`
  - **Nội dung:**
    - Parse câu hỏi tự nhiên (ví dụ: *"Why was PROC_SETTLEMENT slow at 14:32?"*).
    - Trích xuất: `intent_type` (`SLOW_PROCEDURE`, `SLOW_SQL`, `BLOCKING_ISSUE`, `SYSTEM_SLOWNESS`), `entity_type`, `entity_id`, `time_range` (`start_time`, `end_time`), `focus_metric`.

- [ ] **Task 3.2: Bộ Lập Kế Hoạch Điều Tra (`InvestigationPlanner`)**
  - **File:** `db-copilot/src/db_copilot/investigation/planner.py`
  - **Nội dung:**
    - Định nghĩa ma trận các bước điều tra (Investigation Steps) cho từng intent type.
    - Ví dụ cho `SLOW_PROCEDURE`:
      1. `Step 1`: Gọi `get_ash_sql_activity` tìm các `sql_id` do procedure chạy.
      2. `Step 2`: Gọi `get_sql_statistics` cho top SQL ID tìm được.
      3. `Step 3`: Gọi `get_sql_plan` và `get_sql_plan_history` kiểm tra execution plan.
      4. `Step 4`: Gọi `get_object_metadata` kiểm tra thống kê bảng liên quan.
    - Xác lập phụ thuộc động (`dependencies`) giữa các bước.

- [ ] **Task 3.3: Unit Tests cho Intent Parser và Planner**
  - **File:** `db-copilot/tests/unit/investigation/test_planner.py`
  - **Nội dung:** Kiểm tra parser phân loại đúng các mẫu câu hỏi phổ biến, planner sinh đúng danh sách bước và dependency.

---

### GIAI ĐOẠN 4: THỰC THI ĐIỀU TRA & SOURCE CODE MAPPING (Phase 3.4)

- [ ] **Task 4.1: Quản Lý Ngữ Cảnh Điều Tra (`InvestigationContext`)**
  - **File:** `db-copilot/src/db_copilot/investigation/context.py`
  - **Nội dung:**
    - Lưu giữ trạng thái qua từng bước: `step_results`, `collected_evidence`, `errors`, `dynamic_parameters`.
    - Cung cấp hàm `resolve_param(param_expr)` để bước sau lấy giá trị từ output của bước trước.

- [ ] **Task 4.2: Thực Thi Từng Bước Điều Tra (`InvestigationExecutor`)**
  - **File:** `db-copilot/src/db_copilot/investigation/executor.py`
  - **Nội dung:**
    - Lần lượt gọi các tool qua `OracleMcpClient`.
    - Giới hạn thời gian mỗi bước (timeout: 10 giây/call).
    - Cơ chế chịu lỗi: Nếu 1 bước tùy chọn (ví dụ lấy AWR) thất bại, ghi nhận warning và vẫn tiếp tục các bước khác.

- [ ] **Task 4.3: Ánh Xạ Mã Nguồn PL/SQL (`SourceCodeMapper`)**
  - **File:** `db-copilot/src/db_copilot/investigation/source_mapper.py`
  - **Nội dung:**
    - Từ `sql_id`, truy vấn `V$ACTIVE_SESSION_HISTORY` (module, action, plsql_entry_object_id).
    - Gọi tool `get_object_source` và `get_object_dependencies` để định vị procedure name và vị trí dòng lệnh chứa query.

- [ ] **Task 4.4: Unit Tests cho Executor và Source Code Mapper**
  - **File:** `db-copilot/tests/unit/investigation/test_executor.py`
  - **Nội dung:** Test thực thi tuần tự, test truyền param động giữa 2 bước, test timeout xử lý an toàn.

---

### GIAI ĐOẠN 5: INVESTIGATION ENGINE TOÀN DIỆN (Phase 3.5)

- [ ] **Task 5.1: Xây dựng Bộ Điều Phối `InvestigationEngine`**
  - **File:** `db-copilot/src/db_copilot/investigation/engine.py`
  - **Nội dung:**
    - Kết nối toàn bộ quy trình end-to-end:
      1. User Question -> `IntentParser` -> `InvestigationPlan`.
      2. `InvestigationExecutor` thu thập dữ liệu thô qua MCP.
      3. `EvidenceNormalizer` tạo các `Evidence` objects và dựng `EvidenceGraph`.
      4. `HypothesisEngine` đánh giá và xếp hạng 5 giả thuyết gốc.
      5. `AIService` sinh kết luận cuối cùng `DiagnosisResult`.
    - Trả về đối tượng `InvestigationResult`.

- [ ] **Task 5.2: Unit & Integration Tests cho `InvestigationEngine`**
  - **File:** `db-copilot/tests/unit/investigation/test_engine.py`
  - **Nội dung:** Test kịch bản end-to-end hoàn chỉnh với mock MCP tools, thời gian chạy dưới 15 giây.

---

### GIAI ĐOẠN 6: DAILY REPORT SERVICE & SCHEDULED DELIVERY (Phase 3.6)

- [ ] **Task 6.1: Dịch Vụ Tạo Báo Cáo Hàng Ngày (`DailyReportService`)**
  - **File:** `db-copilot/src/db_copilot/application/report_service.py`
  - **Nội dung:**
    - Tổng hợp danh sách incidents phát sinh trong 24 giờ qua.
    - Tính điểm sức khỏe tổng thể (`health_score` từ 0 - 100).
    - Gọi `AIService` sinh narrative tóm tắt tình trạng và hành động cần xử lý.
    - Lưu vào bảng `daily_reports` trong PostgreSQL.

- [ ] **Task 6.2: Tích Hợp Lịch Chạy 6:00 AM vào APScheduler**
  - **File:** `db-copilot/src/db_copilot/evidence/scheduler.py`
  - **Nội dung:** Thêm cron job chạy lúc 06:00 sáng mỗi ngày: `scheduler.add_job(report_service.generate_daily, "cron", hour=6)`.

- [ ] **Task 6.3: Webhook Thông Báo (Slack / Teams / Email)**
  - **File:** `db-copilot/src/db_copilot/application/notification_service.py`
  - **Nội dung:** Gửi bản tóm tắt Daily Report và cảnh báo Incident CRITICAL tới webhook Slack/Teams nếu được cấu hình.

- [ ] **Task 6.4: Unit Tests cho Daily Report & Notifications**
  - **File:** `db-copilot/tests/unit/application/test_report_service.py`
  - **Nội dung:** Test tính đúng health_score, test sinh báo cáo không lỗi khi không có incident nào trong ngày.

---

### GIAI ĐOẠN 7: REST & WEBSOCKET API ENDPOINTS (Phase 3.7)

- [ ] **Task 7.1: API Điều Tra Bất Đồng Bộ**
  - **File:** `db-copilot/src/db_copilot/api/routes/investigate.py`
  - **Nội dung:**
    - `POST /api/v1/investigate`: Nhận `{question: str}`, đưa vào hàng đợi xử lý ngầm (background task), trả về `{id: str, status: "queued"}` ngay lập tức.
    - `GET /api/v1/investigate/{id}`: Trả về trạng thái tiến độ hoặc kết quả điều tra chi tiết (`InvestigationResult`).

- [ ] **Task 7.2: WebSocket Streaming Tiến Độ Điều Tra**
  - **File:** `db-copilot/src/db_copilot/api/routes/investigate_ws.py`
  - **Nội dung:** `WS /api/v1/ws/investigate/{id}`: Bắn sự kiện realtime về frontend mỗi khi hoàn thành một bước điều tra (Step 1 -> Step 2 -> Step 3 -> AI Diagnosis).

- [ ] **Task 7.3: API Tra Cứu Báo Cáo Hàng Ngày**
  - **File:** `db-copilot/src/db_copilot/api/routes/reports.py`
  - **Nội dung:**
    - `GET /api/v1/reports/daily`: Lấy báo cáo mới nhất.
    - `GET /api/v1/reports/daily/{date}`: Lấy báo cáo theo ngày chỉ định (YYYY-MM-DD).

- [ ] **Task 7.4: Đăng Ký Router trong FastAPI App**
  - **File:** `db-copilot/src/db_copilot/api/app.py`
  - **Nội dung:** Đăng ký các router `investigate`, `reports` vào prefix `/api/v1`.

- [ ] **Task 7.5: Unit Tests cho Investigation & Report APIs**
  - **File:** `db-copilot/tests/unit/api/test_investigate_api.py`
  - **Nội dung:** Test gọi API trả về 200/202, validate request body.

---

### GIAI ĐOẠN 8: FRONTEND WEB DASHBOARD (Phase 3.8)

- [ ] **Task 8.1: Khởi Tạo Dự Án Frontend**
  - **Thư mục:** `frontend/`
  - **Nội dung:** React 18+ (Vite), TypeScript, Tailwind CSS, Shadcn UI / Lucide Icons.

- [ ] **Task 8.2: Trang Dashboard Tổng Thể**
  - **Nội dung:**
    - Widget điểm sức khỏe cơ sở dữ liệu (`Health Score Gauge`).
    - Bảng thống kê nhanh (Active Sessions, Blocking Sessions, CPU%).
    - Danh sách Incident Feed theo mức độ nghiêm trọng (Critical/High/Medium).

- [ ] **Task 8.3: Giao Diện Điều Tra Tương Tác (Investigation Copilot Chat)**
  - **Nội dung:**
    - Khung chat hỏi đáp tự nhiên.
    - Timeline hiển thị từng bước điều tra realtime.
    - Khối hiển thị kết luận AI (`DiagnosisResult`) kèm nút xem Recommendation chi tiết.

- [ ] **Task 8.4: Trực Quan Hóa Execution Plan & Metrics**
  - **Nội dung:** Cây biểu diễn execution plan (`sql_plan`) với highlight các node Full Table Scan và Cost cao.

- [ ] **Task 8.5: Trang Báo Cáo Hàng Ngày (Daily Report Viewer)**
  - **Nội dung:** Render markdown narrative báo cáo hàng ngày kèm bộ lọc xem theo lịch.

---

### GIAI ĐOẠN 9: KIỂM THỬ TỔNG HỢP & HOÀN THIỆN (Phase 3.9)

- [ ] **Task 9.1: Kiểm tra Linting và Định dạng**
  - **Lệnh:** `ruff check .`
  - **Yêu cầu:** 0 lỗi linting.

- [ ] **Task 9.2: Kiểm Thử Toàn Diện Test Suite**
  - **Lệnh:** `pytest -v tests/`
  - **Yêu cầu:** 100% unit & integration test cases đều passed.

- [ ] **Task 9.3: Cập nhật Trạng thái Dự án & Tài liệu Hướng Dẫn**
  - **File:** `SESSION_STATE.md`, `README.md`, `docs/04-implementation/implementation-plan.md`.

---


<!-- ======================================================
     FILE: docs/04-implementation/implementation-plan.md
     ====================================================== -->

# Implementation Plan
# Kế Hoạch Triển Khai

**Sản phẩm / Product:** DB Copilot  
**Phiên bản / Version:** 0.1  
**Ngày / Date:** 2026-09-08

---

# 🇻🇳 PHẦN TIẾNG VIỆT

---

## 1. Tổng Quan Chiến Lược

Hệ thống được build theo **4 MVP**, mỗi MVP có deliverable cụ thể và success criteria đo lường được. Ưu tiên backend/engine trước, frontend sau.

### Hai project song song

| Project | Phase bắt đầu | Độc lập |
|---|---|---|
| `oracle-mcp-server` | Phase 0 | Deploy độc lập |
| `db-copilot` | Phase 1 | Phụ thuộc oracle-mcp-server |

---

## 2. Roadmap Tổng Thể

```
Phase 0 (1-2 tuần)
├── oracle-mcp-server: Setup, Oracle connection, 3 tools
└── db-copilot: Project setup, PostgreSQL, FastAPI skeleton

Phase 1 (2-3 tuần)
├── oracle-mcp-server: 32 tools, audit, security
└── db-copilot: MCP client, evidence collection, baselines

Phase 2 (2 tuần)
├── oracle-mcp-server: (stable)
└── db-copilot: Detection rules, incident engine, health engine

Phase 3 (1-2 tuần)
└── db-copilot: AI Daily Report, LLM integration

Phase 4 (2-3 tuần)
└── db-copilot: Investigation Engine, hypothesis engine

Phase 5 (1-2 tuần)
└── db-copilot: React UI, polish, documentation
```

**Tổng ước tính:** 9–14 tuần

---

## 3. Phase 0 — Foundation (1–2 tuần)

### 3.1 oracle-mcp-server

**Tasks:**
- [x] Khởi tạo Python project với `pyproject.toml`
- [x] Cài đặt `python-oracledb` thin mode
- [x] Implement `OracleConnectionPool` với async pool (`oracle/connection.py`)
- [x] Implement `AuditContext` context manager (`security/audit.py`)
- [x] MCP server entry point (`server.py`) — 6 tools registered
- [x] 6 tools: `get_database_info`, `get_top_sql`, `get_sql_statistics`, `get_active_sessions`, `get_blocking_sessions`, `get_long_running_sessions`
- [x] Unit tests với mock Oracle (`tests/unit/test_phase0_tools.py`)
- [x] Dockerfile
- [x] README với setup instructions + Claude Desktop / Cursor config
- [x] `.env.example`
- [x] `security/sanitizer.py` — credential masking
- [x] `models/response_models.py` — Pydantic output contracts

**Success Criteria:**
> `get_database_info` tool trả về database version và instance info từ Oracle thật.

### 3.2 db-copilot

**Tasks:**
- [x] Khởi tạo Python project với `pyproject.toml`
- [x] FastAPI app factory với lifespan
- [x] PostgreSQL async setup (asyncpg + SQLAlchemy)
- [x] Alembic migrations setup
- [x] Domain models: Evidence, Incident, DiagnosisResult
- [x] Settings với Pydantic Settings (env vars)
- [x] Health check endpoint: `GET /api/v1/health`
- [x] Docker Compose (api + postgres)
- [x] CI/CD pipeline skeleton (GitHub Actions)

**Success Criteria:**
> `GET /api/v1/health` trả về 200 với PostgreSQL connection status.

---

## 4. Phase 1 — Oracle MCP Complete (2–3 tuần)

### 4.1 oracle-mcp-server — Tất cả 32 Tools

**Week 1:**
- [x] `tools/sql.py`: `get_top_sql`, `get_sql_statistics`, `get_sql_wait_events`, `get_sql_execution_context`
- [x] `tools/ash.py`: `get_ash_sample`, `get_ash_sql_activity`
- [x] `tools/awr.py`: `get_awr_snapshot`, `get_awr_sql_stats`
- [x] `oracle/repositories/sql_repo.py` với Oracle queries
- [x] `oracle/repositories/awr_repo.py`, `ash_repo.py`

**Week 2:**
- [x] `tools/session.py`: 5 session tools (get_session, get_session_waits added)
- [x] `tools/plan.py`: `get_sql_plan`, `get_sql_plan_history`
- [x] `tools/object.py`: 6 object/code tools
- [x] `tools/storage.py`: 11 storage/job/health tools
- [x] Full audit system (`security/audit.py` + `sanitizer.py`)
- [x] Oracle permission grants script (`docs/grants.sql`)
- [x] MCP SDK 2.x migration (`MCPServer` + `@mcp.tool()` decorators)
- [x] `tests/conftest.py` — fake Oracle env for unit tests

**Week 3 (nếu cần):**
- [ ] Integration tests với Oracle test instance
- [ ] Error handling cho Oracle-specific errors (ORA-xxxxx)
- [ ] Connection retry logic
- [ ] Performance testing (mỗi tool < 5s)

**Success Criteria:**
> AI client (Cursor/Claude Desktop) có thể hỏi và nhận structured Oracle evidence từ tất cả 32 tools.

### 4.2 db-copilot — MCP Client & Evidence Collection

- [x] `OracleMcpClient` implementation
- [x] `SqlCollector`, `SessionCollector`, `StorageCollector`
- [x] `EvidenceNormalizer`
- [x] `EvidenceRepository` (PostgreSQL CRUD)
- [x] APScheduler setup (5-minute collection)
- [x] `BaselineEngine` (hourly recalculation)
- [x] Database migration scripts

**Success Criteria:**
> db-copilot tự động thu thập SQL metrics mỗi 5 phút và lưu vào PostgreSQL.

---

## 5. Phase 2 — Health Engine (2 tuần)

**Tasks:**
- [ ] `SqlRegressionRule`
- [ ] `BlockingSessionRule`
- [ ] `TablespaceThresholdRule`
- [ ] `JobFailureRule`
- [ ] `LongRunningSessionRule`
- [ ] `InvalidObjectRule`
- [ ] `CorrelationEngine` orchestrator
- [ ] `HypothesisEngine` (5 hypothesis definitions)
- [ ] `EvidenceGraph` builder
- [ ] `IncidentRepository` (PostgreSQL)
- [ ] API endpoints: `GET /incidents`, `GET /incidents/{id}`
- [ ] Health score calculator
- [ ] `GET /api/v1/database/status`

**Success Criteria:**
> Hệ thống tự phát hiện SQL regression mà không cần AI. Khi inject SQL chạy chậm, incident tự động được tạo trong < 10 phút.

---

## 6. Phase 3 — AI Daily Report (1–2 tuần)

**Tasks:**
- [ ] `LLMProvider` abstract class
- [ ] `OpenAIProvider` implementation
- [ ] `DiagnosisPrompt` và `ReportPrompt`
- [ ] `AIService` với fallback logic
- [ ] `ReportService` với APScheduler (6:00 AM)
- [ ] `DailyReport` PostgreSQL table + repository
- [ ] API: `GET /reports/daily`, `GET /reports/daily/{date}`
- [ ] Slack webhook delivery (optional)
- [ ] Email delivery (optional)
- [ ] `ClaudeProvider`, `GeminiProvider` (nếu cần)

**Success Criteria:**
> Daily report tự động tạo vào 6:00 AM với structured evidence và AI-generated narrative. Mỗi incident có confidence score và recommendation.

---

## 7. Phase 4 — Investigation Copilot (2–3 tuần)

**Tasks:**
- [ ] `IntentParser` (LLM-based)
- [ ] `InvestigationPlanner` (4 intent types)
- [ ] `InvestigationExecutor` với dynamic deps
- [ ] `InvestigationContext`
- [ ] `EvidenceBuilder` từ investigation results
- [ ] API: `POST /investigate`, `GET /investigate/{id}`
- [ ] Async investigation (queue-based)
- [ ] WebSocket cho streaming results
- [ ] Source code mapping (SQL_ID → Procedure → Line)

**Success Criteria:**
> User hỏi _"Why was PROC_SETTLEMENT slow at 14:32?"_ và nhận diagnosis với evidence trong < 60 giây.

---

## 8. Phase 5 — UI & Polish (1–2 tuần)

**Tasks:**
- [ ] React app setup (Vite)
- [ ] Dashboard với health score
- [ ] Incident feed
- [ ] Investigation chat interface
- [ ] SQL detail page (plan tree, metrics chart)
- [ ] Daily report page
- [ ] Responsive layout
- [ ] Dark mode

**Success Criteria:**
> DBA có thể xem dashboard, đọc daily report và hỏi investigation question chỉ từ browser.

---

## 9. Feature Priority Matrix

| Feature | MVP Phase | Priority |
|---|---|---|
| oracle-mcp-server foundation | Phase 0 | P0 |
| Read-only Oracle security | Phase 0 | P0 |
| All 32 MCP tools | Phase 1 | P0 |
| Audit logging | Phase 1 | P0 |
| Evidence collection (5-min) | Phase 1 | P0 |
| SQL baseline engine | Phase 1 | P0 |
| SQL regression detection | Phase 2 | P0 |
| Blocking detection | Phase 2 | P0 |
| Tablespace detection | Phase 2 | P0 |
| Job failure detection | Phase 2 | P1 |
| Hypothesis engine | Phase 2 | P0 |
| Evidence store (PostgreSQL) | Phase 1 | P0 |
| LLM integration | Phase 3 | P1 |
| Daily report | Phase 3 | P1 |
| AI diagnosis | Phase 3 | P1 |
| Investigation engine | Phase 4 | P1 |
| Source code mapping | Phase 4 | P1 |
| React UI | Phase 5 | P2 |
| Git correlation | Future | P2 |
| Knowledge graph | Future | P2 |
| Autonomous remediation | **Never** | ❌ |

---

## 10. Những Thứ KHÔNG Làm (Non-goals)

| Không làm | Lý do |
|---|---|
| Tự động execute bất kỳ SQL nào lên Oracle | Vi phạm nguyên tắc Human-in-control |
| Autonomous DBA | Không phù hợp với nguyên tắc security |
| Automatic SQL tuning / index / statistics | Ngoài scope MVP |
| Multi-database support (MySQL, SQL Server) | Tập trung Oracle trước |
| Complex BI reporting | Ngoài scope |

---

## 11. Risks & Mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| Oracle test instance không available | Medium | Mock Oracle với pre-recorded responses |
| LLM structured output không consistent | Medium | JSON mode, retry logic, fallback to rule-engine |
| Investigation > 60s | Medium | Per-step timeout (10s), skip optional steps |
| AWS/GCP Oracle connectivity | Low | Document VPN/network requirements |
| LLM cost overrun | Low | Token counting, caching, rate limiting |

---

---

# 🇬🇧 ENGLISH SECTION

---

## 12. Strategy Overview

Build in **4 MVPs**, each with concrete deliverables and measurable success criteria. Prioritize backend/engine first, frontend last.

### Two parallel projects

| Project | Start Phase | Independent |
|---|---|---|
| `oracle-mcp-server` | Phase 0 | Deploy independently |
| `db-copilot` | Phase 1 | Depends on oracle-mcp-server |

---

## 13. Roadmap Summary

| Phase | Duration | Key Deliverables |
|---|---|---|
| Phase 0 — Foundation | 1–2 weeks | Project setup, Oracle connection, 3 tools, PostgreSQL, FastAPI skeleton |
| Phase 1 — Oracle MCP Complete | 2–3 weeks | All 32 MCP tools, audit, evidence collection, baselines |
| Phase 2 — Health Engine | 2 weeks | 6 detection rules, hypothesis engine, incident API |
| Phase 3 — AI Daily Report | 1–2 weeks | LLM integration, daily report, delivery channels |
| Phase 4 — Investigation Copilot | 2–3 weeks | Intent parsing, investigation engine, source code mapping |
| Phase 5 — UI & Polish | 1–2 weeks | React dashboard, investigation UI |

**Total Estimate: 9–14 weeks**

---

## 14. Phase Success Criteria Summary

| Phase | Success Criterion |
|---|---|
| Phase 0 | `get_database_info` returns Oracle info; `GET /health` returns 200 |
| Phase 1 | AI client can ask any of 32 tools and get structured Oracle evidence |
| Phase 2 | System auto-detects SQL regression within 10 minutes without AI |
| Phase 3 | Daily report auto-generated at 6 AM with structured evidence and AI narrative |
| Phase 4 | User asks _"Why was PROC_X slow?"_ and gets evidence-backed diagnosis in < 60s |
| Phase 5 | DBA can use dashboard, read reports, and run investigations from browser |

---

## 15. Non-goals

- Auto-execute any SQL against Oracle — violates Human-in-control
- Autonomous DBA capabilities
- Automatic SQL tuning, index creation, or statistics gathering
- Multi-database support in MVP
- Complex BI reporting

---


<!-- ======================================================
     FILE: docs/04-implementation/test-plan.md
     ====================================================== -->

# Test Plan
# Kế Hoạch Kiểm Thử

**Sản phẩm / Product:** DB Copilot  
**Phiên bản / Version:** 0.1  
**Ngày / Date:** 2026-09-08

---

# 🇻🇳 PHẦN TIẾNG VIỆT

---

## 1. Chiến Lược Kiểm Thử Tổng Quan

Hệ thống gồm hai project: `oracle-mcp-server` và `db-copilot`. Mỗi project có test strategy riêng.

### Test Pyramid

```
                 /\
                /  \
               / E2E \        ← Scenarios (ít nhất)
              /────────\
             / Integrat. \    ← Với Oracle & PostgreSQL
            /────────────\
           /  Unit Tests   \  ← Nhiều nhất, nhanh nhất
          /────────────────\
```

---

## 2. oracle-mcp-server Test Strategy

### 2.1 Unit Tests

**Location:** `oracle-mcp-server/tests/unit/`

**Approach:** Mock Oracle connection, test tool logic và output schema.

```python
# tests/unit/tools/test_sql_tools.py

import pytest
from unittest.mock import AsyncMock, patch
from oracle_mcp.tools.sql import get_sql_statistics
from oracle_mcp.models.sql_models import SqlStatistics

@pytest.mark.asyncio
async def test_get_sql_statistics_returns_correct_schema():
    """
    Test tool trả về đúng schema, không phụ thuộc Oracle thật.
    """
    mock_row = {
        "sql_id": "8f3abc",
        "sql_text": "SELECT * FROM ACCOUNT_POSITION ...",
        "executions": 12450,
        "elapsed_time": 52300000,
        "cpu_time": 21300000,
        "buffer_gets": 182000000,
        "disk_reads": 9300000,
        "rows_processed": 4200000,
        "last_active_time": "2026-09-08 14:32:00",
        "plan_hash_value": 98237412,
        "module": "PROC_SETTLEMENT",
        "action": "UPDATE_PHASE"
    }

    with patch("oracle_mcp.oracle.repositories.sql_repo.SqlRepository.get_sql_statistics",
               new_callable=AsyncMock) as mock_repo:
        mock_repo.return_value = SqlStatistics(**mock_row)

        result = await get_sql_statistics(sql_id="8f3abc")

        assert result["sql_id"] == "8f3abc"
        assert result["executions"] == 12450
        assert result["module"] == "PROC_SETTLEMENT"

@pytest.mark.asyncio
async def test_get_blocking_sessions_returns_empty_when_no_blocking():
    with patch(...) as mock_repo:
        mock_repo.return_value = {"blocking_chains": [], "total_blocked": 0}
        result = await get_blocking_sessions()
        assert result["total_blocked"] == 0

@pytest.mark.asyncio
async def test_audit_log_written_on_success():
    """Audit log phải được ghi dù kết quả thế nào."""
    with patch("oracle_mcp.security.audit._write_audit_log") as mock_audit:
        await get_sql_statistics(sql_id="abc123")
        mock_audit.assert_called_once()
        call_args = mock_audit.call_args[0]
        assert call_args[3] == "success"  # status

@pytest.mark.asyncio
async def test_audit_log_written_on_error():
    with patch("oracle_mcp.oracle.repositories.sql_repo.SqlRepository.get_sql_statistics",
               side_effect=Exception("ORA-00942: table or view does not exist")):
        with patch("oracle_mcp.security.audit._write_audit_log") as mock_audit:
            with pytest.raises(Exception):
                await get_sql_statistics(sql_id="bad")
            mock_audit.assert_called_once()
            assert mock_audit.call_args[0][3] == "error"
```

**Danh sách test cases bắt buộc:**

| Test | Group | Priority |
|---|---|---|
| `get_sql_statistics` trả về đúng schema | SQL | P0 |
| `get_blocking_sessions` trả về empty khi không có blocking | Session | P0 |
| `get_blocking_sessions` trả về full chain khi có blocking | Session | P0 |
| `get_tablespace_usage` trả về usage% đúng | Storage | P0 |
| `get_object_source` trả về source + sql_statements | Object | P0 |
| Audit log ghi khi success | Security | P0 |
| Audit log ghi khi error | Security | P0 |
| Credentials không xuất hiện trong audit log | Security | P0 |
| Tool trả về structured error khi Oracle unreachable | Reliability | P0 |

### 2.2 Integration Tests

**Location:** `oracle-mcp-server/tests/integration/`

**Requirement:** Cần Oracle test instance (Docker Oracle XE hoặc Oracle Free)

```python
# tests/integration/test_oracle_connection.py

@pytest.mark.integration
@pytest.mark.asyncio
async def test_oracle_connection_pool_initializes():
    """Test kết nối thật đến Oracle."""
    pool = await OracleConnectionPool.initialize()
    assert pool is not None

@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_top_sql_returns_real_data():
    """Test với Oracle thật, kiểm tra data format."""
    result = await get_top_sql(metric="elapsed_time", limit=5, hours=1)
    assert isinstance(result, list)
    for sql in result:
        assert "sql_id" in sql
        assert len(sql["sql_id"]) == 13  # Oracle SQL_ID là 13 ký tự
```

---

## 3. db-copilot Test Strategy

### 3.1 Unit Tests

**Location:** `db-copilot/tests/unit/`

#### 3.1.1 Detection Rules Tests

```python
# tests/unit/correlation/test_sql_rules.py

@pytest.mark.asyncio
async def test_sql_regression_detected_when_ratio_exceeds_threshold():
    current = SqlMetric(sql_id="abc", elapsed_time_ms=10_000)
    baseline = SqlBaseline(mean_elapsed_ms=2_000, is_reliable=True, sample_count=10)

    rule = SqlRegressionRule(multiplier=3.0, mcp_client=AsyncMock())
    incident = await rule.evaluate(current, baseline)

    assert incident is not None
    assert incident.category == IncidentCategory.SQL_REGRESSION
    assert incident.severity == Severity.HIGH  # ratio = 5x

@pytest.mark.asyncio
async def test_sql_regression_not_detected_when_baseline_unreliable():
    current = SqlMetric(sql_id="abc", elapsed_time_ms=10_000)
    baseline = SqlBaseline(mean_elapsed_ms=2_000, is_reliable=False, sample_count=3)

    rule = SqlRegressionRule(multiplier=3.0, mcp_client=AsyncMock())
    incident = await rule.evaluate(current, baseline)

    assert incident is None  # Không detect khi baseline unreliable

@pytest.mark.asyncio
async def test_sql_regression_not_detected_when_ratio_below_threshold():
    current = SqlMetric(sql_id="abc", elapsed_time_ms=5_000)
    baseline = SqlBaseline(mean_elapsed_ms=3_000, is_reliable=True, sample_count=10)

    rule = SqlRegressionRule(multiplier=3.0, mcp_client=AsyncMock())
    incident = await rule.evaluate(current, baseline)

    assert incident is None  # ratio = 1.67x < 3.0

@pytest.mark.asyncio
async def test_tablespace_critical_when_above_90_pct():
    ts_data = [{"name": "APP_DATA", "used_pct": 92.5}]
    mock_mcp = AsyncMock()
    mock_mcp.call_tool.return_value = ts_data

    rule = TablespaceThresholdRule(mcp_client=mock_mcp, warning=80, critical=90)
    incidents = await rule.evaluate()

    assert len(incidents) == 1
    assert incidents[0].severity == Severity.CRITICAL
```

#### 3.1.2 Hypothesis Engine Tests

```python
# tests/unit/correlation/test_hypothesis_engine.py

def test_blocking_hypothesis_has_highest_confidence_when_blocking_detected():
    evidence = [
        Evidence(type=EvidenceType.BLOCKING_SESSION, severity=Severity.HIGH, data={}),
        Evidence(type=EvidenceType.LONG_RUNNING_SESSION, severity=Severity.MEDIUM, data={}),
    ]
    engine = HypothesisEngine()
    hypotheses = engine.rank_hypotheses(evidence)

    assert hypotheses[0].name == "Blocking / Concurrency Issue"
    assert hypotheses[0].confidence > 0.90

def test_statistics_issue_hypothesis_confidence_increases_with_supporting_evidence():
    # Only stale statistics
    evidence_weak = [Evidence(type=EvidenceType.STALE_STATISTICS, data={})]
    # Stale statistics + cardinality mismatch + regression
    evidence_strong = [
        Evidence(type=EvidenceType.STALE_STATISTICS, data={}),
        Evidence(type=EvidenceType.CARDINALITY_MISMATCH, data={}),
        Evidence(type=EvidenceType.SQL_REGRESSION, data={}),
    ]

    engine = HypothesisEngine()
    h_weak = engine.rank_hypotheses(evidence_weak)
    h_strong = engine.rank_hypotheses(evidence_strong)

    stats_weak = next(h for h in h_weak if h.name == "Statistics Issue")
    stats_strong = next(h for h in h_strong if h.name == "Statistics Issue")

    assert stats_strong.confidence > stats_weak.confidence

def test_blocking_hypothesis_confidence_reduced_when_no_blocking():
    evidence = [
        Evidence(type=EvidenceType.SQL_REGRESSION, data={}),
        Evidence(type=EvidenceType.SQL_PLAN_CHANGE, data={}),
        # NO blocking_session evidence
    ]
    engine = HypothesisEngine()
    hypotheses = engine.rank_hypotheses(evidence)

    blocking_h = next((h for h in hypotheses if h.name == "Blocking / Concurrency Issue"), None)
    # Không có required evidence → không có trong kết quả
    assert blocking_h is None
```

#### 3.1.3 Investigation Engine Tests

```python
# tests/unit/investigation/test_executor.py

@pytest.mark.asyncio
async def test_investigation_completes_within_60_seconds():
    mock_mcp = AsyncMock()
    mock_mcp.call_tool.return_value = {"data": "mocked"}

    executor = InvestigationExecutor(mcp_client=mock_mcp, ai_service=AsyncMock())

    start = time.time()
    result = await executor.execute("Why was PROC_SETTLEMENT slow at 14:32?")
    duration = time.time() - start

    assert duration < 60.0
    assert result is not None

@pytest.mark.asyncio
async def test_investigation_continues_when_optional_step_fails():
    """Investigation không fail khi optional step timeout."""
    mock_mcp = AsyncMock()
    async def mock_call(tool, args):
        if tool == "get_object_source":
            raise asyncio.TimeoutError()
        return {"data": "ok"}

    mock_mcp.call_tool = mock_call
    executor = InvestigationExecutor(mcp_client=mock_mcp, ai_service=AsyncMock())

    result = await executor.execute("Why was PROC_SETTLEMENT slow?")
    # Không raise exception
    assert result is not None
    # Source code error được ghi lại
    assert "get_object_source" in result.context_errors
```

### 3.2 Integration Tests

**Location:** `db-copilot/tests/integration/`

```python
# tests/integration/test_evidence_collection.py

@pytest.mark.integration
@pytest.mark.asyncio
async def test_sql_collector_saves_to_postgresql():
    """Test với PostgreSQL thật (Docker compose)."""
    collector = SqlCollector(real_mcp_client, real_evidence_repo)
    await collector.collect()

    metrics = await real_evidence_repo.get_recent_sql_metrics(hours=1)
    assert len(metrics) > 0

@pytest.mark.integration
@pytest.mark.asyncio
async def test_baseline_calculation_with_7_days_data():
    """Test baseline với data thật trong PostgreSQL."""
    await seed_7_days_sql_data(real_evidence_repo)
    engine = BaselineEngine(real_evidence_repo)
    await engine.recalculate()

    baseline = await real_evidence_repo.get_baseline("test_sql_id", hour=14, dow=0)
    assert baseline is not None
    assert baseline.is_reliable
    assert baseline.sample_count >= 5

@pytest.mark.integration
@pytest.mark.asyncio
async def test_sql_regression_incident_created_when_detected():
    await seed_baseline(sql_id="abc", mean_ms=1000)
    await seed_current_metric(sql_id="abc", elapsed_ms=8000)  # 8x regression

    engine = CorrelationEngine(real_repos)
    await engine.evaluate_all()

    incidents = await real_incident_repo.get_open_incidents()
    sql_incidents = [i for i in incidents if i.category == IncidentCategory.SQL_REGRESSION]
    assert len(sql_incidents) >= 1
```

---

## 4. End-to-End Scenarios

**Location:** `db-copilot/tests/scenarios/`

Ba scenarios này là **success criteria** của toàn bộ MVP:

### Scenario 1 — Auto Detection

```python
@pytest.mark.e2e
@pytest.mark.asyncio
async def test_scenario_1_auto_detection():
    """
    SQL regression trong DB → Collector phát hiện → Rule engine tạo incident
    → Evidence có đủ thông tin → Daily report gửi đến DBA
    """
    # 1. Seed baseline với normal performance
    await seed_7_days_baseline(sql_id="test_sql", mean_ms=500)

    # 2. Inject slow SQL metric (giả lập regression)
    await inject_slow_sql_metric(sql_id="test_sql", elapsed_ms=5000)  # 10x

    # 3. Trigger collection cycle
    await SqlCollector(mcp_client, repo).collect()

    # 4. Trigger detection
    await CorrelationEngine(repos).evaluate_all()

    # 5. Check incident created
    incidents = await incident_repo.get_open_incidents()
    assert any(i.category == IncidentCategory.SQL_REGRESSION for i in incidents)

    # 6. Generate daily report
    report = await report_service.generate_daily_report()
    assert "SQL Regression" in report.content_markdown
    assert "test_sql" in report.content_markdown
```

### Scenario 2 — SQL Investigation

```python
@pytest.mark.e2e
@pytest.mark.asyncio
async def test_scenario_2_sql_investigation():
    """
    User: "Why was SQL_ID 8f3abc slow yesterday?"
    → Investigation Engine → Evidence-based Diagnosis
    """
    result = await investigation_service.investigate(
        "Why was SQL_ID 8f3abc slow yesterday?"
    )

    assert result is not None
    assert result.diagnosis.confidence > 0.5
    assert len(result.evidence) > 0
    assert result.diagnosis.confidence_explanation != ""

    # Đảm bảo recommendations không có "Execute"
    for rec in result.diagnosis.recommendations:
        assert "DBA must review" in rec.note or "manually" in rec.note
```

### Scenario 3 — Procedure Investigation ⭐

```python
@pytest.mark.e2e
@pytest.mark.asyncio
async def test_scenario_3_procedure_investigation():
    """
    User: "Why was PROC_SETTLEMENT slow at 14:32?"
    → Procedure → SQL → Plan → ASH → Wait → Source → Diagnosis
    """
    import time
    start = time.time()

    result = await investigation_service.investigate(
        "Why was PROC_SETTLEMENT slow at 14:32?"
    )

    duration = time.time() - start

    # Performance requirement
    assert duration < 60.0, f"Investigation took {duration:.1f}s, exceeds 60s limit"

    # Result quality
    assert result.intent.type == IntentType.PROCEDURE_SLOW
    assert len(result.evidence) >= 3, "Must have at least 3 evidence items"
    assert result.diagnosis.confidence > 0.0
    assert len(result.diagnosis.recommendations) > 0

    # Recommendations must not suggest auto-execution
    for rec in result.diagnosis.recommendations:
        assert "automatically" not in rec.action.lower()
        assert "auto" not in rec.action.lower()
```

---

## 5. Security Tests

```python
# tests/unit/security/test_credential_handling.py

def test_oracle_credentials_not_in_audit_log():
    """Credentials tuyệt đối không được xuất hiện trong audit log."""
    from oracle_mcp.security.sanitizer import sanitize_args

    args_with_creds = {
        "sql_id": "abc123",
        "user": "db_copilot_readonly",
        "password": "SECRET_PASSWORD",
        "dsn": "prod-host:1521/ORCL"
    }

    sanitized = sanitize_args(args_with_creds)

    assert "SECRET_PASSWORD" not in str(sanitized)
    assert "password" not in sanitized  # key cũng bị remove
    assert sanitized["sql_id"] == "abc123"  # non-sensitive fields giữ nguyên

def test_llm_provider_does_not_receive_oracle_credentials():
    """Evidence package gửi cho LLM không chứa credentials."""
    package = EvidencePackage(
        question="Why slow?",
        intent=mock_intent,
        evidence=[],
        hypotheses=[]
    )

    # Serialized package không được có credential-like fields
    serialized = json.dumps(dataclasses.asdict(package))
    assert "password" not in serialized
    assert "oracle_user" not in serialized
    assert "oracle_dsn" not in serialized

def test_ai_recommendations_never_include_execute_keyword():
    """Mọi AI recommendation phải là for human review."""
    # Mock LLM trả về recommendation có "execute"
    diagnosis = DiagnosisResult(
        recommendations=[
            Recommendation(
                action="Execute: EXEC DBMS_STATS.GATHER...",
                sql="EXEC DBMS_STATS.GATHER...",
                priority="HIGH",
                note="Run this automatically"  # Bad!
            )
        ]
    )

    # Validation layer phải flag/fix này
    validated = validate_recommendations(diagnosis.recommendations)
    for rec in validated:
        assert "automatically" not in rec.note.lower()
```

---

## 6. Performance Tests

```python
# tests/performance/test_investigation_performance.py

@pytest.mark.performance
@pytest.mark.asyncio
async def test_investigation_completes_in_60_seconds():
    """Investigation time phải < 60 giây."""
    times = []
    for _ in range(5):
        start = time.time()
        await executor.execute("Why was PROC_SETTLEMENT slow?")
        times.append(time.time() - start)

    avg_time = sum(times) / len(times)
    p95_time = sorted(times)[int(len(times) * 0.95)]

    assert avg_time < 45.0, f"Average investigation time {avg_time:.1f}s exceeds 45s"
    assert p95_time < 60.0, f"P95 investigation time {p95_time:.1f}s exceeds 60s"

@pytest.mark.performance
@pytest.mark.asyncio
async def test_mcp_tool_responds_in_5_seconds():
    """Mỗi MCP tool call phải < 5 giây."""
    tools = ["get_top_sql", "get_blocking_sessions", "get_tablespace_usage"]

    for tool in tools:
        start = time.time()
        await mcp_client.call_tool(tool, {})
        duration = time.time() - start
        assert duration < 5.0, f"Tool {tool} took {duration:.1f}s"
```

---

## 7. Test Data Management

### 7.1 Oracle Test Account Setup

```sql
-- Script tạo test data trong Oracle test instance

-- Tạo slow SQL (giả lập regression)
DECLARE
  v_count NUMBER;
BEGIN
  FOR i IN 1..1000000 LOOP
    SELECT COUNT(*) INTO v_count FROM ALL_OBJECTS WHERE OBJECT_TYPE = 'TABLE';
  END LOOP;
END;
/

-- Tạo blocking session
-- Session 1 (chạy trong background):
UPDATE TEST_TABLE SET STATUS = 'LOCKED' WHERE ID = 1;

-- Session 2 (sẽ bị block):
UPDATE TEST_TABLE SET STATUS = 'UPDATE' WHERE ID = 1;
```

### 7.2 PostgreSQL Test Data Seeding

```python
# tests/fixtures/seed_data.py

async def seed_7_days_baseline(sql_id: str, mean_ms: float):
    """Seed 7 ngày dữ liệu để có reliable baseline."""
    base_time = datetime.utcnow() - timedelta(days=7)
    for day in range(7):
        for hour in range(24):
            captured_at = base_time + timedelta(days=day, hours=hour)
            # Add some variance (±10%)
            elapsed = mean_ms * random.uniform(0.9, 1.1)
            await repo.insert_sql_metric(SqlMetric(
                sql_id=sql_id,
                captured_at=captured_at,
                elapsed_time_ms=int(elapsed)
            ))
```

---

---

# 🇬🇧 ENGLISH SECTION

---

## 8. Test Strategy Overview

Two projects, each with unit → integration → E2E test layers.

| Level | oracle-mcp-server | db-copilot |
|---|---|---|
| **Unit** | Mock Oracle, test tool output schema | Mock MCP, test rules/engine |
| **Integration** | Real Oracle (Docker XE) | Real PostgreSQL (Docker) |
| **E2E / Scenarios** | — | 3 MVP scenarios with mocked Oracle |

---

## 9. Key Unit Test Requirements

### oracle-mcp-server
- Every tool returns correct Pydantic schema
- Audit log written on both success and error
- Credentials never appear in audit log
- Server returns structured error (not crash) on Oracle unreachable

### db-copilot
- SQL regression NOT detected when baseline unreliable
- SQL regression detected when `current > baseline × multiplier`
- Hypothesis confidence increases with supporting evidence
- Investigation continues when optional step fails (no crash)
- AI recommendations never suggest automatic execution

---

## 10. E2E Scenario Acceptance Criteria

| Scenario | Must Pass For MVP |
|---|---|
| **Scenario 1** — Auto Detection | SQL regression auto-detected and included in daily report |
| **Scenario 2** — SQL Investigation | Investigation returns evidence-backed diagnosis with confidence > 0.5 |
| **Scenario 3** — Procedure Investigation | Investigation completes in < 60s, produces ≥ 3 evidence items |

---

## 11. Security Test Requirements

- Oracle credentials must never appear in audit logs
- Evidence package sent to LLM must not contain Oracle credentials
- All AI recommendations must include "DBA must review manually" note
- No `execute_sql()` style tool in oracle-mcp-server

---

## 12. Performance Requirements

| Metric | Target |
|---|---|
| Investigation total time | < 60 seconds (p95) |
| MCP tool response | < 5 seconds per tool |
| Dashboard load time | < 3 seconds |
| Evidence collection cycle | < 3 minutes (5-minute interval, must complete before next cycle) |

---
