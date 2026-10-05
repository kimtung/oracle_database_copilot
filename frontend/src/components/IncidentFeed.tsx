import React, { useState } from 'react';
import { Clock, Search, Filter, Bot, Check, ArrowRight, ShieldAlert } from 'lucide-react';
import type { Incident, IncidentStatus, Severity } from '../types';

interface IncidentFeedProps {
  incidents: Incident[];
  onInvestigateIncident: (incident: Incident) => void;
  onStatusChange: (id: string, status: IncidentStatus) => void;
}

export const IncidentFeed: React.FC<IncidentFeedProps> = ({
  incidents,
  onInvestigateIncident,
  onStatusChange,
}) => {
  const [filterSeverity, setFilterSeverity] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const severityBadge = (sev: Severity) => {
    switch (sev) {
      case 'CRITICAL':
        return 'bg-rose-500/15 text-rose-400 border-rose-500/30';
      case 'HIGH':
        return 'bg-orange-500/15 text-orange-400 border-orange-500/30';
      case 'MEDIUM':
        return 'bg-amber-500/15 text-amber-400 border-amber-500/30';
      case 'LOW':
        return 'bg-slate-500/15 text-slate-400 border-slate-500/30';
    }
  };

  const statusBadge = (status: IncidentStatus) => {
    switch (status) {
      case 'OPEN':
        return 'bg-red-500/20 text-red-300';
      case 'INVESTIGATING':
        return 'bg-indigo-500/20 text-indigo-300 animate-pulse';
      case 'ACKNOWLEDGED':
        return 'bg-amber-500/20 text-amber-300';
      case 'RESOLVED':
        return 'bg-emerald-500/20 text-emerald-300';
    }
  };

  const filtered = incidents.filter((inc) => {
    if (filterSeverity !== 'ALL' && inc.severity !== filterSeverity) return false;
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const matchSummary = inc.summary.toLowerCase().includes(q);
      const matchRule = inc.rule_name.toLowerCase().includes(q);
      const matchHypo = inc.root_cause_hypothesis?.toLowerCase().includes(q) ?? false;
      return matchSummary || matchRule || matchHypo;
    }
    return true;
  });

  return (
    <div className="glass-card rounded-2xl p-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-5">
        <div>
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-indigo-400" />
            <h2 className="text-base font-bold text-slate-100 font-sans m-0">
              Danh Sách Sự Cố Phát Hiện (Incident Feed)
            </h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Tự động tương quan qua 6 Deterministic Rules & Evidence Graph
          </p>
        </div>

        {/* Filters & Search */}
        <div className="flex items-center flex-wrap gap-2.5">
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Tìm theo SQL_ID, SID, Rule..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-slate-900/90 border border-slate-800 rounded-xl pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-indigo-500 w-48 sm:w-56"
            />
          </div>

          <div className="flex items-center gap-1 bg-slate-900/90 border border-slate-800 rounded-xl p-1">
            <Filter className="w-3.5 h-3.5 text-slate-500 ml-1.5 mr-0.5" />
            {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM'].map((sev) => (
              <button
                key={sev}
                onClick={() => setFilterSeverity(sev)}
                className={`px-2.5 py-1 text-[11px] font-medium rounded-lg transition-all ${
                  filterSeverity === sev
                    ? 'bg-indigo-600 text-white shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                }`}
              >
                {sev === 'ALL' ? 'Tất cả' : sev}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Incident List */}
      <div className="space-y-3">
        {filtered.length === 0 ? (
          <div className="text-center py-10 text-slate-500 text-xs">
            Không tìm thấy sự cố nào phù hợp với bộ lọc.
          </div>
        ) : (
          filtered.map((inc) => (
            <div
              key={inc.id}
              className="rounded-xl border border-slate-800/80 bg-slate-900/40 hover:bg-slate-800/40 p-4 transition-all flex flex-col md:flex-row md:items-center justify-between gap-4"
            >
              <div className="space-y-1.5 max-w-3xl">
                <div className="flex items-center flex-wrap gap-2">
                  <span className={`px-2 py-0.5 text-[10px] font-bold rounded-md border ${severityBadge(inc.severity)}`}>
                    {inc.severity}
                  </span>
                  <span className={`px-2 py-0.5 text-[10px] font-medium rounded-md ${statusBadge(inc.status)}`}>
                    {inc.status}
                  </span>
                  <span className="text-xs font-mono font-semibold text-slate-300">
                    {inc.rule_name}
                  </span>
                  <span className="text-[11px] text-slate-500 flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {new Date(inc.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>

                <div className="text-sm font-semibold text-slate-100">{inc.summary}</div>
                {inc.description && (
                  <p className="text-xs text-slate-400 line-clamp-2">{inc.description}</p>
                )}

                {inc.root_cause_hypothesis && (
                  <div className="flex items-center gap-2 pt-1 text-xs">
                    <span className="text-slate-400">Giả thuyết gốc:</span>
                    <span className="font-mono text-indigo-400 font-medium bg-indigo-950/40 px-2 py-0.5 rounded border border-indigo-900/50">
                      {inc.root_cause_hypothesis}
                    </span>
                    {inc.confidence_score && (
                      <span className="text-[11px] text-emerald-400 font-semibold font-mono">
                        {(inc.confidence_score * 100).toFixed(0)}% confidence
                      </span>
                    )}
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="flex items-center gap-2 self-end md:self-center shrink-0">
                {inc.status !== 'RESOLVED' && (
                  <button
                    onClick={() => onStatusChange(inc.id, 'RESOLVED')}
                    className="p-1.5 rounded-lg text-slate-400 hover:text-emerald-400 hover:bg-emerald-500/10 border border-transparent hover:border-emerald-500/30 transition-all text-xs flex items-center gap-1 cursor-pointer"
                    title="Đánh dấu đã giải quyết"
                  >
                    <Check className="w-4 h-4" />
                    <span className="text-[11px]">Đóng</span>
                  </button>
                )}

                <button
                  onClick={() => onInvestigateIncident(inc)}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/30 hover:shadow-indigo-600/50 transition-all cursor-pointer"
                >
                  <Bot className="w-4 h-4" />
                  <span>Điều Tra AI</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
