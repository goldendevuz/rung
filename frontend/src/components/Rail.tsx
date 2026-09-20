
import { NavLink } from 'react-router-dom';

export function Rail() {
  return (
    <aside className="rail" aria-label="Asosiy menyu">
      <a className="rail-mark" href="/" aria-label="Rung — bosh sahifa">
        <i /><i /><i />
      </a>
      <nav className="rail-nav" id="railNav">
        <NavLink to="/" className="rung" end>top</NavLink>
        <NavLink to="/kunlik" className="rung">kun</NavLink>
        <NavLink to="/kategoriyalar" className="rung">kat</NavLink>
        <NavLink to="/qoshish" className="rung">+kanal</NavLink>
        <NavLink to="/haqida" className="rung">haq</NavLink>
        <NavLink to="/qoidalar" className="rung">qoi</NavLink>
      </nav>
      <div className="rail-foot">
        <button className="icon-btn" id="phoneBtn" title="Mobil ko'rinish" aria-label="Mobil ko'rinish">
          <svg viewBox="0 0 24 24">
            <rect x="7" y="2.5" width="10" height="19" rx="2.5" />
            <path d="M11 18.5h2" />
          </svg>
        </button>
        <div className="rail-b">1 B = 1 000 so'm</div>
      </div>
    </aside>
  );
}
