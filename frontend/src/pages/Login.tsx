import { useQuery } from '@tanstack/react-query';
import { fetchPublicConfig } from '../api/client';

export const Login = () => {
  const { data: config } = useQuery({
    queryKey: ['public-config'],
    queryFn: fetchPublicConfig,
    staleTime: 5 * 60 * 1000,
  });

  const googleEnabled = config?.google_auth_enabled ?? false;

  return (
    <section id="page-kirish">
      <div className="wrap">
        <div className="login">
          <div className="brand">
            <span className="brand-mark">
              <i />
              <i />
              <i />
            </span>
            rung
          </div>
          <h1>Bir pog'ona yuqoriga</h1>
          <p className="sub">
            Kanal qo'shish va o'rin sotib olish uchun kiring. Bitta akkaunt — ham saytda, ham botda.
          </p>
          <button className="authbtn tg" disabled style={{ opacity: 0.5, cursor: 'not-allowed' }}>
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M21 4 3 11l5.5 2L19 6.5 10.5 15l-.3 4.3L13 16.8l4 3.2L21 4Z" />
            </svg>
            Telegram orqali davom etish (Tez orada)
          </button>
          {googleEnabled && (
            <button className="authbtn" disabled style={{ opacity: 0.5, cursor: 'not-allowed' }}>
              <svg viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" strokeWidth="1.8" />
                <path d="M12 8v8M8 12h8" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
              </svg>
              Google akkaunti bilan kirish (Tez orada)
            </button>
          )}
          <div className="or">yoki</div>
          <button className="authbtn" style={{ minHeight: '46px', fontSize: '14px', color: 'var(--ink-2)' }}>
            Botda ochish: @rung_uz_bot
          </button>
          <p className="fine">
            Davom etish orqali siz{' '}
            <a href="/qoidalar" style={{ color: 'var(--lime-text)' }}>
              qoidalar
            </a>{' '}
            va maxfiylik siyosatiga rozilik bildirasiz. Kanal egaligi alohida tasdiqlanadi.
          </p>
        </div>
      </div>
    </section>
  );
};
