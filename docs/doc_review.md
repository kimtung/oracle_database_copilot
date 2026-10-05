# 📋 Review Toàn Bộ Tài Liệu DB Copilot

**Ngày review:** 2026-09-17  
**Phạm vi:** 01-product, 02-architecture, 03-technical, 04-implementation  

---

## TÓM TẮT EXECUTIVE

Tài liệu tổng thể **khá chắc chắn và nhất quán** ở tầng business + architecture. Các vấn đề chủ yếu nằm ở:
1. **Xung đột số liệu** giữa các tài liệu (tool count, timeline, threshold)
2. **Thiếu tài liệu** cho một số thành phần đã được thiết kế nhưng chưa có spec
3. **Gaps logic** trong một số flow chưa được giải thích rõ
4. **Inconsistency về transport mode** — MCP Stdio vs SSE

---

## 1. ⚠️ XUNG ĐỘT (Conflicts)

### 1.1 Số lượng MCP Tools không nhất quán

| Tài liệu | Số tool được nêu |
|---|---|
| [`hld.md`](file:///d:/2026/oracle_ai/docs/02-architecture/hld.md) Section 3.1 | "7 groups, **~35 tools**" |
| [`oracle-mcp-design.md`](file:///d:/2026/oracle_ai/docs/03-technical/oracle-mcp-design.md) Section 10 | "**Total: ~32 tools**" |
| [`implementation-plan.md`](file:///d:/2026/oracle_ai/docs/04-implementation/implementation-plan.md) Section 4.1 | "All **32 tools**" |
| [`lld.md`](file:///d:/2026/oracle_ai/docs/02-architecture/lld.md) Section 3.1 | "7 groups, **~35 tools**" |

**Vấn đề:** HLD và LLD ghi 35, nhưng tài liệu thiết kế và implementation plan ghi 32. Đếm thực tế: sql(4) + ash(2) + awr(2) + session(5) + plan(2) + object(6) + storage(11) = **32 tools** → HLD/LLD đang sai.

**Fix:** Cập nhật HLD và LLD từ "~35" thành "32 tools".

---

### 1.2 MCP Transport Mode: Stdio vs SSE — xung đột chiến lược

| Tài liệu | Mode được ghi |
|---|---|
| [`oracle-mcp-design.md`](file:///d:/2026/oracle_ai/docs/03-technical/oracle-mcp-design.md) Section 2.1 | "**MVP: Stdio mode** (đơn giản hơn)" |
| [`lld.md`](file:///d:/2026/oracle_ai/docs/02-architecture/lld.md) Section 5 | "db-copilot kết nối qua **SSE Transport với Persistent Connection**" |
| `lld.md` config | `MCP_TRANSPORT=sse`, `MCP_SSE_HOST=0.0.0.0` |

**Vấn đề:** Đây là xung đột thiết kế nghiêm trọng nhất. `oracle-mcp-design.md` khuyến nghị Stdio cho MVP, nhưng `lld.md` đã quyết định SSE và thậm chí viết code `OracleMcpClient` với SSE persistent connection.

**Phân tích:** LLD có lý luận kỹ hơn (performance ~30-100ms vs ~2-3s, SLA < 60s). SSE là lựa chọn đúng hơn.

**Fix:** Cập nhật `oracle-mcp-design.md` Section 2.1 → SSE mode, giải thích tại sao Stdio bị loại bỏ.

---

### 1.3 Timeline không đồng bộ

| Tài liệu | Tổng ước tính |
|---|---|
| [`brd.md`](file:///d:/2026/oracle_ai/docs/01-product/brd.md) Section 13 | **10–15 tuần** |
| [`implementation-plan.md`](file:///d:/2026/oracle_ai/docs/04-implementation/implementation-plan.md) Section 2 | **9–14 tuần** |

**Fix:** Đồng bộ BRD về "9–14 tuần".

---

### 1.4 Tablespace threshold không nhất quán

| Tài liệu | Warning threshold |
|---|---|
| [`prd.md`](file:///d:/2026/oracle_ai/docs/01-product/prd.md) MVP-2 acceptance | "> **85%**" |
| [`correlation-engine-design.md`](file:///d:/2026/oracle_ai/docs/03-technical/correlation-engine-design.md) | "WARNING: > **80%**" |
| Config default | `tablespace_warning_threshold = 80` |

**Fix:** Cập nhật PRD MVP-2 acceptance criteria từ "85%" thành "80% (configurable)".

---

### 1.5 Daily Report schedule — 6 AM vs 7 AM

| Tài liệu | Giờ gửi report |
|---|---|
| [`prd.md`](file:///d:/2026/oracle_ai/docs/01-product/prd.md) US-DBA-01 | "**7:00 AM**" |
| `prd.md` FR-005, config | "**6:00 AM**" |
| `evidence-engine-design.md`, `implementation-plan.md` | "**6:00 AM**" |

**Fix:** Thống nhất về 6AM trong US-DBA-01 (DBA cần đọc report trước giờ làm).

---

### 1.6 Evidence retention: 30 ngày vs 90 ngày

| Tài liệu | Retention |
|---|---|
| [`prd.md`](file:///d:/2026/oracle_ai/docs/01-product/prd.md) FR-001 | "minimum **30 days**" |
| `prd.md` config, [`lld.md`](file:///d:/2026/oracle_ai/docs/02-architecture/lld.md) | `evidence_retention_days = 90` |

**Fix:** Cập nhật FR-001 thành "minimum **90 days** (configurable)".

---

### 1.7 DiagnosisResult schema không đồng bộ

**`prd.md` FR-006** có field `hypothesis_ranking` trong JSON:
```json
{"hypothesis_ranking": [{"hypothesis": "Statistics issue", "confidence": 0.87}]}
```

**`ai-engine-design.md`** `DiagnosisResult` dataclass lại có `alternative_causes: list[str]` thay vì `hypothesis_ranking`.

**Fix:** Quyết định schema cuối cùng — gợi ý giữ `hypothesis_ranking: list[Hypothesis]` là object đầy đủ hơn.

---

## 2. ❓ CHƯA RÕ RÀNG (Needs Clarification)

### 2.1 `get_ash_sql_activity` không có `module` filter — gap logic quan trọng

Trong [`investigation-engine-design.md`](file:///d:/2026/oracle_ai/docs/03-technical/investigation-engine-design.md) PROCEDURE_SLOW plan:

```python
Step("get_ash_sql_activity", 
     args={"begin_time": t_begin, "end_time": t_end},  # ← không có module filter!
     produces="ash_activity")
```

Nhưng tool signature là `get_ash_sql_activity(sql_id, begin_time, end_time)`. Khi điều tra procedure, chưa biết `sql_id` trước, nên không thể filter. Step này sẽ trả về toàn bộ ASH của period đó.

**Câu hỏi:** Cần thêm `module` parameter vào tool, hoặc thêm step `get_ash_sample` trước để filter theo `module = 'PROC_SETTLEMENT'`?

> [!CAUTION]
> Đây là gap logic nghiêm trọng trong PROCEDURE_SLOW investigation pipeline. Nếu không fix, toàn bộ procedure investigation sẽ trả về SQL của procedure khác hoặc không liên quan.

---

### 2.2 `EvidencePackage` constructor — `context` field không tồn tại

**`ai-engine-design.md`** định nghĩa:
```python
@dataclass
class EvidencePackage:
    database_name: str
    investigation_timestamp: datetime
    # Không có 'context' field
```

**`investigation-engine-design.md`** tạo:
```python
package = EvidencePackage(
    intent=intent.__dict__,  # ← dict, không phải InvestigationIntent object
    context={"graph": graph, ...}  # ← field không tồn tại!
)
```

**Fix:** Cập nhật `EvidencePackage` để thêm `context: dict | None = None`.

---

### 2.3 `CorrelationEngine.evaluate_all()` — `rule.name` không được định nghĩa

```python
async def evaluate_all(self, collected_data: dict, context: dict):
    for rule in self.rules:
        incidents = await rule.evaluate(collected_data.get(rule.name), context)
```

Không có Rule class nào định nghĩa attribute `name`. `collected_data.get(rule.name)` sẽ luôn trả về `None`.

**Fix:** Thêm `name: ClassVar[str]` vào mỗi Rule class.

---

### 2.4 Health Score — chưa có công thức tính

BRD, PRD, HLD đều nhắc đến "Health Score 0-100" nhưng **không có tài liệu nào định nghĩa công thức**. Không rõ:
- Tính từ incidents như thế nào?
- CRITICAL incident trừ bao nhiêu điểm?
- Score = 100 khi không có incident?

**Cần thêm:** Section "Health Score Calculation" trong `correlation-engine-design.md`.

---

### 2.5 `temp_usage_high` EvidenceType có rule detect không?

[`evidence-engine-design.md`](file:///d:/2026/oracle_ai/docs/03-technical/evidence-engine-design.md) liệt kê `temp_usage_high` EvidenceType, nhưng [`correlation-engine-design.md`](file:///d:/2026/oracle_ai/docs/03-technical/correlation-engine-design.md) không có `TempUsageRule` nào.

**Câu hỏi:** Có kế hoạch detect temp usage cao không?

---

### 2.6 Stale statistics threshold chưa được config

Problem statement ví dụ: "statistics updated **18 days ago**". Nhưng không có config nào định nghĩa ngưỡng "stale":

- Bao nhiêu ngày thì là stale?
- Khác nhau theo object type (table lớn vs nhỏ)?

**Cần thêm:** Config `stale_statistics_threshold_days: 14` (hoặc tương tự).

---

### 2.7 Hai audit log systems không được sync

- `oracle-mcp-server` → stderr + rotating file `logs/mcp_audit.log`
- `db-copilot` → `mcp_audit_log` table trong PostgreSQL

DBA sẽ phải check 2 nơi. **Câu hỏi:** Design intention hay accident?

---

## 3. 🔴 SAI / KHÔNG HỢP LÝ (Incorrect/Unreasonable)

### 3.1 MCP SDK 2.x API — `app.add_tool()` không tồn tại

[`oracle-mcp-design.md`](file:///d:/2026/oracle_ai/docs/03-technical/oracle-mcp-design.md) dùng:
```python
app = Server("oracle-mcp-server")
app.add_tool(tool_fn)  # ← API này không tồn tại trong MCP SDK 2.x
```

`implementation-plan.md` Phase 1 đã note "MCP SDK 2.x migration với `@mcp.tool()` decorators". API đúng là decorator-based.

**Fix:** Cập nhật code example dùng `@mcp.tool()` pattern.

---

### 3.2 `SqlCollector` → `CorrelationEngine` — circular dependency

```python
# evidence/collectors/sql_collector.py
await CorrelationEngine().evaluate_sql_metrics(metrics)  # ← direct call
```

`SqlCollector` không nên biết về `CorrelationEngine`. Vi phạm single responsibility.

**Fix:** APScheduler orchestrator job nên gọi collector → engine theo sequence, không để collector gọi engine.

---

### 3.3 SQL_ID example dùng 6 ký tự thay vì 13 ký tự

Toàn bộ docs dùng `"8f3abc"` (6 ký tự) nhưng test plan confirm: `assert len(sql_id) == 13`. Oracle SQL_ID thực sự là 13 ký tự.

**Fix:** Thay `8f3abc` → `8f3abcxyz1234` (13 ký tự) ở tất cả examples.

---

### 3.4 `sql_metrics` DDL thiếu UNIQUE constraint

[`evidence-engine-design.md`](file:///d:/2026/oracle_ai/docs/03-technical/evidence-engine-design.md) Section 13: "enforces `UNIQUE(database_id, sql_id, captured_at)`".

[`lld.md`](file:///d:/2026/oracle_ai/docs/02-architecture/lld.md) DDL chỉ có INDEX, không có UNIQUE constraint. `ON CONFLICT (database_id, sql_id, captured_at) DO NOTHING` sẽ fail nếu không có UNIQUE.

**Fix:** Thêm `UNIQUE (database_id, sql_id, captured_at)` vào DDL.

---

### 3.5 `InvestigationResult` không có PostgreSQL table

`GET /investigate/{id}` cần persistence, nhưng không có table `investigations` trong schema của `lld.md`. Khi server restart, tất cả in-flight investigations sẽ mất.

**Fix:** Thêm table:
```sql
CREATE TABLE investigations (
    id UUID PRIMARY KEY,
    question TEXT,
    status VARCHAR(16),  -- queued | running | done | error
    result_json JSONB,
    created_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);
```

---

### 3.6 `get_ash_sql_activity` với PROCEDURE_SLOW — thiếu sql_id làm crash

Chi tiết đã phân tích ở mục 2.1. Tool yêu cầu `sql_id` nhưng plan không truyền vào → tool sẽ raise error hoặc trả về unexpected data.

---

## 4. 🟡 CẦN CẢI THIỆN (Improvements)

### 4.1 `DependsOn` class chưa được định nghĩa

[`investigation-engine-design.md`](file:///d:/2026/oracle_ai/docs/03-technical/investigation-engine-design.md) sử dụng `DependsOn(...)` nhưng không define ở đâu cả.

```python
# Cần thêm:
@dataclass
class DependsOn:
    source: str   # Key trong InvestigationContext.results
    path: str     # JSON path để extract value
```

---

### 4.2 `StorageCollector` thiếu implementation detail

`SqlCollector` và `SessionCollector` có code đầy đủ, nhưng `StorageCollector` chỉ được liệt kê tên trong schedule. Cần thêm implementation cho `get_tablespace_usage`, `get_temp_usage`, `get_undo_usage`, `get_failed_jobs`.

---

### 4.3 API Authentication hoàn toàn không được đề cập

`POST /investigate` không có authentication. Bất kỳ ai biết URL đều có thể trigger investigation và gây tải Oracle DB.

**Gợi ý:** Ít nhất Bearer token hoặc API Key cho MVP.

---

### 4.4 Thiếu rate limiting cho concurrent investigations

10 users cùng `POST /investigate` → 90+ concurrent Oracle queries. Cần queue/semaphore.

---

### 4.5 `long_running_threshold_sec` thiếu trong config docs

`correlation-engine-design.md` dùng `settings.long_running_threshold_sec` nhưng không có trong config tables của PRD hay LLD.

**Fix:** Thêm `LONG_RUNNING_THRESHOLD_SECONDS=1800` vào config docs.

---

### 4.6 Baseline outlier removal bị bypass trong SQL aggregation

`BaselineEngine._remove_outliers()` được code nhưng `recalculate()` dùng SQL aggregation query trực tiếp, không gọi hàm này. Dead code hoặc logic gap.

---

### 4.7 Oracle connection pool không có retry logic

Nếu Oracle restart, pool sẽ fail và không recover. Cần exponential backoff trong `OracleConnectionPool.acquire()`.

---

### 4.8 Test Plan thiếu test cho deduplication

Deduplication (60-min window, severity upgrade, evidence append) là logic phức tạp nhưng không có test case nào trong `test-plan.md`.

---

## 5. 📋 THIẾU TÀI LIỆU

| Thành phần | Trạng thái |
|---|---|
| **Health Score Calculator** — công thức tính | ❌ Chưa có |
| **`StorageCollector` implementation** | ❌ Skeleton only |
| **`DependsOn` class definition** | ❌ Chỉ dùng, chưa định nghĩa |
| **`investigations` PostgreSQL table** | ❌ Thiếu trong schema |
| **API Authentication design** | ❌ Hoàn toàn chưa đề cập |
| **Stale statistics threshold config** | ❌ Không có giá trị mặc định |
| **Long running threshold config** | ❌ Thiếu trong config docs |
| **`get_awr_sql_stats`** — `begin_snap/end_snap` vs `days` parameter | 🟡 Hai places dùng khác nhau |
| **Alembic migration strategy** | 🟡 Đề cập nhưng không detail |
| **Alert delivery channels** (Email/Slack) | 🟡 Đề cập nhưng không detail |

---

## 6. 🟢 ĐIỂM MẠNH CỦA TÀI LIỆU

1. **Business vision nhất quán** — BRD, PRD, Problem Statement đồng bộ tốt.
2. **Security model chắc chắn** — "AI không execute" nhất quán xuyên suốt, có SQL grants cụ thể.
3. **Evidence-first approach** — Correlation Engine chạy trước AI, tránh LLM hallucination.
4. **LLD rất chi tiết** — `OracleMcpClient`, `HypothesisEngine`, `EvidenceNormalizer` có code examples sát thực tế.
5. **Deduplication strategy** — Alert fatigue được giải quyết kỹ.
6. **Fallback chain** — LLM → rule-based diagnosis được thiết kế tốt.
7. **Test Plan đầy đủ** — 3 E2E scenarios, acceptance criteria đo được.
8. **Baseline time-bucket** — `hour_of_day + day_of_week` rất Oracle-savvy, tránh false positives.

---

## 7. 🎯 DANH SÁCH ƯU TIÊN FIX

### P0 — Phải fix ngay (blocking khi implement)

- [ ] **`oracle-mcp-design.md`** Section 2.1 — Đồng bộ transport mode: Stdio → SSE
- [ ] **`correlation-engine-design.md`** — Định nghĩa `rule.name` attribute trong Rule classes
- [ ] **`investigation-engine-design.md`** — Fix `EvidencePackage` constructor (`context` field)
- [ ] **`investigation-engine-design.md`** — Fix PROCEDURE_SLOW plan: `get_ash_sql_activity` thiếu module filter
- [ ] **`lld.md`** — Thêm UNIQUE constraint vào `sql_metrics` DDL
- [ ] **`lld.md`** — Thêm table `investigations` vào PostgreSQL schema

### P1 — Nên fix sớm (consistency)

- [ ] **`hld.md` + `lld.md`** — Tool count: "~35" → "32"
- [ ] **`prd.md`** MVP-2 — Tablespace threshold: 85% → 80%
- [ ] **`prd.md`** US-DBA-01 — Daily report: 7AM → 6AM
- [ ] **`prd.md`** FR-001 — Evidence retention: 30 → 90 ngày
- [ ] **`prd.md` + `ai-engine-design.md`** — DiagnosisResult schema: đồng bộ `hypothesis_ranking`
- [ ] **`investigation-engine-design.md`** — Thêm `DependsOn` class definition
- [ ] **Config docs** — Thêm `long_running_threshold_seconds`, `stale_statistics_threshold_days`
- [ ] **`oracle-mcp-design.md`** — Update MCP server code example sang SDK 2.x API

### P2 — Cải thiện sau

- [ ] Thêm Health Score Calculator spec vào `correlation-engine-design.md`
- [ ] Thêm test case cho deduplication vào `test-plan.md`
- [ ] Thêm `StorageCollector` implementation detail
- [ ] Thiết kế API authentication
- [ ] Thiết kế rate limiting cho concurrent investigations
- [ ] Đổi SQL_ID example → 13-char format nhất quán
- [ ] Fix circular dependency `SqlCollector` → `CorrelationEngine`
- [ ] Oracle connection pool retry logic

---

## 8. SƠ ĐỒ PHỤ THUỘC & CONFLICTS

```
BRD ←──── [CONFLICT: timeline 10-15 vs 9-14 tuần] ────→ Implementation Plan
│
├── PRD ←── [CONFLICT: tablespace 85% vs 80%]
│           [CONFLICT: retention 30 vs 90 ngày]  
│           [CONFLICT: report 7AM vs 6AM]
│           [CONFLICT: DiagnosisResult schema]
│
├── HLD ←── [CONFLICT: tools ~35 vs 32]
│
└── LLD ←── [CONFLICT: transport SSE]
        │
        ├── oracle-mcp-design  ←── [CONFLICT: Stdio vs SSE]
        ├── ai-engine-design   ←── [CONFLICT: EvidencePackage schema]
        ├── correlation-engine ←── [GAP: rule.name, Health Score calc]
        ├── evidence-engine    ←── [GAP: StorageCollector, outlier removal]
        └── investigation-engine ← [GAP: DependsOn, PROCEDURE module filter]
```
