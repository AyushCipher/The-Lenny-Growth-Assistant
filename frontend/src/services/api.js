const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export async function sendChatMessage({ message, sessionId, provider, model, userMetadata }) {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      session_id: sessionId || null,
      provider: provider || null,
      model: model || null,
      user_metadata: userMetadata || {}
    })
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: 'Network error' }));
    throw new Error(err.detail || 'Failed to send message');
  }
  return response.json();
}

export async function generateShip30Essay({ topic, targetAudience, coreTakeaway, guestFocus, sessionId, provider }) {
  const response = await fetch(`${API_BASE_URL}/api/chat/ship30`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      topic,
      target_audience: targetAudience || 'Product Managers & Growth Leaders',
      core_takeaway: coreTakeaway || null,
      guest_focus: guestFocus || null,
      session_id: sessionId || null,
      provider: provider || null
    })
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: 'Network error' }));
    throw new Error(err.detail || 'Failed to generate Ship 30 essay');
  }
  return response.json();
}

export async function fetchSessions() {
  const response = await fetch(`${API_BASE_URL}/api/sessions`);
  if (!response.ok) throw new Error('Failed to load sessions');
  return response.json();
}

export async function createSession(title = 'New Strategy Chat', userMetadata = {}) {
  const response = await fetch(`${API_BASE_URL}/api/sessions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, user_metadata: userMetadata })
  });
  if (!response.ok) throw new Error('Failed to create session');
  return response.json();
}

export async function fetchSessionDetails(sessionId) {
  const response = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}`);
  if (!response.ok) throw new Error('Failed to load session details');
  return response.json();
}

export async function deleteSession(sessionId) {
  const response = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}`, {
    method: 'DELETE'
  });
  if (!response.ok) throw new Error('Failed to delete session');
  return true;
}

export async function fetchModels() {
  const response = await fetch(`${API_BASE_URL}/api/models`);
  if (!response.ok) throw new Error('Failed to load models');
  return response.json();
}

export async function selectActiveModel(provider, model = null) {
  const response = await fetch(`${API_BASE_URL}/api/models/select`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ provider, model })
  });
  if (!response.ok) throw new Error('Failed to select model');
  return response.json();
}

export async function fetchSources(query = null) {
  const url = query ? `${API_BASE_URL}/api/sources?query=${encodeURIComponent(query)}` : `${API_BASE_URL}/api/sources`;
  const response = await fetch(url);
  if (!response.ok) throw new Error('Failed to load sources');
  return response.json();
}

export async function fetchSourceDetails(sourceId) {
  const response = await fetch(`${API_BASE_URL}/api/sources/${sourceId}`);
  if (!response.ok) throw new Error('Failed to load source details');
  return response.json();
}

export async function fetchDiagnostics() {
  const response = await fetch(`${API_BASE_URL}/api/diagnostics`);
  if (!response.ok) throw new Error('Failed to fetch diagnostics');
  return response.json();
}
