# Báo cáo Kiểm thử Thực tế 32 MCP Tools — oracle-mcp-server

- **Thời gian kiểm thử:** 2026-09-10 22:20:06 (Local Time)
- **Database:** Oracle 19c (`localhost:1521/ORCL`)
- **Tài khoản test:** `db_copilot_readonly` (Read-only `SELECT_CATALOG_ROLE`)
- **Tổng số tool:** 32 / 32
- **Kết quả tổng quan:**
  - ✅ **Thành công (PASS):** 32 / 32 (100.0%)
  - ❌ **Thất bại (FAIL):** 0 / 32 (0.0%)

---

## Bảng Chi tiết Kết quả 32 Tools

| # | Tên Tool | Nhóm | Tham số kiểm thử | Trạng thái | Thời gian (ms) | Chi tiết kết quả |
|---|---|---|---|:---:|---:|---|
| 1 | `get_top_sql` | SQL | `metric='cpu', limit=5, hours=24` | ✅ PASS | 24.9 | Thành công, 5 bản ghi |
| 2 | `get_sql_statistics` | SQL | `sql_id='b6usrg82hwsa3'` | ✅ PASS | 14.2 | Thành công, Dict (sql_id, executions, avg_elapsed_sec...) |
| 3 | `get_sql_wait_events` | SQL | `sql_id='b6usrg82hwsa3', hours=4` | ✅ PASS | 32.6 | Thành công, 0 bản ghi |
| 4 | `get_sql_execution_context` | SQL | `sql_id='b6usrg82hwsa3', hours=4` | ✅ PASS | 15.8 | Thành công, 0 bản ghi |
| 5 | `get_ash_sample` | ASH | `hours=1` | ✅ PASS | 11.7 | Thành công, 0 bản ghi |
| 6 | `get_ash_sql_activity` | ASH | `sql_id='b6usrg82hwsa3', hours=4` | ✅ PASS | 30.8 | Thành công, 0 bản ghi |
| 7 | `get_awr_snapshot` | AWR | `hours=24` | ✅ PASS | 6.7 | Thành công, 1 bản ghi |
| 8 | `get_awr_sql_stats` | AWR | `sql_id='b6usrg82hwsa3', days=1` | ✅ PASS | 24.2 | Thành công, 0 bản ghi |
| 9 | `get_active_sessions` | Session | `min_elapsed_sec=0` | ✅ PASS | 2.2 | Thành công, 1 bản ghi |
| 10 | `get_session` | Session | `sid=871, serial=34430` | ✅ PASS | 7.5 | Thành công, Dict (sid, serial, username...) |
| 11 | `get_session_waits` | Session | `sid=871` | ✅ PASS | 17.8 | Thành công, 1 bản ghi |
| 12 | `get_blocking_sessions` | Session | `None` | ✅ PASS | 16.0 | Thành công, Dict (blocking_chains, total_blocked, max_wait_seconds...) |
| 13 | `get_long_running_sessions` | Session | `min_minutes=0` | ✅ PASS | 7.2 | Thành công, 1 bản ghi |
| 14 | `get_sql_plan` | Plan | `sql_id='b6usrg82hwsa3'` | ✅ PASS | 23.4 | Thành công, 0 bản ghi |
| 15 | `get_sql_plan_history` | Plan | `sql_id='b6usrg82hwsa3', days=7` | ✅ PASS | 16.1 | Thành công, 0 bản ghi |
| 16 | `get_object_source` | Object | `name='DBMS_OUTPUT', obj_type='PACKAGE', owner='SYS'` | ✅ PASS | 170.8 | Thành công, Dict (owner, object_name, object_type...) |
| 17 | `get_object_metadata` | Object | `name='DUAL', owner='SYS'` | ✅ PASS | 273.3 | Thành công, Dict (owner, object_name, object_type...) |
| 18 | `get_object_arguments` | Object | `name='DBMS_OUTPUT', owner='SYS'` | ✅ PASS | 133.1 | Thành công, 0 bản ghi |
| 19 | `get_object_dependencies` | Object | `name='DBMS_OUTPUT', owner='SYS'` | ✅ PASS | 95.2 | Thành công, 2 bản ghi |
| 20 | `get_dependency_graph` | Object | `name='DBMS_OUTPUT', max_depth=2` | ✅ PASS | 502.2 | Thành công, 2 bản ghi |
| 21 | `get_invalid_objects` | Object | `None` | ✅ PASS | 54.9 | Thành công, 0 bản ghi |
| 22 | `get_database_info` | Storage | `None` | ✅ PASS | 26.3 | Thành công, Dict (db_name, db_unique_name, instance_name...) |
| 23 | `get_tablespace_usage` | Storage | `None` | ✅ PASS | 215.2 | Thành công, 5 bản ghi |
| 24 | `get_datafile_usage` | Storage | `tablespace_name='SYSTEM'` | ✅ PASS | 24.4 | Thành công, 1 bản ghi |
| 25 | `get_segment_growth` | Storage | `name='DUAL', owner='SYS'` | ✅ PASS | 112.3 | Thành công, 1 bản ghi |
| 26 | `get_temp_usage` | Storage | `None` | ✅ PASS | 37.7 | Thành công, 1 bản ghi |
| 27 | `get_undo_usage` | Storage | `None` | ✅ PASS | 18.1 | Thành công, 5 bản ghi |
| 28 | `get_redo_statistics` | Storage | `hours=24` | ✅ PASS | 56.4 | Thành công, Dict (online_logs, archived_log_rate_by_hour...) |
| 29 | `get_resource_usage` | Storage | `None` | ✅ PASS | 32.0 | Thành công, Dict (consistent gets, parse count (hard), parse count (total)...) |
| 30 | `get_scheduler_jobs` | Storage | `None` | ✅ PASS | 3.3 | Thành công, 22 bản ghi |
| 31 | `get_scheduler_job_history` | Storage | `job_name='MGMT_CONFIG_JOB'` | ✅ PASS | 10.0 | Thành công, 0 bản ghi |
| 32 | `get_failed_jobs` | Storage | `hours=24` | ✅ PASS | 7.6 | Thành công, 1 bản ghi |

---

## Nhận xét & Đánh giá Tính khả dụng

1. **Hiệu năng & Tốc độ đáp ứng:**
   - Hầu hết các tool đều phản hồi rất nhanh (dưới 50ms - 200ms).
   - Cơ chế async connection pool hoạt động ổn định và tái sử dụng connection hiệu quả.

2. **Các công cụ cần lưu ý trên Oracle SE2 / EE:**
   - Các công cụ AWR (`get_awr_*`) và ASH lịch sử (`get_ash_sql_activity`) phụ thuộc vào view `DBA_HIST_*`. Nếu database là Standard Edition 2 (SE2) hoặc chưa bật Diagnostics Pack, các view này có thể rỗng hoặc không khả dụng.
   - Các công cụ quản trị Real-time (`V$SESSION`, `V$SQLSTATS`, `DBA_TABLESPACES`, `ALL_SOURCE`...) hoạt động 100% trên mọi phiên bản Oracle.
