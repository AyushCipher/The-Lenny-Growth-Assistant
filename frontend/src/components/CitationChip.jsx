import React from 'react';
import { BookOpen } from 'lucide-react';

export default function CitationChip({ citation, onSelect }) {
  if (!citation) return null;

  return (
    <button
      onClick={() => onSelect(citation.source_id)}
      className="inline-flex items-center gap-1.5 px-2.5 py-1 my-1 mr-1.5 text-xs font-medium bg-emerald-950/60 text-emerald-300 border border-emerald-800/60 rounded-full hover:bg-emerald-900/80 hover:border-emerald-700 transition-all cursor-pointer shadow-sm group"
      title={`Guest: ${citation.guest} | Episode: ${citation.episode_title}`}
    >
      <BookOpen className="w-3 h-3 text-emerald-400 group-hover:scale-110 transition-transform" />
      <span className="font-semibold">{citation.guest}</span>
      {citation.timestamp_str && (
        <span className="text-emerald-400/80 text-[10px] bg-emerald-900/60 px-1 py-0.2 rounded">
          {citation.timestamp_str}
        </span>
      )}
    </button>
  );
}
