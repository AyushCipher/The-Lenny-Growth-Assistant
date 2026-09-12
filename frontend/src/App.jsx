import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import ArtifactViewer from './components/ArtifactViewer';
import Ship30GeneratorModal from './components/Ship30GeneratorModal';
import SourceDrawer from './components/SourceDrawer';
import DiagnosticsModal from './components/DiagnosticsModal';
import {
  fetchSessions,
  createSession,
  fetchSessionDetails,
  deleteSession,
  sendChatMessage,
  generateShip30Essay
} from './services/api';

export default function App() {
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [currentSession, setCurrentSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [activeArtifact, setActiveArtifact] = useState(null);
  const [sessionArtifacts, setSessionArtifacts] = useState([]);
  const [activeSourceId, setActiveSourceId] = useState(null);
  const [isSourceDrawerOpen, setIsSourceDrawerOpen] = useState(false);
  const [isShip30ModalOpen, setIsShip30ModalOpen] = useState(false);
  const [isDiagnosticsModalOpen, setIsDiagnosticsModalOpen] = useState(false);
  const [activeProvider, setActiveProvider] = useState('ollama');
  const [isLoading, setIsLoading] = useState(false);

  // Load initial sessions
  const loadSessionsList = async () => {
    try {
      const data = await fetchSessions();
      setSessions(data);
      if (data.length > 0 && !activeSessionId) {
        selectSession(data[0].id);
      }
    } catch (e) {
      console.error("Failed to fetch sessions", e);
    }
  };

  useEffect(() => {
    loadSessionsList();
  }, []);

  const selectSession = async (sessionId) => {
    setActiveSessionId(sessionId);
    try {
      const details = await fetchSessionDetails(sessionId);
      setCurrentSession(details);
      setMessages(details.messages || []);
      setSessionArtifacts(details.artifacts || []);
      if (details.artifacts && details.artifacts.length > 0) {
        setActiveArtifact(details.artifacts[details.artifacts.length - 1]);
      } else {
        setActiveArtifact(null);
      }
    } catch (e) {
      console.error("Failed to load session details", e);
    }
  };

  const handleNewChat = async () => {
    try {
      const newSess = await createSession("New Strategy Chat");
      setSessions([newSess, ...sessions]);
      setActiveSessionId(newSess.id);
      setCurrentSession(newSess);
      setMessages([]);
      setSessionArtifacts([]);
      setActiveArtifact(null);
    } catch (e) {
      alert(`Error creating session: ${e.message}`);
    }
  };

  const handleDeleteSession = async (sessionId) => {
    try {
      await deleteSession(sessionId);
      const remaining = sessions.filter(s => s.id !== sessionId);
      setSessions(remaining);
      if (activeSessionId === sessionId) {
        if (remaining.length > 0) {
          selectSession(remaining[0].id);
        } else {
          setActiveSessionId(null);
          setCurrentSession(null);
          setMessages([]);
          setActiveArtifact(null);
        }
      }
    } catch (e) {
      alert(`Error deleting session: ${e.message}`);
    }
  };

  const handleSendMessage = async (text) => {
    setIsLoading(true);
    const tempUserMsg = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: text,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, tempUserMsg]);

    try {
      const res = await sendChatMessage({
        message: text,
        sessionId: activeSessionId,
        provider: activeProvider
      });

      if (!activeSessionId) {
        setActiveSessionId(res.session_id);
      }

      // Update messages
      const assistantMsg = {
        id: res.message_id,
        role: 'assistant',
        content: res.content,
        citations: res.citations,
        model_used: `${res.provider}:${res.model}`,
        latency_ms: res.latency_ms,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev.filter(m => m.id !== tempUserMsg.id), tempUserMsg, assistantMsg]);

      // If an artifact was generated, open and set it active
      if (res.artifacts && res.artifacts.length > 0) {
        const latestArtifact = res.artifacts[res.artifacts.length - 1];
        setSessionArtifacts(prev => [...prev, ...res.artifacts]);
        setActiveArtifact(latestArtifact);
      }

      loadSessionsList();
    } catch (e) {
      alert(`Error: ${e.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateShip30 = async (formData) => {
    setIsLoading(true);
    try {
      const res = await generateShip30Essay({
        ...formData,
        sessionId: activeSessionId,
        provider: activeProvider
      });

      if (!activeSessionId) {
        setActiveSessionId(res.session_id);
      }

      const assistantMsg = {
        id: res.message_id,
        role: 'assistant',
        content: res.essay_markdown,
        citations: res.citations,
        model_used: `${res.provider}:${res.model}`,
        latency_ms: res.latency_ms,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, assistantMsg]);
      loadSessionsList();
    } catch (e) {
      alert(`Ship 30 generation error: ${e.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectSource = (sourceId) => {
    setActiveSourceId(sourceId);
    setIsSourceDrawerOpen(true);
  };

  return (
    <div className="flex h-screen w-screen bg-[#0b0f17] text-slate-100 overflow-hidden font-sans">
      {/* Left Sidebar */}
      <Sidebar
        sessions={sessions}
        activeSessionId={activeSessionId}
        onSelectSession={selectSession}
        onNewChat={handleNewChat}
        onDeleteSession={handleDeleteSession}
        onOpenShip30={() => setIsShip30ModalOpen(true)}
        onOpenDiagnostics={() => setIsDiagnosticsModalOpen(true)}
        onOpenKnowledgeBase={() => {
          setActiveSourceId('src_shreyas_doshi_01');
          setIsSourceDrawerOpen(true);
        }}
      />

      {/* Main Workspace Area (Chat + Split Artifact Viewer) */}
      <main className="flex-1 flex overflow-hidden">
        {/* Chat Pane */}
        <ChatArea
          sessionTitle={currentSession?.title}
          messages={messages}
          isLoading={isLoading}
          onSendMessage={handleSendMessage}
          onSelectSource={handleSelectSource}
          onOpenArtifact={(art) => setActiveArtifact(art)}
          activeProvider={activeProvider}
          onModelChanged={(prov) => setActiveProvider(prov)}
          onTriggerShip30={() => setIsShip30ModalOpen(true)}
        />

        {/* Right Split Pane: Claude-Style Artifact Viewer */}
        {activeArtifact && (
          <ArtifactViewer
            artifact={activeArtifact}
            onClose={() => setActiveArtifact(null)}
            allArtifacts={sessionArtifacts}
            onSelectArtifact={(art) => setActiveArtifact(art)}
          />
        )}
      </main>

      {/* Ship 30 for 30 Generator Modal */}
      <Ship30GeneratorModal
        isOpen={isShip30ModalOpen}
        onClose={() => setIsShip30ModalOpen(false)}
        onGenerate={handleGenerateShip30}
        isLoading={isLoading}
      />

      {/* Slide-out Transcript Inspector Drawer */}
      <SourceDrawer
        sourceId={activeSourceId}
        isOpen={isSourceDrawerOpen}
        onClose={() => setIsSourceDrawerOpen(false)}
      />

      {/* Diagnostics & Observability Modal */}
      <DiagnosticsModal
        isOpen={isDiagnosticsModalOpen}
        onClose={() => setIsDiagnosticsModalOpen(false)}
      />
    </div>
  );
}
