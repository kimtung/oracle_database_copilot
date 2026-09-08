-- =============================================================================
-- DB Copilot — Oracle Read-Only Account Setup
-- Run as: sqlplus sys/password@ORCL as sysdba @grants.sql
-- =============================================================================

-- 1. Create the read-only user (change password before running!)
-- =============================================================================
CREATE USER db_copilot_readonly IDENTIFIED BY "ChangeMe_2026!";

-- Allow connection
GRANT CREATE SESSION TO db_copilot_readonly;

-- =============================================================================
-- 2. AWR / ASH — Historical performance data
-- =============================================================================
GRANT SELECT ON SYS.DBA_HIST_SQLSTAT            TO db_copilot_readonly;
GRANT SELECT ON SYS.DBA_HIST_SQL_PLAN           TO db_copilot_readonly;
GRANT SELECT ON SYS.DBA_HIST_SQLTEXT            TO db_copilot_readonly;
GRANT SELECT ON SYS.DBA_HIST_SNAPSHOT           TO db_copilot_readonly;
GRANT SELECT ON SYS.DBA_HIST_SYS_TIME_MODEL     TO db_copilot_readonly;
GRANT SELECT ON SYS.DBA_HIST_ACTIVE_SESS_HISTORY TO db_copilot_readonly;
GRANT SELECT ON SYS.DBA_HIST_SYSSTAT            TO db_copilot_readonly;

-- =============================================================================
-- 3. V$ Dynamic Views — Real-time monitoring
-- =============================================================================
GRANT SELECT ON SYS.V_$SQL                      TO db_copilot_readonly;
GRANT SELECT ON SYS.V_$SQLSTATS                 TO db_copilot_readonly;
GRANT SELECT ON SYS.V_$SQL_PLAN                 TO db_copilot_readonly;
GRANT SELECT ON SYS.V_$SQL_PLAN_STATISTICS_ALL  TO db_copilot_readonly;
GRANT SELECT ON SYS.V_$SESSION                  TO db_copilot_readonly;
GRANT SELECT ON SYS.V_$SESSION_WAIT             TO db_copilot_readonly;
GRANT SELECT ON SYS.V_$ACTIVE_SESSION_HISTORY   TO db_copilot_readonly;
GRANT SELECT ON SYS.V_$DATABASE                 TO db_copilot_readonly;
GRANT SELECT ON SYS.V_$INSTANCE                 TO db_copilot_readonly;
GRANT SELECT ON SYS.V_$PARAMETER                TO db_copilot_readonly;
GRANT SELECT ON SYS.V_$SYSSTAT                  TO db_copilot_readonly;
GRANT SELECT ON SYS.V_$SYSEVENT                 TO db_copilot_readonly;
GRANT SELECT ON SYS.V_$LOG                      TO db_copilot_readonly;
GRANT SELECT ON SYS.V_$ARCHIVED_LOG             TO db_copilot_readonly;
GRANT SELECT ON SYS.V_$TEMPSTAT                 TO db_copilot_readonly;
GRANT SELECT ON SYS.V_$UNDOSTAT                 TO db_copilot_readonly;

-- =============================================================================
-- 4. Storage — Tablespace, segments
-- =============================================================================
GRANT SELECT ON SYS.DBA_DATA_FILES              TO db_copilot_readonly;
GRANT SELECT ON SYS.DBA_FREE_SPACE              TO db_copilot_readonly;
GRANT SELECT ON SYS.DBA_SEGMENTS                TO db_copilot_readonly;
GRANT SELECT ON SYS.DBA_TABLESPACES             TO db_copilot_readonly;
GRANT SELECT ON SYS.DBA_TEMP_FILES              TO db_copilot_readonly;

-- =============================================================================
-- 5. Scheduler Jobs
-- =============================================================================
GRANT SELECT ON SYS.DBA_SCHEDULER_JOBS          TO db_copilot_readonly;
GRANT SELECT ON SYS.DBA_SCHEDULER_JOB_RUN_DETAILS TO db_copilot_readonly;
GRANT SELECT ON SYS.DBA_SCHEDULER_RUNNING_JOBS  TO db_copilot_readonly;

-- =============================================================================
-- 6. PL/SQL Source & Objects
-- =============================================================================
GRANT SELECT ON SYS.ALL_SOURCE                  TO db_copilot_readonly;
GRANT SELECT ON SYS.ALL_OBJECTS                 TO db_copilot_readonly;
GRANT SELECT ON SYS.DBA_OBJECTS                 TO db_copilot_readonly;
GRANT SELECT ON SYS.ALL_DEPENDENCIES            TO db_copilot_readonly;
GRANT SELECT ON SYS.ALL_ARGUMENTS               TO db_copilot_readonly;
GRANT SELECT ON SYS.DBA_TAB_STATISTICS          TO db_copilot_readonly;
GRANT SELECT ON SYS.DBA_IND_STATISTICS          TO db_copilot_readonly;
GRANT SELECT ON SYS.DBA_INDEXES                 TO db_copilot_readonly;

-- =============================================================================
-- 7. Diagnostics (Alert Log)
-- =============================================================================
GRANT SELECT ON SYS.V_$DIAG_ALERT_EXT          TO db_copilot_readonly;

-- =============================================================================
-- VERIFICATION — Run these to confirm grants are in place
-- =============================================================================
-- SELECT * FROM SESSION_PRIVS;
-- SELECT * FROM USER_TAB_PRIVS;

-- =============================================================================
-- NOT GRANTED (enforced explicitly):
--   INSERT, UPDATE, DELETE, MERGE
--   CREATE, ALTER, DROP, TRUNCATE
--   EXECUTE (any procedure)
--   DBA role
-- =============================================================================

COMMIT;
