import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, Loader2, Feather, ArrowUpRight, Compass } from 'lucide-react';
import MessageItem from './MessageItem';
import ModelSelector from './ModelSelector';

export default function ChatArea({
  sessionTitle,
  messages,
  isLoading,
  onSendMessage,
  onSelectSource,
  onOpenArtifact,
  activeProvider,
  onModelChanged,
  onTriggerShip30,
  sessionArtifacts = [],
  activeArtifact = null
}) {
  const [inputMessage, setInputMessage] = useState('');
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = (e) => {
    e?.preventDefault();
    if (!inputMessage.trim() || isLoading) return;
    onSendMessage(inputMessage.trim());
    setInputMessage('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const starterQuestions = [
    {
      title: "High-Agency vs. Low-Agency PMs",
      guest: "Shreyas Doshi",
      query: "How does Shreyas Doshi define 'High Agency' in product management, and what is the LNO framework?"
    },
    {
      title: "B2B Product-Led Growth (PLG)",
      guest: "Elena Verna",
      query: "According to Elena Verna, what defines a true Product-Qualified Lead (PQL) and when should a company layer on sales?"
    },
    {
      title: "Growth Loops vs. Marketing Funnels",
      guest: "Brian Balfour",
      query: "Explain Brian Balfour's Four Growth Fits and why Growth Loops compound better than traditional funnels."
    },
    {
      title: "SPADE Decision Framework",
      guest: "Gokul Rajaram",
      query: "How do you run the SPADE framework for high-velocity product decisions according to Gokul Rajaram?"
    }
  ];

  return (
    <div className="flex-1 flex flex-col h-full bg-[#0b0f17] relative overflow-hidden">
      {/* Top Bar */}
      <header className="h-14 px-6 border-b border-slate-800/80 bg-slate-950/70 backdrop-blur-md flex items-center justify-between shrink-0 z-10">
        <div className="flex items-center gap-3 truncate">
          <h2 className="text-sm font-bold text-slate-100 truncate max-w-md">
            {sessionTitle || 'New Strategy Chat'}
          </h2>
        </div>

        <div className="flex items-center gap-3">
          {sessionArtifacts && sessionArtifacts.length > 0 && (
            <button
              onClick={() => {
                if (activeArtifact) {
                  onOpenArtifact(null);
                } else {
                  onOpenArtifact(sessionArtifacts[sessionArtifacts.length - 1]);
                }
              }}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all cursor-pointer shadow-sm ${
                activeArtifact
                  ? 'bg-indigo-600 text-white border-indigo-500 shadow-indigo-500/20'
                  : 'bg-indigo-950/40 text-indigo-300 border-indigo-500/40 hover:bg-indigo-900/60 hover:text-white'
              }`}
            >
              <Sparkles className="w-3.5 h-3.5 text-indigo-300" />
              <span>{activeArtifact ? 'Hide Artifact' : `View Artifact (${sessionArtifacts.length})`}</span>
            </button>
          )}

          <ModelSelector
            activeProvider={activeProvider}
            onModelChanged={onModelChanged}
          />
        </div>
      </header>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto px-4 md:px-8 py-6">
        <div className="max-w-4xl mx-auto">
          {messages.length === 0 ? (
            <div className="py-12 md:py-20 text-center animate-fadeIn">
              <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-indigo-500 to-violet-600 flex items-center justify-center text-white mx-auto shadow-xl shadow-indigo-500/20 mb-5">
                <Compass className="w-7 h-7" />
              </div>
              <h3 className="text-2xl font-bold text-slate-100 tracking-tight">
                The Lenny Growth Assistant
              </h3>
              <p className="text-sm text-slate-400 max-w-lg mx-auto mt-2 leading-relaxed">
                Query 200+ hours of Lenny's Podcast wisdom. Grounded answers, traceable citations, Claude-style HTML/CSS artifacts, and Ship 30 for 30 essays.
              </p>

              {/* Starter Question Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-10 text-left">
                {starterQuestions.map((q, idx) => (
                  <button
                    key={idx}
                    onClick={() => onSendMessage(q.query)}
                    className="p-4 rounded-xl bg-slate-900/80 hover:bg-slate-850 border border-slate-800 hover:border-indigo-500/50 transition-all group shadow-sm flex flex-col justify-between"
                  >
                    <div>
                      <div className="flex items-center justify-between text-[11px] font-semibold text-indigo-400 mb-1">
                        <span>{q.guest}</span>
                        <ArrowUpRight className="w-3.5 h-3.5 opacity-0 group-hover:opacity-100 transition-opacity text-indigo-300" />
                      </div>
                      <h4 className="text-xs font-bold text-slate-200 group-hover:text-indigo-200 transition-colors">
                        {q.title}
                      </h4>
                      <p className="text-[11px] text-slate-400 mt-1 line-clamp-2">
                        {q.query}
                      </p>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <>
              {messages.map((msg) => (
                <MessageItem
                  key={msg.id}
                  message={msg}
                  onSelectSource={onSelectSource}
                  onOpenArtifact={onOpenArtifact}
                  allArtifacts={sessionArtifacts}
                />
              ))}

              {isLoading && (
                <div className="py-4 px-6 rounded-2xl bg-slate-900/40 border border-slate-800/80 mr-12 flex items-center gap-3 text-xs text-indigo-300 font-medium animate-pulse">
                  <Loader2 className="w-4 h-4 animate-spin text-indigo-400" />
                  <span>Synthesizing grounded transcript wisdom and evaluating citations...</span>
                </div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>
      </div>

      {/* Input Bar */}
      <div className="p-4 md:p-6 bg-gradient-to-t from-slate-950 via-slate-950/90 to-transparent shrink-0">
        <form
          onSubmit={handleSubmit}
          className="max-w-4xl mx-auto rounded-2xl bg-slate-900/90 border border-slate-700/80 shadow-2xl p-2 md:p-2.5 focus-within:border-indigo-500/70 transition-all"
        >
          <div className="flex items-end gap-2">
            <textarea
              ref={textareaRef}
              rows={1}
              value={inputMessage}
              onChange={(e) => {
                setInputMessage(e.target.value);
                e.target.style.height = 'auto';
                e.target.style.height = `${Math.min(e.target.scrollHeight, 160)}px`;
              }}
              onKeyDown={handleKeyDown}
              placeholder="Ask a strategic product or growth question from Lenny's transcripts..."
              className="flex-1 bg-transparent px-3 py-2 text-xs md:text-sm text-slate-100 placeholder-slate-500 focus:outline-none resize-none max-h-40 leading-relaxed font-sans"
            />

            <div className="flex items-center gap-1.5 shrink-0 pb-1">
              <button
                type="button"
                onClick={onTriggerShip30}
                className="p-2 text-indigo-400 hover:text-indigo-300 hover:bg-slate-800 rounded-xl transition-colors"
                title="Ship 30 for 30 Skill"
              >
                <Feather className="w-4 h-4" />
              </button>

              <button
                type="submit"
                disabled={isLoading || !inputMessage.trim()}
                className="p-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 disabled:hover:bg-indigo-600 text-white transition-all shadow-md shadow-indigo-600/30 active:scale-95 cursor-pointer"
                title="Send message (Enter)"
              >
                {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
              </button>
            </div>
          </div>
        </form>
        <div className="max-w-4xl mx-auto mt-2 text-center text-[10px] text-slate-400">
          Strictly grounded in Lenny's Podcast transcripts. Evaluated with Local Ollama & Anthropic Claude Agent SDK.
        </div>
      </div>
    </div>
  );
}
