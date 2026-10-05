import React, { useState } from 'react';
import { GitBranch, AlertTriangle, CheckCircle, Search, Layers, Zap } from 'lucide-react';

interface PlanNode {
  id: number;
  operation: string;
  options?: string;
  objectName?: string;
  cost: number;
  cardinality: number;
  bytes: string;
  cpuCost?: string;
  isExpensive?: boolean;
  warning?: string;
  children?: PlanNode[];
}

export const ExecutionPlanViewer: React.FC = () => {
  const [selectedSqlId, setSelectedSqlId] = useState('7v62q4pm90ab1');

  // Sample Execution Plan for SQL 7v62q4pm90ab1
  const planData: PlanNode = {
    id: 0,
    operation: 'SELECT STATEMENT',
    options: 'ALL_ROWS',
    cost: 9410,
    cardinality: 15400,
    bytes: '3.2 MB',
    children: [
      {
        id: 1,
        operation: 'HASH JOIN',
        options: '',
        cost: 9408,
        cardinality: 15400,
        bytes: '3.2 MB',
        children: [
          {
            id: 2,
            operation: 'TABLE ACCESS',
            options: 'FULL',
            objectName: 'INVOICE_ITEMS',
            cost: 8950,
            cardinality: 1250000,
            bytes: '84 MB',
            isExpensive: true,
            warning: 'Full Table Scan! Chiếm 95.1% tổng cost của câu lệnh.',
          },
          {
            id: 3,
            operation: 'TABLE ACCESS',
            options: 'BY INDEX ROWID BATCHED',
            objectName: 'INVOICES',
            cost: 450,
            cardinality: 15400,
            bytes: '1.1 MB',
            children: [
              {
                id: 4,
                operation: 'INDEX',
                options: 'RANGE SCAN',
                objectName: 'IDX_INVOICE_STATUS',
                cost: 12,
                cardinality: 15400,
                bytes: '128 KB',
              },
            ],
          },
        ],
      },
    ],
  };

  const renderNode = (node: PlanNode, level = 0) => {
    const isFTS = node.options === 'FULL' || node.isExpensive;
    const isIndex = node.operation.includes('INDEX');

    return (
      <div key={node.id} className="space-y-2">
        <div
          className={`p-3.5 rounded-xl border transition-all flex flex-col md:flex-row md:items-center justify-between gap-3 ${
            isFTS
              ? 'bg-rose-950/20 border-rose-500/40 hover:border-rose-500/60 shadow-sm shadow-rose-900/10'
              : isIndex
              ? 'bg-emerald-950/20 border-emerald-500/30 hover:border-emerald-500/50'
              : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
          }`}
          style={{ marginLeft: `${level * 24}px` }}
        >
          <div className="flex items-start gap-3">
            <div className="mt-0.5">
              {isFTS ? (
                <div className="p-1 rounded bg-rose-500/20 text-rose-400">
                  <AlertTriangle className="w-4 h-4" />
                </div>
              ) : isIndex ? (
                <div className="p-1 rounded bg-emerald-500/20 text-emerald-400">
                  <Zap className="w-4 h-4" />
                </div>
              ) : (
                <div className="p-1 rounded bg-slate-800 text-slate-400">
                  <Layers className="w-4 h-4" />
                </div>
              )}
            </div>

            <div>
              <div className="flex items-center flex-wrap gap-2">
                <span className="text-xs font-mono font-bold text-slate-100">
                  ID #{node.id}: {node.operation} {node.options && `(${node.options})`}
                </span>
                {node.objectName && (
                  <span className="px-2 py-0.5 text-[11px] font-mono font-bold rounded bg-indigo-950/60 text-indigo-300 border border-indigo-800/60">
                    {node.objectName}
                  </span>
                )}
                {isFTS && (
                  <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-rose-500/20 text-rose-300 border border-rose-500/40 animate-pulse">
                    FULL TABLE SCAN
                  </span>
                )}
              </div>

              {node.warning && (
                <p className="text-xs text-rose-400 mt-1 font-medium">{node.warning}</p>
              )}
            </div>
          </div>

          {/* Metrics per node */}
          <div className="flex items-center gap-4 text-xs font-mono shrink-0">
            <div>
              <span className="text-slate-500 block text-[10px]">Cost</span>
              <span className={node.cost > 5000 ? 'text-rose-400 font-bold' : 'text-slate-300'}>
                {node.cost.toLocaleString()}
              </span>
            </div>
            <div>
              <span className="text-slate-500 block text-[10px]">Rows (Card)</span>
              <span className="text-slate-300">{node.cardinality.toLocaleString()}</span>
            </div>
            <div>
              <span className="text-slate-500 block text-[10px]">Volume</span>
              <span className="text-slate-300">{node.bytes}</span>
            </div>
          </div>
        </div>

        {node.children?.map((child) => renderNode(child, level + 1))}
      </div>
    );
  };

  return (
    <div className="glass-card rounded-2xl p-6 space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <GitBranch className="w-5 h-5 text-indigo-400" />
            <h2 className="text-base font-bold text-slate-100 font-sans m-0">
              Trực Quan Hóa Execution Plan (Oracle CBO Tree)
            </h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Hiển thị cây chi phí và cảnh báo các thao tác quét toàn bộ bảng (*Full Table Scan*)
          </p>
        </div>

        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={selectedSqlId}
              onChange={(e) => setSelectedSqlId(e.target.value)}
              placeholder="Nhập SQL_ID..."
              className="bg-slate-900 border border-slate-700 rounded-xl pl-8 pr-3 py-1.5 text-xs text-slate-200 font-mono focus:outline-none focus:border-indigo-500 w-44"
            />
          </div>
          <button className="px-3 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-sm transition-all cursor-pointer">
            Tải Plan
          </button>
        </div>
      </div>

      {/* Plan summary badge */}
      <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between flex-wrap gap-4 text-xs font-mono">
        <div>
          <span className="text-slate-500">SQL_ID: </span>
          <span className="text-indigo-400 font-bold">{selectedSqlId}</span>
        </div>
        <div>
          <span className="text-slate-500">Plan Hash Value: </span>
          <span className="text-slate-200">394827110</span>
        </div>
        <div>
          <span className="text-slate-500">Tổng Cost: </span>
          <span className="text-rose-400 font-bold">9,410</span>
        </div>
        <div>
          <span className="text-slate-500">Optimizer Mode: </span>
          <span className="text-emerald-400 font-semibold">ALL_ROWS</span>
        </div>
      </div>

      {/* Plan Hierarchy */}
      <div className="space-y-3 pt-2">
        {renderNode(planData)}
      </div>

      {/* Recommendations Box */}
      <div className="rounded-xl border border-indigo-900/40 bg-indigo-950/20 p-4 flex items-start gap-3">
        <CheckCircle className="w-5 h-5 text-indigo-400 shrink-0 mt-0.5" />
        <div className="text-xs text-slate-300 space-y-1">
          <span className="font-semibold text-white block">Đánh giá tối ưu của Copilot:</span>
          <p className="m-0 leading-relaxed">
            Thao tác <code className="text-rose-400 bg-rose-950/50 px-1 py-0.5 rounded">TABLE ACCESS FULL</code> trên bảng <code className="text-indigo-300 font-bold">INVOICE_ITEMS</code> đang chiếm hơn 95% chi phí của cây thực thi. Cần tạo Index ghép trên cặp khóa <code className="text-emerald-400 font-bold">(INVOICE_ID, CREATED_DATE)</code> để đưa câu lệnh về <code className="text-emerald-400">INDEX RANGE SCAN</code> (giảm Cost dự kiến từ 9,410 xuống dưới 80).
          </p>
        </div>
      </div>
    </div>
  );
};
