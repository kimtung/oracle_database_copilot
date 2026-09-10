# 📋 Task Breakdown: Mục 4.2 — db-copilot MCP Client & Evidence Collection

Tài liệu chi tiết phân tách **Mục 4.2** thành các task nhỏ nhất (atomic tasks), có tiêu chí nghiệm thu rõ ràng, dễ dàng triển khai và kiểm thử từng bước.

---

## 📌 Tổng Quan Phạm Vi Mục 4.2

- **Mục tiêu:** Xây dựng tầng MCP Client Gateway kết nối với `oracle-mcp-server` và bộ máy thu thập bằng chứng (`Evidence Engine`) lưu vào PostgreSQL của `db-copilot`.
- **Thư mục tác động chính:** `db-copilot/src/db_copilot/` (`mcp/`, `evidence/`, `config/`, `api/`) và `db-copilot/tests/unit/evidence/`.

---

## 📑 Danh Sách Task Chi Tiết

### GIAI ĐOẠN 1: MÔI TRƯỜNG & CẤU HÌNH (Phase 1.1)

- [ ] **Task 1.1: Bổ sung Dependencies**
  - **File:** `db-copilot/pyproject.toml`
  - **Nội dung:** Thêm `mcp>=1.0.0` và `apscheduler>=3.10.0,<4.0.0` vào danh sách `dependencies`.
  - **Tiêu chuẩn hoàn thành:** Chạy `uv pip install --system -e ".[dev]"` thành công không xung đột package.

- [ ] **Task 1.2: Mở rộng Settings**
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

- [ ] **Task 1.3: Cập nhật File Mẫu Biến Môi Trường**
  - **File:** `db-copilot/.env.example`
  - **Nội dung:** Bổ sung phần cấu hình MCP Server và Oracle target credentials.
  - **Tiêu chuẩn hoàn thành:** File `.env.example` đầy đủ ghi chú cho từng biến mới.

---

### GIAI ĐOẠN 2: TẦNG MCP CLIENT GATEWAY (Phase 1.2)

- [ ] **Task 2.1: Khởi tạo Module MCP Client**
  - **File:** `db-copilot/src/db_copilot/mcp/__init__.py`, `db-copilot/src/db_copilot/mcp/client.py`
  - **Nội dung:** Tạo class `OracleMcpClient` nhận cấu hình server command, args, env và cwd.

- [ ] **Task 2.2: Triển khai Hàm `call_tool` qua Stdio Transport**
  - **File:** `db-copilot/src/db_copilot/mcp/client.py`
  - **Nội dung:** Sử dụng `mcp.client.stdio.stdio_client` và `ClientSession` để kết nối, khởi tạo session, gọi tool theo tên và arguments, trích xuất dữ liệu TextContent / JSON.
  - **Tiêu chuẩn hoàn thành:** Trả về Python dict/list chuẩn sau khi parse JSON từ output của MCP tool.

- [ ] **Task 2.3: Đo lường và Xử lý Lỗi Cuộc gọi MCP**
  - **File:** `db-copilot/src/db_copilot/mcp/client.py`
  - **Nội dung:** Bổ sung đo thời gian thực thi `duration_ms`, bắt ngoại lệ timeout/connection error, trả về kết quả hoặc throw MCPClientError có cấu trúc.

- [ ] **Task 2.4: Unit Tests cho `OracleMcpClient`**
  - **File:** `db-copilot/tests/unit/evidence/test_mcp_client.py`
  - **Nội dung:** Test `call_tool` thành công với mock session, test khi server trả về lỗi, test khi JSON parse lỗi.
  - **Tiêu chuẩn hoàn thành:** Pytest xanh 100%, không cần chạy server thật.

---

### GIAI ĐOẠN 3: EVIDENCE REPOSITORY (Phase 1.3)

- [ ] **Task 3.1: Khởi tạo Module Evidence Repository**
  - **File:** `db-copilot/src/db_copilot/evidence/__init__.py`, `db-copilot/src/db_copilot/evidence/repository.py`
  - **Nội dung:** Khởi tạo class `EvidenceRepository` nhận SQLAlchemy `AsyncSession` hoặc `async_sessionmaker`.

- [ ] **Task 3.2: CRUD Database Instance**
  - **File:** `db-copilot/src/db_copilot/evidence/repository.py`
  - **Nội dung:** Hàm `get_or_create_default_database(name, host, service_name, version) -> Database`.

- [ ] **Task 3.3: Ghi nhận Snapshot Định kỳ**
  - **File:** `db-copilot/src/db_copilot/evidence/repository.py`
  - **Nội dung:** Hàm `create_snapshot(database_id, captured_at, active_sessions, blocking_sessions, cpu_pct, health_score, raw_data) -> Snapshot`.

- [ ] **Task 3.4: Lưu trữ SQL Metrics Hàng loạt**
  - **File:** `db-copilot/src/db_copilot/evidence/repository.py`
  - **Nội dung:** Hàm `save_sql_metrics(metrics: list[dict], database_id: UUID, snapshot_id: UUID | None)` bulk insert vào bảng `sql_metrics`.

- [ ] **Task 3.5: Truy vấn Dữ liệu Lịch sử SQL (7 ngày)**
  - **File:** `db-copilot/src/db_copilot/evidence/repository.py`
  - **Nội dung:**
    - `get_active_sql_ids(database_id: UUID, days: int = 7) -> list[str]`
    - `get_sql_metrics_history(database_id: UUID, sql_id: str, days: int = 7) -> list[SqlMetric]`

- [ ] **Task 3.6: Quản lý SQL Baseline**
  - **File:** `db-copilot/src/db_copilot/evidence/repository.py`
  - **Nội dung:**
    - `upsert_baseline(baseline: SqlBaseline)`: Cập nhật hoặc thêm mới baseline theo primary key `(database_id, sql_id, hour_of_day, day_of_week)`.
    - `get_baseline(database_id: UUID, sql_id: str, hour: int, dow: int) -> SqlBaseline | None`.

- [ ] **Task 3.7: Lưu trữ Evidence Items**
  - **File:** `db-copilot/src/db_copilot/evidence/repository.py`
  - **Nội dung:** Hàm `save_evidence(evidence: Evidence, incident_id: UUID | None = None) -> EvidenceItem`.

- [ ] **Task 3.8: Ghi Log Audit MCP Phía Client**
  - **File:** `db-copilot/src/db_copilot/evidence/repository.py`
  - **Nội dung:** Hàm `log_mcp_audit(tool_name, input_args, duration_ms, rows_returned, status, error_message, database_id)` ghi vào bảng `mcp_audit_log`.

- [ ] **Task 3.9: Unit Tests cho `EvidenceRepository`**
  - **File:** `db-copilot/tests/unit/evidence/test_repository.py`
  - **Nội dung:** Test các phương thức của repository bằng mock session hoặc SQLite in-memory.

---

### GIAI ĐOẠN 4: EVIDENCE NORMALIZER (Phase 1.4)

- [ ] **Task 4.1: Khởi tạo Class EvidenceNormalizer**
  - **File:** `db-copilot/src/db_copilot/evidence/normalizers/__init__.py`, `db-copilot/src/db_copilot/evidence/normalizers/evidence_normalizer.py`

- [ ] **Task 4.2: Chuẩn hóa SQL Regression**
  - **File:** `db-copilot/src/db_copilot/evidence/normalizers/evidence_normalizer.py`
  - **Nội dung:** Hàm `normalize_sql_regression(current_elapsed_ms, baseline, multiplier=3.0) -> Evidence | None`.
    - Bỏ qua nếu `baseline.is_reliable == False`.
    - Bỏ qua nếu `ratio < multiplier`.
    - Gán Severity: ratio >= 10 -> `CRITICAL`, >= 5 -> `HIGH`, >= 3 -> `MEDIUM`.

- [ ] **Task 4.3: Chuẩn hóa Blocking Sessions**
  - **File:** `db-copilot/src/db_copilot/evidence/normalizers/evidence_normalizer.py`
  - **Nội dung:** Hàm `normalize_blocking_chain(blocking_data: dict) -> list[Evidence]`:
    - Tạo `EvidenceType.BLOCKING_SESSION` với thông tin root blocker, blocked sessions, wait event.

- [ ] **Task 4.4: Chuẩn hóa Tablespace Usage**
  - **File:** `db-copilot/src/db_copilot/evidence/normalizers/evidence_normalizer.py`
  - **Nội dung:** Hàm `normalize_tablespace_usage(tablespaces: list[dict], warning_pct=80.0, critical_pct=90.0) -> list[Evidence]`.
    - Tạo `EvidenceType.TABLESPACE_FULL` với Severity `CRITICAL` (> 90%) hoặc `HIGH` (> 80%).

- [ ] **Task 4.5: Chuẩn hóa Failed Jobs**
  - **File:** `db-copilot/src/db_copilot/evidence/normalizers/evidence_normalizer.py`
  - **Nội dung:** Hàm `normalize_failed_jobs(failed_jobs: list[dict]) -> list[Evidence]`.
    - Tạo `EvidenceType.JOB_FAILURE` cho từng job lỗi kèm error code và message.

- [ ] **Task 4.6: Chuẩn hóa Long Running Sessions & Invalid Objects**
  - **File:** `db-copilot/src/db_copilot/evidence/normalizers/evidence_normalizer.py`
  - **Nội dung:**
    - `normalize_long_running_sessions(sessions: list[dict], threshold_sec=1800) -> list[Evidence]`
    - `normalize_invalid_objects(invalid_objects: list[dict]) -> list[Evidence]`

- [ ] **Task 4.7: Unit Tests cho `EvidenceNormalizer`**
  - **File:** `db-copilot/tests/unit/evidence/test_normalizer.py`
  - **Nội dung:** Kiểm tra đầy đủ mọi nhánh logic, tỷ lệ ngưỡng, mức độ nghiêm trọng và bỏ qua khi dữ liệu không đủ.

---

### GIAI ĐOẠN 5: COLLECTORS (Phase 1.5)

- [ ] **Task 5.1: Xây dựng BaseCollector**
  - **File:** `db-copilot/src/db_copilot/evidence/collectors/__init__.py`, `db-copilot/src/db_copilot/evidence/collectors/base.py`
  - **Nội dung:** Base class nhận `OracleMcpClient`, `EvidenceRepository`, `EvidenceNormalizer` và `database_id`.

- [ ] **Task 5.2: Triển khai SqlCollector**
  - **File:** `db-copilot/src/db_copilot/evidence/collectors/sql_collector.py`
  - **Nội dung:**
    1. Gọi tool `get_top_sql` (metric="elapsed_time", limit=100, hours=1).
    2. Tạo `Snapshot` và lưu metrics vào `sql_metrics`.
    3. Đối chiếu nhanh với baseline để sinh `EvidenceType.SQL_REGRESSION` (nếu có).

- [ ] **Task 5.3: Triển khai SessionCollector**
  - **File:** `db-copilot/src/db_copilot/evidence/collectors/session_collector.py`
  - **Nội dung:**
    1. Gọi `get_active_sessions`, `get_blocking_sessions`, `get_long_running_sessions`.
    2. Cập nhật số active & blocking sessions vào `Snapshot`.
    3. Chuẩn hóa và lưu trữ các `Evidence` blocking/long-running.

- [ ] **Task 5.4: Triển khai StorageCollector**
  - **File:** `db-copilot/src/db_copilot/evidence/collectors/storage_collector.py`
  - **Nội dung:**
    1. Gọi `get_tablespace_usage`, `get_failed_jobs`, `get_invalid_objects`.
    2. Chuẩn hóa và lưu trữ các `Evidence` cảnh báo dung lượng và lỗi job.

- [ ] **Task 5.5: Unit Tests cho Collectors**
  - **File:** `db-copilot/tests/unit/evidence/test_collectors.py`
  - **Nội dung:** Mock MCP client responses và mock repository để kiểm tra logic điều phối thu thập của cả 3 collectors.

---

### GIAI ĐOẠN 6: BASELINE ENGINE (Phase 1.6)

- [ ] **Task 6.1: Khởi tạo Class BaselineEngine**
  - **File:** `db-copilot/src/db_copilot/evidence/baseline_engine.py`
  - **Nội dung:** Nhận `EvidenceRepository` và cấu hình số ngày cửa sổ trượt (mặc định 7 ngày).

- [ ] **Task 6.2: Thuật toán Lọc Outliers**
  - **File:** `db-copilot/src/db_copilot/evidence/baseline_engine.py`
  - **Nội dung:** Hàm `_remove_outliers(samples: list[float]) -> list[float]`: Loại bỏ giá trị ngoài khoảng `mean ± 2 * stddev`.

- [ ] **Task 6.3: Thuật toán Tính toán Chỉ số Thống kê**
  - **File:** `db-copilot/src/db_copilot/evidence/baseline_engine.py`
  - **Nội dung:** Tính `mean`, `stddev`, `p50` (median), `p95` (95th percentile) bằng thư viện `statistics` hoặc thuật toán mảng.

- [ ] **Task 6.4: Cơ chế Đánh giá Độ tin cậy (Reliability)**
  - **File:** `db-copilot/src/db_copilot/evidence/baseline_engine.py`
  - **Nội dung:** Nếu số mẫu sau khi lọc `>= 5` -> `is_reliable = True`; nếu `< 5` -> `is_reliable = False`.

- [ ] **Task 6.5: Triển khai Hàm `recalculate`**
  - **File:** `db-copilot/src/db_copilot/evidence/baseline_engine.py`
  - **Nội dung:**
    - Lấy danh sách `sql_id` hoạt động trong 7 ngày.
    - Lặp qua 24 giờ x 7 ngày trong tuần.
    - Tính baseline và gọi `repo.upsert_baseline`.

- [ ] **Task 6.6: Unit Tests cho `BaselineEngine`**
  - **File:** `db-copilot/tests/unit/evidence/test_baseline_engine.py`
  - **Nội dung:** Test lọc nhiễu, test tính đúng p50/p95/mean/stddev, test gắn cờ `is_reliable` chính xác.

---

### GIAI ĐOẠN 7: SCHEDULER & APP INTEGRATION (Phase 1.7)

- [ ] **Task 7.1: Quản lý AsyncIOScheduler**
  - **File:** `db-copilot/src/db_copilot/evidence/scheduler.py`
  - **Nội dung:** Class `EvidenceScheduler` đóng gói `AsyncIOScheduler`, định nghĩa các hàm wrapper chạy an toàn (bắt ngoại lệ không để crash scheduler).

- [ ] **Task 7.2: Đăng ký Định kỳ Các Jobs**
  - **File:** `db-copilot/src/db_copilot/evidence/scheduler.py`
  - **Nội dung:**
    - Job `collect_sql`: interval 5 phút.
    - Job `collect_sessions`: interval 5 phút.
    - Job `collect_storage`: interval 5 phút.
    - Job `recalculate_baselines`: interval 1 giờ.

- [ ] **Task 7.3: Tích hợp vào FastAPI Lifespan**
  - **File:** `db-copilot/src/db_copilot/api/app.py`
  - **Nội dung:**
    - Khi startup: Nếu `settings.enable_scheduler` là `True`, khởi động `scheduler.start()`.
    - Khi shutdown: Gọi `scheduler.shutdown()` để kết thúc các task ngầm an toàn.

- [ ] **Task 7.4: Unit Tests cho Scheduler Lifecycle**
  - **File:** `db-copilot/tests/unit/evidence/test_scheduler.py`
  - **Nội dung:** Test start/stop scheduler, test cờ enable/disable scheduler.

---

### GIAI ĐOẠN 8: KIỂM THỬ TỔNG HỢP & HOÀN THIỆN (Phase 1.8)

- [ ] **Task 8.1: Kiểm tra Linting và Định dạng Mã Nguồn**
  - **Lệnh:** `ruff check .`
  - **Yêu cầu:** Không có bất kỳ lỗi syntax, import, hay typing cảnh báo nào.

- [ ] **Task 8.2: Chạy Toàn Bộ Test Suite**
  - **Lệnh:** `pytest -v tests/`
  - **Yêu cầu:** 100% test cases của cả Mục 3.2 và Mục 4.2 đều passed.

- [ ] **Task 8.3: Cập nhật Trạng thái Dự án**
  - **File:** `SESSION_STATE.md` và `docs/04-implementation/implementation-plan.md`
  - **Nội dung:** Đánh dấu hoàn thành Mục 4.2 và chuẩn bị bước vào Phase 2 (Correlation Engine).
