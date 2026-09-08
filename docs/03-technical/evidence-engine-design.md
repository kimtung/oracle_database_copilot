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
        1. Gọi get_top_sql từ oracle-mcp-server
        2. Normalize thành SqlMetric objects
        3. Lưu vào PostgreSQL
        4. Trigger correlation rules
        """
        raw = await self.mcp.call_tool("get_top_sql", {
            "metric": "elapsed_time",
            "limit": 100,
            "hours": 1
        })

        metrics = [SqlMetric.from_mcp_response(item) for item in raw]

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
        if blocking["total_blocked"] > 0:
            # Immediate: tạo evidence và incident
            evidence = Evidence(
                type=EvidenceType.BLOCKING_SESSION,
                severity=Severity.HIGH,
                data=blocking
            )
            await CorrelationEngine().raise_incident(evidence)
```

---

## 6. Evidence Normalization

```python
# src/db_copilot/evidence/normalizers/evidence_normalizer.py

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

        return Evidence(
            type=EvidenceType.SQL_REGRESSION,
            source="sql_metrics + sql_baselines",
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
        await db.execute(
            """
            INSERT INTO sql_metrics (database_id, snapshot_id, sql_id, captured_at,
                executions, elapsed_time_ms, cpu_time_ms, buffer_gets,
                disk_reads, rows_processed, plan_hash_value)
            VALUES (:database_id, :snapshot_id, :sql_id, :captured_at,
                :executions, :elapsed_time_ms, :cpu_time_ms, :buffer_gets,
                :disk_reads, :rows_processed, :plan_hash_value)
            ON CONFLICT DO NOTHING
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

```python
# src/db_copilot/evidence/collectors/sql_collector.py (BaselineEngine)

class BaselineEngine:
    """
    Tính baseline từ 7 ngày lịch sử, theo time bucket (hour, day_of_week).
    Chạy mỗi giờ.
    """

    async def recalculate(self):
        sql_ids = await self.repo.get_active_sql_ids(days=7)

        for sql_id in sql_ids:
            for hour in range(24):
                for dow in range(7):
                    samples = await self.repo.get_sql_metrics(
                        sql_id=sql_id,
                        hour=hour,
                        day_of_week=dow,
                        days=7
                    )

                    if len(samples) < 5:
                        # Không đủ data, đánh dấu unreliable
                        await self.repo.upsert_baseline(SqlBaseline(
                            sql_id=sql_id,
                            hour_of_day=hour,
                            day_of_week=dow,
                            sample_count=len(samples),
                            is_reliable=False
                        ))
                        continue

                    # Loại bỏ outliers (> 2 stddev)
                    filtered = self._remove_outliers(samples)

                    elapsed_values = [s.elapsed_time_ms for s in filtered]
                    baseline = SqlBaseline(
                        sql_id=sql_id,
                        hour_of_day=hour,
                        day_of_week=dow,
                        sample_count=len(filtered),
                        mean_elapsed_ms=statistics.mean(elapsed_values),
                        stddev_elapsed_ms=statistics.stdev(elapsed_values),
                        p50_elapsed_ms=statistics.median(elapsed_values),
                        p95_elapsed_ms=self._p95(elapsed_values),
                        is_reliable=True
                    )
                    await self.repo.upsert_baseline(baseline)
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
| `SqlCollector` | Every 5 min | Top 100 SQL by elapsed time, CPU, IO |
| `SessionCollector` | Every 5 min | Active sessions, blocking chains, long-running |
| `StorageCollector` | Every 5 min | Tablespace usage, temp, undo |
| `BaselineEngine` | Every 1 hour | Recalculate SQL baselines (7-day rolling window) |
| `ReportService` | Daily 6:00 AM | Generate daily health report |

---

## 11. Evidence Types

_(See Section 3 — same table)_

12 evidence types covering SQL performance, sessions, storage, jobs, and objects.

---

## 12. Normalization Rules

- **SQL Regression**: `current_elapsed > baseline_mean × multiplier` (default 3.0)
- **Severity mapping**: ratio ≥ 10 → CRITICAL, ≥ 5 → HIGH, ≥ 3 → MEDIUM
- **Minimum baseline samples**: 5 required for reliable baseline
- **Outlier removal**: Remove samples > 2 standard deviations before baseline calculation

---

## 13. Evidence Store

PostgreSQL tables: `snapshots`, `sql_metrics`, `sql_baselines`, `incidents`, `evidence_items`

Key design:
- `sql_baselines` keyed on `(database_id, sql_id, hour_of_day, day_of_week)` — time-bucketed
- `evidence_items.data` as JSONB — flexible schema per evidence type
- Evidence is retained for 90 days (configurable)
