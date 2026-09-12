# 📋 TÀI LIỆU TRÌNH BÀY DỰ ÁN: ORACLE DATABASE COPILOT
> **Dành cho buổi báo cáo với Tech Leader**  
> **Người trình bày:** Team Dự án (Góc nhìn kỹ sư C# chuyển đổi sang Python)  
> **Ngày cập nhật:** 12/09/2026  
> **Workspace:** `d:\2026\oracle_ai`  

---

## 1. TỔNG QUAN HỆ THỐNG (SYSTEM OVERVIEW)

Hệ thống **Oracle Database Copilot** là trợ lý AI tự động giám sát, phát hiện và chẩn đoán sự cố cơ sở dữ liệu Oracle theo thời gian thực. Hệ thống được chia thành 2 sub-projects độc lập và phân tách trách nhiệm rõ ràng:

```
┌─────────────────────────────────────────────────────────────┐
│                      db-copilot                             │
│   FastAPI Backend + PostgreSQL + AI Chẩn đoán (Port 8000)   │
│   - Evidence Engine (Baseline & Thu thập 5 phút/lần)        │
│   - Correlation & Investigation Engine                      │
└──────────────┬────────────────────────▲─────────────────────┘
               │ (1) Gửi lệnh JSON-RPC  │ (4) Nhận kết quả chẩn đoán
               │     qua stdin          │     qua stdout
               ▼                        │
┌─────────────────────────────────────────────────────────────┐
│                   oracle-mcp-server                         │
│   Observability Gateway — 32 Read-Only Tools (MCP SDK 2.x)   │
└──────────────┬────────────────────────▲─────────────────────┘
               │ (2) Query SQL (SELECT) │ (3) Dữ liệu trả về
               ▼                        │
┌─────────────────────────────────────────────────────────────┐
│               Oracle Database (Instance: ORCL)              │
│   Oracle 19c Enterprise/SE2 — Port 1521 (Thin Mode)         │
└─────────────────────────────────────────────────────────────┘
```

| Sub-project | Vai trò chính | Tech Stack |
|---|---|---|
| **`oracle-mcp-server`** | Cổng giao tiếp an toàn (Gateway) trích xuất dữ liệu quan sát từ Oracle | Python 3.13, MCP SDK 2.2, `python-oracledb` (Thin Mode), Pydantic v2 |
| **`db-copilot`** | Bộ não phân tích, lưu trữ dữ liệu lịch sử, tính toán baseline và kích hoạt AI chẩn đoán | Python 3.13, FastAPI, PostgreSQL (asyncpg + SQLAlchemy 2.0), APScheduler |

---

## 2. BÁO CÁO THỰC THI & KIỂM THỬ THỰC TẾ (DEMO EVIDENCE)

Server đã được kiểm tra trực tiếp với **Oracle Database 19c thực tế** (`localhost:1521/ORCL`):
* **Tài khoản kết nối:** `db_copilot_readonly` (Đảm bảo an toàn tuyệt đối: chỉ có quyền `SELECT` trên các `V$` và `DBA_` views, không có quyền DML/DDL).
* **Driver:** `python-oracledb` 26.0.0 — Thin Mode (kết nối trực tiếp, không cần Oracle Client).
* **Connection Pool:** Khởi tạo `AsyncConnectionPool` thành công.

### Kết quả chạy thử nghiệm các công cụ tiêu biểu:
1. **`get_database_info`**: Đọc chính xác trạng thái DB: `ORCL`, Oracle 19.0.0.0.0, Host: `HI-WINDOWS11`, Status: `OPEN`. Thời gian phản hồi: **165ms**.
2. **`get_tablespace_usage`**: Tính toán tự động dung lượng đã dùng:
   * `SYSTEM`: 99.33% (926 MB / 933 MB)
   * `SYSAUX`: 94.45% (415 MB / 440 MB)
   * `USERS`: 85.0% (4.4 MB / 5.2 MB)
3. **`get_active_sessions`**: Nhận diện tức thời các session đang chạy trong database.
4. **`get_top_sql`**: Bắt được câu SQL chiếm dụng tài nguyên lớn nhất gần đây (`b6usrg82hwsa3` - `gather_database_stats_job_proc` chạy mất 53.7s CPU/elapsed).
5. **Unit Tests:** **14/14 tests pass 100%**, cơ chế tự động che giấu mật khẩu (sanitizer) và ghi audit log hoạt động chính xác.

---

## 3. CÁC ĐIỂM KỸ THUẬT QUAN TRỌNG ĐÃ LÀM RÕ

### 3.1. Cơ chế Thin Mode vs Thick Mode trong `python-oracledb`
* **Thin Mode (Hiện tại dự án đang dùng):**
  * Viết bằng 100% Python/Rust, tự nói chuyện trực tiếp qua socket mạng cổng 1521.
  * **Ưu điểm vượt trội:** **Không cần cài Oracle Instant Client** (không cần các file DLL/SO nặng hàng trăm MB), không cần biến môi trường `ORACLE_HOME` hay `PATH`. Docker container siêu nhẹ (~150MB).
  * Hỗ trợ đầy đủ connection pool bất đồng bộ, bind variables, mã hóa mạng (nhờ package `cryptography`).
* **Khi nào bắt buộc phải dùng Thick Mode?**
  * Khi phải kết nối tới Oracle Database cổ (11g trở xuống; Thin mode yêu cầu từ 12.1+).
  * Khi cần các tính năng Enterprise cao cấp của OCI: *Continuous Query Notification (CQN)*, *Advanced Queuing (AQ)*, *Application Continuity (TAC)* khi failover RAC, hoặc xác thực Kerberos/OS.
  * 👉 **Kết luận kiến trúc:** Với mục đích chỉ đọc thông số hiệu năng (Read-only observability), **Thin Mode là giải pháp tối ưu và nhẹ nhất**.

---

### 3.2. Kiến trúc Logging & Bảo mật trong MCP Server
* **Tại sao log không ghi vào `stdout`?**  
  Theo chuẩn giao thức Model Context Protocol (MCP), kênh `stdout` được dành riêng làm đường truyền dữ liệu gói tin **JSON-RPC** giữa Client và Server. Bất kỳ dòng text log nào in ra `stdout` sẽ làm vỡ định dạng gói tin và đứt kết nối ngay lập tức.
* **Luồng ghi hiện tại:**  
  * Log ứng dụng và **Audit Log JSON** đều được đẩy ra **`sys.stderr`**. Các MCP Client (Claude Desktop, Cursor, Antigravity) sẽ tự động bắt luồng này ghi vào file log của hệ thống.
  * Mỗi request đều sinh 1 dòng JSON Audit: `{"timestamp", "tool", "args", "duration_ms", "status"}`. Mọi password hay credential đều bị xóa/mask tự động trước khi ghi.
* **Mở rộng ghi file:** Khi cần xuất ra file log riêng cho production (ví dụ `logs/oracle_mcp.log`), có thể gắn thêm `RotatingFileHandler` (tương đương RollingFile trong Serilog/NLog của .NET) mà không ảnh hưởng tới `stderr`.

---

### 3.3. Các giải pháp đóng gói `oracle-mcp-server`
Đã xây dựng sẵn cấu hình để đóng gói theo 3 hướng:

1. **Giải pháp 1: Docker Container (Khuyến nghị cho Production & AI Agent Desktop)**
   * Dùng [Dockerfile](file:///d:/2026/oracle_ai/oracle-mcp-server/Dockerfile) trên nền `python:3.12-slim`. Nhờ Thin Mode, container không cần cài thêm thư viện Oracle.
   * Client (Claude/Cursor) chỉ cần chạy: `docker run -i --rm --network=host --env-file .env oracle-mcp-server`.
2. **Giải pháp 2: Python Wheel Package (`.whl`)**
   * Đã cấu hình `hatchling` trong [pyproject.toml](file:///d:/2026/oracle_ai/oracle-mcp-server/pyproject.toml). Build ra file `.whl` bằng lệnh `uv build`.
   * Cài đặt và phân phối gọn gàng qua `pip install` hoặc chạy nhanh không cần cài đặt bằng `uvx oracle-mcp-server`.
3. **Giải pháp 3: Standalone Executable (`.exe`)**
   * Sử dụng `PyInstaller` đóng gói toàn bộ Python runtime và code thành 1 file `.exe` duy nhất cho các máy Windows của DBA/Client không cài sẵn Python.

---

### 3.4. Cơ chế `OracleMcpClient` trong `db-copilot`
* **Bản chất kiến trúc:** Áp dụng **Gateway / Adapter Pattern** (tương tự `HttpClient` hoặc `gRPC Client` trong C# .NET).
* **Mục đích:** Giúp `db-copilot` không bị phụ thuộc vào Oracle driver hay kết nối trực tiếp đến Oracle.
* **Cơ chế IPC qua `stdio`:**
  * `db-copilot` spawn tiến trình con `oracle-mcp-server`.
  * Giao tiếp ngầm hai chiều qua pipe: ghi lệnh gọi Tool vào `stdin` của tiến trình con và đọc kết quả trả về từ `stdout`.
  * Tự động đo thời gian phản hồi, bắt lỗi trả về `McpClientError`, deserialize JSON sang domain models.

---

### 3.5. Cơ chế chạy nền `EvidenceScheduler` trong `db-copilot`
* **Bản chất kiến trúc:** Đóng vai trò như **`BackgroundService` (hoặc `IHostedService`)** kết hợp bộ lập lịch dạng **Quartz.NET / Hangfire** trong C#.
* **Vòng đời (Lifecycle):** Được gắn vào `lifespan(app)` của FastAPI trong [app.py](file:///d:/2026/oracle_ai/db-copilot/src/db_copilot/api/app.py):
  * Web API bật (`Startup`) ➔ Khởi động Scheduler chạy ngầm trên event-loop (không block API).
  * Web API tắt (`Shutdown`) ➔ Dừng scheduler an toàn và giải phóng DB connection pool.
* **Các tác vụ chạy định kỳ (Recurring Jobs):**
  1. `run_sql_collection()` (Mỗi **5 phút**): Lấy Top SQL, tính toán delta và phát hiện SQL chạy chậm bất thường (SQL Regression).
  2. `run_session_collection()` (Mỗi **5 phút**): Quét tìm session chạy lâu và phát hiện cây khóa chặn (Lock contention / Blocking tree).
  3. `run_storage_collection()` (Mỗi **5 phút**): Giám sát ngưỡng dung lượng Tablespace, Job Oracle chạy lỗi, Object bị INVALID.
  4. `run_baseline_recalculation()` (Mỗi **1 giờ**): Dùng dữ liệu lịch sử 7 ngày, lọc nhiễu ngoại lai theo chuẩn phân phối thống kê ($\mu \pm 2\sigma$), tính lại Mean, P50, P95 cho `elapsed_time`, `cpu_time`, `buffer_gets` để làm mốc so sánh.

---

## 4. GÓC NHÌN CHUYỂN ĐỔI KỸ THUẬT: C# (.NET) ➔ PYTHON

| Khái niệm trong C# (.NET) | Tương đương trong dự án Python này | Ý nghĩa thực tế |
|---|---|---|
| **Namespace & Assembly (`.dll`)** | **`__init__.py` & Thư mục Package** | Biến thư mục thành Package. Đóng vai trò Static Constructor và làm Facade re-export rút gọn đường dẫn import. |
| **`public` vs `internal`** | Biến `__all__ = [...]` trong `__init__.py` | Khai báo các đối tượng công khai cho bên ngoài dùng, ẩn các module nội bộ. |
| **`IHostedService` / Quartz.NET** | **`EvidenceScheduler` + `APScheduler`** | Chạy background job định kỳ không làm nghẽn luồng xử lý Web Request. |
| **`HttpClient` / `gRPC Client`** | **`OracleMcpClient` (stdio transport)** | Gọi các service/tool bên ngoài thông qua chuẩn IPC JSON-RPC. |
| **`DbContext` (Entity Framework)** | **`AsyncSession` (SQLAlchemy 2.0)** | Quản lý Unit of Work và transaction xuống PostgreSQL. |
| **`appsettings.json` / Options Pattern** | **Pydantic-Settings (`settings.py`)** | Validate cấu hình mạnh (strongly-typed) từ biến môi trường / `.env`. |

---

## 5. ĐỀ XUẤT BƯỚC ĐI TIẾP THEO (NEXT ACTIONS)

Sau khi hoàn thành và nghiệm thu xong 2 phần nền tảng:
* [x] **Phase 0 & 1:** `oracle-mcp-server` (32 tools hoàn thiện, thin mode, audit log, test green 100%).
* [x] **Phase 1 (db-copilot):** Foundation DB PostgreSQL, MCP Client, Collectors, Normalizers, Baseline Engine & Scheduler.

👉 **Kế hoạch tiếp theo (Phase 2 — Health & Correlation Engine):**
1. Xây dựng `IncidentRepository` & Quản lý vòng đời sự cố (OPEN, INVESTIGATING, RESOLVED, Deduplication).
2. Xây dựng 6 Luật phát hiện tất định (`SqlRegressionRule`, `BlockingSessionRule`, `TablespaceThresholdRule`, v.v.).
3. Xây dựng `EvidenceGraph` (Đồ thị nguyên nhân - kết quả để tìm Root Cause tự động bằng thuật toán duyệt BFS).
4. Xây dựng `HypothesisEngine` và API phục vụ bảng điều khiển Incident.
