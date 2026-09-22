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

export async function fetchPublicConfig() {
  const res = await fetch(`${API_BASE}/public-config`);
  if (!res.ok) throw new Error('Failed to fetch public config');
  return res.json() as Promise<{
    show_demo_button: boolean;
    google_auth_enabled: boolean;
    stars_enabled: boolean;
    paynet_enabled: boolean;
    payment_provider_text: string;
  }>;
}

export async function fetchListing(id: string) {
  const res = await fetch(`${API_BASE}/listings/${id}`, { headers: getHeaders() });
  if (!res.ok) throw new Error('Not found');
  return res.json();
}

export async function fetchMyListings() {
  const res = await fetch(`${API_BASE}/users/me/listings`, { headers: getHeaders() });
  if (!res.ok) throw new Error('Failed to fetch my listings');
  return res.json();
}

export async function createListing(data: any) {
  const res = await fetch(`${API_BASE}/users/me/listings`, {
    method: 'POST',
    headers: { ...getHeaders(), 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to create listing');
  }
  return res.json();
}
