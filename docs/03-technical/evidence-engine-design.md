# Evidence Engine Design
# Thiết Kế Evidence Engine

**Project:** `db-copilot` — `evidence/`  
**Phiên bản / Version:** 0.1  
**Ngày / Date:** 2026-09-08

---

# 🇻🇳 PHẦN TIẾNG VIỆT

---

## 1. Tổng Quan

Evidence Engine là layer trong `db-copilot` chịu trách nhiệm:

1. **Thu thập** (Collect): Gọi oracle-mcp-server định kỳ để lấy dữ liệu
2. **Chuẩn hóa** (Normalize): Convert raw data thành Evidence objects có type rõ ràng
3. **Lưu trữ** (Store): Persist vào PostgreSQL Evidence Store
4. **Cung cấp** (Serve): Cung cấp evidence cho Correlation Engine và Investigation Engine

Evidence Engine **không phân tích** và **không quyết định** — đó là nhiệm vụ của Correlation Engine và AI Service.

---

## 2. Component Overview

```
db-copilot/evidence/
│
├── collectors/
│   ├── sql_collector.py      # Thu thập SQL metrics mỗi 5 phút
│   ├── session_collector.py  # Thu thập session data
│   └── storage_collector.py  # Thu thập storage metrics
│
├── normalizers/
│   └── evidence_normalizer.py # Raw data → Evidence objects
│
├── builders/
│   └── evidence_builder.py   # Build EvidencePackage cho investigation
│
└── repository.py             # PostgreSQL read/write
```

---

## 3. Evidence Types

| Type | Nguồn MCP Tool | Mô tả |
|---|---|---|
| `sql_regression` | `get_sql_statistics` | Elapsed time tăng so với baseline |
| `sql_plan_change` | `get_sql_plan_history` | Plan hash thay đổi |
| `cardinality_mismatch` | `get_sql_plan` | Estimated rows ≠ actual rows |
| `high_physical_reads` | `get_sql_statistics` | Disk reads tăng đột biến |
| `stale_statistics` | `get_object_metadata` | Statistics quá cũ (> N ngày) |
| `blocking_session` | `get_blocking_sessions` | Có session bị block |
| `long_running_session` | `get_long_running_sessions` | Session chạy quá lâu |
| `tablespace_threshold` | `get_tablespace_usage` | Tablespace vượt ngưỡng % |
| `temp_usage_high` | `get_temp_usage` | TEMP usage cao |
| `job_failure` | `get_failed_jobs` | Scheduler job thất bại |
| `invalid_object` | `get_invalid_objects` | Object bị INVALID |
| `wait_event_anomaly` | `get_sql_wait_events` | Wait event bất thường |

---

## 4. Evidence Schema

```python
# src/db_copilot/domain/models/evidence.py

from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from uuid import UUID

class EvidenceType(str, Enum):
    SQL_REGRESSION = "sql_regression"
    SQL_PLAN_CHANGE = "sql_plan_change"
    CARDINALITY_MISMATCH = "cardinality_mismatch"
    HIGH_PHYSICAL_READS = "high_physical_reads"
    STALE_STATISTICS = "stale_statistics"
    BLOCKING_SESSION = "blocking_session"
    LONG_RUNNING_SESSION = "long_running_session"
    TABLESPACE_THRESHOLD = "tablespace_threshold"
    JOB_FAILURE = "job_failure"
    INVALID_OBJECT = "invalid_object"
    WAIT_EVENT_ANOMALY = "wait_event_anomaly"

class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

@dataclass
class Evidence:
    id: UUID
    incident_id: UUID | None        # None nếu chưa gán incident
    type: EvidenceType
    source: str                      # Oracle view/tool name
    timestamp: datetime
    entity_type: str                 # "SQL", "SESSION", "TABLE", "PROCEDURE", "JOB"
    entity_id: str                   # sql_id, session_id, object_name
    severity: Severity
    data: dict                       # Raw evidence payload (JSONB in DB)
    supports_hypothesis: list[str] = field(default_factory=list)
    contradicts_hypothesis: list[str] = field(default_factory=list)
```

---

## 5. Collection Flow

### 5.1 APScheduler Setup

```python
# src/db_copilot/api/app.py (lifespan)

from apscheduler.schedulers.asyncio import AsyncIOScheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = AsyncIOScheduler()

    # Evidence collection — mỗi 5 phút
    scheduler.add_job(SqlCollector().collect, "interval", minutes=5, id="sql_collector")
    scheduler.add_job(SessionCollector().collect, "interval", minutes=5, id="session_collector")
    scheduler.add_job(StorageCollector().collect, "interval", minutes=5, id="storage_collector")

    # Baseline recalculation — mỗi giờ
    scheduler.add_job(BaselineEngine().recalculate, "interval", hours=1, id="baseline")

    # Daily report — 6:00 AM
    scheduler.add_job(ReportService().generate_daily, "cron", hour=6, id="daily_report")

    scheduler.start()
    yield
    scheduler.shutdown()
```

### 5.2 SQL Collector

```python
# src/db_copilot/evidence/collectors/sql_collector.py

class SqlCollector:
    def __init__(self, mcp_client: OracleMcpClient, repo: EvidenceRepository):
        self.mcp = mcp_client
        self.repo = repo

    async def collect(self):
        """
        Chu kỳ: mỗi 5 phút
        1. Gọi get_top_sql đa chiều (elapsed_time, cpu_time, disk_reads) để phát hiện
           cả latency spikes, CPU hogs và IO hogs ([EE-04]).
        2. Deduplicate theo sql_id và normalize thành SqlMetric objects.
        3. Lưu snapshot và metrics vào PostgreSQL (ON CONFLICT explicit key).
        4. Trigger correlation detection rules.
        """
        metrics_by_sql_id: dict[str, SqlMetric] = {}

        # Thu thập theo 3 chiều đo lường cốt lõi ([EE-04])
        for sort_metric in ["elapsed_time", "cpu_time", "disk_reads"]:
            raw = await self.mcp.call_tool("get_top_sql", {
                "metric": sort_metric,
                "limit": 50,
                "hours": 1
            })
            for item in raw:
                metric = SqlMetric.from_mcp_response(item)
                # Giữ lại hoặc merge metric mới nhất
                metrics_by_sql_id[metric.sql_id] = metric

        metrics = list(metrics_by_sql_id.values())

        async with self.repo.session() as session:
            snapshot = await session.create_snapshot()
            for metric in metrics:
                await session.upsert_sql_metric(metric, snapshot_id=snapshot.id)

        # Trigger detection rules
        await CorrelationEngine().evaluate_sql_metrics(metrics)
```

### 5.3 Session Collector

```python
class SessionCollector:
    async def collect(self):
        """
        Thu thập:
        - Active sessions (get_active_sessions)
        - Blocking chains (get_blocking_sessions)
        - Long running sessions (get_long_running_sessions)
        """
        blocking = await self.mcp.call_tool("get_blocking_sessions", {})
        if blocking.get("total_blocked", 0) > 0:
            # Immediate: tạo evidence với đầy đủ required fields ([EE-01])
            evidence = Evidence(
                id=uuid4(),
                incident_id=None,
                type=EvidenceType.BLOCKING_SESSION,
                source="V$SESSION / get_blocking_sessions",
                timestamp=datetime.utcnow(),
                entity_type="SESSION",
                entity_id=str(blocking.get("root_blocker_sid", "UNKNOWN")),
                severity=Severity.HIGH,
                data=blocking
            )
            await CorrelationEngine().raise_incident(evidence)
```

---

## 6. Evidence Normalization

```python
# src/db_copilot/evidence/normalizers/evidence_normalizer.py

from uuid import uuid4
from datetime import datetime

class EvidenceNormalizer:
    """
    Convert raw MCP tool response thành typed Evidence objects.
    Áp dụng business logic (thresholds, severity mapping).
    """

    def normalize_sql_regression(
        self,
        current: SqlMetric,
        baseline: SqlBaseline,
        multiplier: float
    ) -> Evidence | None:
        if not baseline.is_reliable:
            return None  # Không đủ data

        ratio = current.elapsed_time_ms / baseline.mean_elapsed_ms
        if ratio < multiplier:
            return None  # Không regression

        # Cung cấp đầy đủ required fields để tránh TypeError/Runtime Crash ([EE-01])
        return Evidence(
            id=uuid4(),
            incident_id=None,
            type=EvidenceType.SQL_REGRESSION,
            source="sql_metrics + sql_baselines",
            timestamp=datetime.utcnow(),
            entity_type="SQL",
            entity_id=current.sql_id,
            severity=self._severity_from_ratio(ratio),
            data={
                "sql_id": current.sql_id,
                "current_elapsed_ms": current.elapsed_time_ms,
                "baseline_avg_ms": baseline.mean_elapsed_ms,
                "regression_ratio": ratio,
                "baseline_sample_count": baseline.sample_count
            }
        )

    def _severity_from_ratio(self, ratio: float) -> Severity:
        if ratio >= 10:
            return Severity.CRITICAL
        elif ratio >= 5:
            return Severity.HIGH
        elif ratio >= 3:
            return Severity.MEDIUM
        return Severity.LOW
```

---

## 7. Evidence Repository (PostgreSQL)

```python
# src/db_copilot/evidence/repository.py

class EvidenceRepository:
    async def upsert_sql_metric(self, metric: SqlMetric, snapshot_id: UUID):
        # Bắt buộc khai báo explicit conflict target (database_id, sql_id, captured_at)
        # để tuân thủ cú pháp PostgreSQL ([EE-05])
        await db.execute(
            """
            INSERT INTO sql_metrics (database_id, snapshot_id, sql_id, captured_at,
                executions, elapsed_time_ms, cpu_time_ms, buffer_gets,
                disk_reads, rows_processed, plan_hash_value)
            VALUES (:database_id, :snapshot_id, :sql_id, :captured_at,
                :executions, :elapsed_time_ms, :cpu_time_ms, :buffer_gets,
                :disk_reads, :rows_processed, :plan_hash_value)
            ON CONFLICT (database_id, sql_id, captured_at) DO NOTHING
            """,
            metric.dict()
        )

    async def get_baseline(self, sql_id: str, hour: int, dow: int) -> SqlBaseline | None:
        row = await db.fetch_one(
            """
            SELECT * FROM sql_baselines
            WHERE database_id = :db_id AND sql_id = :sql_id
              AND hour_of_day = :hour AND day_of_week = :dow
            """,
            {"db_id": current_db_id, "sql_id": sql_id, "hour": hour, "dow": dow}
        )
        return SqlBaseline(**row) if row else None

    async def get_evidence_for_incident(self, incident_id: UUID) -> list[Evidence]:
        rows = await db.fetch_all(
            "SELECT * FROM evidence_items WHERE incident_id = :id",
            {"id": incident_id}
        )
        return [Evidence(**row) for row in rows]
```

---

## 8. Baseline Calculation

### 8.1 Vấn đề N+1 Query & Giải pháp Aggregation SQL ([EE-03])
Thay vì lặp 3 vòng lồng nhau `N SQL IDs × 24 giờ × 7 ngày = 16,800 DB queries/giờ` làm quá tải kết nối và I/O, hệ thống sử dụng **1 single SQL aggregation query** trực tiếp trong PostgreSQL kết hợp hàm window thống kê `PERCENTILE_CONT`:

```sql
-- Query tính toán toàn bộ baseline 7 ngày chỉ với 1 lượt quét ([EE-03])
SELECT 
    sql_id,
    EXTRACT(HOUR FROM captured_at)::INT AS hour_of_day,
    EXTRACT(DOW  FROM captured_at)::INT AS day_of_week,
    COUNT(*) AS sample_count,
    AVG(elapsed_time_ms)::DECIMAL(15,2) AS mean_elapsed_ms,
    COALESCE(STDDEV(elapsed_time_ms), 0)::DECIMAL(15,2) AS stddev_elapsed_ms,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY elapsed_time_ms)::DECIMAL(15,2) AS p50_elapsed_ms,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY elapsed_time_ms)::DECIMAL(15,2) AS p95_elapsed_ms
FROM sql_metrics
WHERE database_id = :db_id 
  AND captured_at >= NOW() - INTERVAL '7 days'
GROUP BY sql_id, hour_of_day, day_of_week
```

### 8.2 BaselineEngine Implementation

```python
# src/db_copilot/evidence/baseline.py

import statistics
from datetime import datetime
from db_copilot.domain.models.sql_metric import SqlMetric
from db_copilot.domain.models.baseline import SqlBaseline

class BaselineEngine:
    """
    Tính toán baseline hiệu năng SQL từ dữ liệu 7 ngày gần nhất.
    Chạy định kỳ mỗi 1 giờ.
    """

    def __init__(self, repo: EvidenceRepository):
        self.repo = repo

    def _remove_outliers(self, samples: list[SqlMetric]) -> list[SqlMetric]:
        """
        Loại bỏ các điểm đo dị biệt (> 2 độ lệch chuẩn stddev) ([EE-02]).
        Nếu mẫu < 3 thì giữ nguyên để tránh bias thống kê.
        """
        if len(samples) < 3:
            return samples
        mean = statistics.mean(s.elapsed_time_ms for s in samples)
        stddev = statistics.stdev(s.elapsed_time_ms for s in samples)
        return [s for s in samples if abs(s.elapsed_time_ms - mean) <= 2 * stddev]

    async def recalculate(self, database_id: str):
        """
        Thực thi tính toán baseline:
        - Sử dụng aggregation query duy nhất để lấy thống kê ([EE-03])
        - Batch upsert vào bảng sql_baselines với conflict target rõ ràng
        """
        rows = await self.repo.calculate_aggregated_baselines(database_id, days=7)

        baselines_to_upsert = []
        for r in rows:
            sample_count = r["sample_count"]
            is_reliable = sample_count >= 5

            baselines_to_upsert.append(SqlBaseline(
                database_id=database_id,
                sql_id=r["sql_id"],
                hour_of_day=r["hour_of_day"],
                day_of_week=r["day_of_week"],
                sample_count=sample_count,
                mean_elapsed_ms=float(r["mean_elapsed_ms"]),
                stddev_elapsed_ms=float(r["stddev_elapsed_ms"]),
                p50_elapsed_ms=float(r["p50_elapsed_ms"]),
                p95_elapsed_ms=float(r["p95_elapsed_ms"]),
                is_reliable=is_reliable,
                calculated_at=datetime.utcnow()
            ))

        await self.repo.batch_upsert_baselines(baselines_to_upsert)
```

---

---

# 🇬🇧 ENGLISH SECTION

---

## 9. Overview

Evidence Engine is the layer in `db-copilot` responsible for:

1. **Collect**: Call oracle-mcp-server periodically to fetch data
2. **Normalize**: Convert raw data into typed Evidence objects
3. **Store**: Persist to PostgreSQL Evidence Store
4. **Serve**: Provide evidence to Correlation Engine and Investigation Engine

The Evidence Engine does **not analyze** and does **not make decisions** — that is the job of Correlation Engine and AI Service.

---

## 10. Collection Schedule

| Collector | Interval | What it collects |
|---|---|---|
| `SqlCollector` | Every 5 min | Multi-dimensional Top SQL (elapsed_time, cpu_time, disk_reads) to detect latency spikes, CPU hogs, and IO hogs ([EE-04]) |
| `SessionCollector` | Every 5 min | Active sessions, blocking chains, long-running (full `id`, `timestamp` fields [EE-01]) |
| `StorageCollector` | Every 5 min | Tablespace usage, temp, undo |
| `BaselineEngine` | Every 1 hour | Recalculate SQL baselines using single PostgreSQL aggregation query ([EE-03]) |
| `ReportService` | Daily 6:00 AM | Generate daily health report |

---

## 11. Evidence Types

_(See Section 3 — same table)_

12 evidence types covering SQL performance, sessions, storage, jobs, and objects.

---

## 12. Normalization & Reliability Rules

- **Full Constructor Fields ([EE-01])**: All `Evidence` instantiations include required `id: UUID`, `incident_id: UUID | None`, and `timestamp: datetime` to avoid runtime TypeErrors.
- **SQL Regression**: `current_elapsed > baseline_mean × multiplier` (default 3.0)
- **Severity mapping**: ratio ≥ 10 → CRITICAL, ≥ 5 → HIGH, ≥ 3 → MEDIUM
- **Minimum baseline samples**: 5 required for reliable baseline
- **Outlier removal ([EE-02])**: `_remove_outliers()` filters samples > 2 standard deviations when sample size ≥ 3.
- **Single Aggregation Query ([EE-03])**: Eliminates 16,800 DB queries/hour by executing 1 analytical query using `PERCENTILE_CONT(0.5)` and `PERCENTILE_CONT(0.95)` with `GROUP BY sql_id, hour_of_day, day_of_week`.

---

## 13. Evidence Store

PostgreSQL tables: `snapshots`, `sql_metrics`, `sql_baselines`, `incidents`, `evidence_items`

Key design:
- `sql_metrics` enforces `UNIQUE(database_id, sql_id, captured_at)` to support explicit `ON CONFLICT (database_id, sql_id, captured_at) DO NOTHING` ([EE-05]).
- `sql_baselines` keyed on `(database_id, sql_id, hour_of_day, day_of_week)` — time-bucketed.
- `evidence_items.data` as JSONB — flexible schema per evidence type.
- Evidence is retained for 90 days (configurable).
