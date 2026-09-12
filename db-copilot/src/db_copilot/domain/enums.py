from enum import StrEnum


class Severity(StrEnum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class IncidentCategory(StrEnum):
    SQL_REGRESSION = "SQL_REGRESSION"
    BLOCKING = "BLOCKING"
    TABLESPACE = "TABLESPACE"
    JOB_FAILURE = "JOB_FAILURE"
    LONG_RUNNING_SESSION = "LONG_RUNNING_SESSION"
    INVALID_OBJECT = "INVALID_OBJECT"


class IncidentStatus(StrEnum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"


class EvidenceType(StrEnum):
    SQL_PLAN_CHANGE = "sql_plan_change"
    SQL_REGRESSION = "sql_regression"
    STALE_STATISTICS = "stale_statistics"
    CARDINALITY_MISMATCH = "cardinality_mismatch"
    BLOCKING_SESSION = "blocking_session"
    LONG_RUNNING_SESSION = "long_running_session"
    TABLESPACE_FULL = "tablespace_full"
    JOB_FAILURE = "job_failure"
    INVALID_OBJECTS = "invalid_objects"
    HIGH_CPU = "high_cpu"
    TEMP_FULL = "temp_full"
    UNDO_CONTENTION = "undo_contention"
