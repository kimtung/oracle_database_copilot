export type Severity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';

export type IncidentStatus = 'OPEN' | 'INVESTIGATING' | 'ACKNOWLEDGED' | 'RESOLVED';

export interface Incident {
  id: string;
  incident_id?: string;
  title?: string;
  summary: string;
  description?: string;
  severity: Severity;
  status: IncidentStatus;
  rule_name: string;
  root_cause_hypothesis?: string;
  confidence_score?: number;
  created_at: string;
  updated_at?: string;
  evidence_count?: number;
  metadata?: Record<string, unknown>;
}

export type StepStatus = 'PENDING' | 'RUNNING' | 'SUCCESS' | 'FAILED' | 'SKIPPED';

export interface InvestigationStep {
  step_id: string;
  tool_name: string;
  description?: string;
  params: Record<string, unknown>;
  status: StepStatus;
  result?: unknown;
  duration_ms?: number;
  error?: string;
}

export interface Recommendation {
  action: string;
  priority: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  command?: string;
  rationale?: string;
}

export interface DiagnosisResult {
  incident_id?: string;
  root_cause: string;
  confidence: number;
  impacted_components: string[];
  recommendations: Recommendation[];
  explanation: string;
  full_diagnosis?: string;
}

export interface InvestigationSession {
  investigation_id: string;
  intent: string;
  status: 'QUEUED' | 'IN_PROGRESS' | 'COMPLETED' | 'FAILED';
  target_object?: string;
  steps: InvestigationStep[];
  diagnosis?: DiagnosisResult;
  created_at: string;
  completed_at?: string;
}

export interface DailyReport {
  id?: string;
  report_date: string;
  health_score: number;
  summary: string;
  incidents_count: number;
  markdown_narrative?: string;
  metrics_summary?: {
    avg_cpu_percent?: number;
    peak_active_sessions?: number;
    max_tablespace_pct?: number;
    total_sql_executed?: number;
  };
}

export interface SystemMetrics {
  health_score: number;
  active_sessions: number;
  blocking_sessions: number;
  cpu_utilization: number;
  tablespace_utilization: number;
  long_running_count: number;
  invalid_objects_count: number;
  oracle_status: 'CONNECTED' | 'DISCONNECTED' | 'DEGRADED';
  mcp_status: 'HEALTHY' | 'WARNING' | 'DOWN';
}
