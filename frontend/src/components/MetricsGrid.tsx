import React from 'react';
import { Users, Lock, Cpu, HardDrive, AlertCircle } from 'lucide-react';
import type { SystemMetrics } from '../types';

interface MetricsGridProps {
  metrics: SystemMetrics;
}

export const MetricsGrid: React.FC<MetricsGridProps> = ({ metrics }) => {
  const cards = [
    {
      title: 'Active Sessions',
      value: metrics.active_sessions,
      subtext: 'Đang xử lý trong DB',
      icon: Users,
      color: 'text-indigo-400',
      bgGlow: 'from-indigo-600/10 to-indigo-900/5',
      badge: 'Bình thường',
      badgeColor: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20',
    },
    {
      title: 'Blocking Sessions',
      value: metrics.blocking_sessions,
      subtext: metrics.blocking_sessions > 0 ? 'TX / TM lock contention' : 'Không có tranh chấp khóa',
      icon: Lock,
      color: metrics.blocking_sessions > 0 ? 'text-rose-400' : 'text-emerald-400',
      bgGlow: metrics.blocking_sessions > 0 ? 'from-rose-600/15 to-rose-950/10' : 'from-emerald-600/10 to-emerald-950/5',
      badge: metrics.blocking_sessions > 0 ? 'Cần xử lý' : 'An toàn',
      badgeColor: metrics.blocking_sessions > 0 ? 'bg-rose-500/15 text-rose-400 border-rose-500/30' : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
      animate: metrics.blocking_sessions > 0,
    },
    {
      title: 'CPU Utilization',
      value: `${metrics.cpu_utilization.toFixed(1)}%`,
      subtext: 'Instance CPU load',
      icon: Cpu,
      color: metrics.cpu_utilization > 80 ? 'text-amber-400' : 'text-cyan-400',
      bgGlow: 'from-cyan-600/10 to-cyan-950/5',
      badge: metrics.cpu_utilization > 80 ? 'Tải cao' : 'Ổn định',
      badgeColor: metrics.cpu_utilization > 80 ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' : 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20',
    },
    {
      title: 'Tablespace Đầy Nhất',
      value: `${metrics.tablespace_utilization.toFixed(1)}%`,
      subtext: 'USERS (Ngưỡng: 85%)',
      icon: HardDrive,
      color: metrics.tablespace_utilization > 85 ? 'text-rose-400' : 'text-violet-400',
      bgGlow: metrics.tablespace_utilization > 85 ? 'from-rose-600/10 to-rose-950/5' : 'from-violet-600/10 to-violet-950/5',
      badge: metrics.tablespace_utilization > 85 ? 'Cảnh báo 85%' : 'Khả dụng',
      badgeColor: metrics.tablespace_utilization > 85 ? 'bg-rose-500/15 text-rose-400 border-rose-500/30' : 'bg-violet-500/10 text-violet-400 border-violet-500/20',
    },
    {
      title: 'Invalid Objects',
      value: metrics.invalid_objects_count,
      subtext: 'Packages / Triggers cần recompile',
      icon: AlertCircle,
      color: metrics.invalid_objects_count > 0 ? 'text-amber-400' : 'text-slate-400',
      bgGlow: 'from-slate-700/10 to-slate-900/5',
      badge: metrics.invalid_objects_count > 0 ? '1 Object' : '0 Object',
      badgeColor: metrics.invalid_objects_count > 0 ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' : 'bg-slate-700/20 text-slate-400 border-slate-700/40',
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3.5">
      {cards.map((card, idx) => {
        const Icon = card.icon;
        return (
          <div
            key={idx}
            className={`glass-card rounded-2xl p-4 relative overflow-hidden bg-gradient-to-br ${card.bgGlow} flex flex-col justify-between`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-slate-400">{card.title}</span>
              <div className={`p-1.5 rounded-lg bg-slate-900/60 border border-slate-800 ${card.color}`}>
                <Icon className={`w-4 h-4 ${card.animate ? 'animate-bounce' : ''}`} />
              </div>
            </div>

            <div className="my-1">
              <div className="text-2xl font-black font-mono tracking-tight text-white flex items-baseline gap-1.5">
                {card.value}
              </div>
              <p className="text-[11px] text-slate-400 truncate mt-0.5">{card.subtext}</p>
            </div>

            <div className="mt-2 pt-2 border-t border-slate-800/60 flex items-center justify-between">
              <span className={`px-2 py-0.5 text-[10px] font-semibold rounded-full border ${card.badgeColor}`}>
                {card.badge}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
};
