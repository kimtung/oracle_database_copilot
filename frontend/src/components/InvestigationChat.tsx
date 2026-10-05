import React, { useState } from 'react';
import { Send, Bot, Sparkles, CheckCircle2, Copy, Check, ChevronRight, Terminal, Cpu } from 'lucide-react';
import type { InvestigationSession, InvestigationStep } from '../types';
import { apiService } from '../services/api';

interface InvestigationChatProps {
  initialPrompt?: string;
  initialTarget?: string;
}

export const InvestigationChat: React.FC<InvestigationChatProps> = ({
  initialPrompt,
  initialTarget,
}) => {
  const [prompt, setPrompt] = useState(initialPrompt || '');
  const [targetObject, setTargetObject] = useState(initialTarget || '');
  const [isLoading, setIsLoading] = useState(false);
  const [currentSession, setCurrentSession] = useState<InvestigationSession | null>(null);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const quickPrompts = [
    { label: 'Phân tích chậm SQL 7v62q4pm90ab1', prompt: 'Điều tra nguyên nhân SQL_ID 7v62q4pm90ab1 tăng thời gian thực thi bất thường', target: '7v62q4pm90ab1' },
    { label: 'Điều tra khóa tranh chấp SID 142', prompt: 'Tìm hiểu tại sao session SID 142 đang giữ exclusive lock gây tắc nghẽn', target: '142' },
    { label: 'Kiểm tra cảnh báo Tablespace USERS', prompt: 'Dự báo nguy cơ đầy dung lượng và segment tăng trưởng nhanh trên USERS', target: 'USERS' },
    { label: 'Chẩn đoán Job PURGE_AUDIT_LOG thất bại', prompt: 'Tìm nguyên nhân lỗi ORA-01555 của job PURGE_AUDIT_LOG_JOB', target: 'PURGE_AUDIT_LOG_JOB' },
  ];

  const handleStartInvestigation = async (userPrompt?: string, target?: string) => {
    const activePrompt = userPrompt || prompt;
    if (!activePrompt.trim() || isLoading) return;

    setIsLoading(true);
    const session = await apiService.startInvestigation(activePrompt, target || targetObject);
    setCurrentSession(session);
    setIsLoading(false);
  };

  const copyToClipboard = (text: string, index: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  return (
    <div className="space-y-6">
      {/* Header and prompt input bar */}
      <div className="glass-card rounded-2xl p-6 relative overflow-hidden">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-600 text-white shadow-lg shadow-indigo-600/30">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white font-sans m-0 flex items-center gap-2">
              Autonomous Investigation Copilot
              <span className="px-2 py-0.5 text-[11px] font-semibold bg-indigo-500/20 text-indigo-300 rounded-full border border-indigo-500/30">
                Multi-LLM Engine
              </span>
            </h2>
            <p className="text-xs text-slate-400">
              Nhập ngôn ngữ tự nhiên hoặc chọn sự cố, Copilot sẽ tự động lập kế hoạch gọi 32 Oracle MCP Tools
            </p>
          </div>
        </div>

        {/* Input form */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleStartInvestigation();
          }}
          className="mt-4"
        >
          <div className="flex flex-col sm:flex-row gap-2">
            <div className="relative flex-1">
              <Terminal className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Ví dụ: Phân tích hiệu năng câu lệnh SQL 7v62q4pm90ab1 và đề xuất tối ưu..."
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                className="w-full bg-slate-900/90 border border-slate-700/80 rounded-xl pl-10 pr-4 py-3 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all font-sans"
              />
            </div>

            <div className="w-full sm:w-48">
              <input
                type="text"
                placeholder="Target (SQL_ID/SID)"
                value={targetObject}
                onChange={(e) => setTargetObject(e.target.value)}
                className="w-full bg-slate-900/90 border border-slate-700/80 rounded-xl px-3 py-3 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-indigo-500 font-mono"
              />
            </div>

            <button
              type="submit"
              disabled={isLoading || !prompt.trim()}
              className="px-5 py-3 rounded-xl bg-gradient-to-r from-indigo-600 via-indigo-500 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white text-sm font-semibold shadow-lg shadow-indigo-600/30 hover:shadow-indigo-600/50 transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed shrink-0"
            >
              {isLoading ? (
                <>
                  <Sparkles className="w-4 h-4 animate-spin text-white" />
                  <span>Đang Phân Tích...</span>
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  <span>Bắt Đầu Điều Tra</span>
                </>
              )}
            </button>
          </div>
        </form>

        {/* Quick prompt suggestions */}
        <div className="mt-3.5 flex items-center flex-wrap gap-2 text-xs">
          <span className="text-slate-400 font-medium text-[11px]">Gợi ý nhanh:</span>
          {quickPrompts.map((qp, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => {
                setPrompt(qp.prompt);
                setTargetObject(qp.target);
                handleStartInvestigation(qp.prompt, qp.target);
              }}
              className="px-2.5 py-1 rounded-lg bg-slate-900/70 hover:bg-indigo-950/40 border border-slate-800 hover:border-indigo-700/50 text-slate-300 hover:text-indigo-300 transition-all text-[11px] cursor-pointer"
            >
              {qp.label}
            </button>
          ))}
        </div>
      </div>

      {/* Investigation Progress & Results */}
      {currentSession && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left 1/3: Multi-step MCP execution timeline */}
          <div className="glass-card rounded-2xl p-5">
            <div className="flex items-center justify-between mb-4 pb-2 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <Cpu className="w-4 h-4 text-indigo-400" />
                <h3 className="text-sm font-bold text-slate-200 font-sans m-0">
                  Lộ Trình Thu Thập MCP
                </h3>
              </div>
              <span className="text-[11px] font-mono bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded-full border border-emerald-500/20">
                {currentSession.status}
              </span>
            </div>

            <div className="space-y-3">
              {currentSession.steps.map((step: InvestigationStep, idx: number) => (
                <div
                  key={step.step_id || idx}
                  className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/80 space-y-1.5"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-mono font-bold text-indigo-300 flex items-center gap-1.5">
                      <ChevronRight className="w-3.5 h-3.5 text-indigo-400" />
                      {step.tool_name}
                    </span>
                    <span className="flex items-center gap-1 text-[10px] text-emerald-400 bg-emerald-950/40 px-1.5 py-0.5 rounded font-mono">
                      <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                      {step.duration_ms ? `${step.duration_ms}ms` : 'Xong'}
                    </span>
                  </div>

                  <p className="text-[11px] text-slate-400">{step.description}</p>

                  {step.result != null ? (
                    <div className="bg-slate-950/80 rounded-lg p-2 text-[10px] font-mono text-slate-300 overflow-x-auto border border-slate-800/50">
                      <pre className="m-0">{JSON.stringify(step.result, null, 2)}</pre>
                    </div>
                  ) : null}
                </div>
              ))}
            </div>
          </div>

          {/* Right 2/3: AI Diagnosis & Actionable Recommendations */}
          <div className="lg:col-span-2 space-y-6">
            {currentSession.diagnosis && (
              <>
                {/* Diagnosis Banner */}
                <div className="glass-card rounded-2xl p-6 border-l-4 border-indigo-500 bg-gradient-to-br from-indigo-950/30 to-slate-900/50">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <Sparkles className="w-4 h-4 text-indigo-400" />
                        <span className="text-xs font-bold text-indigo-400 uppercase tracking-wider">
                          Kết Luận Của AI Copilot (Root Cause Diagnosis)
                        </span>
                      </div>
                      <h4 className="text-lg font-bold text-white font-sans mt-1">
                        {currentSession.diagnosis.root_cause}
                      </h4>
                    </div>

                    <div className="shrink-0 flex flex-col items-end">
                      <span className="text-xs text-slate-400">Độ tin cậy</span>
                      <span className="text-xl font-black font-mono text-emerald-400">
                        {(currentSession.diagnosis.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>

                  <p className="text-sm text-slate-300 mt-3 leading-relaxed">
                    {currentSession.diagnosis.explanation}
                  </p>

                  {/* Impacted Components */}
                  {currentSession.diagnosis.impacted_components?.length > 0 && (
                    <div className="mt-4 pt-3 border-t border-slate-800 flex items-center flex-wrap gap-1.5">
                      <span className="text-xs text-slate-400 mr-1">Thực thể bị tác động:</span>
                      {currentSession.diagnosis.impacted_components.map((comp, i) => (
                        <span
                          key={i}
                          className="px-2 py-0.5 rounded-md bg-slate-800 text-[11px] font-mono text-slate-300 border border-slate-700"
                        >
                          {comp}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {/* Recommendations */}
                <div className="glass-card rounded-2xl p-6">
                  <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider mb-4 flex items-center gap-2 font-sans m-0">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    Khuyến Nghị Khắc Phục (Actionable SQL Remediations)
                  </h3>

                  <div className="space-y-4">
                    {currentSession.diagnosis.recommendations.map((rec, idx) => (
                      <div
                        key={idx}
                        className="rounded-xl border border-slate-800/80 bg-slate-900/50 p-4 space-y-2.5"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <span
                              className={`px-2 py-0.5 text-[10px] font-bold rounded-md border ${
                                rec.priority === 'CRITICAL' || rec.priority === 'HIGH'
                                  ? 'bg-rose-500/15 text-rose-400 border-rose-500/30'
                                  : 'bg-indigo-500/15 text-indigo-400 border-indigo-500/30'
                              }`}
                            >
                              {rec.priority}
                            </span>
                            <span className="text-sm font-semibold text-slate-100">
                              {rec.action}
                            </span>
                          </div>
                        </div>

                        {rec.rationale && (
                          <p className="text-xs text-slate-400">{rec.rationale}</p>
                        )}

                        {rec.command && (
                          <div className="relative group rounded-xl bg-slate-950 p-3 border border-slate-800">
                            <pre className="text-xs font-mono text-emerald-400 whitespace-pre-wrap break-all m-0">
                              {rec.command}
                            </pre>
                            <button
                              onClick={() => copyToClipboard(rec.command!, idx)}
                              className="absolute right-2 top-2 p-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-300 hover:text-white transition-all text-xs flex items-center gap-1 cursor-pointer"
                              title="Sao chép lệnh SQL"
                            >
                              {copiedIndex === idx ? (
                                <>
                                  <Check className="w-3.5 h-3.5 text-emerald-400" />
                                  <span className="text-[10px] text-emerald-400">Đã chép</span>
                                </>
                              ) : (
                                <>
                                  <Copy className="w-3.5 h-3.5" />
                                  <span className="text-[10px]">Copy SQL</span>
                                </>
                              )}
                            </button>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
