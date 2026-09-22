import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link, useNavigate } from 'react-router-dom';
import { fetchTabs, fetchBoard, fetchCategories, fetchQuote, fetchPublicStats, fetchPublicConfig, fetchMyListings, claimRank } from '../api/client';
import { formatB, formatDateSafe } from '../utils/formatters';
import { ListingRow, MiniListing, EmptyRankSlot } from '../components/ListingRow';
import { useAuth } from '../contexts/AuthContext';

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

const LAUNCH_DATE = new Date('2026-09-21T00:00:00+05:00');

export function Home() {
  const navigate = useNavigate();
  const { user, mutate: refreshUser } = useAuth();
  const queryClient = useQueryClient();

  const [period, setPeriod] = useState<string>('all_time');
  const [cat, setCat] = useState<string>('all');
  const [search] = useState<string>('');
  const [page, setPage] = useState<number>(1);

  // Claim modal state
  const [claimModalOpen, setClaimModalOpen] = useState(false);
  const [claimTargetRank, setClaimTargetRank] = useState(1);
  const [selectedListingId, setSelectedListingId] = useState<string>('');

  const { data: tabs = [] } = useQuery({
    queryKey: ['tabs'],
    queryFn: fetchTabs
  });

  const { data: categories = [] } = useQuery({
    queryKey: ['categories'],
    queryFn: fetchCategories
  });

  const { data: myListings = [] } = useQuery({
    queryKey: ['my-listings'],
    queryFn: fetchMyListings,
    enabled: !!user
  });

  // Set default selected listing
  React.useEffect(() => {
    if (myListings && myListings.length > 0 && !selectedListingId) {
      setSelectedListingId(myListings[0].id);
    }
  }, [myListings, selectedListingId]);

  const categoryMap = React.useMemo(() => {
    return categories.reduce((acc: any, c: any) => {
      acc[c.slug] = { n: c.name_uz, c: c.color, i: c.icon };
      return acc;
    }, {});
  }, [categories]);

  const { data: boardPage, isLoading } = useQuery({
    queryKey: ['board', period, page, cat === 'all' ? undefined : cat, search],
    queryFn: () => fetchBoard(period, page, cat === 'all' ? undefined : cat, search),
    retry: false,
  });

  const { data: heroQuote } = useQuery({
    queryKey: ['quote', boardPage?.board_id, 1],
    queryFn: () => fetchQuote(boardPage!.board_id, 1),
    enabled: !!boardPage?.board_id && boardPage?.board_id !== '00000000-0000-0000-0000-000000000000',
  });

  const { data: sideDailyBoard } = useQuery({
    queryKey: ['board', 'daily', 1, undefined, undefined],
    queryFn: () => fetchBoard('daily', 1),
    retry: false,
  });

  const entries = boardPage?.entries || [];
  const basePriceUnits = heroQuote ? heroQuote.min_cost_units : 1000;

  const [heroPriceUnits, setHeroPriceUnits] = useState<number | null>(null);
  
  React.useEffect(() => {
    if (heroQuote) {
      setHeroPriceUnits(heroQuote.min_cost_units);
    }
  }, [heroQuote]);

  const displayPriceUnits = Math.max(heroPriceUnits ?? basePriceUnits, basePriceUnits);
  const note = PERIOD_NOTES[period] || '';

  const { data: publicConfig } = useQuery({
    queryKey: ['public-config'],
    queryFn: fetchPublicConfig,
    staleTime: 5 * 60 * 1000,
  });

  const { data: stats } = useQuery({
    queryKey: ['stats'],
    queryFn: fetchPublicStats,
  });

  // Claim mutation
  const claimMutation = useMutation({
    mutationFn: claimRank,
    onSuccess: (data: any) => {
      queryClient.invalidateQueries({ queryKey: ['board'] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
      queryClient.invalidateQueries({ queryKey: ['tabs'] });
      refreshUser();
      alert(data.message || "Muvaffaqiyatli! Kanalingiz reytingda joylashtirildi!");
      setClaimModalOpen(false);
    },
    onError: (err: Error) => {
      alert(err.message || "Xatolik yuz berdi");
    }
  });

  const handleOpenClaim = (targetRank: number = 1) => {
    if (!user) {
      navigate('/kirish');
      return;
    }
    if (!myListings || myListings.length === 0) {
      alert("Reytingda o'rin olish uchun avval profilingizda kanal qo'shishingiz kerak.");
      navigate('/profil');
      return;
    }
    setClaimTargetRank(targetRank);
    setClaimModalOpen(true);
  };

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
          <p className="uzs">≈ <span className="num">{new Intl.NumberFormat('ru-RU').format(displayPriceUnits).replace(',', ' ')}</span> so'm · {publicConfig?.payment_provider_text || "to'lov: Karta, Click, Payme, Paynet, Alif, AnorBank, Visa/MC"}</p>
          
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
            <button className="btn-primary" id="heroClaim" onClick={() => handleOpenClaim(1)}>O'rinni olish</button>
          </div>
          <p style={{ margin: '14px 0 0', fontSize: '13.5px', color: 'var(--ink-3)' }}>
            Kanalingiz hali ro'yxatda yo'qmi? <Link to="/profil" style={{ color: 'var(--lime-text)', fontWeight: 600 }}>Avval kanalni qo'shing →</Link>
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
                  <button className="btn-primary" onClick={() => handleOpenClaim(1)}>1-o'rinni 1 B ga olish</button>
                </div>
              )}
              {!isLoading && entries.length > 0 && entries.map((entry: any) => {
                const mappedItem = {
                  rank: entry.rank,
                  price: entry.paid_b,
                  priceUnits: entry.paid_units,
                  ch: {
                    id: entry.listing.id,
                    n: entry.listing.name,
                    h: entry.listing.handle,
                    d: entry.listing.description,
                    c: entry.listing.category_slug,
                    g: [entry.listing.gradient_start, entry.listing.gradient_end],
                    v: entry.listing.verified,
                    s: entry.listing.subscribers,
                    k: entry.listing.clickthroughs,
                    t: formatDateSafe(entry.listing.created_at || entry.entered_at),
                    free: entry.listing.free_label,
                    logo_url: entry.listing.logo_url,
                    category: categoryMap[entry.listing.category_slug] || { name: entry.listing.category_slug, color: entry.listing.category_color }
                  }
                };

                return (
                  <React.Fragment key={entry.listing.id}>
                    <ListingRow item={mappedItem} onClaim={() => handleOpenClaim(entry.rank)} />
                    {entry.rank === 10 && (
                      <div className="divider"><span>TOP 10</span></div>
                    )}
                  </React.Fragment>
                );
              })}
              {page === 1 && cat === 'all' && !search && entries.length > 0 && entries.length < 10 && (
                Array.from({ length: 10 - entries.length }, (_, idx) => {
                  const emptyRank = entries.length + idx + 1;
                  return (
                    <React.Fragment key={`empty-slot-${emptyRank}`}>
                      <EmptyRankSlot 
                        rank={emptyRank} 
                        onClaim={() => handleOpenClaim(emptyRank)} 
                      />
                      {emptyRank === 10 && (
                        <div className="divider"><span>TOP 10</span></div>
                      )}
                    </React.Fragment>
                  );
                })
              )}
            </div>
            {boardPage && boardPage.total > 0 && boardPage.total_pages > 1 && (
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
            {boardPage && boardPage.total > 0 && (
              <p className="pg-info" id="pagerInfo">
                {((page - 1) * boardPage.page_size) + 1}–{Math.min(boardPage.total, page * boardPage.page_size)} / jami {boardPage.total} kanal
              </p>
            )}
          </div>

          <aside className="side">
            <div className="card">
              <div className="card-h" id="sideTitle">Bugungi reyting <Link to="/kunlik">Hammasi →</Link></div>
              <div id="sideList">
                {sideDailyBoard?.entries?.slice(0, 5).map((entry: any) => {
                  const mappedItem = {
                    rank: entry.rank,
                    price: entry.paid_b,
                    ch: {
                      id: entry.listing.id,
                      n: entry.listing.name,
                      g: [entry.listing.gradient_start, entry.listing.gradient_end],
                      logo_url: entry.listing.logo_url,
                    }
                  };
                  return <MiniListing key={entry.listing.id} item={mappedItem} />;
                })}
              </div>
            </div>

            {/* Dynamic Hamyon Card */}
            {user ? (
              <div className="card wallet">
                <div className="card-h" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span>Hamyon</span>
                  <span style={{ fontSize: '11px', color: '#B8F03C', fontWeight: '600', background: 'rgba(184, 240, 60, 0.12)', padding: '2px 8px', borderRadius: '10px', border: '1px solid rgba(184, 240, 60, 0.25)' }}>
                    ● Ulangan
                  </span>
                </div>
                <div className="bal" style={{ fontSize: '28px', fontWeight: '800', fontFamily: 'var(--mono)', color: 'var(--brand)', margin: '6px 0 2px' }}>
                  {user.balance?.toLocaleString()} B
                </div>
                <p style={{ margin: '4px 0 14px', fontSize: '12.5px', color: 'var(--ink-3)' }}>
                  Reytingda o'rin sotib olish uchun mavjud balansingiz.
                </p>
                <Link to="/profil" className="btn-ghost" style={{ width: '100%', display: 'block', textAlign: 'center', textDecoration: 'none', padding: '8px 0', fontSize: '13.5px', borderRadius: '10px' }}>
                  Profilga o'tish →
                </Link>
              </div>
            ) : (
              <div className="card wallet">
                <div className="card-h">Hamyon</div>
                <p style={{ marginTop: '8px', fontSize: '14px', color: 'var(--ink-2)' }}>O'rin sotib olish uchun tizimga kiring.</p>
                <Link to="/kirish"><button className="btn-ghost" style={{ width: '100%', marginTop: '12px' }}>Kirish</button></Link>
              </div>
            )}

            <div className="card">
              <div className="card-h">Qanday ishlaydi</div>
              <p style={{ margin: 0, fontSize: '13.5px', color: 'var(--ink-2)' }}>
                Har bir o'rinning narxi bor. <b style={{ color: 'var(--ink)' }}>k</b>-o'rinni olish uchun shu o'rindagi kanaldan <b style={{ color: 'var(--ink)' }}>1 B</b> ko'p to'laysiz. Ular bir pog'ona pastga tushadi. <Link to="/qoidalar" style={{ color: 'var(--lime-text)' }}>Qoidalar →</Link>
              </p>
            </div>
          </aside>
        </div>

        <section className="stats">
          <h2>Rung <b>{Math.max(1, Math.floor((Date.now() - LAUNCH_DATE.getTime()) / (1000 * 60 * 60 * 24)))} kun</b> oldin ishga tushdi. O'shandan beri:</h2>
          <div className="stat-grid">
            <div className="stat"><div className="v num">{stats?.visits_today ?? 0}</div><div className="k">tashrif (tekshirilgan, botlarsiz)</div></div>
            <div className="stat accent"><div className="v num">{stats ? formatB(stats.total_paid_units) : '0'} B</div><div className="k">o'rinlar uchun to'langan</div></div>
            <div className="stat"><div className="v num">{stats?.total_listings ?? 0}</div><div className="k">ro'yxatdagi kanal</div></div>
          </div>
        </section>
      </div>

      {/* Claim Modal */}
      {claimModalOpen && (
        <div 
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-md"
          onClick={(e) => { if (e.target === e.currentTarget) setClaimModalOpen(false); }}
        >
          <div className="w-full max-w-md bg-[#12151A] border border-white/10 rounded-2xl p-6 sm:p-7 shadow-2xl relative">
            <button 
              onClick={() => setClaimModalOpen(false)}
              className="absolute top-4 right-4 w-8 h-8 rounded-full flex items-center justify-center text-white/50 hover:text-white hover:bg-white/10 transition-colors"
            >
              ✕
            </button>

            <div className="flex items-center gap-2 mb-2">
              <span className="text-xl">🚀</span>
              <h2 className="text-xl font-bold text-white">#{claimTargetRank}-o'rinni olish</h2>
            </div>
            <p className="text-sm text-white/60 mb-5">
              Kanalingizni ushbu davrda #{claimTargetRank}-o'ringa chiqarish uchun tasdiqlang.
            </p>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-white/60 mb-2">
                  Kanalni tanlang
                </label>
                <select 
                  value={selectedListingId || myListings[0]?.id}
                  onChange={(e) => setSelectedListingId(e.target.value)}
                  className="w-full bg-[#181B20] border border-white/10 rounded-xl px-4 py-3 text-sm text-white outline-none focus:border-[#B8F03C]"
                  style={{ color: '#fff', backgroundColor: '#181B20' }}
                >
                  {myListings.map((l: any) => (
                    <option key={l.id} value={l.id} style={{ color: '#fff', backgroundColor: '#181B20' }}>
                      {l.name} ({l.handle})
                    </option>
                  ))}
                </select>
              </div>

              <div className="p-4 rounded-xl bg-white/[0.03] border border-white/10 space-y-2.5">
                <div className="flex justify-between text-sm">
                  <span className="text-white/60">Tanlangan o'rin:</span>
                  <span className="font-bold text-white">#{claimTargetRank}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-white/60">Narxi:</span>
                  <span className="font-bold text-[#B8F03C]">1 B</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-white/60">Joriy balansingiz:</span>
                  <span className="font-medium text-white">{user?.balance?.toLocaleString()} B</span>
                </div>
                <div className="flex justify-between text-sm pt-2.5 border-t border-white/10">
                  <span className="text-white/60">To'lovdan keyin:</span>
                  <span className="font-bold text-white">{((user?.balance ?? 0) - 1).toLocaleString()} B</span>
                </div>
              </div>

              <div className="pt-2 flex gap-3">
                <button 
                  type="button"
                  onClick={() => setClaimModalOpen(false)}
                  className="flex-1 py-3 px-4 rounded-xl border border-white/10 text-white/80 hover:text-white hover:bg-white/5 font-semibold text-sm transition-all"
                >
                  Bekor qilish
                </button>
                <button 
                  type="button"
                  disabled={claimMutation.isPending || (user?.balance ?? 0) < 1}
                  onClick={() => {
                    const listingId = selectedListingId || myListings[0]?.id;
                    if (!listingId) return;
                    claimMutation.mutate({
                      listing_id: listingId,
                      period_type: period,
                      target_rank: claimTargetRank,
                      paid_b: 1
                    });
                  }}
                  className="flex-1 py-3 px-4 rounded-xl bg-[#B8F03C] hover:bg-[#c6fa4d] text-[#0D0F11] font-bold text-sm transition-all disabled:opacity-50"
                >
                  {claimMutation.isPending ? 'To\'lanmoqda...' : '1 B to\'lash'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
