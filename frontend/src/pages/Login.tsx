import { useEffect, useState, useRef } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { fetchPublicConfig } from '../api/client';
import { useAuth } from '../contexts/AuthContext';

export const Login = () => {
  const navigate = useNavigate();
  const { user, mutate } = useAuth();
  const [loadingMsg, setLoadingMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const pollTimer = useRef<number | null>(null);

  const { data: config } = useQuery({
    queryKey: ['public-config'],
    queryFn: fetchPublicConfig,
    staleTime: 5 * 60 * 1000,
  });

  const googleEnabled = config?.google_auth_enabled ?? false;

  useEffect(() => {
    if (user) {
      navigate('/');
    }
  }, [user, navigate]);

  useEffect(() => {
    // Check for Mini App initData
    const tg = (window as any).Telegram?.WebApp;
    if (tg?.initData) {
      setLoadingMsg('Telegram orqali avtomatik kirilmoqda...');
      fetch('/api/v1/auth/telegram/miniapp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ initData: tg.initData }),
      })
        .then((res) => {
          if (!res.ok) throw new Error('Avtorizatsiya xatosi');
          return res.json();
        })
        .then(() => {
          mutate();
        })
        .catch(() => {
          setErrorMsg('Telegram orqali kirishda xatolik yuz berdi.');
          setLoadingMsg('');
        });
    }
    return () => {
      if (pollTimer.current) clearInterval(pollTimer.current);
    };
  }, [mutate]);

  const handleTelegramLogin = async () => {
    try {
      setErrorMsg('');
      setLoadingMsg('Ulanilmoqda...');
      const res = await fetch('/api/v1/auth/telegram/start', { method: 'POST' });
      if (!res.ok) {
        if (res.status === 429) throw new Error("Ko'p urinishlar, birozdan so'ng qayta urinib ko'ring.");
        throw new Error('Server xatosi');
      }
      const data = await res.json();
      
      const botUrl = `https://t.me/rung_uz_bot?start=login_${data.token}`;
      window.open(botUrl, '_blank');
      
      setLoadingMsg("Telegram'da tasdiqlashingiz kutilmoqda...");
      
      pollTimer.current = window.setInterval(async () => {
        try {
          const pollRes = await fetch(`/api/v1/auth/telegram/poll?token=${data.token}`);
          if (pollRes.status === 200) {
            if (pollTimer.current) clearInterval(pollTimer.current);
            setLoadingMsg('Muvaffaqiyatli! Yo\'naltirilmoqda...');
            await mutate();
            navigate('/');
          } else if (pollRes.status === 410) {
            if (pollTimer.current) clearInterval(pollTimer.current);
            setErrorMsg("Havola muddati o'tgan.");
            setLoadingMsg('');
          }
        } catch (e) {
          // ignore network errors on polling
        }
      }, 2000);
      
    } catch (e: any) {
      setErrorMsg(e.message || 'Xatolik yuz berdi');
      setLoadingMsg('');
    }
  };

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
            Kanal qo'shish va o'rin sotib olish uchun kiring. Bitta akkaunt — ham saytda, ham botda. Bizning platformamiz orqali O Uzbekistaning eng yaxshi Telegram kanallarini topishingiz va o z kanalingizni ommalashtirishingiz mumkin. Kirish orqali siz barcha qulayliklarga ega bolasiz va yangi imkoniyatlarni kashf etasiz.
          </p>
          
          {errorMsg && <div style={{ color: 'var(--red)', marginBottom: 16, fontWeight: 'bold' }}>{errorMsg}</div>}
          {loadingMsg && <div style={{ color: 'var(--lime-text)', marginBottom: 16, fontWeight: 'bold' }}>{loadingMsg}</div>}

          <button 
            className="authbtn tg" 
            onClick={handleTelegramLogin}
            disabled={!!loadingMsg}
            style={{ opacity: loadingMsg ? 0.7 : 1, cursor: loadingMsg ? 'wait' : 'pointer' }}
          >
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M21 4 3 11l5.5 2L19 6.5 10.5 15l-.3 4.3L13 16.8l4 3.2L21 4Z" />
            </svg>
            Telegram orqali davom etish
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
          <button className="authbtn" style={{ minHeight: '46px', fontSize: '14px', color: 'var(--ink-2)' }} onClick={() => window.open('https://t.me/rung_uz_bot', '_blank')}>
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
