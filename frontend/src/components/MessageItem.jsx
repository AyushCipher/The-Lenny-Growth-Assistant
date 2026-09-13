import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { User, Sparkles, Clock, Zap, Cpu, Eye, Code, Layers } from 'lucide-react';
import CitationChip from './CitationChip';

export default function MessageItem({ message, onSelectSource, onOpenArtifact, allArtifacts = [] }) {
  const isUser = message.role === 'user';
  const citations = message.citations || [];

  // Check if message generated or references an artifact
  const hasArtifactMention = typeof message.content === 'string' && (
    message.content.includes('Artifact Generated:') ||
    message.content.includes(':::artifact') ||
    message.content.includes('<!DOCTYPE html>')
  );

  const matchedArtifact = (allArtifacts && allArtifacts.length > 0)
    ? (allArtifacts.find(a => a.message_id === message.id) || allArtifacts[allArtifacts.length - 1])
    : null;

  const showArtifactCard = !isUser && (hasArtifactMention || message.artifacts?.length > 0) && matchedArtifact;

  return (
    <div className={`py-5 px-4 md:px-6 rounded-2xl mb-4 transition-all ${
      isUser 
        ? 'bg-slate-900/80 border border-slate-800 ml-8 md:ml-20' 
        : 'bg-slate-900/40 border border-slate-800/80 mr-4 md:mr-12 shadow-sm'
    }`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-2.5">
        <div className="flex items-center gap-2">
          <div className={`w-7 h-7 rounded-lg flex items-center justify-center font-bold text-xs ${
            isUser ? 'bg-indigo-600 text-white' : 'bg-gradient-to-tr from-indigo-500 to-violet-600 text-white shadow-indigo-500/20 shadow-md'
          }`}>
            {isUser ? <User className="w-4 h-4" /> : <Sparkles className="w-4 h-4" />}
          </div>
          <span className="text-sm font-semibold text-slate-200">
            {isUser ? 'You' : 'The Lenny Growth Assistant'}
          </span>
        </div>

        {!isUser && (
          <div className="flex items-center gap-3 text-[11px] text-slate-400 font-mono">
            {message.model_used && (
              <span className="flex items-center gap-1 bg-slate-800/60 px-2 py-0.5 rounded border border-slate-700/50">
                <Cpu className="w-3 h-3 text-indigo-400" />
                {message.model_used}
              </span>
            )}
            {message.latency_ms && (
              <span className="flex items-center gap-1 text-slate-400">
                <Clock className="w-3 h-3 text-slate-500" />
                {(message.latency_ms / 1000).toFixed(2)}s
              </span>
            )}
          </div>
        )}
      </div>

      {/* Message Content */}
      <div className="text-sm leading-relaxed text-slate-200 font-normal prose prose-invert max-w-none prose-p:my-2 prose-headings:text-slate-100 prose-headings:font-bold prose-pre:bg-slate-950 prose-pre:border prose-pre:border-slate-800 prose-code:text-indigo-300">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {message.content}
        </ReactMarkdown>
      </div>

      {/* Interactive Artifact Card */}
      {showArtifactCard && (
        <div className="mt-4 p-3.5 rounded-xl bg-gradient-to-r from-indigo-950/70 via-slate-900 to-purple-950/70 border border-indigo-500/40 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-lg shadow-indigo-950/30 animate-fadeIn">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-indigo-600/30 text-indigo-400 flex items-center justify-center shrink-0 border border-indigo-500/30">
              <Layers className="w-5 h-5 text-indigo-300" />
            </div>
            <div>
              <div className="text-xs font-bold text-slate-100 flex items-center gap-2">
                <span>{matchedArtifact.title || "Interactive Growth Application"}</span>
                <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                  {matchedArtifact.type || "HTML"}
                </span>
              </div>
              <div className="text-[11px] text-slate-400 mt-0.5">
                Live interactive tool with real-time sliders, compounding simulation, and source code.
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={() => onOpenArtifact && onOpenArtifact(matchedArtifact)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/30 transition-all cursor-pointer hover:scale-[1.02] active:scale-[0.98]"
            >
              <Eye className="w-3.5 h-3.5" />
              <span>Preview & Code</span>
            </button>
          </div>
        </div>
      )}

      {/* Citations Shelf */}
      {citations.length > 0 && (
        <div className="mt-4 pt-3 border-t border-slate-800/80">
          <div className="text-[11px] font-semibold text-emerald-400/90 uppercase tracking-wider mb-2 flex items-center gap-1.5">
            <Zap className="w-3 h-3" /> Grounded Transcript Sources ({citations.length}):
          </div>
          <div className="flex flex-wrap gap-1.5">
            {citations.map((cite, idx) => (
              <CitationChip
                key={idx}
                citation={cite}
                onSelect={onSelectSource}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
