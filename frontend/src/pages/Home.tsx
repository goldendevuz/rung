import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchTabs, fetchBoard, fetchCategories, fetchQuote, fetchPublicStats } from '../api/client';
import { formatB } from '../utils/formatters';
import { ListingRow, MiniListing } from '../components/ListingRow';

const PERIOD_NAMES: Record<string, string> = {
  all_time: "Barcha vaqt",
  daily: "Bugun",
  weekly: "Hafta",
  monthly: "Oy",
  yearly: "Yil",
  season: "Fasl"
};

const PERIOD_NOTES: Record<string, string> = {
  all_time: "Umumiy taxta — hech qachon yopilmaydi.",
  daily: "Har kuni 00:00 da (Toshkent) yopiladi",
  weekly: "Dushanba 00:00 da yangilanadi",
  monthly: "Oy boshida yangilanadi",
  yearly: "Yil boshida yangilanadi",
  season: "Fasl boshida yangilanadi"
};

export function Home() {
  const [period, setPeriod] = useState<string>('all_time');
  const [cat, setCat] = useState<string>('all');
  const [search] = useState<string>('');
  const [page, setPage] = useState<number>(1);

  const { data: tabs = [] } = useQuery({
    queryKey: ['tabs'],
    queryFn: fetchTabs
  });

  const { data: categories = [] } = useQuery({
    queryKey: ['categories'],
    queryFn: fetchCategories
  });

  const categoryMap = React.useMemo(() => {
    return categories.reduce((acc: any, c: any) => {
      acc[c.slug] = { n: c.name_uz, c: c.color, i: c.icon };
      return acc;
    }, {});
  }, [categories]);

  const { data: boardPage, isLoading } = useQuery({
    queryKey: ['board', period, page, cat === 'all' ? undefined : cat, search],
    queryFn: () => fetchBoard(period, page, cat === 'all' ? undefined : cat, search),
    retry: false, // 404 means no active board
  });

  const { data: heroQuote } = useQuery({
    queryKey: ['quote', boardPage?.board_id, 1],
    queryFn: () => fetchQuote(boardPage!.board_id, 1),
    enabled: !!boardPage?.board_id,
  });

  const { data: sideDailyBoard } = useQuery({
    queryKey: ['board', 'daily', 1, undefined, undefined],
    queryFn: () => fetchBoard('daily', 1),
    retry: false,
  });

  const entries = boardPage?.entries || [];
  
  // Base price in units
  const basePriceUnits = heroQuote ? heroQuote.min_cost_units : 1000;

  // Use state for hero price so user can increment it
  const [heroPriceUnits, setHeroPriceUnits] = useState<number | null>(null);
  
  // Update hero price when quote changes, if user hasn't explicitly set it
  React.useEffect(() => {
    if (heroQuote) {
      setHeroPriceUnits(heroQuote.min_cost_units);
    }
  }, [heroQuote]);

  const displayPriceUnits = Math.max(heroPriceUnits ?? basePriceUnits, basePriceUnits);
  const note = PERIOD_NOTES[period] || '';

  const { data: stats } = useQuery({
    queryKey: ['stats'],
    queryFn: fetchPublicStats,
  });

  return (
    <section id="page-home">
      <div className="wrap">
        <div className="hero">
          <div className="periods" role="tablist" aria-label="Davrlar">
            {tabs.map((t: any) => (
              <button 
                key={t.period_type} 
                className="ptab" 
                aria-selected={period === t.period_type ? "true" : "false"}
                onClick={() => { setPeriod(t.period_type); setPage(1); }}
              >
                {t.period_type === 'daily' && <span className="dot" />}
                {PERIOD_NAMES[t.period_type] || t.period_type}
              </button>
            ))}
            {tabs.length === 0 && (
              <button className="ptab" aria-selected="true"><span className="dot" />Barcha vaqt</button>
            )}
          </div>
          
          <div className="catbar" id="catbar" style={{ display: 'flex', gap: '8px', overflowX: 'auto', paddingBottom: '16px' }}>
            <button 
              className="cpill" 
              aria-pressed={cat === 'all' ? "true" : "false"}
              onClick={() => { setCat('all'); setPage(1); }}
            >
              <span className="sq" style={{ '--c': 'var(--ink-3)' } as any} />Hammasi
            </button>
            {categories.map((c: any) => (
              <button 
                key={c.slug}
                className="cpill" 
                aria-pressed={cat === c.slug ? "true" : "false"}
                onClick={() => { setCat(cat === c.slug ? 'all' : c.slug); setPage(1); }}
              >
                <span className="sq" style={{ '--c': c.color } as any} />{c.name_uz} <span className="num">{c.listing_count}</span>
              </button>
            ))}
          </div>

          <p className="period-note">{note}</p>
          <h1 className="claim">
            <span>{period === 'daily' ? "Bugungi 1-o'rinni" : "1-o'rinni"}</span>
            <button className="step" aria-label="Narxni kamaytirish" 
              disabled={displayPriceUnits <= basePriceUnits}
              onClick={() => setHeroPriceUnits(displayPriceUnits - 1000)}
            >−</button>
            <span className="price-big"><span className="num">{formatB(displayPriceUnits)}</span> B</span>
            <button className="step" aria-label="Narxni oshirish"
              onClick={() => setHeroPriceUnits(displayPriceUnits + 1000)}
            >+</button>
            <span>ga oling</span>
          </h1>
          <p className="uzs">≈ <span className="num">{new Intl.NumberFormat('ru-RU').format(displayPriceUnits).replace(',', ' ')}</span> so'm · to'lov Telegram Stars yoki Paynet orqali</p>
          
          <div className="claimbar">
            <label className="field">
              <svg viewBox="0 0 24 24"><path d="M21 4 3 11l6 2.5L11.5 20 21 4Z"/></svg>
              <input id="heroHandle" placeholder="@kanal yoki t.me havolasi" aria-label="Kanal manzili" />
            </label>
            <select className="field" id="heroCat" aria-label="Kategoriya">
              <option value="">Kategoriyani tanlang</option>
              {categories.map((c: any) => (
                <option key={c.slug} value={c.slug}>{c.name_uz}</option>
              ))}
            </select>
            <button className="btn-primary" id="heroClaim">O'rinni olish</button>
          </div>
          <p style={{ margin: '14px 0 0', fontSize: '13.5px', color: 'var(--ink-3)' }}>
            Kanalingiz hali ro'yxatda yo'qmi? <a href="/qoshish" style={{ color: 'var(--lime-text)', fontWeight: 600 }}>Avval kanalni qo'shing →</a>
          </p>
        </div>

        <div className="board">
          <div>
            <div id="list">
              {isLoading && <p>Yuklanmoqda...</p>}
              {!isLoading && entries.length === 0 && (
                <div className="empty">
                  <div className="rungs"><i /><i /><i /></div>
                  <h3>Bu yerda hali hech kim yo'q</h3>
                  <p>{search ? 'Qidiruv bo\'yicha kanal topilmadi.' : (cat === "all" ? 'Bu davrda birorta ham faol kanal yo\'q.' : 'Bu kategoriya hozircha bo\'sh. Birinchi bo\'ling.')}</p>
                  <button className="btn-primary" onClick={() => {}}>1-o'rinni 1 B ga olish</button>
                </div>
              )}
              {!isLoading && entries.length > 0 && entries.map((entry: any, i: number) => {
                const mappedItem = {
                  rank: entry.rank,
                  price: entry.paid_b,
                  priceUnits: entry.paid_units,
                  ch: {
                    n: entry.listing.name,
                    h: entry.listing.handle,
                    d: entry.listing.description,
                    c: entry.listing.category_slug,
                    g: [entry.listing.gradient_start, entry.listing.gradient_end],
                    v: entry.listing.verified,
                    s: entry.listing.subscribers,
                    k: entry.listing.clickthroughs,
                    t: new Date(entry.listing.created_at).toLocaleDateString('ru-RU'),
                    free: entry.listing.free_label,
                    category: categoryMap[entry.listing.category_slug] || { name: entry.listing.category_slug, color: entry.listing.category_color }
                  }
                };

                return (
                  <React.Fragment key={entry.listing.slug}>
                    <ListingRow item={mappedItem} onClaim={() => {}} />
                    {entry.rank === 10 && i < entries.length - 1 && (
                      <div className="divider"><span>TOP 10</span></div>
                    )}
                  </React.Fragment>
                );
              })}
            </div>
            {boardPage && boardPage.total_pages > 1 && (
              <div className="pager" id="pager">
                <button 
                  className="pg-btn" 
                  disabled={page === 1} 
                  onClick={() => setPage(page - 1)}
                >‹</button>
                <div className="pg-nums">
                  <button className="pg-btn" aria-current="page">{page}</button>
                </div>
                <button 
                  className="pg-btn" 
                  disabled={page === boardPage.total_pages}
                  onClick={() => setPage(page + 1)}
                >›</button>
              </div>
            )}
            {boardPage && (
              <p className="pg-info" id="pagerInfo">
                {((page - 1) * boardPage.page_size) + 1}–{Math.min(boardPage.total, page * boardPage.page_size)} / jami {boardPage.total} kanal
              </p>
            )}
          </div>

          <aside className="side">
            <div className="card">
              <div className="card-h" id="sideTitle">Bugungi reyting <a href="/kunlik">Hammasi →</a></div>
              <div id="sideList">
                {sideDailyBoard?.entries?.slice(0, 5).map((entry: any) => {
                  const mappedItem = {
                    rank: entry.rank,
                    price: entry.paid_b,
                    ch: {
                      n: entry.listing.name,
                      g: [entry.listing.gradient_start, entry.listing.gradient_end],
                    }
                  };
                  return <MiniListing key={entry.listing.slug} item={mappedItem} />;
                })}
              </div>
            </div>
            <div className="card wallet">
              <div className="card-h">Hamyon</div>
              <p style={{ marginTop: '8px', fontSize: '14px', color: 'var(--ink-2)' }}>O'rin sotib olish uchun tizimga kiring.</p>
              <button className="btn-ghost" style={{ width: '100%', marginTop: '12px' }}>Kirish</button>
            </div>
            <div className="card">
              <div className="card-h">Qanday ishlaydi</div>
              <p style={{ margin: 0, fontSize: '13.5px', color: 'var(--ink-2)' }}>
                Har bir o'rinning narxi bor. <b style={{ color: 'var(--ink)' }}>k</b>-o'rinni olish uchun shu o'rindagi kanaldan <b style={{ color: 'var(--ink)' }}>1 B</b> ko'p to'laysiz. Ular bir pog'ona pastga tushadi. <a href="/qoidalar" style={{ color: 'var(--lime-text)' }}>Qoidalar →</a>
              </p>
            </div>
          </aside>
        </div>

        <section className="stats">
          <h2>Rung statistikasi:</h2>
          <div className="stat-grid">
            <div className="stat"><div className="v num">{stats?.visits_today ?? 0}</div><div className="k">tashrif (tekshirilgan, botlarsiz)</div></div>
            <div className="stat accent"><div className="v num">{stats ? formatB(stats.total_paid_units) : '0'} B</div><div className="k">o'rinlar uchun to'langan</div></div>
            <div className="stat"><div className="v num">{stats?.total_listings ?? 0}</div><div className="k">ro'yxatdagi kanal</div></div>
          </div>
        </section>
      </div>
    </section>
  );
}
