export const AddChannel = () => {
  return (
    <section id="page-qoshish">
      <div className="wrap">
        <div className="page-head">
          <h1>Kanal qo'shish</h1>
          <p>
            Avval kanal ro'yxatga tushadi, keyin egaligi tasdiqlanadi. Faqat
            tasdiqlangan egalar o'rin sotib oladi.
          </p>
        </div>
        <div className="board" style={{ paddingTop: '22px' }}>
          <div className="card">
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <p className="lbl">Kanal manzili</p>
                <input
                  className="inp"
                  id="aHandle"
                  placeholder="@kanal yoki https://t.me/kanal"
                />
              </div>
              <div>
                <p className="lbl">Ko'rinadigan nom</p>
                <input
                  className="inp"
                  id="aName"
                  placeholder="Masalan: Kodlash.uz"
                />
              </div>
              <div>
                <p className="lbl">Bir qatorli tavsif</p>
                <input
                  className="inp"
                  id="aDesc"
                  maxLength={90}
                  placeholder="Reklama beruvchi nimani ko'radi (90 belgigacha)"
                />
              </div>
              <div>
                <p className="lbl">Kategoriya</p>
                <select className="inp" id="aCat" style={{ cursor: 'pointer' }}></select>
              </div>
              <div>
                <p className="lbl">Egalikni tasdiqlash</p>
                <div className="breakdown" style={{ gap: '10px' }}>
                  <div className="li">
                    <span>1. Botni kanalga admin qiling</span>
                    <b className="num">@rung_uz_bot</b>
                  </div>
                  <div className="li">
                    <span>2. Kod postini joylang</span>
                    <b className="num">RUNG-4F2A</b>
                  </div>
                  <div className="li">
                    <span>3. Bot tekshiradi</span>
                    <b style={{ color: 'var(--lime-text)' }}>~1 daqiqa</b>
                  </div>
                </div>
              </div>
              <div className="notice">
                <span>⌁</span>
                <span>
                  Taqiqlangan mavzular: tibbiyot va dori, moliya/kredit/kripto,
                  alkogol va tamaki, qimor, kattalar uchun kontent.{' '}
                  <b>Har bir pulli o'rin "Reklama" deb belgilanadi.</b>
                </span>
              </div>
              <button
                className="btn-primary"
                id="aGo"
                style={{ width: '100%', opacity: 0.5, cursor: 'not-allowed' }}
                disabled
              >
                Kirish talab etiladi (Tez orada)
              </button>
              <p style={{ margin: 0, fontSize: '12.5px', color: 'var(--ink-3)' }}>
                Yuborish pul talab qilmaydi. O'rin sotib olish tasdiqdan keyin
                ochiladi.
              </p>
            </div>
          </div>
          <aside className="side">
            <div className="card">
              <div className="card-h">Reytingda shunday ko'rinadi</div>
              <div id="aPreview">
                <div className="row plain" style={{ marginTop: '0', pointerEvents: 'none' }}>
                  <div className="rank">?</div>
                  <div className="ava" style={{ background: 'var(--surface-2)', color: 'var(--ink-3)' }}>
                    ?
                  </div>
                  <div style={{ minWidth: 0 }}>
                    <h3 className="rtitle" style={{ color: 'var(--ink-3)' }}>
                      Kanal nomi
                    </h3>
                    <p className="rdesc">Bir qatorli tavsif</p>
                    <div className="rmeta">
                      <span className="sq" style={{ background: 'var(--ink-3)' }}></span>
                      <b style={{ color: 'var(--ink-3)' }}>Kategoriya</b>
                      <span className="sep">·</span>0 obunachi
                    </div>
                  </div>
                  <div className="rprice">
                    0 <span style={{ fontSize: '12px', color: 'var(--ink-3)' }}>B</span>
                  </div>
                </div>
              </div>
            </div>
            <div className="card">
              <div className="card-h">Keyin nima bo'ladi</div>
              <p style={{ margin: 0, fontSize: '13.5px', color: 'var(--ink-2)' }}>
                Tasdiqlangunga qadar kanal "Katalog" bo'limida pulsiz turadi va
                "Egasi tasdiqlanmagan" deb belgilanadi. Tasdiqdan keyin istalgan
                o'rinni sotib olishingiz mumkin.
              </p>
            </div>
          </aside>
        </div>
      </div>
    </section>
  );
};
