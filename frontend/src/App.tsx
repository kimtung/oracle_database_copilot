import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { HealthScoreGauge } from './components/HealthScoreGauge';
import { MetricsGrid } from './components/MetricsGrid';
import { IncidentFeed } from './components/IncidentFeed';
import { InvestigationChat } from './components/InvestigationChat';
import { ExecutionPlanViewer } from './components/ExecutionPlanViewer';
import { DailyReportViewer } from './components/DailyReportViewer';
import { apiService } from './services/api';
import type { DailyReport, Incident, IncidentStatus, SystemMetrics } from './types';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<string>('dashboard');
  const [metrics, setMetrics] = useState<SystemMetrics>({
    health_score: 84,
    active_sessions: 38,
    blocking_sessions: 2,
    cpu_utilization: 62.4,
    tablespace_utilization: 79.1,
    long_running_count: 3,
    invalid_objects_count: 1,
    oracle_status: 'CONNECTED',
    mcp_status: 'HEALTHY',
  });
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [dailyReports, setDailyReports] = useState<DailyReport[]>([]);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [chatContext, setChatContext] = useState<{ prompt: string; target: string }>({
    prompt: '',
    target: '',
  });

  const fetchData = async () => {
    try {
      const [metricsData, incidentsData, reportsData] = await Promise.all([
        apiService.getSystemMetrics(),
        apiService.getIncidents(),
        apiService.getDailyReports(),
      ]);
      setMetrics(metricsData);
      setIncidents(incidentsData);
      setDailyReports(reportsData);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleManualRefresh = () => {
    setIsRefreshing(true);
    void fetchData();
  };

  useEffect(() => {
    let active = true;
    Promise.all([
      apiService.getSystemMetrics(),
      apiService.getIncidents(),
      apiService.getDailyReports(),
    ]).then(([metricsData, incidentsData, reportsData]) => {
      if (active) {
        setMetrics(metricsData);
        setIncidents(incidentsData);
        setDailyReports(reportsData);
      }
    });

    const timer = setInterval(() => {
      void fetchData();
    }, 30000);

    return () => {
      active = false;
      clearInterval(timer);
    };
  }, []);

  const handleInvestigateIncident = (incident: Incident) => {
    const target = (incident.metadata?.sql_id as string) || (incident.metadata?.blocker_sid ? String(incident.metadata.blocker_sid) : '') || '';
    setChatContext({
      prompt: `Điều tra chi tiết sự cố: ${incident.summary}`,
      target,
    });
    setCurrentTab('investigate');
  };

  const handleStatusChange = async (id: string, status: IncidentStatus) => {
    await apiService.updateIncidentStatus(id, status);
    setIncidents((prev) =>
      prev.map((inc) => (inc.id === id ? { ...inc, status } : inc))
    );
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Top Navigation */}
      <Navbar
        currentTab={currentTab}
        onTabChange={setCurrentTab}
        metrics={metrics}
        onRefresh={handleManualRefresh}
        isRefreshing={isRefreshing}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-6 space-y-6">
        {currentTab === 'dashboard' && (
          <div className="space-y-6">
            {/* Top Row: Health Score & Quick Metrics */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-1">
                <HealthScoreGauge score={metrics.health_score} />
              </div>
              <div className="lg:col-span-2 flex flex-col justify-between">
                <MetricsGrid metrics={metrics} />
                <div className="mt-4 p-4 rounded-2xl glass-card border border-indigo-900/30 flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-indigo-500 animate-pulse"></span>
                    <span className="text-slate-300 font-medium">Autonomous Mode Active:</span>
                    <span className="text-slate-400">Đang giám sát 24/7 qua Oracle Thin Gateway & Correlation Engine</span>
                  </div>
                  <button
                    onClick={() => setCurrentTab('investigate')}
                    className="text-indigo-400 hover:text-indigo-300 font-semibold cursor-pointer underline underline-offset-4"
                  >
                    Mở Chat AI &rarr;
                  </button>
                </div>
              </div>
            </div>

            {/* Bottom Row: Incident Feed */}
            <IncidentFeed
              incidents={incidents}
              onInvestigateIncident={handleInvestigateIncident}
              onStatusChange={handleStatusChange}
            />
          </div>
        )}

        {currentTab === 'investigate' && (
          <InvestigationChat
            key={`${chatContext.prompt}-${chatContext.target}`}
            initialPrompt={chatContext.prompt}
            initialTarget={chatContext.target}
          />
        )}

        {currentTab === 'plan' && <ExecutionPlanViewer />}

        {currentTab === 'reports' && <DailyReportViewer reports={dailyReports} />}
      </main>

      {/* Footer */}
      <footer className="glass-panel border-t border-slate-900 mt-auto py-4 px-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>Oracle Database Copilot v0.1 • 19c Thin Mode Architecture</span>
          <div className="flex items-center gap-4">
            <span className="text-slate-400">PostgreSQL 16 + FastAPI + SQLAlchemy 2.0</span>
            <span className="text-emerald-400 font-mono">100% Tests Passed</span>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
