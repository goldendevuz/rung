
import { Outlet, Link } from 'react-router-dom';
import { Rail } from './Rail';
import { Topbar } from './Topbar';


const LAUNCH_DATE = new Date('2026-09-22');
function daysSinceLaunch(): number {
  return Math.max(0, Math.floor((Date.now() - LAUNCH_DATE.getTime()) / 86400000));
}

export function Layout() {
  const exitPhoneMode = () => {
    document.body.classList.remove('phone-mode');
  };

  return (
    <div className="app">
      {import.meta.env.DEV && (
        <button 
          type="button" 
          className="exit-phone-bar" 
          onClick={exitPhoneMode}
          title="Mobil ko'rinishdan chiqish"
        >
          📱 Mobil ko'rinish faol · Chiqish ✕
        </button>
      )}
      <Rail />
      <div className="viewport">
        <Topbar />
        <main id="main">
          <Outlet />
        </main>
        <footer>
          <div className="wrap">
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', alignItems: 'center', justifyContent: 'space-between' }}>
              <span>Rung — o'zbek Telegram kanallari uchun ochiq reyting · <a href="https://t.me/rung_uz_bot" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--lime-text)' }}>@rung_uz_bot</a></span>
              <span style={{ fontSize: '12px', color: 'var(--ink-3)' }}>{daysSinceLaunch()} kun oldin ishga tushdi</span>
            </div>
            <div className="flinks">
              <Link to="/">Top reyting</Link><span>·</span>
              <Link to="/haqida">Haqida</Link><span>·</span>
              <Link to="/qoidalar">Qoidalar</Link><span>·</span>
              <Link to="/statistika" style={{ color: 'var(--lime-text)', fontWeight: 600 }}>Jonli statistika ↗</Link>
            </div>
            <div className="slogan">BIR POG'ONA YUQORIGA</div>
          </div>
        </footer>
      </div>
    </div>
  );
}
