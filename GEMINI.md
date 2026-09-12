# AI Assistant Instructions & Workspace Rules

Dự án: **Oracle Database Copilot** (`oracle_ai`)

## 1. BẮT BUỘC: TỰ ĐỘNG GHI NHẬT KÝ PROMPT (PROMPT LOGGING)
Theo quy định tại [docs/vibecode.md](file:///d:/2026/oracle_ai/docs/vibecode.md):
- **Luôn tự động cập nhật** file [docs/promt_log.md](file:///d:/2026/oracle_ai/docs/promt_log.md) sau mỗi phiên làm việc hoặc khi hoàn thành yêu cầu của User mà **KHÔNG CẦN USER PHẢI NHẮC LẠI**.
- Cấu trúc bắt buộc gồm:
  1. *ID / Phiên & Thời gian*
  2. *Prompt Người Dùng* (nguyên văn hoặc ý chính)
  3. *AI Đặt Câu Hỏi / Làm Rõ*
  4. *User Phản Hồi / Quyết Định*
  5. *Kết Quả AI Tạo Ra* (files, code, tests, docs)
  6. *Yêu Cầu Sửa Lại (Revision)* (Có/Không, nội dung sửa)
  7. *Đánh Giá & Hài Lòng*

## 2. QUY CHUẨN KỸ THUẬT CỐT LÕI (TECHNICAL RULES)
1. **An toàn Oracle & Bảo mật**:
   - `oracle-mcp-server` kết nối Oracle 19c qua **Thin Mode** (không cần Oracle Instant Client).
   - Chỉ dùng quyền `SELECT` (Read-only) trên các `V$` và `DBA_` views hiệu năng. Tuyệt đối không DDL/DML.
   - Luôn làm sạch credentials trong logs bằng Sanitizer.
2. **Giao thức MCP**:
   - Kênh `stdout` chỉ dành riêng cho gói tin JSON-RPC. Toàn bộ log ứng dụng và audit log đẩy ra `sys.stderr`.
3. **Quy trình Pair Programming**:
   - Luôn trình bày giải pháp/kế hoạch và xin ý kiến User trước khi thực hiện các thay đổi lớn.
   - Đảm bảo 100% unit tests pass và linting (`ruff check .`) sạch sẽ trước khi kết thúc task.
