import React, { useState } from 'react';
import { Feather, X, Sparkles, Send } from 'lucide-react';

export default function Ship30GeneratorModal({ isOpen, onClose, onGenerate, isLoading }) {
  const [topic, setTopic] = useState('');
  const [targetAudience, setTargetAudience] = useState('Product Managers & Growth Leaders');
  const [coreTakeaway, setCoreTakeaway] = useState('');
  const [guestFocus, setGuestFocus] = useState('Shreyas Doshi & Elena Verna');

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!topic.trim()) return;
    onGenerate({
      topic,
      targetAudience,
      coreTakeaway,
      guestFocus
    });
    onClose();
  };

  const presetTopics = [
    { label: "Why Most Startups Fail at Product-Led Growth (PLG)", guest: "Elena Verna" },
    { label: "High Agency vs. Low Agency: The Single Predictor of Elite PMs", guest: "Shreyas Doshi" },
    { label: "The Four Growth Fits Every $100M SaaS Must Solve", guest: "Brian Balfour" },
    { label: "The SPADE Framework for High-Velocity Product Decisions", guest: "Gokul Rajaram" },
    { label: "The 40% Product-Market Fit Engine and Sean Ellis Survey", guest: "Sean Ellis" },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fadeIn">
      <div className="w-full max-w-xl rounded-2xl bg-slate-900 border border-slate-700 shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-950/60">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-indigo-500 to-violet-600 flex items-center justify-center text-white shadow-md">
              <Feather className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-100">Ship 30 for 30 Essay Generator</h2>
              <p className="text-xs text-slate-400">Generate a viral, grounded ~1,250-word atomic essay</p>
            </div>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-200">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4 text-xs">
          <div>
            <label className="block text-slate-300 font-semibold mb-1">Core Topic / Contrarian Insight *</label>
            <input
              type="text"
              required
              placeholder="e.g. Why B2B SaaS Startups Shouldn't Copy Slack's PLG Model"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-lg bg-slate-950 border border-slate-700 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 text-xs"
            />
          </div>

          {/* Presets */}
          <div>
            <span className="block text-slate-400 font-medium mb-1.5">Or choose a high-signal Lenny topic:</span>
            <div className="flex flex-wrap gap-1.5">
              {presetTopics.map((p, idx) => (
                <button
                  type="button"
                  key={idx}
                  onClick={() => {
                    setTopic(p.label);
                    setGuestFocus(p.guest);
                  }}
                  className="px-2.5 py-1 rounded-full bg-slate-800 hover:bg-slate-700 text-slate-300 text-[11px] border border-slate-700/60 transition-colors text-left"
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-slate-300 font-semibold mb-1">Target Audience</label>
              <input
                type="text"
                value={targetAudience}
                onChange={(e) => setTargetAudience(e.target.value)}
                className="w-full px-3.5 py-2 rounded-lg bg-slate-950 border border-slate-700 text-slate-100 text-xs focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div>
              <label className="block text-slate-300 font-semibold mb-1">Podcast Guest Focus</label>
              <input
                type="text"
                value={guestFocus}
                onChange={(e) => setGuestFocus(e.target.value)}
                placeholder="e.g. Shreyas Doshi, Elena Verna"
                className="w-full px-3.5 py-2 rounded-lg bg-slate-950 border border-slate-700 text-slate-100 text-xs focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-slate-300 font-semibold mb-1">Core Actionable Takeaway</label>
            <input
              type="text"
              value={coreTakeaway}
              onChange={(e) => setCoreTakeaway(e.target.value)}
              placeholder="e.g. Implement a 3-step reverse trial framework"
              className="w-full px-3.5 py-2 rounded-lg bg-slate-950 border border-slate-700 text-slate-100 text-xs focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div className="p-3 bg-indigo-950/30 border border-indigo-900/60 rounded-xl text-[11px] text-indigo-300 leading-relaxed">
            ✨ <strong>Skill Mechanics:</strong> Enforces the <strong>Hook Formula</strong>, <strong>2-Year Test</strong>, <strong>1-3-1 Pacing</strong>, <strong>Selective Bold Emphasis</strong>, and <strong>Transcript Citations</strong> for ~1,250 words.
          </div>

          {/* Footer */}
          <div className="flex items-center justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-xs font-semibold text-slate-400 hover:text-slate-200"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading || !topic.trim()}
              className="flex items-center gap-1.5 px-5 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs transition-all shadow-md shadow-indigo-600/30 disabled:opacity-50"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>Generate Ship 30 Essay</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
