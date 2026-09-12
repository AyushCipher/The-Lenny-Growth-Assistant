import React from 'react';
import { Plus, MessageSquare, Feather, Trash2, Activity, BookOpen, User } from 'lucide-react';

export default function Sidebar({
  sessions,
  activeSessionId,
  onSelectSession,
  onNewChat,
  onDeleteSession,
  onOpenShip30,
  onOpenDiagnostics,
  onOpenKnowledgeBase
}) {
  return (
    <aside className="w-64 md:w-72 bg-slate-900/95 border-r border-slate-800 flex flex-col h-full select-none">
      {/* Brand Header */}
      <div className="p-4 border-b border-slate-800/80 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-500 via-indigo-600 to-violet-600 flex items-center justify-center text-white font-bold shadow-lg shadow-indigo-500/20">
            LG
          </div>
          <div>
            <h1 className="text-sm font-bold text-slate-100 leading-tight">Lenny Assistant</h1>
            <span className="text-[10px] text-indigo-400 font-medium">Forward Deployed AI</span>
          </div>
        </div>
      </div>

      {/* Main Actions */}
      <div className="p-3 space-y-2">
        <button
          onClick={onNewChat}
          className="w-full flex items-center justify-center gap-2 px-3.5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs transition-all shadow-md shadow-indigo-600/20 active:scale-[0.98]"
        >
          <Plus className="w-4 h-4" />
          <span>New Strategy Chat</span>
        </button>

        <button
          onClick={onOpenShip30}
          className="w-full flex items-center justify-center gap-2 px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700/80 text-indigo-300 font-medium text-xs border border-indigo-500/20 transition-all hover:border-indigo-500/40"
        >
          <Feather className="w-3.5 h-3.5 text-indigo-400" />
          <span>Ship 30 for 30 Skill</span>
        </button>
      </div>

      {/* Chat History List */}
      <div className="flex-1 overflow-y-auto px-3 py-2 space-y-1">
        <div className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 px-2 py-1">
          Recent Sessions ({sessions.length})
        </div>

        {sessions.length === 0 ? (
          <div className="text-center py-8 text-xs text-slate-400">
            No previous chats. Start a new session above!
          </div>
        ) : (
          sessions.map((sess) => {
            const isActive = sess.id === activeSessionId;
            return (
              <div
                key={sess.id}
                onClick={() => onSelectSession(sess.id)}
                className={`group flex items-center justify-between px-3 py-2 rounded-xl text-xs font-medium cursor-pointer transition-all ${
                  isActive
                    ? 'bg-slate-800 text-indigo-200 border border-slate-700/80 shadow-sm'
                    : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'
                }`}
              >
                <div className="flex items-center gap-2 truncate pr-2">
                  <MessageSquare className={`w-3.5 h-3.5 shrink-0 ${isActive ? 'text-indigo-400' : 'text-slate-500'}`} />
                  <span className="truncate">{sess.title}</span>
                </div>

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    if (confirm(`Delete session "${sess.title}"?`)) {
                      onDeleteSession(sess.id);
                    }
                  }}
                  className="opacity-0 group-hover:opacity-100 p-1 hover:text-rose-400 text-slate-500 transition-opacity"
                  title="Delete session"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            );
          })
        )}
      </div>

      {/* Footer Navigation */}
      <div className="p-3 border-t border-slate-800 bg-slate-950/60 space-y-1.5 text-xs">
        <button
          onClick={onOpenKnowledgeBase}
          className="w-full flex items-center gap-2 px-3 py-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 transition-colors"
        >
          <BookOpen className="w-4 h-4 text-emerald-400" />
          <span>Knowledge Library</span>
        </button>

        <button
          onClick={onOpenDiagnostics}
          className="w-full flex items-center gap-2 px-3 py-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 transition-colors"
        >
          <Activity className="w-4 h-4 text-amber-400" />
          <span>Telemetry & Diagnostics</span>
        </button>

        <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between px-2 text-[11px] text-slate-400">
          <span className="flex items-center gap-1 font-medium">
            <User className="w-3 h-3 text-slate-400" /> Ayush Verma
          </span>
          <span className="font-mono text-[10px] text-slate-400">v1.0.0</span>
        </div>
      </div>
    </aside>
  );
}
