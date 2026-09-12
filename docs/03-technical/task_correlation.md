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
