"""Oracle query strings for ASH (Active Session History)."""

# ── Real-time ASH (V$ACTIVE_SESSION_HISTORY) ────────────────────────────────

ASH_SAMPLE = """
SELECT
    sample_id,
    sample_time,
    session_id,
    session_serial#                     AS session_serial,
    user_id,
    sql_id,
    sql_child_number,
    sql_plan_hash_value,
    session_state,
    wait_class,
    event,
    time_waited,
    module,
    action,
    machine,
    program
FROM v$active_session_history
WHERE sample_time BETWEEN :begin_time AND :end_time
ORDER BY sample_time DESC
"""

# ── Historical ASH (DBA_HIST_ACTIVE_SESS_HISTORY) ────────────────────────────

ASH_SQL_ACTIVITY = """
SELECT
    h.sample_time,
    h.session_id,
    h.session_serial#                   AS session_serial,
    h.sql_id,
    h.sql_plan_hash_value,
    h.session_state,
    h.wait_class,
    h.event,
    h.time_waited,
    h.module,
    h.action,
    h.machine
FROM dba_hist_active_sess_history h
WHERE h.sql_id = :sql_id
  AND h.sample_time BETWEEN :begin_time AND :end_time
ORDER BY h.sample_time DESC
FETCH FIRST 1000 ROWS ONLY
"""

ASH_TOP_SQL_IN_RANGE = """
SELECT
    sql_id,
    COUNT(*)                            AS sample_count,
    SUM(time_waited) / 1e6             AS total_wait_sec,
    MAX(sql_plan_hash_value)            AS plan_hash_value,
    MAX(module)                         AS module,
    MAX(action)                         AS action
FROM dba_hist_active_sess_history
WHERE sample_time BETWEEN :begin_time AND :end_time
  AND sql_id IS NOT NULL
GROUP BY sql_id
ORDER BY sample_count DESC
FETCH FIRST 20 ROWS ONLY
"""

# ── SQL Wait Events ───────────────────────────────────────────────────────────

SQL_WAIT_EVENTS = """
SELECT
    event,
    wait_class,
    COUNT(*)                            AS wait_count,
    SUM(time_waited) / 1e6             AS total_wait_sec,
    ROUND(AVG(time_waited) / 1e3, 2)   AS avg_wait_ms,
    MAX(time_waited) / 1e6             AS max_wait_sec
FROM v$active_session_history
WHERE sql_id = :sql_id
  AND sample_time >= SYSDATE - :hours / 24
  AND event IS NOT NULL
GROUP BY event, wait_class
ORDER BY total_wait_sec DESC
"""

# ── SQL Execution Context ────────────────────────────────────────────────────

SQL_EXECUTION_CONTEXT = """
SELECT
    sql_id,
    module,
    action,
    program,
    machine,
    COUNT(DISTINCT session_id)          AS distinct_sessions,
    COUNT(*)                            AS sample_count,
    MAX(sample_time)                    AS last_seen
FROM v$active_session_history
WHERE sql_id = :sql_id
  AND sample_time >= SYSDATE - :hours / 24
GROUP BY sql_id, module, action, program, machine
ORDER BY sample_count DESC
FETCH FIRST 10 ROWS ONLY
"""
