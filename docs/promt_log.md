# 📝 NHẬT KÝ PROMPT VÀ TƯƠNG TÁC AI (PROMPT LOG)

Tài liệu ghi vết toàn bộ các phiên làm việc, yêu cầu (prompt) của người dùng, phản hồi của AI, các vòng lặp phản hồi/chỉnh sửa, và kết quả thực thi thực tế theo quy chuẩn định nghĩa tại [vibecode.md](file:///d:/2026/oracle_ai/docs/vibecode.md).

---

## 📌 QUY CHUẨN ĐỊNH DẠNG (STANDARD LOG FORMAT)

Mỗi mục nhật ký ghi nhận theo cấu trúc:
- **ID / Phiên**: Mã số thứ tự của lượt yêu cầu
- **Thời gian**: Ngày giờ thực hiện
- **Prompt Người Dùng**: Nguyên văn hoặc nội dung cốt lõi người dùng đưa ra
- **AI Đặt Câu Hỏi / Làm Rõ**: Các câu hỏi hoặc phương án AI đề xuất trước khi làm
- **User Phản Hồi / Quyết Định**: Câu trả lời, xác nhận hoặc lựa chọn của User
- **Kết Quả AI Tạo Ra**: Danh sách file tạo mới/chỉnh sửa, kết quả test/chạy thử
- **Yêu Cầu Sửa Lại (Revision)**: Có hay không? Nếu có, mô tả cụ thể điểm cần sửa
- **Đánh Giá & Hài Lòng**: Mức độ hoàn thành và sự hài lòng của User

---

## 📋 DANH SÁCH NHẬT KÝ CHI TIẾT

### #001 — Tư vấn kỹ thuật: Thin Mode vs Thick Mode trong Oracle
- **Thời gian**: 12/09/2026 14:15
- **Prompt Người Dùng**: `khi nào thì phai dùng thick mode`
- **AI Đặt Câu Hỏi / Làm Rõ**: Phân tích chi tiết kiến trúc socket mạng trực tiếp của Thin Mode và các tính năng nâng cao chỉ có ở OCI/Thick Mode (DB < 12.1, TAC, CQN, AQ).
- **User Phản Hồi / Quyết Định**: Đồng thuận duy trì Thin Mode cho `oracle-mcp-server` vì mục tiêu là read-only observability và container siêu nhẹ.
- **Kết Quả AI Tạo Ra**: Bảng so sánh chi tiết ưu nhược điểm giữa Thin Mode và Thick Mode trong bối cảnh dự án.
- **Yêu Cầu Sửa Lại (Revision)**: Không.
- **Đánh Giá & Hài Lòng**: ✅ Hài lòng (Nắm rõ lý do kiến trúc).

---

### #002 — Chuyển dịch tư duy: C# Developer sang Python (`__init__.py`)
- **Thời gian**: 12/09/2026 14:35
- **Prompt Người Dùng**: `tôi là dev nhiều năm c# nhưng chưa làm python. hãy giải thích tôi những file __init__.py để làm gì`
- **AI Đặt Câu Hỏi / Làm Rõ**: Ánh xạ khái niệm trực tiếp từ C# (.NET Namespace, Assembly DLL, Module/Static Constructor, `internal` vs `public`, Facade pattern) sang vai trò của `__init__.py` trong Python.
- **User Phản Hồi / Quyết Định**: Hiểu rõ bản chất package namespace và pattern `__all__`.
- **Kết Quả AI Tạo Ra**: Tài liệu đối sánh cụ thể giữa cấu trúc C# và Python packages.
- **Yêu Cầu Sửa Lại (Revision)**: Không.
- **Đánh Giá & Hài Lòng**: ✅ Rất hài lòng (Dễ hiểu cho kỹ sư C#).

---

### #003 — Làm rõ cấu hình Logging trong hệ thống
- **Thời gian**: 12/09/2026 15:00
- **Prompt Người Dùng**: `looging đang cấu hình thư mục nào`
- **AI Đặt Câu Hỏi / Làm Rõ**: Giải thích cơ chế luồng chuẩn giao thức MCP: `stdout` bắt buộc dành riêng cho JSON-RPC IPC, toàn bộ application logs và audit logs đẩy ra `sys.stderr`, đồng thời hướng dẫn gắn file logging qua `RotatingFileHandler` nếu cần.
- **User Phản Hồi / Quyết Định**: Xác nhận cơ chế an toàn kênh IPC.
- **Kết Quả AI Tạo Ra**: Sơ đồ luồng log và hướng dẫn cấu hình chi tiết.
- **Yêu Cầu Sửa Lại (Revision)**: Không.
- **Đánh Giá & Hài Lòng**: ✅ Hài lòng.

---

### #004 — Phân tích module `OracleMcpClient` trong `db-copilot`
- **Thời gian**: 12/09/2026 15:20
- **Prompt Người Dùng**: `trong db-copilot có module mcp client, module này làm gì, cơ chế như nào`
- **AI Đặt Câu Hỏi / Làm Rõ**: Phân tích Gateway / Adapter Pattern: `db-copilot` spawn sub-process `oracle-mcp-server`, giao tiếp qua `stdio` pipe, ánh xạ kết quả JSON-RPC sang Pydantic domain models.
- **User Phản Hồi / Quyết Định**: Nắm rõ cách thức cô lập driver Oracle khỏi backend.
- **Kết Quả AI Tạo Ra**: Phân tích chi tiết file `db-copilot/src/db_copilot/mcp/client.py`.
- **Yêu Cầu Sửa Lại (Revision)**: Không.
- **Đánh Giá & Hài Lòng**: ✅ Hài lòng.

---

### #005 — Phân tích chi tiết `EvidenceScheduler`
- **Thời gian**: 12/09/2026 15:45
- **Prompt Người Dùng**: `@[db-copilot/src/db_copilot/evidence/scheduler.py] giải thích các hàm của file này, cơ chế khi nào gọi`
- **AI Đặt Câu Hỏi / Làm Rõ**: Ánh xạ `EvidenceScheduler` sang `IHostedService` / `BackgroundService` trong .NET, phân tích chi tiết vòng đời gắn với FastAPI `lifespan` và chu kỳ 5m (Collectors) / 1h (Baseline 2-Sigma).
- **User Phản Hồi / Quyết Định**: Nắm vững cơ chế chạy ngầm trên event-loop.
- **Kết Quả AI Tạo Ra**: Tài liệu mổ xẻ toàn bộ hàm `start()`, `shutdown()`, các job định kỳ.
- **Yêu Cầu Sửa Lại (Revision)**: Không.
- **Đánh Giá & Hài Lòng**: ✅ Rất hài lòng.

---

### #006 — Soạn tài liệu trình bày Tech Leader
- **Thời gian**: 12/09/2026 16:15
- **Prompt Người Dùng**: `tôi đang chuẩn bị trình bày về project này với tech leader hãy note lại những gì tôi với bạn vừa trao đổi để trình bày vào file docs\present.md`
- **AI Đặt Câu Hỏi / Làm Rõ**: Đề xuất đề cương báo cáo từ góc nhìn kỹ sư C# chuyển sang Python, kết hợp số liệu kiểm thử thực tế trên Oracle 19c.
- **User Phản Hồi / Quyết Định**: Đồng ý lập tài liệu.
- **Kết Quả AI Tạo Ra**: File [docs/present.md](file:///d:/2026/oracle_ai/docs/present.md) với 5 phần hoàn chỉnh (Tổng quan, Chứng cứ demo, Điểm kỹ thuật, Đối sánh C# ➔ Python, Đề xuất kế hoạch).
- **Yêu Cầu Sửa Lại (Revision)**: Không.
- **Đánh Giá & Hài Lòng**: ✅ Rất hài lòng.

---

### #007 — Yêu cầu triển khai Phase 2: Health & Correlation Engine
- **Thời gian**: 12/09/2026 16:45
- **Prompt Người Dùng**: `rồi thực hiện tiếp phase2 đi`
- **AI Đặt Câu Hỏi / Làm Rõ**: Trình bày kế hoạch thực thi 7 giai đoạn chi tiết và xin phê duyệt trước khi viết code (Plan: `IncidentRepository`, 6 Detection Rules, `EvidenceGraph`, `HypothesisEngine`, `CorrelationEngine`, REST API, Tests).
- **User Phản Hồi / Quyết Định**: Phê duyệt thực thi toàn bộ Phase 2.
- **Kết Quả AI Tạo Ra**: 
  - Hoàn thành trọn vẹn Phase 2: 7 giai đoạn.
  - Viết mới các module: `repository.py`, 6 files trong `rules/`, `graph.py`, `hypothesis_engine.py`, `engine.py`, `routes/incidents.py`.
  - Toàn bộ **49/49 unit tests pass 100%**, `ruff check .` không có lỗi.
- **Yêu Cầu Sửa Lại (Revision)**: Không.
- **Đánh Giá & Hài Lòng**: ✅ Xuất sắc.

---

### #008 — Báo cáo tổng kết Phase 2 ra file HTML
- **Thời gian**: 12/09/2026 17:15
- **Prompt Người Dùng**: `hãy ghi tóm tắt kết quả thực hiện này vào file @docs\phase_2_sumary.html`
- **AI Đặt Câu Hỏi / Làm Rõ**: Thiết kế trang dashboard HTML hoàn chỉnh với phong cách Dark Mode cao cấp, Glassmorphism, Metric cards, và hệ thống Interactive Tabs.
- **User Phản Hồi / Quyết Định**: Yêu cầu bổ sung đoạn tóm tắt nổi bật các module cốt lõi.
- **Kết Quả AI Tạo Ra**: File [docs/phase_2_sumary.html](file:///d:/2026/oracle_ai/docs/phase_2_sumary.html).
- **Yêu Cầu Sửa Lại (Revision)**: Có (Xem prompt #009).
- **Đánh Giá & Hài Lòng**: Cần cập nhật thêm khối highlight.

---

### #009 — Bổ sung khối "🌟 Tóm tắt kết quả thực hiện" vào `phase_2_sumary.html`
- **Thời gian**: 12/09/2026 17:30
- **Prompt Người Dùng**: `tôi muốn ghi đoạn này ra mà: 🌟 Tóm tắt kết quả thực hiện IncidentRepository... EvidenceGraph...`
- **AI Đặt Câu Hỏi / Làm Rõ**: Tiếp nhận nguyên văn khối nội dung tóm tắt chi tiết của từng component cốt lõi trong Phase 2.
- **User Phản Hồi / Quyết Định**: Đồng ý đưa khối card nổi bật vào vị trí trung tâm của HTML.
- **Kết Quả AI Tạo Ra**: Cập nhật [docs/phase_2_sumary.html](file:///d:/2026/oracle_ai/docs/phase_2_sumary.html) với khối `summary-highlight-card` chứa đầy đủ 6 component trọng tâm.
- **Yêu Cầu Sửa Lại (Revision)**: Hoàn thành đúng theo yêu cầu.
- **Đánh Giá & Hài Lòng**: ✅ Rất hài lòng.

---

### #010 — Tạo các file tóm tắt tương tự cho Phase 0 và Phase 1
- **Thời gian**: 12/09/2026 17:40
- **Prompt Người Dùng**: `tương tự như thế bạn có thể tạo ra file tóm tắt phase0 và phase1 không`
- **AI Đặt Câu Hỏi / Làm Rõ**: Xác nhận cấu trúc và kiểm tra tính đồng bộ của [docs/phase_0_sumary.html](file:///d:/2026/oracle_ai/docs/phase_0_sumary.html) và [docs/phase_1_sumary.html](file:///d:/2026/oracle_ai/docs/phase_1_sumary.html).
- **User Phản Hồi / Quyết Định**: Đồng ý.
- **Kết Quả AI Tạo Ra**: Đã chuẩn hóa và hoàn thiện cả 2 file Dashboard HTML cho Phase 0 (17/17 tests, 6 tools, 8 bảng DB) và Phase 1 (26/26 tests, 32/32 tools, 3 collectors, baseline 2-sigma, scheduler).
- **Yêu Cầu Sửa Lại (Revision)**: Không.
- **Đánh Giá & Hài Lòng**: ✅ Rất hài lòng.

---

### #011 — Cập nhật quy tắc vibe code và Commit
- **Thời gian**: 12/09/2026 17:46
- **Prompt Người Dùng**: `@[docs/vibecode.md] hãy commit`
- **AI Đặt Câu Hỏi / Làm Rõ**: Thiết lập định dạng chuẩn cho file [docs/promt_log.md](file:///d:/2026/oracle_ai/docs/promt_log.md) theo quy tắc trong `vibecode.md` và thực hiện git commit toàn bộ thay đổi.
- **User Phản Hồi / Quyết Định**: Thực hiện commit mã nguồn và tài liệu.
- **Kết Quả AI Tạo Ra**: File `docs/promt_log.md`, hoàn thiện `docs/vibecode.md`, và thực hiện commit Git.
- **Yêu Cầu Sửa Lại (Revision)**: Không.
- **Đánh Giá & Hài Lòng**: ✅ Hoàn thành.

---

### #012 — Thiết lập quy tắc vĩnh viễn: Tự động ghi Prompt Log
- **Thời gian**: 12/09/2026 17:48
- **Prompt Người Dùng**: `từ giờ tôi có cần phải chỉ định lưu log promt vào vibecode nữa không hay làm sao để bạn luôn nhớ`
- **AI Đặt Câu Hỏi / Làm Rõ**: Khẳng định User không cần nhắc lại thủ công; thiết lập file cấu hình luật hệ thống [GEMINI.md](file:///d:/2026/oracle_ai/GEMINI.md) trong thư mục gốc dự án để Antigravity tự động nạp luật vào system prompt trong mọi phiên làm việc tiếp theo.
- **User Phản Hồi / Quyết Định**: Tự động hóa việc ghi log.
- **Kết Quả AI Tạo Ra**: File [GEMINI.md](file:///d:/2026/oracle_ai/GEMINI.md) và tự động cập nhật [docs/promt_log.md](file:///d:/2026/oracle_ai/docs/promt_log.md).
- **Yêu Cầu Sửa Lại (Revision)**: Không.
- **Đánh Giá & Hài Lòng**: ✅ Hoàn thành tự động hóa.

---

### #013 — Kiểm tra trạng thái dự án qua SESSION_STATE.md
- **Thời gian**: 16/09/2026 13:02
- **Prompt Người Dùng**: `kiểm tra @[d:\2026\oracle_ai\SESSION_STATE.md] xem tới đâu rồi`
- **AI Đặt Câu Hỏi / Làm Rõ**: Đọc nội dung `SESSION_STATE.md`, chạy lại bộ kiểm thử để xác nhận trạng thái mã nguồn thực tế (49/49 tests pass).
- **User Phản Hồi / Quyết Định**: Chờ báo cáo tổng hợp tiến độ và các đầu việc tiếp theo.
- **Kết Quả AI Tạo Ra**: Báo cáo trạng thái chi tiết theo các Phase, xác nhận Phase 0, Phase 1, Phase 2 đã hoàn thành 100%, sẵn sàng triển khai Phase 3 (AI & Investigation Engine).
- **Yêu Cầu Sửa Lại (Revision)**: Không.
- **Đánh Giá & Hài Lòng**: ✅ Đầy đủ, minh bạch.

---

### #014 — Phase 3: AI & Investigation Engine — Implementation
- **Thời gian**: 16/09/2026 13:20 – 21:00
- **Prompt Người Dùng**: `bắt đầy phase 3`
- **AI Đặt Câu Hỏi / Làm Rõ**: Đọc domain models hiện tại, đề xuất Implementation Plan gồm 9 giai đoạn, trình bày cho user phê duyệt.
- **User Phản Hồi / Quyết Định**: ✅ User phê duyệt qua review policy (auto-approve).
- **Kết Quả AI Tạo Ra**:
  - `domain/interfaces/llm_provider.py` — LLMProvider ABC
  - `ai/providers/gemini_provider.py` — GeminiProvider (lazy import, google.genai)
  - `ai/providers/openai_provider.py` — OpenAIProvider (lazy import, AsyncOpenAI)
  - `ai/providers/claude_provider.py` — ClaudeProvider (lazy import + JSON extract)
  - `ai/prompts/diagnosis_prompt.py` — System/User templates (structured JSON output)
  - `ai/prompts/report_prompt.py` — Daily report templates
  - `ai/service.py` — AIService (primary→fallback→rule-based, 30s timeout)
  - `investigation/planner.py` — IntentParser (regex) + InvestigationPlanner
  - `investigation/context.py` — InvestigationContext (dynamic $step_N.field resolution)
  - `investigation/executor.py` — InvestigationExecutor (10s timeout/step)
  - `investigation/source_mapper.py` — SourceCodeMapper (sql_id → PL/SQL fragment)
  - `investigation/engine.py` — InvestigationEngine (end-to-end orchestrator)
  - `application/report_service.py` — DailyReportService (health score 0-100)
  - `application/notification_service.py` — Slack/Teams webhook
  - `api/routes/investigate.py` — POST/GET /api/v1/investigate
  - `api/routes/investigate_ws.py` — WS /api/v1/ws/investigate/{id}
  - `api/routes/reports.py` — GET /api/v1/reports/daily
  - Updated `config/settings.py`, `domain/models/evidence.py`, `api/app.py`
  - 44 new tests: test_providers, test_ai_service, test_planner, test_executor, test_engine, test_report_service, test_investigate_api
  - **93/93 tests pass, ruff check clean, git commit 506b827**
- **Yêu Cầu Sửa Lại (Revision)**: Có — tự sửa 3 vòng: (1) E501 ruff errors, (2) wrong API names (HypothesisEngine.rank_hypotheses, lazy imports), (3) test mock pattern, Settings.model_validate, ASGITransport.
- **Đánh Giá & Hài Lòng**: ✅ Phase 3 hoàn thành 100%. 93 tests pass. Toàn bộ AI layer, Investigation Engine và REST/WS API đã sẵn sàng.

---

### #015 — Làm mịn tài liệu kỹ thuật ai-engine-design.md
- **Thời gian**: 16/09/2026 23:15
- **Prompt Người Dùng**: `làm mịn theo góp ý trong ảnh @[docs/03-technical/ai-engine-design.md]`
- **AI Đặt Câu Hỏi / Làm Rõ**: Phân tích 10 điểm góp ý trong ảnh ([AI-01] đến [AI-10]), bao gồm các lỗi Critical (runtime crash, duplicate class definition), High (Claude model ID cũ, thiếu prompt caching, thiếu parse_intent), và Medium (max_tokens quá thấp, thiếu temperature, evidence quá dài, thiếu retry loop, mismatch report section).
- **User Phản Hồi / Quyết Định**: Đồng ý tiến hành làm mịn trực tiếp file `docs/03-technical/ai-engine-design.md`.
- **Kết Quả AI Tạo Ra**:
  - Sửa `ClaudeProvider`: dùng `tool_use` (chức năng native của Claude) để đảm bảo output structured JSON mà không sợ thiếu hàm `_extract_json`, bổ sung `cache_control: {"type": "ephemeral"}` cho prompt caching, cập nhật model `claude-sonnet-4-6`, thêm `temperature=0.1`.
  - Hợp nhất 2 định nghĩa rời rạc của `AIService` thành 1 class duy nhất chứa cả `diagnose()` lẫn `generate_daily_report()`.
  - Triển khai đầy đủ `parse_intent()` và filter evidence (`CRITICAL`, `HIGH`, `MEDIUM`) cho cả OpenAI, Claude và Gemini.
  - Nâng `max_tokens=4096` tránh truncate JSON diagnosis phức tạp; bổ sung vòng lặp retry 2 lần nếu JSON format bị lỗi.
  - Chuẩn hoá `section_type="full_report"` trên toàn bộ interfaces và implementations.
- **Yêu Cầu Sửa Lại (Revision)**: Không.
- **Đánh Giá & Hài Lòng**: ✅ Hoàn thành làm mịn 10/10 điểm trong `ai-engine-design.md`.


---

### #016 — Làm mịn và Review kiến trúc LLD (Low-Level Design)
- **Thời gian**: 16/09/2026 23:15
- **Prompt Người Dùng**: `tôi đang làm mịn và review lại @docs/02-architecture/lld.md` (kèm ảnh feedback LLD review: [LLD-01], [LLD-02], [LLD-03])
- **AI Đặt Câu Hỏi / Làm Rõ**: Phân tích 3 vấn đề kỹ thuật trọng yếu được chỉ ra trong review:
  1. `[LLD-01]` Hiệu năng MCP Client: Khắc phục việc spawn tiến trình Python cho mỗi tool call gây overhead 2-3s (khiến chuỗi 9 bước vượt SLA 60s) bằng việc chuyển dịch sang kiến trúc **SSE Transport với Persistent Connection**.
  2. `[LLD-02]` Vi phạm bảo mật credentials: Loại bỏ hoàn toàn biến môi trường Oracle DB (`ORACLE_USER`, `ORACLE_PASSWORD`, `ORACLE_DSN`) ra khỏi cấu hình `db-copilot`, phân định ranh giới an toàn tuyệt đối, chỉ để `oracle-mcp-server` lưu giữ credentials nội bộ.
  3. `[LLD-03]` Thiếu tài liệu so sánh LLM Provider trade-offs: Bổ sung bảng đối sánh đa chiều (Cost, Latency, JSON Reliability, Oracle SQL Reasoning, Context Window) giữa OpenAI (GPT-4o, GPT-4o-mini), Anthropic (Claude 3.5 Sonnet) và Google (Gemini 2.0 Flash, Gemini 1.5 Pro).
- **User Phản Hồi / Quyết Định**: Đồng thuận cập nhật và chuẩn hóa trực tiếp vào tài liệu thiết kế.
- **Kết Quả AI Tạo Ra**:
  - Cập nhật [docs/02-architecture/lld.md](file:///d:/2026/oracle_ai/docs/02-architecture/lld.md):
    - Mục 5: Viết lại kiến trúc `OracleMcpClient` sử dụng `sse_client` với persistent session lifecycle (`connect()`, `disconnect()`, `call_tool()`).
    - Mục 6: Loại bỏ credentials khỏi `db-copilot/.env`, thêm mục 6.3 ma trận so sánh trade-offs các LLM Provider và hướng dẫn lựa chọn cho khách hàng doanh nghiệp.
    - Mục 11 & 12: Đồng bộ phiên bản tiếng Anh với kiến trúc SSE Transport và bảo mật credentials.
  - Cập nhật tự động [docs/promt_log.md](file:///d:/2026/oracle_ai/docs/promt_log.md).
- **Yêu Cầu Sửa Lại (Revision)**: Không.
- **Đánh Giá & Hài Lòng**: ✅ Hoàn thành làm mịn tài liệu LLD chuẩn xác theo toàn bộ các mục review.

---

### #017 — Làm mịn tài liệu kỹ thuật Evidence Engine Design (docs/03-technical/evidence-engine-design.md)
- **Thời gian**: 16/09/2026 23:22
- **Prompt Người Dùng**: `@[docs/03-technical/evidence-engine-design.md] chỉnh sửa theo góp ý trong ảnh` (kèm 2 ảnh feedback review [EE-01] đến [EE-05])
- **AI Đặt Câu Hỏi / Làm Rõ**: Phân tích toàn bộ 5 vấn đề:
  1. `[EE-01]` (CRITICAL): `Evidence` dataclass thiếu required fields (`id=uuid4()`, `incident_id=None`, `timestamp=datetime.utcnow()`) trong normalizer và session collector gây runtime `TypeError`.
  2. `[EE-02]` (CRITICAL): Hàm `_remove_outliers()` chưa được implement trong `BaselineEngine` gây `AttributeError`.
  3. `[EE-03]` (HIGH): Vòng lặp `N SQL IDs × 24 giờ × 7 ngày = 16,800 DB queries/giờ` làm tê liệt kết nối DB. Thay bằng **1 single PostgreSQL aggregation query** với hàm window `PERCENTILE_CONT(0.5)` và `PERCENTILE_CONT(0.95)`.
  4. `[EE-04]` (LOW): `SqlCollector` chỉ lấy `elapsed_time`. Bổ sung thu thập theo cả `cpu_time` và `disk_reads` để nhận diện CPU hogs và IO hogs.
  5. `[EE-05]` (LOW): `ON CONFLICT DO NOTHING` thiếu explicit conflict key gây lỗi cú pháp PostgreSQL. Sửa thành `ON CONFLICT (database_id, sql_id, captured_at) DO NOTHING`.
- **User Phản Hồi / Quyết Định**: Đồng ý cập nhật trực tiếp vào file `docs/03-technical/evidence-engine-design.md`.
- **Kết Quả AI Tạo Ra**:
  - Cập nhật [docs/03-technical/evidence-engine-design.md](file:///d:/2026/oracle_ai/docs/03-technical/evidence-engine-design.md) toàn bộ các mục 5.2, 5.3, 6, 7, 8 và các mục tiếng Anh 10, 12, 13.
  - Cập nhật tự động [docs/promt_log.md](file:///d:/2026/oracle_ai/docs/promt_log.md).
- **Yêu Cầu Sửa Lại (Revision)**: Không.
- **Đánh Giá & Hài Lòng**: ✅ Hoàn thành làm mịn đầy đủ và chính xác 5/5 điểm trong `evidence-engine-design.md`.

---

### #018 — Làm mịn tài liệu kỹ thuật Oracle MCP Server Design (docs/03-technical/oracle-mcp-design.md)
- **Thời gian**: 16/09/2026 23:25
- **Prompt Người Dùng**: `@[docs/03-technical/oracle-mcp-design.md] chỉnh sửa theo góp ý trong ảnh` (kèm ảnh feedback review [MCP-01] đến [MCP-04])
- **AI Đặt Câu Hỏi / Làm Rõ**: Phân tích 4 vấn đề kỹ thuật:
  1. `[MCP-01]` (HIGH): Thiếu quyền `SYS.V_$DIAG_ALERT_EXT` dẫn đến lỗi `ORA-00942` khi tool `get_alert_events` truy vấn.
  2. `[MCP-02]` (HIGH): Thiếu quyền `SYS.V_$ARCHIVED_LOG` trong file grant dẫn đến lỗi khi chạy tool `get_redo_statistics`.
  3. `[MCP-03]` (HIGH): Audit Log bị mất khi chạy Stdio Mode do stderr bị discard nếu parent process không chủ động capture. Cần bổ sung ghi ra file xoay vòng (Rotating File Handler) để đáp ứng chuẩn SOC2/Compliance cho thương mại hoá.
  4. `[MCP-04]` (MEDIUM): Trích xuất `sql_statements` trong PL/SQL Source Code bằng parsing AST toàn diện là bài toán khó. Cần làm rõ phạm vi MVP dùng regex-based cho static DML và document rõ giới hạn (không hỗ trợ Dynamic SQL).
- **User Phản Hồi / Quyết Định**: Đồng ý tiến hành cập nhật trực tiếp file tài liệu `docs/03-technical/oracle-mcp-design.md`.
- **Kết Quả AI Tạo Ra**:
  - Cập nhật mục 6 và 12 của [docs/03-technical/oracle-mcp-design.md](file:///d:/2026/oracle_ai/docs/03-technical/oracle-mcp-design.md): Bổ sung `RotatingFileHandler` cho file `logs/mcp_audit.log` (10MB x 5 backups) chạy song song với stderr.
  - Cập nhật mục 7 và 11: Bổ sung `GRANT SELECT ON SYS.V_$ARCHIVED_LOG` và `GRANT SELECT ON SYS.V_$DIAG_ALERT_EXT` vào danh mục phân quyền Oracle.
  - Cập nhật mục 8.3: Bổ sung ghi chú kỹ thuật `[MCP-04]` làm rõ giải pháp heuristic regex cho static DML và giới hạn không hỗ trợ Dynamic SQL.
- **Yêu Cầu Sửa Lại (Revision)**: Không.
- **Đánh Giá & Hài Lòng**: ✅ Hoàn thành làm mịn 4/4 điểm trong `oracle-mcp-design.md`.

---

### #019 — Chỉnh sửa tài liệu kỹ thuật Correlation Engine Design (docs/03-technical/correlation-engine-design.md)
- **Thời gian**: 16/09/2026 23:28
- **Prompt Người Dùng**: `chỉnh sửa @[docs/03-technical/correlation-engine-design.md] theo góp ý trong ảnh` (kèm ảnh feedback review [CE-01] đến [CE-07])
- **AI Đặt Câu Hỏi / Làm Rõ**: Phân tích 7 vấn đề kỹ thuật từ ảnh:
  1. `[CE-01]` (HIGH): `SqlRegressionRule` gọi MCP bên trong detection rule vi phạm nguyên tắc kiến trúc (rule phải deterministic, không phụ thuộc MCP call đồng bộ). Chuyển sang so sánh `plan_hash_value` của current metric với metric trước đó từ PostgreSQL.
  2. `[CE-02 + CE-03]` (HIGH): `EvidenceGraph` không được liên kết trong MVP correlation loop (`add_relationship` không được gọi, các core methods rỗng). Làm rõ phạm vi: MVP correlation dùng flat evidence list; `EvidenceGraph` cùng thuật toán BFS causal chain phục vụ chuyên biệt cho Investigation Engine (Phase 3).
  3. `[CE-04]` (MEDIUM): "Data Volume Increase" hypothesis có `required_evidence: []` dẫn tới luôn xuất hiện ở 0.40 confidence gây noise. Bổ sung `"required_evidence": [EvidenceType.CARDINALITY_MISMATCH]`.
  4. `[CE-05]` (MEDIUM): Thiếu cơ chế incident deduplication (SQL chậm 30 phút sinh 6 incidents riêng biệt). Bổ sung cơ chế deduplication: tra cứu incident đang `OPEN` cùng `(database_id, category, entity_id)` trong vòng 60 phút, merge evidence và update severity thay vì tạo mới.
  5. `[CE-06]` (MEDIUM): `BlockingSessionRule` mặc định mọi blocking là `HIGH` gây alert fatigue. Phân tầng thang đo severity: Wait < 30s + <= 2 sessions -> `MEDIUM`, Wait 30-300s HOẶC 3-9 sessions -> `HIGH`, Wait > 300s HOẶC >= 10 sessions -> `CRITICAL`.
  6. `[CE-07]` (MEDIUM): Bổ sung đặc tả implementation chi tiết cho `LongRunningSessionRule` và `InvalidObjectRule` trong Mục 3.
  7. Đồng bộ hoá toàn diện cả 2 phần Tiếng Việt và English Section.
- **User Phản Hồi / Quyết Định**: Đồng ý cập nhật trực tiếp vào file tài liệu `docs/03-technical/correlation-engine-design.md`.
- **Kết Quả AI Tạo Ra**:
  - Cập nhật [docs/03-technical/correlation-engine-design.md](file:///d:/2026/oracle_ai/docs/03-technical/correlation-engine-design.md) tại Mục 3.1, 3.2, 3.5, 3.6, 4, 5, 6, 8, 9, 10, 11, 12.
  - Tự động cập nhật [docs/promt_log.md](file:///d:/2026/oracle_ai/docs/promt_log.md).
- **Yêu Cầu Sửa Lại (Revision)**: Không.
- **Đánh Giá & Hài Lòng**: ✅ Hoàn thành làm mịn 7/7 điểm kỹ thuật trong `correlation-engine-design.md`.

---

### #019 — Làm mịn tài liệu kỹ thuật Investigation Engine Design (docs/03-technical/investigation-engine-design.md)
- **Thời gian**: 16/09/2026 23:28
- **Prompt Người Dùng**: `chỉnh sửa theo góp ý trong ảnh @[docs/03-technical/investigation-engine-design.md]` (kèm 2 ảnh feedback review [IE-01] đến [IE-08])
- **AI Đặt Câu Hỏi / Làm Rõ**: Phân tích toàn bộ 8 điểm kỹ thuật:
  1. `[IE-01]` (CRITICAL): `EvidencePackage` khởi tạo sai schema (truyền `graph` và `context_data` không tồn tại trong class definition gây runtime crash). Đồng bộ đóng gói vào `context={"graph": graph, ...}`.
  2. `[IE-02]` (CRITICAL): Plan `PROCEDURE_SLOW` dùng `get_ash_sql_activity` không filter theo procedure/module name, dễ lấy nhầm top_sql của query khác trong hệ thống bận. Bổ sung step fallback gọi `get_object_dependencies` để lấy danh sách objects/tables mà procedure access để cross-reference.
  3. `[IE-03]` (HIGH): Mismatch tham số `get_awr_sql_stats` (truyền `days: 1` trong khi tool định nghĩa `begin_snap`, `end_snap`). Thống nhất sử dụng snapshot IDs được resolve từ ASH activity hoặc truyền range hợp lệ.
  4. `[IE-04]` (HIGH): `DependsOn` fails silently khi giá trị trả về là `None` dẫn đến gọi tool hạ nguồn với `sql_id=None`. Bổ sung kiểm tra tường minh: nếu required dependency bị `None` thì skip step và log explicit warning vào `context.errors`.
  5. `[IE-05]` (MEDIUM): Các bước trong plan chạy tuần tự (9 steps × 10s = 90s, vượt SLA 60s). Gom nhóm các bước độc lập (metadata, dependencies, ash, blocking, resource) thành từng wave và chạy song song bằng `asyncio.gather()`.
  6. `[IE-06]` (MEDIUM): `IntentParser` không có cơ chế fallback khi LLM gặp sự cố hoặc timeout. Bổ sung regex heuristic fallback cho các intent phổ biến.
  7. `[IE-07]` (MEDIUM): `GENERAL_INCIDENT` intent không có plan riêng. Thống nhất tự động map sang `HEALTH_CHECK` plan.
  8. `[IE-08]` (MEDIUM): Plan `SQL_SLOW` thiếu bước kiểm tra statistics staleness (nguyên nhân hàng đầu gây plan regression). Bổ sung step gọi `get_object_metadata` kiểm tra thống kê bảng liên quan.
- **User Phản Hồi / Quyết Định**: Đồng ý tiến hành cập nhật trực tiếp file tài liệu `docs/03-technical/investigation-engine-design.md`.
- **Kết Quả AI Tạo Ra**:
  - Cập nhật mục 4.1, 4.3 của [docs/03-technical/investigation-engine-design.md](file:///d:/2026/oracle_ai/docs/03-technical/investigation-engine-design.md): Thêm regex fallback cho IntentParser và mapping `GENERAL_INCIDENT` -> `HEALTH_CHECK`.
  - Cập nhật mục 5.1 & 5.2: Bổ sung dependency fallback `get_object_dependencies` trong procedure plan, bổ sung `get_object_metadata` kiểm tra table stats trong SQL plan, chuẩn hoá tham số AWR stats.
  - Cập nhật mục 6: Viết lại `InvestigationExecutor` với cơ chế Wave Parallel (`asyncio.gather`), kiểm tra `DependsOn` tránh `None` downstream, và align 100% schema `EvidencePackage`.
- **Yêu Cầu Sửa Lại (Revision)**: Không.
- **Đánh Giá & Hài Lòng**: ✅ Hoàn thành làm mịn 8/8 điểm trong `investigation-engine-design.md`.


