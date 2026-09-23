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

export async function fetchVisitorsStats() {
  const res = await fetch(`${API_BASE}/stats/visitors`, { headers: getHeaders() });
  if (!res.ok) throw new Error('Failed to fetch visitors stats');
  return res.json() as Promise<{
    configured: boolean;
    visitors_today: number | null;
    visitors_30d: number | null;
    start_at: string | null;
    end_at: string | null;
  }>;
}

export async function fetchQuote(boardId: string | number, targetRank: number, category?: string) {
  const catParam = category && category !== 'all' ? `&category=${encodeURIComponent(category)}` : '';
  const res = await fetch(`${API_BASE}/boards/${boardId}/quote?target_rank=${targetRank}${catParam}`, { headers: getHeaders() });
  if (!res.ok) throw new Error('Failed to fetch quote');
  return res.json() as Promise<{
    board_id: string;
    target_rank: number;
    holder_paid_b: string;
    holder_paid_units: number;
    min_cost_b: string;
    min_cost_units: number;
    resulting_rank: number;
  }>;
}

export async function fetchCandidates(boardId: string | number, limit: number = 10, category?: string) {
  const catParam = category && category !== 'all' ? `&category=${encodeURIComponent(category)}` : '';
  const res = await fetch(`${API_BASE}/boards/${boardId}/candidates?limit=${limit}${catParam}`, { headers: getHeaders() });
  if (!res.ok) throw new Error('Failed to fetch candidate ranks');
  return res.json() as Promise<Array<{
    rank: number;
    is_occupied: boolean;
    holder_name: string | null;
    holder_handle: string | null;
    holder_paid_b: number;
    price_b: number;
  }>>;
}

export async function fetchRecentActivity(limit: number = 8) {
  const res = await fetch(`${API_BASE}/boards/activity?limit=${limit}`, { headers: getHeaders() });
  if (!res.ok) throw new Error('Failed to fetch recent activity');
  return res.json() as Promise<Array<{
    id: string;
    listing_id: string;
    listing_name: string;
    listing_handle: string;
    listing_logo_url: string | null;
    listing_gradient_start: string | null;
    listing_gradient_end: string | null;
    paid_b: string;
    paid_units: number;
    entered_at: string;
    period_type: string | null;
  }>>;
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

export async function fetchListing(slug: string) {
  const res = await fetch(`${API_BASE}/listings/${slug}`, { headers: getHeaders() });
  if (!res.ok) {
    if (res.status === 404) throw new Error('Not Found');
    throw new Error('Server Error');
  }
  return res.json();
}

export async function createTopup(b_amount: number) {
  const res = await fetch(`${API_BASE}/wallet/topup`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getHeaders(),
    },
    body: JSON.stringify({ b_amount }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "To'lovni boshlashda xatolik yuz berdi");
  }
  return res.json() as Promise<{ pay_url: string; order_id: string }>;
}

export async function fetchTopupStatus(orderId: string) {
  const res = await fetch(`${API_BASE}/wallet/topup/${orderId}`, {
    headers: getHeaders(),
  });
  if (!res.ok) {
    throw new Error('Holatni tekshirishda xatolik yuz berdi');
  }
  return res.json() as Promise<{
    order_id: string;
    b_amount: number;
    amount_uzs: number;
    status: 'pending' | 'completed' | 'failed';
    created_at: string;
  }>;
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

export async function claimRank(data: { listing_id: string; period_type?: string; target_rank?: number; paid_b?: number; category?: string }) {
  const res = await fetch(`${API_BASE}/boards/claim`, {
    method: 'POST',
    headers: { ...getHeaders(), 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "O'rinni olishda xatolik yuz berdi");
  }
  return res.json();
}

export async function uploadLogo(file: File): Promise<{ url: string }> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/uploads/logo`, {
    method: 'POST',
    headers: getHeaders(),
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Logotip yuklashda xatolik yuz berdi');
  }
  return res.json();
}

export async function updateListing(id: string, data: { name?: string; description?: string; logo_url?: string }) {
  const res = await fetch(`${API_BASE}/users/me/listings/${id}`, {
    method: 'PATCH',
    headers: { ...getHeaders(), 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Kanal ma'lumotlarini yangilashda xatolik yuz berdi");
  }
  return res.json();
}


