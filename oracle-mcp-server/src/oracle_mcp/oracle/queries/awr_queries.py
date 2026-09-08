"""Oracle query strings for AWR (Automatic Workload Repository)."""

# ── AWR Snapshots ─────────────────────────────────────────────────────────────

AWR_SNAPSHOTS = """
SELECT
    snap_id,
    dbid,
    instance_number,
    startup_time,
    begin_interval_time,
    end_interval_time,
    flush_elapsed,
    snap_level
FROM dba_hist_snapshot
WHERE begin_interval_time >= SYSDATE - :hours / 24
ORDER BY snap_id
"""

# ── AWR SQL Stats ─────────────────────────────────────────────────────────────

AWR_SQL_STATS = """
SELECT
    s.snap_id,
    sn.begin_interval_time,
    sn.end_interval_time,
    s.sql_id,
    s.plan_hash_value,
    s.executions_delta                  AS executions,
    ROUND(s.elapsed_time_delta / 1e6, 3) AS elapsed_time_sec,
    ROUND(s.cpu_time_delta / 1e6, 3)    AS cpu_time_sec,
    s.buffer_gets_delta                 AS buffer_gets,
    s.disk_reads_delta                  AS disk_reads,
    s.rows_processed_delta              AS rows_processed,
    CASE
        WHEN s.executions_delta > 0
        THEN ROUND(s.elapsed_time_delta / s.executions_delta / 1e6, 4)
        ELSE NULL
    END                                 AS avg_elapsed_sec
FROM dba_hist_sqlstat s
JOIN dba_hist_snapshot sn
    ON s.snap_id = sn.snap_id AND s.dbid = sn.dbid
WHERE s.sql_id = :sql_id
  AND sn.begin_interval_time >= SYSDATE - :days
ORDER BY s.snap_id
"""

# ── AWR SQL Stats by snap range ───────────────────────────────────────────────

AWR_SQL_STATS_BY_SNAP = """
SELECT
    s.snap_id,
    sn.begin_interval_time,
    sn.end_interval_time,
    s.sql_id,
    s.plan_hash_value,
    s.executions_delta                  AS executions,
    ROUND(s.elapsed_time_delta / 1e6, 3) AS elapsed_time_sec,
    ROUND(s.cpu_time_delta / 1e6, 3)    AS cpu_time_sec,
    s.buffer_gets_delta                 AS buffer_gets,
    s.disk_reads_delta                  AS disk_reads,
    s.rows_processed_delta              AS rows_processed
FROM dba_hist_sqlstat s
JOIN dba_hist_snapshot sn
    ON s.snap_id = sn.snap_id AND s.dbid = sn.dbid
WHERE s.sql_id = :sql_id
  AND s.snap_id BETWEEN :begin_snap AND :end_snap
ORDER BY s.snap_id
"""
