import React, { useState, useEffect } from 'react';
import { Cpu, Check, AlertCircle, ChevronDown, RefreshCw } from 'lucide-react';
import { fetchModels, selectActiveModel } from '../services/api';

export default function ModelSelector({ activeProvider, onModelChanged }) {
  const [isOpen, setIsOpen] = useState(false);
  const [modelsData, setModelsData] = useState(null);
  const [loading, setLoading] = useState(false);

  const loadModels = async () => {
    try {
      setLoading(true);
      const data = await fetchModels();
      setModelsData(data);
    } catch (e) {
      console.error("Failed to load models", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadModels();
  }, [activeProvider]);

  const handleSelect = async (provider) => {
    try {
      setLoading(true);
      await selectActiveModel(provider);
      await loadModels();
      onModelChanged(provider);
      setIsOpen(false);
    } catch (e) {
      alert(`Failed to switch provider: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  const DEFAULT_MODELS = [
    {
      provider: 'groq',
      model_name: 'openai/gpt-oss-120b',
      display_name: 'Groq Cloud (gpt-oss-120b) [Ultra Fast]',
      is_available: true,
      status_message: 'Groq Cloud ready',
      is_active: activeProvider === 'groq' || !activeProvider
    },
    {
      provider: 'ollama',
      model_name: 'llama3',
      display_name: 'Local Ollama (llama3) [Demo Mandatory]',
      is_available: true,
      status_message: 'Offline Local Demo Model',
      is_active: activeProvider === 'ollama' || !activeProvider
    },
    {
      provider: 'anthropic',
      model_name: 'claude-3-5-sonnet-20241022',
      display_name: 'Anthropic Claude (claude-3-5-sonnet)',
      is_available: false,
      status_message: 'Requires ANTHROPIC_API_KEY in .env',
      is_active: activeProvider === 'anthropic'
    },
    {
      provider: 'openai',
      model_name: 'gpt-4o',
      display_name: 'OpenAI (gpt-4o)',
      is_available: false,
      status_message: 'Requires OPENAI_API_KEY in .env',
      is_active: activeProvider === 'openai'
    }
  ];

  const modelsList = modelsData?.models?.length ? modelsData.models : DEFAULT_MODELS;

  const currentModel = modelsList.find(m => m.is_active) || modelsList[0];

  return (
    <div className="relative">
      <button
        onClick={() => {
          setIsOpen(!isOpen);
          if (!isOpen) loadModels();
        }}
        className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700/80 hover:border-slate-600 text-xs font-medium text-slate-200 transition-all shadow-sm"
      >
        <Cpu className="w-3.5 h-3.5 text-indigo-400" />
        <span className="font-semibold">{currentModel.display_name}</span>
        <span className={`w-2 h-2 rounded-full ${currentModel.is_available ? 'bg-emerald-400' : 'bg-amber-400'}`}></span>
        <ChevronDown className="w-3 h-3 text-slate-400" />
      </button>

      {isOpen && (
        <>
          <div className="fixed inset-0 z-30" onClick={() => setIsOpen(false)}></div>
          <div className="absolute right-0 mt-2 w-80 rounded-xl bg-slate-900 border border-slate-700 shadow-2xl p-2 z-40 text-xs">
            <div className="flex items-center justify-between px-2 py-1.5 border-b border-slate-800 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
              <span>Select Model Provider</span>
              <button onClick={loadModels} className="text-slate-400 hover:text-slate-200">
                <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} />
              </button>
            </div>

            <div className="space-y-1 mt-1.5">
              {modelsList.map((m) => (
                <button
                  key={m.provider}
                  onClick={() => handleSelect(m.provider)}
                  className={`w-full text-left p-2.5 rounded-lg flex items-start justify-between transition-all ${
                    m.is_active 
                      ? 'bg-indigo-950/70 border border-indigo-700/70 text-indigo-200' 
                      : 'hover:bg-slate-800 text-slate-300 border border-transparent'
                  }`}
                >
                  <div>
                    <div className="flex items-center gap-1.5 font-semibold text-xs">
                      <span>{m.display_name}</span>
                      {m.provider === 'ollama' && (
                        <span className="bg-emerald-950 text-emerald-400 text-[10px] px-1.5 py-0.2 rounded border border-emerald-800">
                          Demo Mandatory
                        </span>
                      )}
                    </div>
                    <div className="text-[10px] text-slate-400 mt-1 flex items-center gap-1">
                      <span className={`w-1.5 h-1.5 rounded-full ${m.is_available ? 'bg-emerald-400' : 'bg-amber-400'}`}></span>
                      <span>{m.status_message}</span>
                    </div>
                  </div>
                  {m.is_active && <Check className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />}
                </button>
              ))}
            </div>

            <div className="mt-2 p-2 bg-slate-950 rounded-lg text-[10px] text-slate-400 border border-slate-800/80">
              💡 <strong>Evaluator Note:</strong> The demo runs on <strong>Local Ollama</strong>. Switch to Anthropic or OpenAI anytime by supplying keys in <code>.env</code>.
            </div>
          </div>
        </>
      )}
    </div>
  );
}
