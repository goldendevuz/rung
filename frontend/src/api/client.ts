export const API_BASE = '/api/v1';

function getHeaders() {
  const headers: HeadersInit = {};
  if (typeof window !== 'undefined' && localStorage.getItem('rung_demo') === '1') {
    headers['X-Rung-Demo'] = '1';
  }
  return headers;
}

export async function fetchTabs() {
  const res = await fetch(`${API_BASE}/boards/tabs`, { headers: getHeaders() });
  if (!res.ok) throw new Error('Failed to fetch tabs');
  return res.json();
}

export async function fetchBoard(periodType: string, page: number = 1, category?: string, q?: string) {
  const params = new URLSearchParams({ page: String(page) });
  if (category) params.set('category', category);
  if (q) params.set('q', q);
  
  const res = await fetch(`${API_BASE}/boards/${periodType}/current?${params.toString()}`, { headers: getHeaders() });
  if (!res.ok) {
    if (res.status === 404) return null;
    throw new Error('Failed to fetch board');
  }
  return res.json();
}

export async function fetchCategories() {
  const res = await fetch(`${API_BASE}/categories`, { headers: getHeaders() });
  if (!res.ok) throw new Error('Failed to fetch categories');
  return res.json();
}

export async function fetchPublicStats() {
  const res = await fetch(`${API_BASE}/stats/public`, { headers: getHeaders() });
  if (!res.ok) throw new Error('Failed to fetch stats');
  return res.json();
}

export async function fetchQuote(boardId: number, targetRank: number) {
  const res = await fetch(`${API_BASE}/boards/${boardId}/quote?target_rank=${targetRank}`, { headers: getHeaders() });
  if (!res.ok) throw new Error('Failed to fetch quote');
  return res.json();
}
