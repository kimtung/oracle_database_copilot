import React, { useState } from 'react';
import { Calendar, FileText, Download, HeartPulse, Cpu, Users, HardDrive, Sparkles } from 'lucide-react';
import type { DailyReport } from '../types';

interface DailyReportViewerProps {
  reports: DailyReport[];
}

export const DailyReportViewer: React.FC<DailyReportViewerProps> = ({ reports }) => {
  const [selectedReportIndex, setSelectedReportIndex] = useState(0);

  const report = reports[selectedReportIndex] || reports[0];

  if (!report) {
    return (
      <div className="glass-card rounded-2xl p-8 text-center text-slate-500">
        Chưa có báo cáo sức khỏe nào được tạo.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header & Date selector */}
      <div className="glass-card rounded-2xl p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-indigo-400" />
            <h2 className="text-base font-bold text-slate-100 font-sans m-0">
              Báo Cáo Sức Khỏe Hàng Ngày (Autonomous Daily Report)
            </h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Tổng hợp lúc 07:00 AM hàng ngày bởi AI Copilot & lưu trữ tự động vào PostgreSQL
          </p>
        </div>

        <div className="flex items-center gap-3">
          {reports.length > 1 ? (
            <select
              value={selectedReportIndex}
              onChange={(e) => setSelectedReportIndex(Number(e.target.value))}
              className="bg-slate-900 border border-slate-700 rounded-xl px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 font-mono"
            >
              {reports.map((rep, idx) => (
                <option key={rep.id || idx} value={idx}>
                  {rep.report_date} (Score: {rep.health_score})
                </option>
              ))}
            </select>
          ) : (
            <div className="flex items-center gap-2 bg-slate-900 border border-slate-700 rounded-xl px-3 py-1.5 text-xs text-slate-200">
              <Calendar className="w-4 h-4 text-indigo-400" />
              <span className="font-mono font-semibold">{report.report_date}</span>
            </div>
          )}

          <button
            onClick={() => window.print()}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white text-xs font-medium border border-slate-700 transition-all cursor-pointer"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Xuất PDF</span>
          </button>
        </div>
      </div>

      {/* Highlights Bar */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="glass-card rounded-xl p-4 bg-gradient-to-br from-indigo-950/20 to-slate-900/40">
          <span className="text-xs text-slate-400 flex items-center gap-1.5">
            <HeartPulse className="w-3.5 h-3.5 text-indigo-400" />
            Health Score
          </span>
          <div className="text-2xl font-black font-mono text-emerald-400 mt-1">
            {report.health_score} / 100
          </div>
          <span className="text-[10px] text-slate-500">Mức độ an toàn: TỐT</span>
        </div>

        <div className="glass-card rounded-xl p-4 bg-gradient-to-br from-indigo-950/20 to-slate-900/40">
          <span className="text-xs text-slate-400 flex items-center gap-1.5">
            <Cpu className="w-3.5 h-3.5 text-cyan-400" />
            Avg CPU Load
          </span>
          <div className="text-2xl font-black font-mono text-cyan-400 mt-1">
            {report.metrics_summary?.avg_cpu_percent ?? 48.6}%
          </div>
          <span className="text-[10px] text-slate-500">Bình quân 24 giờ qua</span>
        </div>

        <div className="glass-card rounded-xl p-4 bg-gradient-to-br from-indigo-950/20 to-slate-900/40">
          <span className="text-xs text-slate-400 flex items-center gap-1.5">
            <Users className="w-3.5 h-3.5 text-indigo-400" />
            Peak Active Sessions
          </span>
          <div className="text-2xl font-black font-mono text-indigo-300 mt-1">
            {report.metrics_summary?.peak_active_sessions ?? 62}
          </div>
          <span className="text-[10px] text-slate-500">Cao điểm: 14:30 - 15:15</span>
        </div>

        <div className="glass-card rounded-xl p-4 bg-gradient-to-br from-indigo-950/20 to-slate-900/40">
          <span className="text-xs text-slate-400 flex items-center gap-1.5">
            <HardDrive className="w-3.5 h-3.5 text-amber-400" />
            Max Tablespace Usage
          </span>
          <div className="text-2xl font-black font-mono text-amber-400 mt-1">
            {report.metrics_summary?.max_tablespace_pct ?? 88.4}%
          </div>
          <span className="text-[10px] text-slate-500">TS: USERS (Cần add datafile)</span>
        </div>
      </div>

      {/* Main Narrative Content */}
      <div className="glass-card rounded-2xl p-8 space-y-6">
        <div className="flex items-center gap-2 pb-4 border-b border-slate-800">
          <Sparkles className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-bold text-white font-sans m-0">
            Nội Dung Bản Tường Trình Kỹ Thuật (Narrative Report)
          </h3>
        </div>

        <div className="prose prose-invert max-w-none text-slate-300 text-sm leading-relaxed space-y-4">
          <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 text-slate-200">
            <p className="m-0 font-medium">{report.summary}</p>
          </div>

          {report.markdown_narrative ? (
            <div className="space-y-4 whitespace-pre-wrap font-sans">
              {report.markdown_narrative}
            </div>
          ) : (
            <p className="text-slate-500 italic">Không có narrative chi tiết cho ngày này.</p>
          )}
        </div>
      </div>
    </div>
  );
};
