import React from 'react';
import { HeartPulse, CheckCircle2, AlertTriangle, AlertOctagon, TrendingUp } from 'lucide-react';

interface HealthScoreGaugeProps {
  score: number;
}

export const HealthScoreGauge: React.FC<HealthScoreGaugeProps> = ({ score }) => {
  // SVG circular gauge geometry
  const radius = 68;
  const stroke = 12;
  const normalizedRadius = radius - stroke * 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  let statusText = 'Tối ưu (Optimal)';
  let statusColor = 'text-emerald-400';
  let strokeColor = '#10b981'; // emerald
  let StatusIcon = CheckCircle2;

  if (score < 60) {
    statusText = 'Nghiêm trọng (Critical)';
    statusColor = 'text-rose-500';
    strokeColor = '#f43f5e';
    StatusIcon = AlertOctagon;
  } else if (score < 80) {
    statusText = 'Cần chú ý (Warning)';
    statusColor = 'text-amber-400';
    strokeColor = '#f59e0b';
    StatusIcon = AlertTriangle;
  }

  return (
    <div className="glass-card rounded-2xl p-6 relative overflow-hidden flex flex-col justify-between">
      {/* Subtle Background Glow */}
      <div
        className="absolute -top-12 -right-12 w-48 h-48 rounded-full blur-3xl opacity-20 pointer-events-none"
        style={{ backgroundColor: strokeColor }}
      />

      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <HeartPulse className="w-5 h-5 text-indigo-400" />
          <h2 className="text-sm font-semibold text-slate-200 uppercase tracking-wider font-sans m-0">
            Điểm Sức Khỏe Cơ Sở Dữ Liệu
          </h2>
        </div>
        <span className="text-[11px] text-slate-400 bg-slate-800/80 px-2 py-0.5 rounded-full border border-slate-700/60 font-mono">
          0 – 100 INDEX
        </span>
      </div>

      <div className="flex flex-col sm:flex-row items-center justify-around gap-6 my-2">
        {/* SVG Circular Gauge */}
        <div className="relative flex items-center justify-center">
          <svg height={radius * 2} width={radius * 2} className="rotate-[-90deg]">
            <circle
              stroke="rgba(255, 255, 255, 0.08)"
              fill="transparent"
              strokeWidth={stroke}
              r={normalizedRadius}
              cx={radius}
              cy={radius}
            />
            <circle
              stroke={strokeColor}
              fill="transparent"
              strokeWidth={stroke}
              strokeDasharray={`${circumference} ${circumference}`}
              style={{ strokeDashoffset, transition: 'stroke-dashoffset 0.8s ease-in-out' }}
              strokeLinecap="round"
              r={normalizedRadius}
              cx={radius}
              cy={radius}
            />
          </svg>

          {/* Centered score number */}
          <div className="absolute flex flex-col items-center justify-center">
            <span className="text-4xl font-black tracking-tight text-white font-mono">
              {score}
            </span>
            <span className="text-[11px] font-medium text-slate-400">/ 100</span>
          </div>
        </div>

        {/* Status description & sub-indices */}
        <div className="flex flex-col gap-3 min-w-[200px]">
          <div className="flex items-center gap-2">
            <StatusIcon className={`w-5 h-5 ${statusColor}`} />
            <div>
              <div className={`text-base font-bold ${statusColor}`}>{statusText}</div>
              <div className="text-xs text-slate-400">Đánh giá theo chuẩn Oracle CBO & AWR</div>
            </div>
          </div>

          <div className="space-y-1.5 pt-2 border-t border-slate-800/80 text-xs">
            <div className="flex items-center justify-between text-slate-400">
              <span>SQL Latency Index:</span>
              <span className="font-mono text-emerald-400 font-semibold">92%</span>
            </div>
            <div className="flex items-center justify-between text-slate-400">
              <span>Concurrency & Locks:</span>
              <span className="font-mono text-amber-400 font-semibold">74%</span>
            </div>
            <div className="flex items-center justify-between text-slate-400">
              <span>Storage & Undo Headroom:</span>
              <span className="font-mono text-emerald-400 font-semibold">86%</span>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
        <span className="flex items-center gap-1">
          <TrendingUp className="w-3.5 h-3.5 text-indigo-400" />
          <span>Baseline μ±2σ được hiệu chuẩn 1 giờ/lần</span>
        </span>
        <span className="font-mono text-[11px] text-slate-400">P95: 18.2ms</span>
      </div>
    </div>
  );
};
