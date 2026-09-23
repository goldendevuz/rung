import React from 'react';
import { createPortal } from 'react-dom';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { fetchPublicStats, fetchVisitorsStats } from '../api/client';
import { useAuth } from '../contexts/AuthContext';

function UserAvatar({ photoUrl, name }: { photoUrl?: string | null; name?: string | null }) {
  const [error, setError] = React.useState(false);
  const initial = (name || '?')[0].toUpperCase();

  if (photoUrl && !error) {
    return (
      <img 
        src={photoUrl} 
        alt="Avatar" 
        onError={() => setError(true)}
        style={{ width: 32, height: 32, borderRadius: '50%', objectFit: 'cover' }} 
      />
    );
  }

  return (
    <div 
      style={{ 
        width: 32, 
        height: 32, 
        borderRadius: '50%', 
        background: 'linear-gradient(135deg, #B8F03C, #059669)', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center', 
        fontSize: '13px', 
        fontWeight: 'bold', 
        color: '#0D0F11' 
      }}
    >
      {initial}
    </div>
  );
}

export function Topbar() {
  const [searchOpen, setSearchOpen] = React.useState(false);
  const [mobileNavOpen, setMobileNavOpen] = React.useState(false);
  const [theme, setTheme] = React.useState(() => localStorage.getItem('theme') || 'dark');
  const { user } = useAuth();

  const toggleTheme = () => {
    const next = theme === 'dark' ? 'light' : 'dark';
    setTheme(next);
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
  };

  React.useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const { data: stats } = useQuery({
    queryKey: ['stats'],
    queryFn: fetchPublicStats,
    refetchInterval: 30000,
  });

  const { data: visitorsStats } = useQuery({
    queryKey: ['visitors-stats'],
    queryFn: fetchVisitorsStats,
    refetchInterval: 60000,
    retry: false,
  });

  const showLiveStats = stats?.online_now != null;
  const visitorsCount = (visitorsStats?.configured && visitorsStats.visitors_today != null)
    ? visitorsStats.visitors_today
    : (stats?.visits_today || 1);
  const visitorsLabel = 'bugun';


  return (
    <header className="topbar">
      <div className="wrap">
        <div className="topbar-in">
          <Link className="brand" to="/">
            <span className="brand-mark"><i /><i /><i /></span>
            rung
          </Link>
          {showLiveStats && (
            <a
              href="https://datafa.st/share/6ab279beba28fc830cd8714b"
              target="_blank"
              rel="noopener noreferrer"
              className="live"
              title="Jonli statistikani ko'rish (DataFast)"
              style={{ textDecoration: 'none' }}
            >
              <span className="dot" />
              <b className="num">{stats.online_now || 1}</b> onlayn{' '}
              <span className="hide-xs">
                · {visitorsLabel} <b className="num">{new Intl.NumberFormat('uz-UZ').format(visitorsCount).replace(',', ' ')}</b> tashrif · <span className="stat-arrow" style={{ textDecoration: 'underline' }}>statistika →</span>
              </span>
            </a>
          )}
          <nav className="topnav">
            <Link to="/kunlik" className="hide-sm">Kunlik</Link>
            <Link to="/kategoriyalar" className="hide-sm">Kategoriyalar</Link>
            <Link to="/haqida" className="hide-sm">Haqida</Link>
            <Link to="/qoidalar" className="hide-sm">Qoidalar</Link>
            <button className="icon-btn" onClick={() => setSearchOpen(!searchOpen)} aria-label="Qidirish">
              <svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="6.5" /><path d="m16 16 4.5 4.5" /></svg>
            </button>
            <button className="icon-btn" onClick={toggleTheme} aria-label="Mavzuni almashtirish">
              <svg viewBox="0 0 24 24"><path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5Z" /></svg>
            </button>
            {user ? (
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <Link to="/hamyon" style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '5px 12px',
                  borderRadius: '20px',
                  background: 'rgba(184, 240, 60, 0.1)',
                  border: '1px solid rgba(184, 240, 60, 0.25)',
                  color: 'var(--brand)',
                  fontWeight: '700',
                  fontSize: '13px',
                  textDecoration: 'none',
                  fontFamily: 'var(--mono)'
                }} title="Hamyonni to'ldirish">
                  <span>{user.balance?.toLocaleString() ?? 0} B</span>
                  <span style={{ fontSize: '11px', opacity: 0.8 }}>+</span>
                </Link>
                <Link to="/profil" style={{ display: 'flex', alignItems: 'center', gap: '8px', textDecoration: 'none', color: 'var(--fg)', fontWeight: '500' }} className="user-profile-link">
                  <UserAvatar photoUrl={user.photo_url} name={user.first_name || user.username} />
                  <span className="hide-sm">{user.first_name || user.username}</span>
                </Link>
              </div>
            ) : (
              <Link to="/kirish"><button className="btn-login">Kirish</button></Link>
            )}
            <button 
              id="mobile-menu-btn"
              className="icon-btn mobile-menu-btn" 
              onClick={() => setMobileNavOpen(!mobileNavOpen)} 
              aria-label="Menyu"
              aria-expanded={mobileNavOpen}
            >
              <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round">
                {mobileNavOpen ? (
                  <path d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </nav>
        </div>
        {searchOpen && (
          <div id="searchRow" style={{ paddingBottom: '4px' }}>
            <label className="field" style={{ maxWidth: '520px', minHeight: '44px' }}>
              <svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="6.5" /><path d="m16 16 4.5 4.5" /></svg>
              <input id="searchInput" placeholder="Kanal nomi yoki @manzili" aria-label="Kanallar orasidan qidirish" autoFocus />
            </label>
          </div>
        )}
      </div>

      {mobileNavOpen && typeof document !== 'undefined' && createPortal(
        <div className="mobile-drawer-backdrop" onClick={() => setMobileNavOpen(false)}>
          <div className="mobile-drawer" onClick={(e) => e.stopPropagation()}>
            <div className="mobile-drawer-head">
              <div className="brand" style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 800, fontSize: '18px' }}>
                <span className="brand-mark"><i /><i /><i /></span>
                rung
              </div>
              <button 
                className="icon-btn" 
                onClick={() => setMobileNavOpen(false)} 
                aria-label="Yopish"
                style={{ fontSize: '18px', width: '36px', height: '36px' }}
              >
                ✕
              </button>
            </div>
            <nav className="mobile-drawer-nav">
              <Link to="/" onClick={() => setMobileNavOpen(false)} className="mobile-nav-link">
                <span>🏆</span> Top reyting
              </Link>
              <Link to="/kunlik" onClick={() => setMobileNavOpen(false)} className="mobile-nav-link">
                <span>⚡</span> Kunlik
              </Link>
              <Link to="/kategoriyalar" onClick={() => setMobileNavOpen(false)} className="mobile-nav-link">
                <span>🏷️</span> Kategoriyalar
              </Link>
              <Link to="/qoshish" onClick={() => setMobileNavOpen(false)} className="mobile-nav-link" style={{ color: 'var(--lime-text)', fontWeight: 700 }}>
                <span>➕</span> Kanal qo'shish
              </Link>
              <Link to="/haqida" onClick={() => setMobileNavOpen(false)} className="mobile-nav-link">
                <span>💡</span> Haqida
              </Link>
              <Link to="/qoidalar" onClick={() => setMobileNavOpen(false)} className="mobile-nav-link">
                <span>📜</span> Qoidalar
              </Link>
              <Link to="/statistika" onClick={() => setMobileNavOpen(false)} className="mobile-nav-link">
                <span>📊</span> Jonli statistika
              </Link>
              {user ? (
                <>
                  <div style={{ height: '1px', background: 'var(--line)', margin: '8px 0' }} />
                  <Link to="/hamyon" onClick={() => setMobileNavOpen(false)} className="mobile-nav-link">
                    <span>💳</span> Hamyon: <strong style={{ color: 'var(--brand)', marginLeft: '4px' }}>{user.balance?.toLocaleString()} B</strong>
                  </Link>
                  <Link to="/profil" onClick={() => setMobileNavOpen(false)} className="mobile-nav-link">
                    <span>👤</span> Profil: <strong style={{ marginLeft: '4px' }}>{user.first_name || user.username}</strong>
                  </Link>
                </>
              ) : (
                <>
                  <div style={{ height: '1px', background: 'var(--line)', margin: '8px 0' }} />
                  <Link to="/kirish" onClick={() => setMobileNavOpen(false)} className="mobile-nav-link btn-primary" style={{ textAlign: 'center', justifyContent: 'center', padding: '10px 16px', borderRadius: '12px' }}>
                    Kirish
                  </Link>
                </>
              )}
            </nav>
          </div>
        </div>,
        document.body
      )}
    </header>
  );
}
