import { useQuery } from '@tanstack/react-query';
import { fetchPublicStats, fetchVisitorsStats, fetchTimeseries, fetchTopClicked } from '../api/client';
import { nf } from '../utils/formatters';

// Function to format the date string to a time like "14:00"
function formatHour(dateStr: string) {
  try {
    const d = new Date(dateStr);
    let h = d.getHours();
    return `${h < 10 ? '0' : ''}${h}:00`;
  } catch (e) {
    return dateStr;
  }
}

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

  const { data: timeseries } = useQuery({
    queryKey: ['timeseries'],
    queryFn: fetchTimeseries,
    refetchInterval: 60000,
  });

  const { data: topClicked } = useQuery({
    queryKey: ['top-clicked'],
    queryFn: fetchTopClicked,
    refetchInterval: 60000,
  });

  const tsData = timeseries?.data || [];
  const maxPageViews = Math.max(...tsData.map((d: any) => d.pageviews), 1);

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

        <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '32px', marginBottom: '40px' }}>
          
          {/* Chart Section */}
          <div style={{
            background: 'var(--surface)',
            border: '1px solid var(--line)',
            borderRadius: '16px',
            padding: '24px',
          }}>
            <h2 style={{ fontSize: '18px', marginBottom: '24px', color: 'var(--ink)' }}>Sahifa ko'rishlar (So'nggi 24 soat)</h2>
            <div style={{ height: '240px', display: 'flex', alignItems: 'flex-end', gap: '8px', paddingBottom: '24px', position: 'relative' }}>
              {!timeseries ? (
                <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--ink-3)' }}>
                  Yuklanmoqda...
                </div>
              ) : tsData.length === 0 ? (
                <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--ink-3)' }}>
                  Hali ma'lumot yo'q
                </div>
              ) : (
                tsData.map((d: any, idx: number) => {
                  const heightPct = Math.max((d.pageviews / maxPageViews) * 100, 2);
                  return (
                    <div key={idx} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px', height: '100%', justifyContent: 'flex-end', position: 'relative' }} className="chart-bar-group">
                      <div 
                        title={`${d.pageviews} views`}
                        style={{
                          width: '100%',
                          height: `${heightPct}%`,
                          background: 'linear-gradient(180deg, rgba(220, 255, 6, 0.8) 0%, rgba(220, 255, 6, 0.2) 100%)',
                          borderRadius: '4px',
                          transition: 'height 0.3s ease',
                          minHeight: '4px',
                        }}
                      />
                      <div style={{ fontSize: '10px', color: 'var(--ink-3)', position: 'absolute', bottom: '-20px', whiteSpace: 'nowrap' }}>
                        {idx % 3 === 0 || idx === tsData.length - 1 ? formatHour(d.date) : ''}
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>

          {/* Top Clicked Section */}
          <div style={{
            background: 'var(--surface)',
            border: '1px solid var(--line)',
            borderRadius: '16px',
            padding: '24px',
          }}>
            <h2 style={{ fontSize: '18px', marginBottom: '16px', color: 'var(--ink)' }}>Eng ko'p o'tilgan kanallar (Top)</h2>
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              {!topClicked ? (
                <div style={{ padding: '24px', textAlign: 'center', color: 'var(--ink-3)' }}>Yuklanmoqda...</div>
              ) : topClicked.length === 0 ? (
                <div style={{ padding: '24px', textAlign: 'center', color: 'var(--ink-3)' }}>Hali ma'lumot yo'q</div>
              ) : (
                topClicked.map((listing: any, index: number) => (
                  <div key={listing.id} style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '16px',
                    padding: '12px 0',
                    borderBottom: index < topClicked.length - 1 ? '1px solid var(--line)' : 'none'
                  }}>
                    <div style={{ width: '24px', fontSize: '14px', color: 'var(--ink-3)', fontWeight: 600, textAlign: 'center' }}>
                      {index + 1}
                    </div>
                    {listing.logo_url ? (
                      <img src={listing.logo_url} alt={listing.name} style={{ width: '40px', height: '40px', borderRadius: '50%', objectFit: 'cover' }} />
                    ) : (
                      <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: 'var(--surface-2)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--ink-2)', fontSize: '16px', fontWeight: 600 }}>
                        {listing.name.charAt(0).toUpperCase()}
                      </div>
                    )}
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontWeight: 500, color: 'var(--ink)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {listing.name}
                      </div>
                      <div style={{ fontSize: '13px', color: 'var(--ink-3)' }}>{listing.handle}</div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div className="num" style={{ fontWeight: 600, color: 'var(--accent)', fontSize: '16px' }}>
                        {nf(listing.clickthroughs)} <span style={{ fontSize: '12px', color: 'var(--ink-3)', fontWeight: 400 }}>o'tish</span>
                      </div>
                      {listing.current_price_b && (
                        <div className="num" style={{ fontSize: '12px', color: 'var(--ink-2)' }}>
                          joriy bidi: {listing.current_price_b} B
                        </div>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
