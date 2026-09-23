import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchBoard } from '../api/client';
import { ListingRow } from '../components/ListingRow';

const TASHKENT_TZ = 'Asia/Tashkent';

function getMidnightCountdown(): string {
  const now = new Date();
  const tashkent = new Date(now.toLocaleString('en-US', { timeZone: TASHKENT_TZ }));
  const midnight = new Date(tashkent);
  midnight.setHours(24, 0, 0, 0);
  const diff = midnight.getTime() - tashkent.getTime();
  const h = Math.floor(diff / 3600000);
  const m = Math.floor((diff % 3600000) / 60000);
  return `${h}s ${m}d`;
}

export function Kunlik() {
  const [page, setPage] = useState(1);

  const { data: board, isLoading } = useQuery({
    queryKey: ['board', 'daily', page],
    queryFn: () => fetchBoard('daily', page),
    refetchInterval: 30000,
  });


  const entries = board?.entries ?? [];
  const isEmpty = !isLoading && entries.length === 0;

  return (
    <section id="page-kunlik">
      <div className="wrap">
        <div className="page-head">
          <h1>Kunlik reyting</h1>
          <p>Har kun yarim tunda Toshkent vaqti bo'yicha taxta yangilanadi va 1 B dan boshlanadi.</p>
          <p style={{ fontSize: '13px', color: 'var(--ink-3)', marginTop: '4px' }}>
            ⏱ Keyingi yangilanish: <strong>{getMidnightCountdown()}</strong> dan keyin
          </p>
        </div>

        {isEmpty ? (
          <div className="empty-state" style={{ padding: '60px 20px', textAlign: 'center' }}>
            <p style={{ fontSize: '32px', marginBottom: '12px' }}>🌙</p>
            <p>Bugungi kunlik reytingda hali hech kim o'rin olmagan.</p>
            <p style={{ color: 'var(--ink-3)', fontSize: '14px', marginTop: '8px' }}>
              Birinchi bo'ling — bor-yo'g'i 1 B!
            </p>
            <a href="/" className="btn-primary" style={{ marginTop: '20px', display: 'inline-block', padding: '12px 28px', textDecoration: 'none', borderRadius: '12px' }}>
              O'rin olish →
            </a>
          </div>
        ) : (
          <div>
            <div className="board-list">
              {entries.map((e: any) => (
                <ListingRow key={e.listing.id} item={e} />
              ))}
            </div>
            {board && board.total_pages > 1 && (
              <div style={{ display: 'flex', gap: '8px', justifyContent: 'center', marginTop: '20px' }}>
                <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}
                  style={{ padding: '8px 16px', borderRadius: '8px', border: '1px solid var(--line)', background: 'none', color: 'var(--ink)', cursor: page === 1 ? 'not-allowed' : 'pointer', opacity: page === 1 ? 0.5 : 1 }}>← Oldingi</button>
                <span style={{ padding: '8px 12px', fontSize: '13px', color: 'var(--ink-2)' }}>{page} / {board.total_pages}</span>
                <button onClick={() => setPage(p => p + 1)} disabled={page >= board.total_pages}
                  style={{ padding: '8px 16px', borderRadius: '8px', border: '1px solid var(--line)', background: 'none', color: 'var(--ink)', cursor: 'pointer' }}>Keyingi →</button>
              </div>
            )}
          </div>
        )}
      </div>
    </section>
  );
}
