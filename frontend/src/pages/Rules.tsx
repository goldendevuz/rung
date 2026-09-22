

export function Rules() {
  return (
    <section id="page-qoidalar">
      <div className="wrap prose">
        <div className="page-head" style={{ paddingBottom: 0 }}>
          <h1>Qoidalar</h1>
          <p>Qisqa va ochiq. Savol qolsa — <a href="https://t.me/rung_uz_bot" style={{ color: 'var(--lime-text)' }}>@rung_uz_bot</a>.</p>
        </div>

        <h2>Taxtalar</h2>
        <p>Har bir davr — alohida bozor: <strong>butun davr</strong>, <strong>kunlik</strong>, <strong>haftalik</strong>, <strong>oylik</strong>, <strong>fasl</strong> va <strong>yillik</strong>. Davr tugaganda taxta yopiladi, yangisi yana <code>1 B</code> dan boshlanadi. Avtomatik uzaytirish yoqilgan bo'lsa va hamyonda pul yetsa, kanal yangi davrga eng past narxda qayta kiradi; aks holda "Yakunlanganlar" ro'yxatiga o'tadi.</p>
        <p>Bo'sh davr ko'rsatilmaydi: faqat kamida bitta faol kanali bor taxta sarlavhada chiqadi.</p>

        <h2>Reyting qanday hisoblanadi</h2>
        <ul>
          <li>O'rin — hisoblanadigan qiymat: avval <strong>to'langan B</strong> bo'yicha, teng bo'lsa <strong>kim oldin kirgani</strong> bo'yicha.</li>
          <li>Eng past narx — <code>1 B</code>. Bidlar faqat butun B da.</li>
          <li><strong>k</strong>-o'rinni olish uchun shu o'rindagi kanal to'lagan summadan <code>1 B</code> ko'p to'laysiz.</li>
          <li>1 B = 1 000 so'm. Interfeysda faqat B ko'rsatiladi.</li>
          <li>Soxta yoki o'zini-o'zi ko'tarish uchun qilingan bidlar taqiqlanadi.</li>
        </ul>

        <h2>Nimani joylash mumkin</h2>
        <ul>
          <li>Hozircha faqat <strong>Telegram kanallari</strong>. Guruh, bot, mini-app va saytlar keyingi bosqichda.</li>
          <li>Kanal egaligi tasdiqlanishi shart: faqat <strong>tasdiqlangan</strong> egalar o'rin sotib oladi.</li>
          <li>Taqiqlangan mavzular: dori-darmon va tibbiyot, moliya/kredit/kripto, alkogol va tamaki, qimor, kattalar uchun kontent.</li>
          <li>Har bir pulli o'rin <strong>"Reklama"</strong> deb belgilanadi va to'langan B miqdori ochiq ko'rsatiladi.</li>
        </ul>

        <h2>To'lovdan keyin</h2>
        <p>O'rin to'lov tasdiqlangan zahoti ochiladi. To'lov qaytarilmaydi — istisno: xizmat nosozligi. To'lovni beta davrida admin qo'lda qaytarishi mumkin, agar kirim qilingan B hali sarflanmagan bo'lsa.</p>

        <h2 id="shartlar">Foydalanish shartlari (Oferta)</h2>
        <p>Rung platformasidan foydalanish orqali siz quyidagi qoidalarga rozilik bildirasiz:</p>
        <ul>
          <li>Foydalanuvchi o'zi qo'shayotgan Telegram kanalining qonuniy egasi yoki ishonchli vakili ekanini kafolatlaydi.</li>
          <li>O'zbekiston Respublikasi qonunlariga zid bo'lgan, firibgarlik yoki axloqsiz mazmundagi kanallar ma'muriyat tomonidan zudlik bilan chetlatiladi.</li>
          <li>Rung platformasi kanallar tomonidan e'lon qilinadigan kontent uchun javobgar emas.</li>
          <li>Taxtadagi o'rinlar ochiq kimoshdi (bidding) tamoyili asosida beriladi va belgilangan davr oxirigacha amal qiladi.</li>
        </ul>

        <h2 id="maxfiylik">Maxfiylik siyosati</h2>
        <p>Platformada xavfsizlik va shaxsiy ma'lumotlar muhofazasi quyidagicha ta'minlanadi:</p>
        <ul>
          <li>Kirishda faqat ochiq Telegram ma'lumotlari (Telegram ID, ism, rasm) olinadi.</li>
          <li>Bank kartasi rekvizitlari Rung tizimida saqlanmaydi — barcha to'lovlar litsenziyalangan to'lov tizimlari orqali amalga oshiriladi.</li>
          <li>Kanallarning tashrif va klik ma'lumotlari xavfsiz va shaffof tahlil uchun yuritiladi.</li>
        </ul>
      </div>
    </section>
  );
}
