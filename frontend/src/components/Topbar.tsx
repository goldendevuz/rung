import React from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { fetchPublicStats, fetchPublicConfig } from '../api/client';
import { useAuth } from '../contexts/AuthContext';

export function Topbar() {
  const [searchOpen, setSearchOpen] = React.useState(false);
  const [theme, setTheme] = React.useState(() => localStorage.getItem('theme') || 'dark');
  const { user, logout } = useAuth();

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
    queryFn: fetchPublicStats
  });

  const showLiveStats = import.meta.env.VITE_SHOW_LIVE_STATS === 'true' && stats?.online_now != null;
  const { data: publicConfig } = useQuery({
    queryKey: ['public-config'],
    queryFn: fetchPublicConfig,
    staleTime: 5 * 60 * 1000,
  });
  const showDemoBtn = publicConfig ? publicConfig.show_demo_button : true;
  const isDemo = typeof window !== 'undefined' && localStorage.getItem('rung_demo') === '1';

  const enableDemo = () => {
    localStorage.setItem('rung_demo', '1');
    window.location.reload();
  };
  const disableDemo = () => {
    localStorage.removeItem('rung_demo');
    window.location.reload();
  };

  return (
    <>
    {isDemo && (
      <div style={{ background: '#f59e0b', color: '#000', padding: '8px', textAlign: 'center', fontWeight: 'bold' }}>
        Demo ma'lumotlar, haqiqiy emas
        <button onClick={disableDemo} style={{ marginLeft: '16px', padding: '4px 8px', border: '1px solid #000', borderRadius: '4px', background: 'transparent', cursor: 'pointer', fontWeight: 'bold' }}>Chiqish</button>
      </div>
    )}
    <header className="topbar">
      <div className="wrap">
        <div className="topbar-in">
          <Link className="brand" to="/">
            <span className="brand-mark"><i /><i /><i /></span>
            rung
          </Link>
          {showLiveStats && (
            <span className="live">
              <span className="dot" />
              <b className="num">{stats.online_now || 0}</b> onlayn{' '}
              <span className="hide-xs">· bugun <b className="num">{new Intl.NumberFormat('ru-RU').format(stats.visits_today || 0).replace(',', ' ')}</b> tashrif · statistika →</span>
            </span>
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
            {showDemoBtn && !isDemo && (
              <button onClick={enableDemo} style={{ padding: '4px 12px', background: '#f59e0b', color: '#000', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>Demo</button>
            )}
            {user ? (
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                {user.photo_url && <img src={user.photo_url} alt="Avatar" style={{ width: 28, height: 28, borderRadius: '50%' }} />}
                <span className="hide-sm" style={{ fontWeight: '500' }}>{user.first_name || user.username}</span>
                <button className="btn-login" onClick={logout} style={{ marginLeft: 8 }}>Chiqish</button>
              </div>
            ) : (
              <Link to="/kirish"><button className="btn-login">Kirish</button></Link>
            )}
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
        {/* Category bar will be rendered conditionally in the Category page or Search */}
      </div>
    </header>
    </>
  );
}
