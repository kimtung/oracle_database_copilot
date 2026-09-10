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
