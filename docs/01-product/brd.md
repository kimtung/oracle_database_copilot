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
