import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { User, Sparkles, Clock, Zap, Cpu } from 'lucide-react';
import CitationChip from './CitationChip';

export default function MessageItem({ message, onSelectSource, onOpenArtifact }) {
  const isUser = message.role === 'user';

  // Helper to replace raw citation tags in text with clickable spans or just let ReactMarkdown render
  const citations = message.citations || [];

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
