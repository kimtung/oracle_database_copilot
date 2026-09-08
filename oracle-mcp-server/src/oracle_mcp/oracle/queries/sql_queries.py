"""SQL query strings for oracle/repositories/sql_repo.py and storage_repo.py."""

# ── Database / Instance Info ─────────────────────────────────────────────────

DATABASE_INFO = """
SELECT
    d.name              AS db_name,
    d.db_unique_name    AS db_unique_name,
    d.created           AS created,
    d.log_mode          AS log_mode,
    i.instance_name     AS instance_name,
    i.host_name         AS host_name,
    i.version           AS version,
    i.status            AS status,
    i.startup_time      AS startup_time,
    i.logins            AS logins
FROM v$database d
CROSS JOIN v$instance i
"""

# ── Top SQL ──────────────────────────────────────────────────────────────────

TOP_SQL_BY_ELAPSED = """
SELECT
    sql_id,
    SUBSTR(sql_text, 1, 200)            AS sql_text_fragment,
    executions,
    ROUND(elapsed_time / 1e6, 3)        AS elapsed_time_sec,
    ROUND(cpu_time / 1e6, 3)            AS cpu_time_sec,
    buffer_gets,
    disk_reads,
    rows_processed,
    plan_hash_value,
    module,
    action,
    last_active_time
FROM v$sqlstats
WHERE executions > 0
  AND last_active_time >= SYSDATE - :hours / 24
ORDER BY elapsed_time DESC
FETCH FIRST :limit ROWS ONLY
"""

TOP_SQL_BY_CPU = """
SELECT
    sql_id,
    SUBSTR(sql_text, 1, 200)            AS sql_text_fragment,
    executions,
    ROUND(elapsed_time / 1e6, 3)        AS elapsed_time_sec,
    ROUND(cpu_time / 1e6, 3)            AS cpu_time_sec,
    buffer_gets,
    disk_reads,
    rows_processed,
    plan_hash_value,
    module,
    action,
    last_active_time
FROM v$sqlstats
WHERE executions > 0
  AND last_active_time >= SYSDATE - :hours / 24
ORDER BY cpu_time DESC
FETCH FIRST :limit ROWS ONLY
"""

TOP_SQL_BY_IO = """
SELECT
    sql_id,
    SUBSTR(sql_text, 1, 200)            AS sql_text_fragment,
    executions,
    ROUND(elapsed_time / 1e6, 3)        AS elapsed_time_sec,
    ROUND(cpu_time / 1e6, 3)            AS cpu_time_sec,
    buffer_gets,
    disk_reads,
    rows_processed,
    plan_hash_value,
    module,
    action,
    last_active_time
FROM v$sqlstats
WHERE executions > 0
  AND last_active_time >= SYSDATE - :hours / 24
ORDER BY disk_reads DESC
FETCH FIRST :limit ROWS ONLY
"""

TOP_SQL_BY_BUFFER_GETS = """
SELECT
    sql_id,
    SUBSTR(sql_text, 1, 200)            AS sql_text_fragment,
    executions,
    ROUND(elapsed_time / 1e6, 3)        AS elapsed_time_sec,
    ROUND(cpu_time / 1e6, 3)            AS cpu_time_sec,
    buffer_gets,
    disk_reads,
    rows_processed,
    plan_hash_value,
    module,
    action,
    last_active_time
FROM v$sqlstats
WHERE executions > 0
  AND last_active_time >= SYSDATE - :hours / 24
ORDER BY buffer_gets DESC
FETCH FIRST :limit ROWS ONLY
"""

TOP_SQL_BY_EXECUTIONS = """
SELECT
    sql_id,
    SUBSTR(sql_text, 1, 200)            AS sql_text_fragment,
    executions,
    ROUND(elapsed_time / 1e6, 3)        AS elapsed_time_sec,
    ROUND(cpu_time / 1e6, 3)            AS cpu_time_sec,
    buffer_gets,
    disk_reads,
    rows_processed,
    plan_hash_value,
    module,
    action,
    last_active_time
FROM v$sqlstats
WHERE executions > 0
  AND last_active_time >= SYSDATE - :hours / 24
ORDER BY executions DESC
FETCH FIRST :limit ROWS ONLY
"""

# ── SQL Statistics (single SQL_ID) ──────────────────────────────────────────

SQL_STATISTICS = """
SELECT
    s.sql_id,
    SUBSTR(s.sql_fulltext, 1, 4000)     AS sql_text,
    s.executions,
    ROUND(s.elapsed_time / 1e6, 3)      AS elapsed_time_sec,
    ROUND(s.cpu_time / 1e6, 3)          AS cpu_time_sec,
    s.buffer_gets,
    s.disk_reads,
    s.rows_processed,
    s.plan_hash_value,
    s.module,
    s.action,
    s.last_active_time,
    ROUND(s.elapsed_time / GREATEST(s.executions, 1) / 1e6, 3) AS avg_elapsed_sec,
    ROUND(s.cpu_time     / GREATEST(s.executions, 1) / 1e6, 3) AS avg_cpu_sec,
    ROUND(s.buffer_gets  / GREATEST(s.executions, 1), 0)       AS avg_buffer_gets,
    ROUND(s.disk_reads   / GREATEST(s.executions, 1), 0)       AS avg_disk_reads
FROM v$sql s
WHERE s.sql_id = :sql_id
  AND ROWNUM = 1
"""

# ── Active Sessions ───────────────────────────────────────────────────────────

ACTIVE_SESSIONS = """
SELECT
    s.sid,
    s.serial#                           AS serial,
    s.username,
    s.status,
    s.sql_id,
    s.prev_sql_id,
    s.module,
    s.action,
    s.machine,
    s.program,
    s.osuser,
    s.logon_time,
    s.last_call_et                      AS elapsed_seconds,
    s.blocking_session,
    s.blocking_session_status,
    s.event                             AS wait_event,
    s.wait_time,
    s.seconds_in_wait
FROM v$session s
WHERE s.type = 'USER'
  AND s.status != 'INACTIVE'
  AND s.last_call_et >= :min_elapsed_sec
ORDER BY s.last_call_et DESC
"""

# ── Blocking Sessions ────────────────────────────────────────────────────────

BLOCKING_SESSIONS = """
SELECT
    blocker.sid                         AS blocker_sid,
    blocker.serial#                     AS blocker_serial,
    blocker.username                    AS blocker_user,
    blocker.sql_id                      AS blocker_sql_id,
    blocker.event                       AS blocker_wait_event,
    blocker.last_call_et                AS blocker_elapsed_sec,
    blocked.sid                         AS blocked_sid,
    blocked.serial#                     AS blocked_serial,
    blocked.username                    AS blocked_user,
    blocked.sql_id                      AS blocked_sql_id,
    blocked.event                       AS blocked_wait_event,
    blocked.seconds_in_wait             AS blocked_wait_sec
FROM v$session blocked
JOIN v$session blocker
    ON blocked.blocking_session = blocker.sid
   AND blocked.blocking_session_status = 'VALID'
WHERE blocked.type = 'USER'
ORDER BY blocked.seconds_in_wait DESC
"""

# ── Long-running Sessions ────────────────────────────────────────────────────

LONG_RUNNING_SESSIONS = """
SELECT
    s.sid,
    s.serial#                           AS serial,
    s.username,
    s.sql_id,
    s.module,
    s.action,
    s.machine,
    s.logon_time,
    s.last_call_et                      AS elapsed_seconds,
    s.event                             AS wait_event,
    s.state
FROM v$session s
WHERE s.type = 'USER'
  AND s.status = 'ACTIVE'
  AND s.last_call_et >= :min_seconds
ORDER BY s.last_call_et DESC
"""
