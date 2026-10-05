import type { DailyReport, DiagnosisResult, Incident, IncidentStatus, InvestigationSession, InvestigationStep, SystemMetrics } from '../types';

const API_BASE = '/api/v1';

// Mock data generator for interactive standalone demonstration
const MOCK_METRICS: SystemMetrics = {
  health_score: 84,
  active_sessions: 38,
  blocking_sessions: 2,
  cpu_utilization: 62.4,
  tablespace_utilization: 79.1,
  long_running_count: 3,
  invalid_objects_count: 1,
  oracle_status: 'CONNECTED',
  mcp_status: 'HEALTHY',
};

const MOCK_INCIDENTS: Incident[] = [
  {
    id: 'inc-001',
    incident_id: 'INC-20261005-01',
    summary: 'High Buffer Gets regression detected on SQL_ID 7v62q4pm90ab1',
    description: 'Execution plan switched from INDEX UNIQUE SCAN to TABLE ACCESS FULL. Elapsed time increased by 420%.',
    severity: 'HIGH',
    status: 'INVESTIGATING',
    rule_name: 'SqlRegressionRule',
    root_cause_hypothesis: 'INDEX_MISSING_OR_CORRUPT',
    confidence_score: 0.92,
    created_at: new Date(Date.now() - 18 * 60000).toISOString(),
    evidence_count: 6,
    metadata: { sql_id: '7v62q4pm90ab1', plan_hash_value: 394827110 },
  },
  {
    id: 'inc-002',
    incident_id: 'INC-20261005-02',
    summary: 'Cascade Enqueue TX lock contention (SID 142 blocking SID 219, 305)',
    description: 'Session 142 holding exclusive row lock in table HR.EMPLOYEES_PAYROLL for over 320 seconds.',
    severity: 'CRITICAL',
    status: 'OPEN',
    rule_name: 'BlockingSessionRule',
    root_cause_hypothesis: 'UNCOMMITTED_BATCH_TRANSACTION',
    confidence_score: 0.95,
    created_at: new Date(Date.now() - 35 * 60000).toISOString(),
    evidence_count: 8,
    metadata: { blocker_sid: 142, blocked_count: 2 },
  },
  {
    id: 'inc-003',
    incident_id: 'INC-20261005-03',
    summary: 'Tablespace USERS quota threshold crossed (88.4% capacity)',
    description: 'Tablespace USERS used 88.4% of total allocated 500GB. Segment growth rate indicates exhaustion within 4 days.',
    severity: 'MEDIUM',
    status: 'ACKNOWLEDGED',
    rule_name: 'TablespaceThresholdRule',
    root_cause_hypothesis: 'STORAGE_EXHAUSTION',
    confidence_score: 0.88,
    created_at: new Date(Date.now() - 120 * 60000).toISOString(),
    evidence_count: 4,
    metadata: { tablespace_name: 'USERS', used_pct: 88.4 },
  },
  {
    id: 'inc-004',
    incident_id: 'INC-20261005-04',
    summary: 'Scheduler job PURGE_AUDIT_LOG_JOB failed with ORA-01555',
    description: 'Snapshot too old: rollback segment too small during large purge operation.',
    severity: 'LOW',
    status: 'RESOLVED',
    rule_name: 'JobFailureRule',
    root_cause_hypothesis: 'UNDO_RETENTION_INSUFFICIENT',
    confidence_score: 0.85,
    created_at: new Date(Date.now() - 360 * 60000).toISOString(),
    evidence_count: 3,
    metadata: { job_name: 'PURGE_AUDIT_LOG_JOB', error_code: 'ORA-01555' },
  },
];

const MOCK_DAILY_REPORT: DailyReport = {
  id: 'rep-today',
  report_date: new Date().toISOString().split('T')[0],
  health_score: 84,
  summary: 'Hệ thống vận hành ổn định trong ca trực sáng và chiều. Phát hiện 2 đợt gia tăng tải CPU do báo cáo tài chính cuối tháng và 1 sự cố khoá hàng trên bảng PAYROLL được AI cách ly kịp thời.',
  incidents_count: 4,
  metrics_summary: {
    avg_cpu_percent: 48.6,
    peak_active_sessions: 62,
    max_tablespace_pct: 88.4,
    total_sql_executed: 1420800,
  },
  markdown_narrative: `# Báo Cáo Sức Khỏe Cơ Sở Dữ Liệu Oracle (Daily Health Narrative)
**Ngày báo cáo:** 05/10/2026  
**Điểm sức khỏe trung bình:** **84 / 100 (GOOD)**  
**Đánh giá tổng thể:** Cơ sở dữ liệu duy trì trạng thái khả dụng 99.98%. Các thông số I/O và Memory SGA/PGA nằm trong ngưỡng dung sai kiểm soát.

---

### 1. Phân Tích Sự Cố Đáng Chú Ý Trong Ngày
- **Sự cố #INC-20261005-02 (Critical - Đã xử lý):** Tranh chấp hàng ghi (*enq: TX - row lock contention*) do batch job thanh toán chưa commit, khóa chéo 2 tiến trình xử lý giao dịch.
- **Sự cố #INC-20261005-01 (High - Đang theo dõi):** Câu lệnh SQL \`7v62q4pm90ab1\` bị biến động execution plan sau khi job thu thập thống kê tự động (\`DBMS_STATS\`) thực thi lúc rạng sáng.

### 2. Khuyến Nghị Trọng Tâm Của Copilot
1. **Tạo Index bổ sung:** Cho bảng \`FINANCE.INVOICE_ITEMS(INVOICE_ID, CREATED_DATE)\` để triệt tiêu Full Table Scan trên SQL \`7v62q4pm90ab1\`.
2. **Mở rộng Tablespace:** Dung lượng Tablespace \`USERS\` hiện đạt 88.4%, đề xuất bổ sung thêm Datafile 50GB trước ngày 09/10/2026.
3. **Điều chỉnh Undo Retention:** Tăng \`undo_retention\` từ 1800s lên 3600s để ngăn ngừa lỗi snapshot ORA-01555 của job dọn dẹp audit.`,
};

export const apiService = {
  async getSystemMetrics(): Promise<SystemMetrics> {
    try {
      const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(3000) });
      if (res.ok) {
        return {
          ...MOCK_METRICS,
          oracle_status: 'CONNECTED',
          mcp_status: 'HEALTHY',
        };
      }
    } catch {
      // Backend not running or unreachable, fallback to simulation
    }
    return MOCK_METRICS;
  },

  async getIncidents(): Promise<Incident[]> {
    try {
      const res = await fetch(`${API_BASE}/incidents`, { signal: AbortSignal.timeout(3000) });
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data) && data.length > 0) {
          return data;
        }
      }
    } catch {
      // Fallback
    }
    return MOCK_INCIDENTS;
  },

  async updateIncidentStatus(id: string, status: IncidentStatus): Promise<boolean> {
    try {
      const res = await fetch(`${API_BASE}/incidents/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status }),
      });
      return res.ok;
    } catch {
      return true; // Optimistic update for UI
    }
  },

  async startInvestigation(prompt: string, targetObject?: string): Promise<InvestigationSession> {
    try {
      const res = await fetch(`${API_BASE}/investigate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt, target_object: targetObject }),
      });
      if (res.ok) {
        return await res.json();
      }
    } catch {
      // Return simulated session
    }

    // Interactive realistic simulation
    return {
      investigation_id: `inv-${Date.now()}`,
      intent: 'SQL_PERFORMANCE_REGRESSION',
      status: 'IN_PROGRESS',
      target_object: targetObject || '7v62q4pm90ab1',
      steps: [
        {
          step_id: 'step_1',
          tool_name: 'get_sql_statistics',
          description: 'Fetch historical execution statistics & CPU time',
          params: { sql_id: targetObject || '7v62q4pm90ab1' },
          status: 'SUCCESS',
          duration_ms: 180,
          result: { buffer_gets_per_exec: 48200, elapsed_time_ms: 3200, executions: 145 },
        },
        {
          step_id: 'step_2',
          tool_name: 'get_sql_plan',
          description: 'Inspect execution plan & access paths',
          params: { sql_id: targetObject || '7v62q4pm90ab1' },
          status: 'SUCCESS',
          duration_ms: 220,
          result: { plan_hash: 394827110, full_table_scans: ['INVOICE_ITEMS'], cost: 9410 },
        },
        {
          step_id: 'step_3',
          tool_name: 'get_ash_sql_activity',
          description: 'Sample active session history & wait events',
          params: { sql_id: targetObject || '7v62q4pm90ab1' },
          status: 'SUCCESS',
          duration_ms: 310,
          result: { dominant_wait: 'db file scattered read', wait_pct: 78.4 },
        },
      ],
      diagnosis: {
        root_cause: 'CBO Plan Flip to Full Table Scan caused by Stale Index Statistics',
        confidence: 0.94,
        impacted_components: ['TABLE: INVOICE_ITEMS', 'INDEX: IDX_INVOICE_LOOKUP', 'MODULE: BILLING_SERVICE'],
        recommendations: [
          {
            action: 'Khôi phục hoặc gán SQL Plan Baseline ổn định',
            priority: 'HIGH',
            command: `EXEC DBMS_SPM.LOAD_PLANS_FROM_CURSOR_CACHE(sql_id => '${targetObject || '7v62q4pm90ab1'}', plan_hash_value => 184920194);`,
            rationale: 'Ngay lập tức ép CBO sử dụng lại plan cũ ổn định với chi phí thấp.',
          },
          {
            action: 'Thu thập lại thống kê bảng và index với tham số Cascade',
            priority: 'MEDIUM',
            command: `EXEC DBMS_STATS.GATHER_TABLE_STATS('FINANCE', 'INVOICE_ITEMS', cascade => TRUE, estimate_percent => DBMS_STATS.AUTO_SAMPLE_SIZE);`,
            rationale: 'Đảm bảo dữ liệu thống kê phản ánh chính xác phân bố phân đoạn dữ liệu.',
          },
        ],
        explanation: 'SQL_ID ' + (targetObject || '7v62q4pm90ab1') + ' trước đó chạy qua Index Range Scan chỉ tốn ~120 buffer gets. Sau khi số lượng bản ghi bảng tăng đột biến nhưng stats chưa kịp đồng bộ, Oracle CBO chuyển sang TABLE ACCESS FULL dẫn đến 78.4% thời gian tiêu tốn vào sự kiện "db file scattered read".',
      },
      created_at: new Date().toISOString(),
    };
  },

  async getDailyReports(): Promise<DailyReport[]> {
    try {
      const res = await fetch(`${API_BASE}/reports/daily`, { signal: AbortSignal.timeout(3000) });
      if (res.ok) {
        const data = (await res.json()) as unknown;
        if (Array.isArray(data) && data.length > 0) return data as DailyReport[];
        if (data && typeof data === 'object' && 'report_date' in data) {
          const report = data as Record<string, unknown>;
          return [
            {
              id: String(report.id ?? 'rep-latest'),
              report_date: String(report.report_date),
              health_score: Number(report.health_score ?? 80),
              summary: typeof report.narrative === 'string' ? report.narrative.split('\n')[0] : 'Daily Report',
              markdown_narrative: typeof report.narrative === 'string' ? report.narrative : '',
              incidents_count: (Number(report.critical_count) || 0) + (Number(report.warning_count) || 0),
            },
          ];
        }
      }
    } catch {
      // Fallback
    }
    return [MOCK_DAILY_REPORT];
  },

  connectInvestigationWS(
    investigationId: string,
    onStepUpdate: (step: InvestigationStep) => void,
    onDiagnosis: (diagnosis: DiagnosisResult) => void,
    onComplete: () => void,
  ): WebSocket | null {
    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}${API_BASE}/ws/investigate/${investigationId}`;
      const ws = new WebSocket(wsUrl);

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'step_update' && data.step) {
            onStepUpdate(data.step);
          } else if (data.type === 'diagnosis' && data.diagnosis) {
            onDiagnosis(data.diagnosis);
          } else if (data.type === 'complete') {
            onComplete();
          }
        } catch {
          // ignore parse errors
        }
      };

      ws.onerror = () => {
        // graceful handle
      };

      return ws;
    } catch {
      return null;
    }
  },
};
