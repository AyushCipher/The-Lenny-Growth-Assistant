import React, { useState, useEffect } from 'react';
import { X, BookOpen, User, Hash, Tag, Clock } from 'lucide-react';
import { fetchSourceDetails } from '../services/api';

export default function SourceDrawer({ sourceId, isOpen, onClose }) {
  const [sourceData, setSourceData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (sourceId && isOpen) {
      setLoading(true);
      fetchSourceDetails(sourceId)
        .then(data => setSourceData(data))
        .catch(err => console.error("Error fetching source details", err))
        .finally(() => setLoading(false));
    }
  }, [sourceId, isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full max-w-lg bg-slate-900 border-l border-slate-700 shadow-2xl flex flex-col animate-slideLeft">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-slate-800 bg-slate-950/80">
        <div className="flex items-center gap-2">
          <BookOpen className="w-4 h-4 text-emerald-400" />
          <h2 className="text-sm font-bold text-slate-100">Transcript Inspector</h2>
        </div>
        <button onClick={onClose} className="text-slate-400 hover:text-slate-200 p-1">
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-5 space-y-4 text-xs">
        {loading ? (
          <div className="flex items-center justify-center py-20 text-slate-400">
            <div className="animate-spin w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full mr-2"></div>
            Loading source metadata...
          </div>
        ) : sourceData ? (
          <>
            {/* Metadata Card */}
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2.5">
              <h3 className="text-sm font-bold text-slate-100">{sourceData.episode_title}</h3>
              
              <div className="grid grid-cols-2 gap-2 text-slate-400 text-[11px]">
                <div className="flex items-center gap-1.5">
                  <User className="w-3.5 h-3.5 text-indigo-400" />
                  <span><strong>Guest:</strong> {sourceData.guest}</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <Hash className="w-3.5 h-3.5 text-indigo-400" />
                  <span><strong>Episode:</strong> {sourceData.episode_id}</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <Tag className="w-3.5 h-3.5 text-indigo-400" />
                  <span><strong>Topic:</strong> {sourceData.topic}</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <BookOpen className="w-3.5 h-3.5 text-indigo-400" />
                  <span><strong>Ref:</strong> {sourceData.source_reference}</span>
                </div>
              </div>

              {sourceData.metadata_json && (
                <div className="pt-2 border-t border-slate-800/80 text-[10px] text-slate-500 font-mono">
                  SHA256: {sourceData.metadata_json.source_hash} • Version: {sourceData.metadata_json.transcript_version}
                </div>
              )}
            </div>

            {/* Transcript Text */}
            <div>
              <div className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5 text-emerald-400" /> Full Dialogue Transcripts:
              </div>
              <div className="p-4 bg-slate-950 rounded-xl border border-slate-800/80 font-mono text-xs leading-relaxed text-slate-300 whitespace-pre-wrap">
                {sourceData.content}
              </div>
            </div>
          </>
        ) : (
          <div className="text-center py-20 text-slate-400">
            Source not found.
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-slate-800 bg-slate-950/80 text-[11px] text-slate-400 flex items-center justify-between">
        <span>Verified Grounding Evidence</span>
        <button
          onClick={onClose}
          className="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded font-medium text-xs transition-colors"
        >
          Close Drawer
        </button>
      </div>
    </div>
  );
}
