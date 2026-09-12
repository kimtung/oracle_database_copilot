import logging
import math
import statistics
import uuid
from datetime import UTC, datetime
from typing import Any

from db_copilot.db.schema import SqlBaseline
from db_copilot.evidence.repository import EvidenceRepository

logger = logging.getLogger(__name__)


class BaselineEngine:
    """Calculates statistical performance baselines for SQL statements across time buckets."""

    def __init__(self, repo: EvidenceRepository, rolling_days: int = 7, min_samples: int = 5):
        self.repo = repo
        self.rolling_days = rolling_days
        self.min_samples = min_samples

    def remove_outliers(self, values: list[float]) -> list[float]:
        """Filter out values outside mean ± 2 * stddev when sample size allows."""
        if len(values) < 4:
            return values

        mean = statistics.mean(values)
        stddev = statistics.stdev(values)
        if stddev == 0:
            return values

        lower_bound = mean - 2 * stddev
        upper_bound = mean + 2 * stddev
        filtered = [v for v in values if lower_bound <= v <= upper_bound]
        return filtered if filtered else values

    def calculate_p95(self, values: list[float]) -> float:
        """Calculate the 95th percentile using linear interpolation."""
        if not values:
            return 0.0
        if len(values) == 1:
            return values[0]

        sorted_vals = sorted(values)
        k = (len(sorted_vals) - 1) * 0.95
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return sorted_vals[int(k)]
        return sorted_vals[f] * (c - k) + sorted_vals[c] * (k - f)

    def compute_stats(self, values: list[float]) -> dict[str, Any]:
        """Compute mean, stddev, median (p50), and p95 after outlier filtering."""
        filtered = self.remove_outliers(values)
        count = len(filtered)
        if count == 0:
            return {
                "sample_count": 0,
                "mean_elapsed_ms": 0.0,
                "stddev_elapsed_ms": 0.0,
                "p50_elapsed_ms": 0.0,
                "p95_elapsed_ms": 0.0,
                "is_reliable": False,
            }

        mean = statistics.mean(filtered)
        stddev = statistics.stdev(filtered) if count > 1 else 0.0
        p50 = statistics.median(filtered)
        p95 = self.calculate_p95(filtered)
        is_reliable = count >= self.min_samples

        return {
            "sample_count": count,
            "mean_elapsed_ms": round(mean, 2),
            "stddev_elapsed_ms": round(stddev, 2),
            "p50_elapsed_ms": round(p50, 2),
            "p95_elapsed_ms": round(p95, 2),
            "is_reliable": is_reliable,
        }

    async def recalculate(self, database_id: uuid.UUID) -> int:
        """Recalculate baselines for all active SQL statements for the past rolling days."""
        logger.info(f"Starting baseline recalculation for database {database_id}")
        active_sql_ids = await self.repo.get_active_sql_ids(database_id, days=self.rolling_days)
        updated_count = 0

        for sql_id in active_sql_ids:
            for hour in range(24):
                for dow in range(7):
                    samples = await self.repo.get_sql_metrics_by_bucket(
                        database_id=database_id,
                        sql_id=sql_id,
                        hour_of_day=hour,
                        day_of_week=dow,
                        days=self.rolling_days,
                    )
                    elapsed_times = [
                        float(m.elapsed_time_ms)
                        for m in samples
                        if m.elapsed_time_ms is not None
                    ]

                    if not elapsed_times:
                        continue

                    stats = self.compute_stats(elapsed_times)
                    baseline = SqlBaseline(
                        database_id=database_id,
                        sql_id=sql_id,
                        hour_of_day=hour,
                        day_of_week=dow,
                        sample_count=stats["sample_count"],
                        mean_elapsed_ms=stats["mean_elapsed_ms"],
                        stddev_elapsed_ms=stats["stddev_elapsed_ms"],
                        p50_elapsed_ms=stats["p50_elapsed_ms"],
                        p95_elapsed_ms=stats["p95_elapsed_ms"],
                        is_reliable=stats["is_reliable"],
                        calculated_at=datetime.now(UTC),
                    )
                    await self.repo.upsert_baseline(baseline)
                    updated_count += 1

        logger.info(f"Baseline recalculation completed: updated {updated_count} baseline buckets")
        return updated_count
