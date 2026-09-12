import React, { useState } from 'react';
import { Code, Eye, Copy, Check, Download, Maximize2, Minimize2, X, ShieldCheck, Sparkles } from 'lucide-react';
import DOMPurify from 'dompurify';

export default function ArtifactViewer({ artifact, onClose, allArtifacts = [], onSelectArtifact }) {
  const [activeTab, setActiveTab] = useState('preview'); // preview | code
  const [copied, setCopied] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);

  if (!artifact) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(artifact.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const ext = artifact.type === 'html' ? 'html' : 'md';
    const blob = new Blob([artifact.content], { type: artifact.type === 'html' ? 'text/html' : 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${artifact.title.toLowerCase().replace(/\s+/g, '_')}.${ext}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className={`flex flex-col bg-slate-900 border-l border-slate-800 h-full transition-all duration-300 ${
      isFullscreen ? 'fixed inset-0 z-50 bg-slate-950' : 'w-full lg:w-[50%] h-full'
    }`}>
      {/* Top Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800 bg-slate-950/80 backdrop-blur-sm">
        <div className="flex items-center gap-2.5">
          <div className="w-6 h-6 rounded bg-indigo-500/20 text-indigo-400 flex items-center justify-center font-bold text-xs border border-indigo-500/30">
            <Sparkles className="w-3.5 h-3.5" />
          </div>
          <div>
            <h3 className="text-xs md:text-sm font-semibold text-slate-100 truncate max-w-[200px] md:max-w-[300px]">
              {artifact.title}
            </h3>
            <div className="flex items-center gap-2 text-[10px] text-slate-400">
              <span className="uppercase font-mono font-bold text-indigo-400">{artifact.type}</span>
              <span>•</span>
              <span className="flex items-center gap-1 text-emerald-400 font-medium">
                <ShieldCheck className="w-3 h-3" /> Sandboxed Isolation
              </span>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-1.5">
          {/* Tab Switcher */}
          <div className="flex bg-slate-800/80 p-0.5 rounded-lg border border-slate-700/60 mr-2">
            <button
              onClick={() => setActiveTab('preview')}
              className={`flex items-center gap-1 px-2.5 py-1 text-xs font-medium rounded-md transition-all ${
                activeTab === 'preview' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Eye className="w-3 h-3" /> Preview
            </button>
            <button
              onClick={() => setActiveTab('code')}
              className={`flex items-center gap-1 px-2.5 py-1 text-xs font-medium rounded-md transition-all ${
                activeTab === 'code' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Code className="w-3 h-3" /> Code
            </button>
          </div>

          {/* Copy Button */}
          <button
            onClick={handleCopy}
            className="p-1.5 text-slate-400 hover:text-slate-100 hover:bg-slate-800 rounded-md transition-colors"
            title="Copy source code"
            aria-label="Copy source code"
          >
            {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
          </button>

          {/* Download Button */}
          <button
            onClick={handleDownload}
            className="p-1.5 text-slate-400 hover:text-slate-100 hover:bg-slate-800 rounded-md transition-colors"
            title="Download artifact"
            aria-label="Download artifact"
          >
            <Download className="w-4 h-4" />
          </button>

          {/* Fullscreen Toggle */}
          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            className="p-1.5 text-slate-400 hover:text-slate-100 hover:bg-slate-800 rounded-md transition-colors"
            title={isFullscreen ? "Exit Fullscreen" : "Fullscreen"}
            aria-label="Toggle fullscreen"
          >
            {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
          </button>

          {/* Close Button */}
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-slate-100 hover:bg-slate-800 rounded-md transition-colors"
            title="Close Artifact Pane"
            aria-label="Close Artifact Pane"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Version Selector (if multiple artifacts in session) */}
      {allArtifacts.length > 1 && (
        <div className="px-4 py-1.5 bg-slate-950/40 border-b border-slate-800/60 flex items-center gap-2 text-xs text-slate-400 overflow-x-auto">
          <span className="text-[11px] font-medium text-slate-500 whitespace-nowrap">Session Artifacts:</span>
          {allArtifacts.map((art, idx) => (
            <button
              key={art.id || idx}
              onClick={() => onSelectArtifact(art)}
              className={`px-2.5 py-0.5 rounded text-[11px] font-medium whitespace-nowrap transition-colors ${
                art.id === artifact.id 
                  ? 'bg-indigo-900/60 text-indigo-300 border border-indigo-700/60' 
                  : 'bg-slate-800/40 text-slate-400 hover:text-slate-200 border border-transparent'
              }`}
            >
              {art.title} (v{art.version || 1})
            </button>
          ))}
        </div>
      )}

      {/* Main Content Area */}
      <div className="flex-1 overflow-hidden relative bg-slate-950">
        {activeTab === 'preview' ? (
          artifact.type === 'html' ? (
            <iframe
              title={artifact.title}
              srcDoc={artifact.sanitized_content || artifact.content}
              sandbox="allow-scripts"
              className="w-full h-full border-0 bg-white"
            />
          ) : (
            <div className="p-6 overflow-y-auto h-full text-slate-200 prose prose-invert max-w-none text-sm leading-relaxed">
              <pre className="whitespace-pre-wrap font-sans bg-transparent p-0 border-0">
                {artifact.content}
              </pre>
            </div>
          )
        ) : (
          <div className="p-4 overflow-y-auto h-full font-mono text-xs text-slate-300 bg-slate-950">
            <pre className="whitespace-pre-wrap">
              <code>{artifact.content}</code>
            </pre>
          </div>
        )}
      </div>

      {/* Security Footer Badge */}
      <div className="px-4 py-2 border-t border-slate-800 bg-slate-950/90 text-[10px] text-slate-400 flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span><strong>Sandbox Active:</strong> Scripts allowed in unique origin; parent DOM, cookies, and network access strictly blocked.</span>
        </div>
        <span className="font-mono text-slate-500">CSP: default-src 'none'</span>
      </div>
    </div>
  );
}
