
import { Outlet, Link } from 'react-router-dom';
import { Rail } from './Rail';
import { Topbar } from './Topbar';

export function Layout() {
  const exitPhoneMode = () => {
    document.body.classList.remove('phone-mode');
  };

  return (
    <div className="app">
      <button 
        type="button" 
        className="exit-phone-bar" 
        onClick={exitPhoneMode}
        title="Mobil ko'rinishdan chiqish"
      >
        📱 Mobil ko'rinish faol · Chiqish ✕
      </button>
      <Rail />
      <div className="viewport">
        <Topbar />
        <main id="main">
          <Outlet />
        </main>
        <footer>
          <div className="wrap">
            <div>Rung — o'zbek Telegram kanallari uchun ochiq reyting · <a href="https://t.me/rung_uz_bot" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--lime-text)' }}>@rung_uz_bot</a></div>
            <div className="flinks">
              <Link to="/qoidalar">Qoidalar</Link><span>·</span>
              <Link to="/haqida">Savol-javob</Link><span>·</span>
              <Link to="/qoidalar#shartlar">Shartlar</Link><span>·</span>
              <Link to="/qoidalar#maxfiylik">Maxfiylik</Link><span>·</span>
              <Link to="/statistika" style={{ color: 'var(--lime-text)', fontWeight: 600 }}>Jonli statistika ↗</Link>
            </div>
            <div className="slogan">BIR POG'ONA YUQORIGA</div>
          </div>
        </footer>
      </div>
    </div>
  );
}
