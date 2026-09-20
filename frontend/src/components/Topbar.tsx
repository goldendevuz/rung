import React from 'react';
import { Link } from 'react-router-dom';

export function Topbar() {
  const [searchOpen, setSearchOpen] = React.useState(false);
  const [theme, setTheme] = React.useState(() => localStorage.getItem('theme') || 'dark');

  const toggleTheme = () => {
    const next = theme === 'dark' ? 'light' : 'dark';
    setTheme(next);
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
  };

  React.useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  // TODO: Use real API data for stats
  const showLiveStats = import.meta.env.VITE_SHOW_LIVE_STATS === 'true'; 

  return (
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
              <b className="num">37</b> onlayn{' '}
              <span className="hide-xs">· bugun <b className="num">2 145</b> tashrif · statistika →</span>
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
            <Link to="/kirish"><button className="btn-login">Kirish</button></Link>
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
  );
}
