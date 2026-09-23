import { useQuery } from '@tanstack/react-query';
import { fetchPublicStats, fetchVisitorsStats } from '../api/client';
import { nf } from '../utils/formatters';

export function Statistika() {
  const { data: stats } = useQuery({
    queryKey: ['stats'],
    queryFn: fetchPublicStats,
    refetchInterval: 30000,
  });

  const { data: visitorsStats } = useQuery({
    queryKey: ['visitors-stats'],
    queryFn: fetchVisitorsStats,
    refetchInterval: 60000,
  });

  return (
    <section id="page-statistika" style={{ padding: '24px 0 60px' }}>
      <div className="wrap">
        <div className="page-head" style={{ marginBottom: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
            <div>
              <h1 style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <span className="dot" style={{ width: '12px', height: '12px' }} />
                Jonli statistika
              </h1>
              <p style={{ marginTop: '6px', color: 'var(--ink-2)' }}>
                Rung platformasi trafigi, real vaqtdagi foydalanuvchilar va ochiq tahlillar.
              </p>
            </div>
            <a
              href="https://datafa.st/share/6ab279beba28fc830cd8714b"
              target="_blank"
              rel="noopener noreferrer"
              className="btn-login"
              style={{
                textDecoration: 'none',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '10px 18px',
                fontSize: '14px',
              }}
            >
              DataFast'da to'liq ko'rish ↗
            </a>
          </div>
        </div>

        <div className="stat-grid" style={{ marginBottom: '32px' }}>
          <div className="stat accent">
            <div className="v num">{stats ? (stats.online_now || 1) : 1}</div>
            <div className="k">hozir onlayn</div>
          </div>
          <div className="stat">
            <div className="v num">
              {visitorsStats?.configured && visitorsStats.visitors_today != null
                ? nf(visitorsStats.visitors_today)
                : (stats ? nf(stats.visits_today || 1) : 1)}
            </div>
            <div className="k">bugungi tashriflar</div>
          </div>
          <div className="stat">
            <div className="v num">
              {visitorsStats?.configured && visitorsStats.visitors_30d != null
                ? nf(visitorsStats.visitors_30d)
                : (stats ? nf(stats.visits_today || 1) : 1)}
            </div>
            <div className="k">jami tashriflar (30 kun)</div>
          </div>
          <div className="stat">
            <div className="v num">{stats ? nf(stats.total_listings || 0) : 0}</div>
            <div className="k">faol kanallar</div>
          </div>
          <div className="stat">
            <div className="v num">{stats ? nf((stats.total_paid_units || 0) / 1000) : 0} B</div>
            <div className="k">to'langan mablag'</div>
          </div>
        </div>

        <div style={{
          width: '100%',
          minHeight: '750px',
          borderRadius: '16px',
          overflow: 'hidden',
          border: '1px solid var(--line)',
          background: 'var(--surface)',
        }}>
          <iframe
            src="https://datafa.st/share/6ab279beba28fc830cd8714b"
            title="Rung Analytics | DataFast"
            style={{
              width: '100%',
              height: '850px',
              border: 'none',
              display: 'block',
            }}
          />
        </div>
      </div>
    </section>
  );
}
