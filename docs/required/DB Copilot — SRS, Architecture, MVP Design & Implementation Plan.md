# DB Copilot
## AI Database Health & Investigation Copilot for Oracle Database

**Version:** 0.1  
**Status:** MVP Design  
**Target Database:** Oracle Database  
**Primary Users:** DBA, Database Developer, Backend Developer, System Engineer  
**Architecture Principle:** Read-only Observation + Evidence-based AI Diagnosis + Human-controlled Remediation

---

# 1. Executive Summary

DB Copilot là một hệ thống AI hỗ trợ DBA/Developer giám sát, điều tra và chẩn đoán vấn đề hiệu năng của Oracle Database.

DB Copilot không phải là chatbot Oracle thông thường.

Thay vì người dùng hỏi:

> "Oracle `db file sequential read` là gì?"

DB Copilot tập trung vào những câu hỏi thực tế:

> "Database sáng nay có vấn đề gì?"

> "SQL nào hôm qua bị regression?"

> "Tại sao procedure `PROC_SETTLEMENT` lúc 14:32 chạy 18 phút trong khi bình thường chỉ mất 2 phút?"

> "SQL này chậm do index, execution plan, statistics hay database đang bị quá tải?"

> "Có vấn đề nào cần DBA xử lý hôm nay không?"

Hệ thống tự động thu thập dữ liệu từ Oracle, phát hiện anomaly, liên kết các evidence và sử dụng AI để đưa ra diagnosis.

Kiến trúc tổng quát:

```text
                    ┌──────────────────────┐
                    │      DBA / Dev       │
                    └──────────┬───────────┘
                               │
                       Question / Report
                               │
                    ┌──────────▼───────────┐
                    │      DB Copilot      │
                    │                      │
                    │ Intent / Investigation│
                    │ Evidence Correlation │
                    │ AI Diagnosis         │
                    └──────────┬───────────┘
                               │
                         MCP Protocol
                               │
                    ┌──────────▼───────────┐
                    │   Oracle MCP Server  │
                    │                      │
                    │ Read-only Tools      │
                    │ Evidence Gateway     │
                    └──────────┬───────────┘
                               │
                         Read-only User
                               │
                    ┌──────────▼───────────┐
                    │    Oracle Database   │
                    │                      │
                    │ AWR / ASH / V$       │
                    │ SQL / PLAN           │
                    │ Session / Wait       │
                    │ Jobs / Storage       │
                    │ PL/SQL Source        │
                    └──────────────────────┘
```

---

# 2. Product Vision

## 2.1 Vision

Xây dựng một "AI Database Engineer" có khả năng quan sát Oracle Database liên tục và hỗ trợ con người trả lời:

1. Database đang có vấn đề gì?
2. Vấn đề xảy ra khi nào?
3. SQL/session/job nào liên quan?
4. Nguyên nhân có khả năng là gì?
5. Evidence nào chứng minh điều đó?
6. Nên kiểm tra hoặc xử lý gì tiếp theo?

---

# 3. Product Principles

## 3.1 AI không trực tiếp điều khiển Database

Nguyên tắc:

> **AI can observe. AI can reason. AI can recommend. Human controls the database.**

AI:

- được phép đọc
- được phép phân tích
- được phép đưa ra hypothesis
- được phép đề xuất SQL/action

AI không:

- INSERT
- UPDATE
- DELETE
- ALTER
- DROP
- CREATE
- EXECUTE procedure
- chạy remediation tự động

Ngay cả khi AI đề xuất:

```sql
EXEC DBMS_STATS.GATHER_TABLE_STATS(...);
```

hệ thống chỉ hiển thị recommendation.

Không có:

```text
[Execute]
```

---

# 4. Problem Statement

Trong môi trường Oracle thực tế, khi một vấn đề xảy ra, DBA/Developer thường phải kiểm tra nhiều nguồn:

```text
AWR
ASH
V$SQL
V$SESSION
Execution Plan
Wait Events
Tablespace
Jobs
Alert Log
PL/SQL Source
Statistics
Indexes
Application Logs
Deployment History
```

Vấn đề là các dữ liệu này nằm rời rạc.

Ví dụ:

```text
SQL_ID
   ↓
Execution Plan
   ↓
Wait Event
   ↓
Table
   ↓
Statistics
   ↓
Procedure
   ↓
Source Code
```

Con người phải tự liên kết các thông tin này.

DB Copilot sẽ xây dựng lớp:

> **Evidence Correlation**

để tự động liên kết chúng.

---

# 5. Functional Requirements

## FR-001 — Database Health Monitoring

Hệ thống phải có khả năng kiểm tra:

- CPU
- Memory
- IO
- Sessions
- Processes
- Tablespace
- TEMP
- UNDO
- Redo
- Log switch
- Blocking sessions
- Long-running sessions
- SQL performance
- Scheduler jobs
- Invalid objects
- Oracle errors

---

## FR-002 — SQL Performance Monitoring

Hệ thống phải phát hiện:

- SQL chạy chậm
- SQL tăng execution time
- SQL tăng CPU
- SQL tăng logical reads
- SQL tăng physical reads
- SQL tăng executions
- SQL regression
- execution plan change
- cardinality mismatch
- unusual wait events

Ví dụ:

```text
SQL_ID: 8f3abc

Normal execution time:
210 ms

Current:
4.2 sec

Increase:
20x

Plan:
Old    → 18473291
Current → 98237412

Physical Reads:
+920%

Estimated rows:
120

Actual rows:
4,320

Possible cause:
Cardinality estimation / statistics issue
```

---

# 6. FR-003 — Procedure / Function Investigation

User có thể hỏi:

> Why was PROC_SETTLEMENT slow at 14:32?

Hệ thống phải có khả năng:

```text
Procedure
   ↓
Executions
   ↓
SQL executed
   ↓
SQL_ID
   ↓
Execution Plan
   ↓
Wait Event
   ↓
Object
   ↓
Statistics
   ↓
Source Code
```

Sau đó tạo diagnosis.

---

# 7. FR-004 — PL/SQL Source Intelligence

MCP Server phải có khả năng đọc:

- Procedure
- Function
- Package specification
- Package body
- Trigger
- View
- Dependencies

Ví dụ:

```text
PROC_SETTLEMENT
    |
    +-- UPDATE ACCOUNT
    |
    +-- INSERT SETTLEMENT
    |
    +-- SELECT POSITION
    |
    +-- CALL PROC_CALCULATE
```

AI không cần nhận toàn bộ 5.000 dòng source.

Thay vào đó:

```text
Oracle Source
      ↓
Parser
      ↓
Procedure structure
      ↓
SQL statements
      ↓
Relevant source fragment
      ↓
LLM
```

---

# 8. FR-005 — Daily Health Report

Mỗi sáng hệ thống tạo:

# Database Morning Briefing

Ví dụ:

```text
Database Health: 82/100

CRITICAL
1. SQL_ID 8f3abc regressed 20x
   210ms → 4.2s

WARNING
2. Tablespace APP_DATA reached 87%

WARNING
3. 3 Scheduler jobs failed

INFO
4. CPU normal

INFO
5. No blocking sessions detected
```

---

# 9. FR-006 — Evidence-based Diagnosis

Mỗi diagnosis phải có:

```text
Observation
Diagnosis
Evidence
Confidence
Recommendation
```

Ví dụ:

```text
Observation:
PROC_SETTLEMENT took 18m24s at 14:32.

Diagnosis:
Likely SQL execution plan regression.

Confidence:
91%

Evidence:
- SQL_ID 8f3abc consumed 91% of total DB time
- Plan hash changed
- Physical reads increased 920%
- Estimated rows: 120
- Actual rows: 4,320
- Statistics last updated 18 days ago
- No blocking detected
- CPU remained normal

Recommendation:
Review statistics and execution plan before remediation.
```

---

# 10. Non-functional Requirements

## NFR-001 Security

Oracle credentials must not be provided to LLM.

Architecture:

```text
AI Application
      X
      │
      │ no direct DB connection
      X
Oracle

AI
 ↓
MCP
 ↓
Read-only Oracle account
```

---

## NFR-002 Least Privilege

Oracle MCP user chỉ có quyền cần thiết để đọc:

```text
V$ views
DBA_HIST*
DBA_SCHEDULER*
ALL_SOURCE
ALL_OBJECTS
ALL_DEPENDENCIES
ALL_ARGUMENTS
statistics
storage metadata
```

Exact grants sẽ được xác định theo Oracle version và deployment model.

---

## NFR-003 Auditability

Mỗi MCP request phải được audit:

```text
timestamp
user
database
tool
arguments
duration
status
rows
```

Ví dụ:

```json
{
  "timestamp": "...",
  "database": "PROD01",
  "tool": "get_sql_plan_history",
  "sql_id": "8f3abc",
  "duration_ms": 132,
  "status": "success"
}
```

---

# 11. System Architecture

## 11.1 Logical Architecture

```text
┌───────────────────────────────────────────────┐
│                   UI / API                    │
│                                               │
│ Dashboard | Daily Report | Investigation      │
└──────────────────────┬────────────────────────┘
                       │
                       ▼
┌───────────────────────────────────────────────┐
│              Investigation Engine             │
│                                               │
│ Intent Parser                                 │
│ Investigation Planner                         │
│ Evidence Collector                            │
│ Correlation Engine                            │
│ Hypothesis Engine                             │
└──────────────────────┬────────────────────────┘
                       │
                       ▼
┌───────────────────────────────────────────────┐
│                  AI Layer                     │
│                                               │
│ Diagnosis                                     │
│ Explanation                                   │
│ Recommendation                                │
└──────────────────────┬────────────────────────┘
                       │
                       ▼
┌───────────────────────────────────────────────┐
│              Oracle MCP Server                │
│                                               │
│ SQL Tools                                     │
│ Session Tools                                 │
│ AWR / ASH Tools                               │
│ Storage Tools                                 │
│ Job Tools                                     │
│ Code Intelligence Tools                       │
└──────────────────────┬────────────────────────┘
                       │
                       ▼
                 Oracle Database
```

---

# 12. MCP Architecture

MCP Server không nên là:

```text
execute_sql(sql)
```

Mặc dù Oracle account là read-only.

Thiết kế tốt hơn:

```text
get_top_sql()
get_sql_statistics()
get_sql_plan()
get_sql_plan_history()
get_active_sessions()
get_blocking_sessions()
get_session_waits()
get_tablespace_usage()
get_scheduler_job_status()
get_scheduler_job_history()
get_object_source()
get_object_dependencies()
get_object_metadata()
```

MCP trở thành:

> **Oracle Observability & Evidence Gateway**

thay vì generic SQL gateway.

---

# 13. MCP Tool Groups

## Group 1 — SQL

```text
get_top_sql
get_sql_statistics
get_sql_plan
get_sql_plan_history
get_sql_wait_events
get_sql_execution_context
```

---

## Group 2 — Session

```text
get_active_sessions
get_session
get_session_waits
get_blocking_sessions
get_long_running_sessions
```

---

## Group 3 — AWR / ASH

```text
get_awr_snapshot
get_awr_sql_stats
get_awr_sql_plan
get_ash_sample
get_ash_sql_activity
```

---

## Group 4 — Storage

```text
get_tablespace_usage
get_datafile_usage
get_segment_growth
get_temp_usage
get_undo_usage
```

---

## Group 5 — Job

```text
get_scheduler_job_status
get_scheduler_job_history
get_running_jobs
get_failed_jobs
```

---

## Group 6 — Database Health

```text
get_database_parameters
get_instance_status
get_resource_usage
get_redo_statistics
get_alert_events
get_invalid_objects
```

---

## Group 7 — Code Intelligence

```text
get_object_source
get_procedure_source
get_function_source
get_package_spec
get_package_body
get_object_metadata
get_object_arguments
get_object_dependencies
get_dependency_graph
```

---

# 14. Code Intelligence Architecture

Đây là một phần rất quan trọng của sản phẩm.

Không chỉ:

```text
Database → SQL
```

mà:

```text
Database
   ↓
SQL
   ↓
PL/SQL Object
   ↓
Procedure / Package
   ↓
Source Code
   ↓
Source Line
```

Ví dụ:

```text
SQL_ID 8f3abc
      ↓
PACKAGE PKG_SETTLEMENT
      ↓
PROC_SETTLEMENT
      ↓
Line 247
      ↓
UPDATE ACCOUNT_POSITION
```

---

# 15. Source Code Historical Limitation

Cần phân biệt:

```text
LAST_DDL_TIME
```

với:

```text
Historical source code
```

`LAST_DDL_TIME` chỉ chứng minh object đã được DDL.

Nó không chứng minh:

> "Code change này gây ra performance regression."

Muốn kết luận chính xác cần:

```text
Git
+
Deployment history
+
Source snapshot
```

Do đó architecture tương lai nên hỗ trợ:

```text
Oracle Source
       +
Git
       +
Deployment Metadata
       ↓
Code → Performance Correlation
```

---

# 16. Investigation Engine

Đây là "bộ não" thực sự của hệ thống.

Input:

```text
Why was PROC_SETTLEMENT slow at 14:32?
```

Pipeline:

```text
Question
   ↓
Intent Parser
   ↓
Investigation Plan
   ↓
MCP Calls
   ↓
Evidence Collection
   ↓
Evidence Normalization
   ↓
Correlation
   ↓
Hypothesis Generation
   ↓
Evidence Validation
   ↓
Root Cause
   ↓
Recommendation
```

---

# 17. Example Investigation

Question:

```text
Why was PROC_SETTLEMENT slow at 14:32?
```

Investigation Engine tự tạo:

```text
1. Find procedure
2. Find executions
3. Find SQL executed
4. Identify expensive SQL
5. Compare historical performance
6. Check plan changes
7. Check ASH
8. Check wait events
9. Check blocking
10. Check CPU
11. Check IO
12. Check statistics
13. Inspect source code
14. Correlate evidence
```

---

# 18. Hypothesis Engine

Không nên trả lời:

> "The problem is statistics."

Ngay lập tức.

Thay vào đó:

```text
Hypothesis A:
Statistics issue
Confidence: 87%

Hypothesis B:
Execution plan regression
Confidence: 72%

Hypothesis C:
Data volume increase
Confidence: 61%

Hypothesis D:
IO contention
Confidence: 34%

Hypothesis E:
CPU saturation
Confidence: 12%
```

Sau đó Evidence Engine kiểm tra từng hypothesis.

---

# 19. Evidence Model

Mỗi evidence có thể có:

```json
{
  "type": "sql_plan_change",
  "source": "DBA_HIST_SQLSTAT",
  "timestamp": "...",
  "sql_id": "8f3abc",
  "old_plan": 12345,
  "new_plan": 67890,
  "severity": "high"
}
```

Các evidence được liên kết:

```text
Evidence
   ↓
Entity
   ↓
Relationship
```

Ví dụ:

```text
PROC_SETTLEMENT
      |
      | executes
      ↓
SQL_ID 8f3abc
      |
      | uses
      ↓
PLAN 67890
      |
      | accesses
      ↓
ACCOUNT_POSITION
      |
      | has
      ↓
INDEX IDX_ACCOUNT_POSITION
```

---

# 20. Evidence Store

Không nên mỗi lần user hỏi đều query toàn bộ Oracle.

Có thể xây dựng Evidence Store:

```text
Oracle
  ↓
Collector
  ↓
Normalization
  ↓
PostgreSQL
```

Lưu:

- historical metrics
- anomaly
- SQL metadata
- plan history
- health snapshots
- investigation evidence
- audit logs

Oracle vẫn là source of truth.

PostgreSQL là:

> **AI Evidence / Historical Analytics Store**

---

# 21. Recommended MVP Technology Stack

## Backend

```text
.NET 8
ASP.NET Core
```

Lý do:

- phù hợp background của developer
- dễ xây REST API
- dễ viết MCP server
- ODP.NET
- background workers
- dependency injection
- production ready

---

## Database

### Oracle

Source system.

### PostgreSQL

Evidence Store.

---

## AI

Có thể thiết kế abstraction:

```text
ILLMProvider

   ├── OpenAI
   ├── Claude
   └── Gemini
```

Không hard-code một model.

---

## Frontend

MVP:

```text
React
```

hoặc thậm chí:

```text
ASP.NET + simple dashboard
```

Nếu mục tiêu là build nhanh, frontend không nên là trọng tâm MVP đầu tiên.

---

# 22. MVP Strategy

Không nên build toàn bộ hệ thống ngay.

Chia thành 4 MVP.

---

# MVP-1 — Oracle Health Collector

## Objective

Chứng minh:

> Có thể kết nối Oracle read-only và thu thập evidence một cách an toàn.

### Scope

SQL:

```text
V$SQL
DBA_HIST_SQLSTAT
DBA_HIST_SQL_PLAN
```

Session:

```text
V$SESSION
V$SESSION_WAIT
```

Storage:

```text
DBA_DATA_FILES
DBA_FREE_SPACE
DBA_SEGMENTS
```

Job:

```text
DBA_SCHEDULER_JOB_RUN_DETAILS
DBA_SCHEDULER_JOBS
```

Code:

```text
ALL_SOURCE
ALL_OBJECTS
ALL_DEPENDENCIES
```

### Deliverable

MCP Server có khoảng:

```text
10–15 tools
```

và một CLI test client.

---

# MVP-2 — Database Health Engine

## Objective

Tự động phát hiện vấn đề.

Rules:

```text
SQL runtime regression
CPU anomaly
IO anomaly
Blocking session
Tablespace threshold
Failed job
Long-running session
Invalid object
```

Output:

```json
{
  "severity": "HIGH",
  "category": "SQL_REGRESSION",
  "sql_id": "8f3abc",
  "observation": "...",
  "evidence": []
}
```

---

# MVP-3 — AI Daily DBA Report

## Objective

Biến raw evidence thành report.

Pipeline:

```text
Collector
   ↓
Rules
   ↓
Evidence
   ↓
LLM
   ↓
Daily Report
```

Ví dụ:

```text
DB HEALTH REPORT
Date: 2026-09-08

Health Score: 82

Critical
---------
SQL_ID 8f3abc regressed 20x.

Likely cause:
Execution plan regression.

Evidence:
...

Recommendation:
Review execution plan and statistics.
```

---

# MVP-4 — Investigation Copilot

Đây mới là MVP tạo khác biệt lớn.

User hỏi:

```text
Why was PROC_SETTLEMENT slow at 14:32?
```

AI tự lập investigation plan.

```text
Question
 ↓
Plan
 ↓
MCP
 ↓
Evidence
 ↓
Correlation
 ↓
Diagnosis
```

---

# 23. MVP Priority

| Feature | Priority |
|---|---:|
| Oracle MCP | P0 |
| Read-only security | P0 |
| SQL monitoring | P0 |
| AWR/ASH | P0 |
| Execution plan | P0 |
| Tablespace | P0 |
| Jobs | P1 |
| Source code | P1 |
| Rule engine | P0 |
| Evidence store | P1 |
| Daily report | P1 |
| AI diagnosis | P1 |
| Investigation engine | P1 |
| Git correlation | P2 |
| Knowledge graph | P2 |
| Autonomous remediation | NOT MVP |

---

# 24. MVP-1 Detailed Architecture

```text
                  ┌──────────────┐
                  │ MCP Client   │
                  └──────┬───────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Oracle MCP      │
                │ Server          │
                ├─────────────────┤
                │ SQL Tools       │
                │ Session Tools   │
                │ Storage Tools   │
                │ Job Tools       │
                │ Code Tools      │
                └────────┬────────┘
                         │
                    ODP.NET
                         │
                         ▼
                ┌─────────────────┐
                │ Oracle Database │
                └─────────────────┘
```

---

# 25. MVP-1 Project Structure

```text
db-copilot/
│
├── src/
│   │
│   ├── OracleMcpServer/
│   │   ├── Tools/
│   │   │   ├── Sql/
│   │   │   ├── Session/
│   │   │   ├── Storage/
│   │   │   ├── Jobs/
│   │   │   └── Code/
│   │   │
│   │   ├── Oracle/
│   │   │   ├── OracleConnectionFactory.cs
│   │   │   └── OracleQueryExecutor.cs
│   │   │
│   │   ├── Security/
│   │   └── Audit/
│   │
│   ├── HealthEngine/
│   │
│   ├── InvestigationEngine/
│   │
│   ├── AiEngine/
│   │
│   └── Api/
│
├── tests/
│
├── docs/
│
└── docker/
```

---

# 26. First MCP Tools

MVP should start with:

```text
get_database_info

get_top_sql

get_sql_statistics

get_sql_plan

get_sql_plan_history

get_active_sessions

get_blocking_sessions

get_session_waits

get_tablespace_usage

get_scheduler_job_history

get_object_source

get_object_metadata

get_object_dependencies

get_ash_activity

get_awr_sql_stats
```

15 tools are sufficient for the first prototype.

---

# 27. MCP Tool Contract Example

## get_sql_statistics

Input:

```json
{
  "sql_id": "8f3abc"
}
```

Output:

```json
{
  "sql_id": "8f3abc",
  "executions": 12450,
  "elapsed_time_ms": 52300000,
  "cpu_time_ms": 21300000,
  "buffer_gets": 182000000,
  "disk_reads": 9300000,
  "rows_processed": 4200000,
  "last_active_time": "...",
  "plan_hash_value": 98237412
}
```

AI nhận structured evidence thay vì raw SQL output.

---

# 28. Source Tool Contract

## get_object_source

Input:

```json
{
  "owner": "APP",
  "object_name": "PROC_SETTLEMENT",
  "object_type": "PROCEDURE"
}
```

Output:

```json
{
  "owner": "APP",
  "object_name": "PROC_SETTLEMENT",
  "object_type": "PROCEDURE",
  "status": "VALID",
  "last_ddl_time": "...",
  "source_hash": "...",
  "source": "...",
  "dependencies": []
}
```

---

# 29. Source Code Mapping

Hệ thống cố gắng xây dựng:

```text
SQL_ID
   ↓
Execution Context
   ↓
PL/SQL Object
   ↓
Source Line
```

Mapping phải có trạng thái:

```text
exact
inferred
unavailable
```

Không được giả định mapping luôn chính xác.

---

# 30. Detection Engine

Detection engine dùng deterministic rules trước AI.

Ví dụ:

```text
IF current_elapsed > historical_avg × 3
THEN SQL_REGRESSION
```

Hoặc:

```text
IF tablespace_usage > 85%
THEN STORAGE_WARNING
```

Hoặc:

```text
IF blocked_session_count > 0
THEN BLOCKING_INCIDENT
```

AI không quyết định anomaly đầu tiên.

---

# 31. Baseline Engine

Sau khi MVP ổn định, xây historical baseline.

Ví dụ:

```text
PROC_SETTLEMENT

09:00
Normal: 1m40s – 2m30s

14:32
Actual: 18m24s
```

Baseline có thể theo:

```text
hour
day of week
business date
execution count
data volume
```

Điều này quan trọng vì:

> 10 giây không phải lúc nào cũng chậm.

---

# 32. Health Score

Có thể xây score:

```text
100
│
├── SQL Performance     -10
├── Blocking             -0
├── Storage              -5
├── Jobs                 -3
├── CPU                  -0
├── IO                   -8
└── Errors               -2
```

Result:

```text
Health Score = 72
```

Nhưng score chỉ là UX.

Evidence mới là nguồn quyết định.

---

# 33. Daily Report Architecture

```text
Scheduler
    ↓
Collector
    ↓
Detection Engine
    ↓
Evidence Store
    ↓
Correlation
    ↓
AI Diagnosis
    ↓
Report Generator
    ↓
Email / Teams / Slack / Dashboard
```

---

# 34. Report Structure

```text
# DB Morning Briefing

Health Score: 82/100

## Critical

### SQL Regression
SQL_ID: 8f3abc

Runtime:
210ms → 4.2s

Confidence:
91%

Evidence:
...

## Warning

### Tablespace
APP_DATA:
87%

Trend:
+2.1% / day

Estimated full:
6 days

## Jobs

3 failed jobs.

## Recommendations

1. Review SQL execution plan.
2. Validate table statistics.
3. Check index effectiveness.

No automatic database changes were executed.
```

---

# 35. Investigation UI

UI nên tập trung vào:

```text
┌─────────────────────────────────────┐
│ Why was PROC_SETTLEMENT slow?       │
└─────────────────────────────────────┘

Timeline
─────────────────────────────────────

14:20  Normal
14:30  CPU normal
14:31  SQL plan changed
14:32  Runtime increased
14:33  Physical reads increased
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
✓ Statistics stale
✓ No blocking
✓ CPU normal

Source Code
─────────────────────────────────────
PROC_SETTLEMENT
Line 247

UPDATE ACCOUNT_POSITION ...
```

---

# 36. Roadmap

## Phase 0 — Foundation

Duration: 1–2 weeks

Build:

```text
.NET solution
Oracle connection
MCP framework
logging
configuration
Docker
basic tests
```

---

## Phase 1 — Oracle MCP

Duration: 2–3 weeks

Build:

```text
15 MCP tools
read-only account
audit
structured responses
```

Success criteria:

> AI client có thể hỏi và lấy được Oracle evidence.

---

## Phase 2 — Health Engine

Duration: 2 weeks

Build:

```text
SQL regression
blocking
tablespace
jobs
resource anomaly
```

Success criteria:

> Hệ thống tự phát hiện các vấn đề cơ bản mà không cần LLM.

---

## Phase 3 — Evidence Store

Duration: 1–2 weeks

Build PostgreSQL:

```text
database
snapshot
sql_metric
sql_plan
wait_event
anomaly
incident
evidence
audit
```

Success criteria:

> Có historical evidence để so sánh.

---

## Phase 4 — AI Diagnosis

Duration: 1–2 weeks

Build:

```text
Evidence → Prompt → LLM → Diagnosis
```

LLM output phải structured:

```json
{
  "diagnosis": "...",
  "confidence": 0.91,
  "evidence": [],
  "recommendations": []
}
```

---

## Phase 5 — Investigation Engine

Duration: 2–4 weeks

Build:

```text
Intent Parser
Investigation Planner
Tool Selection
Evidence Correlation
Hypothesis Engine
```

Success criteria:

User có thể hỏi:

```text
Why was procedure X slow at time Y?
```

và hệ thống tự điều tra.

---

# 37. MVP Success Criteria

MVP được coi là thành công nếu có thể thực hiện end-to-end:

### Scenario 1

```text
Database có SQL regression
        ↓
Collector phát hiện
        ↓
Rule engine tạo incident
        ↓
MCP lấy evidence
        ↓
AI phân tích
        ↓
Daily report
```

---

### Scenario 2

```text
User:
Why was SQL_ID 8f3abc slow yesterday?

        ↓

Investigation Engine

        ↓

Plan comparison
ASH
Wait event
CPU
IO
Statistics

        ↓

Diagnosis
```

---

### Scenario 3

```text
User:
Why was PROC_SETTLEMENT slow at 14:32?

        ↓

Procedure
        ↓
SQL
        ↓
Plan
        ↓
ASH
        ↓
Wait
        ↓
Source code
        ↓
Diagnosis
```

Đây là scenario quan trọng nhất.

---

# 38. Những thứ KHÔNG làm trong MVP

Không nên làm:

```text
Autonomous DBA
Automatic SQL tuning
Automatic index creation
Automatic statistics gathering
Automatic SQL execution
Automatic database changes
Full knowledge graph
Multi-cloud database support
10 loại database
Complex frontend
```

MVP phải tập trung:

> **Oracle + Evidence + Diagnosis**

---

# 39. Differentiation

Một chatbot thông thường:

```text
User
 ↓
Question
 ↓
LLM
 ↓
Answer
```

DB Copilot:

```text
User
 ↓
Question
 ↓
Investigation Engine
 ↓
Oracle MCP
 ↓
Real Database Evidence
 ↓
Correlation
 ↓
Hypothesis
 ↓
Validation
 ↓
AI
 ↓
Evidence-based Diagnosis
```

Đây là điểm khác biệt cốt lõi.

---

# 40. Long-term Architecture

Sau MVP, hệ thống có thể phát triển thành:

```text
                         ┌───────────────┐
                         │     User      │
                         └───────┬───────┘
                                 │
                         ┌───────▼───────┐
                         │  DB Copilot   │
                         └───────┬───────┘
                                 │
               ┌─────────────────┼─────────────────┐
               │                 │                 │
               ▼                 ▼                 ▼
        Health Agent      Investigation Agent   Report Agent
               │                 │                 │
               └─────────────────┼─────────────────┘
                                 │
                         Evidence Engine
                                 │
                         ┌───────▼───────┐
                         │ Oracle MCP    │
                         └───────┬───────┘
                                 │
       ┌──────────────┬──────────┼──────────┬─────────────┐
       ▼              ▼          ▼          ▼             ▼
     Oracle          Git       Deploy      Logs       Monitoring
```

---

# 41. Future Feature — Code Performance Correlation

Đây có thể trở thành một feature rất mạnh:

```text
Git Commit
    ↓
Deployment
    ↓
Procedure changed
    ↓
SQL changed
    ↓
Plan changed
    ↓
Performance degraded
```

AI có thể trả lời:

> "Performance regression bắt đầu khoảng 8 phút sau deployment version 2.14.3. Procedure PROC_SETTLEMENT được thay đổi trong deployment này. SQL_ID 8f3abc có plan hash mới và elapsed time tăng 18x."

Đây là bước tiến từ:

> Database monitoring

sang:

> **Application + Database observability**

---

# 42. Future Feature — Database Knowledge Graph

Entity:

```text
Database
Instance
Session
SQL
Plan
Procedure
Package
Table
Index
Statistics
Job
Wait Event
Deployment
Git Commit
```

Relationship:

```text
Procedure
 ├─ executes → SQL
 ├─ depends_on → Table
 └─ changed_by → Deployment

SQL
 ├─ uses → Plan
 ├─ accesses → Table
 └─ waits_on → IO

Deployment
 └─ contains → Git Commit
```

Khi đó câu hỏi:

> "What changed before this incident?"

sẽ trở nên rất mạnh.

---

# 43. Final Product Definition

DB Copilot không nên được định vị là:

> "AI Chatbot for Oracle"

Mà là:

> **AI-powered Database Observability and Investigation Platform**

hoặc ngắn hơn:

> **AI Database Engineer**

Nó có 3 capability chính:

```text
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

# 44. Core Principle

Toàn bộ hệ thống có thể được cô đọng thành:

```text
             OBSERVE
                 ↓
             COLLECT
                 ↓
             CORRELATE
                 ↓
             INVESTIGATE
                 ↓
               REASON
                 ↓
              EXPLAIN
                 ↓
            RECOMMEND
                 ↓
           HUMAN DECIDES
```

Không phải:

```text
AI
 ↓
EXECUTE
```

Mà là:

```text
AI
 ↓
EVIDENCE
 ↓
REASONING
 ↓
RECOMMENDATION
 ↓
HUMAN
```

Đây là nguyên tắc kiến trúc và security quan trọng nhất của sản phẩm.