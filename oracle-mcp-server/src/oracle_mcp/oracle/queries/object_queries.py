"""Oracle query strings for execution plans and object/code access."""

# ── Execution Plan (current, from V$SQL_PLAN) ────────────────────────────────

SQL_PLAN_CURRENT = """
SELECT
    p.operation,
    p.options,
    p.object_owner,
    p.object_name,
    p.object_type,
    p.id                                AS plan_line_id,
    p.parent_id,
    p.depth,
    p.position,
    p.cardinality,
    p.bytes,
    p.cost,
    p.cpu_cost,
    p.io_cost,
    p.time,
    p.access_predicates,
    p.filter_predicates,
    p.projection,
    p.plan_hash_value
FROM v$sql_plan p
WHERE p.sql_id = :sql_id
  AND p.child_number = (
      SELECT MIN(child_number) FROM v$sql WHERE sql_id = :sql_id
  )
ORDER BY p.id
"""

# ── Plan History (from DBA_HIST_SQL_PLAN + DBA_HIST_SQLSTAT) ─────────────────

SQL_PLAN_HISTORY = """
SELECT DISTINCT
    s.plan_hash_value,
    MIN(sn.begin_interval_time)         AS first_seen,
    MAX(sn.end_interval_time)           AS last_seen,
    SUM(s.executions_delta)             AS total_executions,
    ROUND(SUM(s.elapsed_time_delta) / GREATEST(SUM(s.executions_delta), 1) / 1e6, 4)
                                        AS avg_elapsed_sec
FROM dba_hist_sqlstat s
JOIN dba_hist_snapshot sn
    ON s.snap_id = sn.snap_id AND s.dbid = sn.dbid
WHERE s.sql_id = :sql_id
  AND sn.begin_interval_time >= SYSDATE - :days
  AND s.executions_delta > 0
GROUP BY s.plan_hash_value
ORDER BY first_seen
"""

# ── Object Source (ALL_SOURCE) ────────────────────────────────────────────────

OBJECT_SOURCE = """
SELECT
    o.owner,
    o.object_name,
    o.object_type,
    o.status,
    o.last_ddl_time,
    o.created
FROM dba_objects o
WHERE o.object_name = :name
  AND o.object_type = :obj_type
  AND (:owner IS NULL OR o.owner = :owner)
  AND ROWNUM = 1
"""

OBJECT_SOURCE_LINES = """
SELECT
    line,
    text
FROM all_source
WHERE name = :name
  AND type = :obj_type
  AND (:owner IS NULL OR owner = :owner)
ORDER BY line
"""

# ── Object Metadata ───────────────────────────────────────────────────────────

OBJECT_METADATA = """
SELECT
    o.owner,
    o.object_name,
    o.object_type,
    o.status,
    o.last_ddl_time,
    o.created,
    t.num_rows,
    t.blocks,
    t.last_analyzed,
    t.stale_stats
FROM dba_objects o
LEFT JOIN dba_tab_statistics t
    ON o.owner = t.owner AND o.object_name = t.table_name
WHERE o.object_name = :name
  AND (:obj_type IS NULL OR o.object_type = :obj_type)
  AND (:owner IS NULL OR o.owner = :owner)
  AND ROWNUM = 1
"""

# ── Object Arguments ──────────────────────────────────────────────────────────

OBJECT_ARGUMENTS = """
SELECT
    argument_name,
    position,
    sequence,
    data_type,
    defaulted,
    in_out,
    data_length,
    data_precision,
    data_scale
FROM all_arguments
WHERE object_name = :name
  AND (:owner IS NULL OR owner = :owner)
ORDER BY position, sequence
"""

# ── Object Dependencies ───────────────────────────────────────────────────────

OBJECT_DEPENDENCIES = """
SELECT
    name,
    type,
    referenced_owner,
    referenced_name,
    referenced_type
FROM all_dependencies
WHERE name = :name
  AND (:obj_type IS NULL OR type = :obj_type)
  AND (:owner IS NULL OR owner = :owner)
ORDER BY referenced_type, referenced_name
"""

# ── Dependency Graph (N levels) ───────────────────────────────────────────────

DEPENDENCY_GRAPH = """
WITH dep_tree (name, type, owner, referenced_name, referenced_type, referenced_owner, lvl) AS (
    SELECT
        name, type, owner,
        referenced_name, referenced_type, referenced_owner,
        1 AS lvl
    FROM all_dependencies
    WHERE name = :name
      AND (:obj_type IS NULL OR type = :obj_type)
      AND (:owner IS NULL OR owner = :owner)
    UNION ALL
    SELECT
        d.name, d.type, d.owner,
        d.referenced_name, d.referenced_type, d.referenced_owner,
        t.lvl + 1
    FROM all_dependencies d
    JOIN dep_tree t ON d.name = t.referenced_name AND d.type = t.referenced_type
    WHERE t.lvl < :max_depth
)
SELECT DISTINCT name, type, owner, referenced_name, referenced_type, referenced_owner, lvl
FROM dep_tree
ORDER BY lvl, name
"""

# ── Invalid Objects ───────────────────────────────────────────────────────────

INVALID_OBJECTS = """
SELECT
    owner,
    object_name,
    object_type,
    status,
    last_ddl_time
FROM dba_objects
WHERE status = 'INVALID'
  AND object_type IN ('PROCEDURE', 'FUNCTION', 'PACKAGE', 'PACKAGE BODY',
                      'TRIGGER', 'VIEW', 'SYNONYM', 'TYPE', 'TYPE BODY')
ORDER BY owner, object_type, object_name
"""
