"""Oracle query strings for storage, jobs, redo, and database health."""

# ── Tablespace Usage ──────────────────────────────────────────────────────────

TABLESPACE_USAGE = """
SELECT
    ts.tablespace_name,
    ts.contents,
    ts.status,
    NVL(f.total_bytes, 0)               AS total_bytes,
    NVL(f.total_bytes, 0) - NVL(fr.free_bytes, 0) AS used_bytes,
    NVL(fr.free_bytes, 0)               AS free_bytes,
    ROUND(
        (NVL(f.total_bytes, 0) - NVL(fr.free_bytes, 0))
        / NULLIF(NVL(f.total_bytes, 0), 0) * 100, 2
    )                                   AS used_pct
FROM dba_tablespaces ts
LEFT JOIN (
    SELECT tablespace_name, SUM(bytes) AS total_bytes
    FROM dba_data_files
    GROUP BY tablespace_name
) f ON ts.tablespace_name = f.tablespace_name
LEFT JOIN (
    SELECT tablespace_name, SUM(bytes) AS free_bytes
    FROM dba_free_space
    GROUP BY tablespace_name
) fr ON ts.tablespace_name = fr.tablespace_name
ORDER BY used_pct DESC NULLS LAST
"""

# ── Datafiles per Tablespace ──────────────────────────────────────────────────

DATAFILE_USAGE = """
SELECT
    file_name,
    tablespace_name,
    bytes,
    maxbytes,
    autoextensible,
    status
FROM dba_data_files
WHERE tablespace_name = :tablespace_name
ORDER BY file_name
"""

# ── Temp Usage ────────────────────────────────────────────────────────────────

TEMP_USAGE = """
SELECT
    tf.tablespace_name,
    SUM(tf.bytes)                       AS total_bytes,
    SUM(ts.bytes_used)                  AS used_bytes,
    SUM(tf.bytes) - SUM(ts.bytes_used)  AS free_bytes,
    ROUND(SUM(ts.bytes_used) / NULLIF(SUM(tf.bytes), 0) * 100, 2) AS used_pct
FROM dba_temp_files tf
JOIN v$tempstat ts ON tf.file_id = ts.file#
GROUP BY tf.tablespace_name
"""

# ── Undo Usage ────────────────────────────────────────────────────────────────

UNDO_USAGE = """
SELECT
    TO_CHAR(begin_time, 'YYYY-MM-DD HH24:MI:SS') AS period_start,
    TO_CHAR(end_time,   'YYYY-MM-DD HH24:MI:SS') AS period_end,
    undoblks,
    txncount,
    maxquerylen,
    activeblks,
    unexpiredblks,
    expiredblks,
    tuned_undoretention
FROM v$undostat
WHERE begin_time >= SYSDATE - 1/24
ORDER BY begin_time DESC
FETCH FIRST 12 ROWS ONLY
"""

# ── Segment Growth ────────────────────────────────────────────────────────────

SEGMENT_GROWTH = """
SELECT
    owner,
    segment_name,
    segment_type,
    tablespace_name,
    bytes,
    blocks,
    extents
FROM dba_segments
WHERE segment_name = :name
  AND (:owner IS NULL OR owner = :owner)
  AND (:segment_type IS NULL OR segment_type = :segment_type)
"""

# ── Redo Log Statistics ───────────────────────────────────────────────────────

REDO_STATISTICS = """
SELECT
    sequence#,
    bytes,
    members,
    status,
    first_time,
    next_time
FROM v$log
ORDER BY sequence# DESC
"""

ARCHIVED_LOG_RATE = """
SELECT
    TRUNC(first_time, 'HH')            AS hour_bucket,
    COUNT(*)                            AS log_count,
    SUM(blocks * block_size) / 1e9     AS total_gb
FROM v$archived_log
WHERE first_time >= SYSDATE - :hours / 24
  AND standby_dest = 'NO'
GROUP BY TRUNC(first_time, 'HH')
ORDER BY hour_bucket DESC
"""

# ── Alert Log Events ──────────────────────────────────────────────────────────

ALERT_EVENTS = """
SELECT
    originating_timestamp,
    message_text,
    message_level
FROM v$diag_alert_ext
WHERE originating_timestamp >= SYSTIMESTAMP - INTERVAL ':hours' HOUR
  AND message_level <= 2
ORDER BY originating_timestamp DESC
FETCH FIRST 100 ROWS ONLY
"""

# ── Resource Usage ────────────────────────────────────────────────────────────

RESOURCE_USAGE = """
SELECT
    name,
    value
FROM v$sysstat
WHERE name IN (
    'physical reads',
    'physical writes',
    'redo size',
    'user commits',
    'user rollbacks',
    'parse count (total)',
    'parse count (hard)',
    'sorts (disk)',
    'table scans (long tables)',
    'consistent gets'
)
ORDER BY name
"""

# ── Scheduler Jobs ────────────────────────────────────────────────────────────

SCHEDULER_JOBS = """
SELECT
    owner,
    job_name,
    job_type,
    state,
    enabled,
    last_start_date,
    last_run_duration,
    next_run_date,
    failure_count,
    run_count,
    schedule_name
FROM dba_scheduler_jobs
ORDER BY owner, job_name
"""

SCHEDULER_JOB_HISTORY = """
SELECT
    owner,
    job_name,
    log_date,
    status,
    error#                              AS error_code,
    actual_start_date,
    run_duration,
    additional_info
FROM dba_scheduler_job_run_details
WHERE job_name = :job_name
  AND (:owner IS NULL OR owner = :owner)
  AND log_date >= SYSDATE - :days
ORDER BY log_date DESC
FETCH FIRST 100 ROWS ONLY
"""

FAILED_JOBS = """
SELECT
    owner,
    job_name,
    log_date,
    status,
    error#                              AS error_code,
    actual_start_date,
    run_duration,
    additional_info
FROM dba_scheduler_job_run_details
WHERE status != 'SUCCEEDED'
  AND log_date >= SYSDATE - :hours / 24
ORDER BY log_date DESC
"""
