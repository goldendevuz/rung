import { useQuery } from '@tanstack/react-query';
import { fetchPublicStats, fetchVisitorsStats } from '../api/client';
import { nf } from '../utils/formatters';

const LAUNCH_DATE = new Date('2026-09-22');

function daysSinceLaunch(): number {
  const now = new Date();
  const diff = now.getTime() - LAUNCH_DATE.getTime();
  return Math.max(0, Math.floor(diff / (1000 * 60 * 60 * 24)));
}

export function About() {
  const { data: stats } = useQuery({
    queryKey: ['stats', 'public'],
    queryFn: fetchPublicStats
  });
  const { data: visitors } = useQuery({
    queryKey: ['stats', 'visitors'],
    queryFn: fetchVisitorsStats
  });

  // Prefer DataFast visitors_30d for the "tashrif" stat; fall back to visits_today
  const tashrifCount = visitors?.configured && visitors.visitors_30d != null
    ? visitors.visitors_30d
    : (stats?.visits_today ?? 0);

  const days = daysSinceLaunch();

  return (
    <section id="page-haqida">
      <div className="wrap">
        <div className="page-head">
          <h1>Rung nima?</h1>
          <p>Reklama beruvchi o'zbek Telegram kanallarini bir joyda ko'radi. Kanal egasi esa yuqoriga chiqish uchun to'laydi — reyting shu tariqa ochiq auksiyonga aylanadi.</p>
          {days > 0 && (
            <p style={{ fontSize: '13px', color: 'var(--ink-3)', marginTop: '6px' }}>
              {days} kun oldin ishga tushdi
            </p>
          )}
        </div>
        <div className="prose" style={{ paddingTop: '8px' }}>
          <h2>Nega bu ishlaydi</h2>
          <p>Oddiy katalogda kim yuqorida turishini admin hal qiladi. Rung'da buni bozor hal qiladi: kim ko'proq to'lasa, o'sha yuqorida. Narx ochiq ko'rinadi, ya'ni reklama beruvchi kanal o'ziga qanchalik ishonishini darrov ko'radi.</p>
          <p>Har bir pulli o'rin <strong>"Reklama"</strong> deb belgilanadi va to'langan summa yashirilmaydi. Soxta bid yoki o'zini-o'zi ko'tarish taqiqlanadi.</p>

          <h2>Raqamlar</h2>
        </div>
        <div className="stat-grid" style={{ marginBottom: '34px' }}>
          <div className="stat"><div className="v num">{nf(tashrifCount)}</div><div className="k">tashrif (30 kun)</div></div>
          <div className="stat accent"><div className="v num">{stats ? nf(stats.total_paid_units) : 0} B</div><div className="k">to'langan</div></div>
          <div className="stat"><div className="v num">{stats && stats.highest_price ? nf(Math.round(stats.highest_price / 1000)) : 0} B</div><div className="k">eng yuqori o'rin narxi</div></div>
          <div className="stat"><div className="v num">{stats ? nf(stats.total_listings) : 0}</div><div className="k">kanal ro'yxatda</div></div>
        </div>
        <div className="prose" style={{ paddingTop: 0 }}>
          <h2>Qanday ishlaydi</h2>
          <ol>
            <li>Kanalingizni ro'yxatga kiriting</li>
            <li>Hamyoningizni B tangalar bilan to'ldiring (1 B = 1 000 so'm)</li>
            <li>Istagan o'rinni oling — o'sha zahoti reytingda ko'rinasiz</li>
            <li>Reklama beruvchilar kanalingizni topadi va murojaat qiladi</li>
          </ol>
        </div>
      </div>
    </section>
  );
}
