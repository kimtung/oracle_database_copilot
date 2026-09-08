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
