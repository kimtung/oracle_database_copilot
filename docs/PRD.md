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
