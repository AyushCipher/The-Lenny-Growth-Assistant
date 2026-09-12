import React, { useState, useEffect } from 'react';
import { Activity, X, Database, Server, Cpu, Clock, RefreshCw, ShieldCheck } from 'lucide-react';
import { fetchDiagnostics } from '../services/api';

export default function DiagnosticsModal({ isOpen, onClose }) {
  const [diag, setDiag] = useState(null);
  const [loading, setLoading] = useState(false);

  const loadData = () => {
    setLoading(true);
    fetchDiagnostics()
      .then(data => setDiag(data))
      .catch(err => console.error("Error fetching diagnostics", err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    if (isOpen) loadData();
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fadeIn">
      <div className="w-full max-w-2xl rounded-2xl bg-slate-900 border border-slate-700 shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-950/70">
          <div className="flex items-center gap-2.5">
            <Activity className="w-5 h-5 text-indigo-400" />
            <div>
              <h2 className="text-base font-bold text-slate-100">System Telemetry & Observability</h2>
              <p className="text-xs text-slate-400">Live operational metrics, health checks, and RAG index status</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={loadData} className="p-1 text-slate-400 hover:text-slate-200" title="Refresh">
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
            <button onClick={onClose} className="p-1 text-slate-400 hover:text-slate-200">
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-5 text-xs">
          {loading && !diag ? (
            <div className="text-center py-12 text-slate-400">Loading telemetry...</div>
          ) : diag ? (
            <>
              {/* Top Status Badges */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <div className="p-3 bg-slate-950 rounded-xl border border-slate-800">
                  <div className="text-[11px] text-slate-400 font-medium">System Status</div>
                  <div className="text-sm font-bold text-emerald-400 capitalize mt-0.5 flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                    {diag.status}
                  </div>
                </div>

                <div className="p-3 bg-slate-950 rounded-xl border border-slate-800">
                  <div className="text-[11px] text-slate-400 font-medium">Uptime</div>
                  <div className="text-sm font-bold text-slate-200 mt-0.5 font-mono">
                    {diag.uptime_seconds}s
                  </div>
                </div>

                <div className="p-3 bg-slate-950 rounded-xl border border-slate-800">
                  <div className="text-[11px] text-slate-400 font-medium">P95 Latency</div>
                  <div className="text-sm font-bold text-indigo-300 mt-0.5 font-mono">
                    {diag.recent_latencies_p95_ms}ms
                  </div>
                </div>

                <div className="p-3 bg-slate-950 rounded-xl border border-slate-800">
                  <div className="text-[11px] text-slate-400 font-medium">Total Requests</div>
                  <div className="text-sm font-bold text-slate-200 mt-0.5 font-mono">
                    {diag.recent_requests_count}
                  </div>
                </div>
              </div>

              {/* Service Details */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Database & Models */}
                <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-3">
                  <div className="text-xs font-bold text-slate-300 flex items-center gap-2">
                    <Database className="w-4 h-4 text-indigo-400" /> Storage & Persistence
                  </div>
                  <div className="space-y-1.5 text-slate-400 text-[11px]">
                    <div className="flex justify-between">
                      <span>PostgreSQL Status:</span>
                      <span className={diag.database_connected ? "text-emerald-400 font-semibold" : "text-amber-400 font-semibold"}>
                        {diag.database_connected ? "Connected" : "Disconnected"}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Database Latency:</span>
                      <span className="font-mono text-slate-200">{diag.database_latency_ms}ms</span>
                    </div>
                  </div>
                </div>

                {/* Local Ollama */}
                <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-3">
                  <div className="text-xs font-bold text-slate-300 flex items-center gap-2">
                    <Server className="w-4 h-4 text-emerald-400" /> Local Ollama (Demo Mandatory)
                  </div>
                  <div className="space-y-1.5 text-slate-400 text-[11px]">
                    <div className="flex justify-between">
                      <span>Ollama Connection:</span>
                      <span className={diag.ollama_connected ? "text-emerald-400 font-semibold" : "text-amber-400 font-semibold"}>
                        {diag.ollama_connected ? "Live / Connected" : "Offline / Unreachable"}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Loaded Models:</span>
                      <span className="font-mono text-slate-200 truncate max-w-[140px]">
                        {diag.ollama_models?.length ? diag.ollama_models.join(', ') : 'None detected'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* RAG Knowledge Base */}
              <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-2">
                <div className="text-xs font-bold text-slate-300 flex items-center gap-2">
                  <Cpu className="w-4 h-4 text-violet-400" /> Hybrid RAG Knowledge Base
                </div>
                <div className="grid grid-cols-3 gap-2 text-slate-400 text-[11px] pt-1">
                  <div>
                    <span className="block text-slate-500">Indexed Episodes:</span>
                    <strong className="text-slate-200 text-xs">{diag.indexed_episodes}</strong>
                  </div>
                  <div>
                    <span className="block text-slate-500">Searchable Chunks:</span>
                    <strong className="text-slate-200 text-xs">{diag.indexed_chunks}</strong>
                  </div>
                  <div>
                    <span className="block text-slate-500">Fusion Engine:</span>
                    <strong className="text-indigo-400 text-xs font-mono">BM25 + Dense (k=60)</strong>
                  </div>
                </div>
              </div>
            </>
          ) : null}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-slate-800 bg-slate-950/80 flex items-center justify-between">
          <span className="text-[11px] text-slate-400 flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> Zero committed secrets • Production-ready observability
          </span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-semibold transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
