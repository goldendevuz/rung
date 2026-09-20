import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchPublicStats } from '../api/client';
import { nf } from '../utils/formatters';

export function About() {
  const { data: stats } = useQuery({
    queryKey: ['stats', 'public'],
    queryFn: fetchPublicStats
  });

  return (
    <section id="page-haqida">
      <div className="wrap">
        <div className="page-head">
          <h1>Rung nima?</h1>
          <p>Reklama beruvchi o'zbek Telegram kanallarini bir joyda ko'radi. Kanal egasi esa yuqoriga chiqish uchun to'laydi — reyting shu tariqa ochiq auksiyonga aylanadi.</p>
        </div>
        <div className="prose" style={{ paddingTop: '8px' }}>
          <h2>Nega bu ishlaydi</h2>
          <p>Oddiy katalogda kim yuqorida turishini admin hal qiladi. Rung'da buni bozor hal qiladi: kim ko'proq to'lasa, o'sha yuqorida. Narx ochiq ko'rinadi, ya'ni reklama beruvchi kanal o'ziga qanchalik ishonishini darrov ko'radi.</p>
          <p>Har bir pulli o'rin <strong>"Reklama"</strong> deb belgilanadi va to'langan summa yashirilmaydi. Soxta bid yoki o'zini-o'zi ko'tarish taqiqlanadi.</p>

          <h2>Raqamlar</h2>
        </div>
        <div className="stat-grid" style={{ marginBottom: '34px' }}>
          <div className="stat"><div className="v num">{stats ? nf(stats.total_clickthroughs) : 0}</div><div className="k">tashrif</div></div>
          <div className="stat accent"><div className="v num">{stats ? nf(stats.total_paid_units/1000) : 0} B</div><div className="k">to'langan</div></div>
          <div className="stat"><div className="v num">{stats ? nf(stats.highest_price/1000) : 0} B</div><div className="k">eng yuqori o'rin narxi</div></div>
          <div className="stat"><div className="v num">{stats ? nf(stats.total_listings) : 0}</div><div className="k">kanal ro'yxatda</div></div>
        </div>
      </div>
    </section>
  );
}
