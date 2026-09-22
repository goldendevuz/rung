import { useState, useRef } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { fetchMyListings, uploadLogo, updateListing } from '../api/client';
import { useAuth } from '../contexts/AuthContext';
import AddListingModal from '../components/AddListingModal';
import { getTelegramUrl, cleanTelegramHandle } from '../utils/formatters';

function ChannelCard({ listing, onLogoUpdated }: { listing: any; onLogoUpdated?: () => void }) {
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const gradient = listing.gradient_start && listing.gradient_end 
    ? `linear-gradient(135deg, ${listing.gradient_start}, ${listing.gradient_end})`
    : 'linear-gradient(135deg, #7C3AED, #2563EB)';

  const initials = listing.name
    ? listing.name.split(' ').map((w: string) => w[0]).slice(0, 2).join('').toUpperCase()
    : 'CH';

  const tgUrl = getTelegramUrl(listing.handle, listing.url);
  const displayHandle = cleanTelegramHandle(listing.handle) || listing.handle;

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      alert("Faqat rasm fayllari (PNG, JPG, WebP) qabul qilinadi.");
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      alert("Rasm hajmi 5 MB dan oshmasligi kerak.");
      return;
    }

    setIsUploading(true);
    try {
      const res = await uploadLogo(file);
      await updateListing(listing.id, { logo_url: res.url });
      if (onLogoUpdated) onLogoUpdated();
      alert("Logotip muvaffaqiyatli yangilandi!");
    } catch (err: any) {
      alert(err.message || "Logotip yuklashda xatolik yuz berdi");
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  return (
    <div 
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '18px 22px',
        background: 'var(--bg-elevated)',
        borderRadius: '16px',
        border: '1px solid rgba(255, 255, 255, 0.08)',
        gap: '16px',
        flexWrap: 'wrap',
        transition: 'border-color 0.2s'
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flex: '1 1 320px' }}>
        <div 
          onClick={() => fileInputRef.current?.click()}
          title="Logotipni o'zgartirish uchun bosing"
          style={{
            width: '52px',
            height: '52px',
            borderRadius: '14px',
            background: listing.logo_url ? 'transparent' : gradient,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: '800',
            fontSize: '18px',
            color: '#fff',
            flexShrink: 0,
            boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
            overflow: 'hidden',
            position: 'relative',
            cursor: 'pointer',
          }}
        >
          {listing.logo_url ? (
            <img src={listing.logo_url} alt={listing.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
          ) : (
            initials
          )}
          {isUploading && (
            <div style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <div style={{ width: '16px', height: '16px', border: '2px solid #B8F03C', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
            </div>
          )}
        </div>
        <input 
          type="file" 
          ref={fileInputRef} 
          onChange={handleFileChange} 
          accept="image/png, image/jpeg, image/webp, image/gif" 
          style={{ display: 'none' }} 
        />
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
            <h3 style={{ margin: 0, fontSize: '17px', fontWeight: '700', color: 'var(--fg)' }}>
              {listing.name}
            </h3>
            {listing.verified && (
              <span title="Tasdiqlangan" style={{ color: 'var(--brand)', fontSize: '14px' }}>✓</span>
            )}
            <span 
              style={{
                fontSize: '11px',
                padding: '2px 8px',
                borderRadius: '10px',
                background: 'rgba(184, 240, 60, 0.12)',
                color: '#B8F03C',
                fontWeight: '600',
                border: '1px solid rgba(184, 240, 60, 0.25)'
              }}
            >
              ● Faol
            </span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginTop: '4px', fontSize: '13px', color: 'var(--fg-dim)', flexWrap: 'wrap' }}>
            <a 
              href={tgUrl} 
              target="_blank" 
              rel="noopener noreferrer"
              style={{ color: 'var(--brand)', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '4px', fontWeight: '500' }}
            >
              {displayHandle}
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6M15 3h6v6M10 14L21 3"/></svg>
            </a>
            {listing.category_slug && (
              <span>· Kategoriya: <strong style={{ color: 'var(--fg)' }}>{listing.category_slug}</strong></span>
            )}
          </div>
          {listing.description && (
            <p style={{ margin: '8px 0 0 0', fontSize: '13.5px', color: 'var(--fg-dim)', lineHeight: 1.4 }}>
              {listing.description}
            </p>
          )}
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          disabled={isUploading}
          style={{
            padding: '10px 14px',
            fontSize: '13px',
            fontWeight: '600',
            background: 'rgba(255,255,255,0.06)',
            color: 'var(--fg)',
            border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: '12px',
            cursor: 'pointer',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            whiteSpace: 'nowrap',
          }}
        >
          <span>🖼️</span> {listing.logo_url ? "Logotipni yangilash" : "Logotip yuklash"}
        </button>
        <Link 
          to="/"
          className="btn-primary" 
          style={{ 
            padding: '10px 18px', 
            fontSize: '13.5px', 
            fontWeight: '700',
            textDecoration: 'none',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            borderRadius: '12px',
            whiteSpace: 'nowrap'
          }}
        >
          <span>🚀</span> Reytingda ko'tarish (1 B)
        </Link>
      </div>
    </div>
  );
}

export function Profile() {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState<'channels' | 'payments' | 'settings'>('channels');
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [avatarError, setAvatarError] = useState(false);

  const { data: listings, isLoading, isError, refetch } = useQuery({
    queryKey: ['my-listings'],
    queryFn: fetchMyListings,
    enabled: !!user,
  });

  if (!user) {
    return (
      <section id="page-profile">
        <div className="wrap">
          <p className="empty-state">Profilni ko'rish uchun tizimga kiring.</p>
        </div>
      </section>
    );
  }

  const initial = (user.first_name || user.username || '?')[0].toUpperCase();

  return (
    <section id="page-profile">
      <div className="wrap">
        <div 
          className="profile-header" 
          style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: '20px', 
            marginBottom: '24px', 
            padding: '24px', 
            background: 'var(--bg-elevated)', 
            borderRadius: '16px',
            border: '1px solid rgba(255, 255, 255, 0.08)'
          }}
        >
          {user.photo_url && !avatarError ? (
            <img 
              src={user.photo_url} 
              alt="Avatar" 
              onError={() => setAvatarError(true)}
              style={{ width: 80, height: 80, borderRadius: '50%', objectFit: 'cover', border: '2px solid rgba(184, 240, 60, 0.3)' }} 
            />
          ) : (
            <div 
              style={{ 
                width: 80, 
                height: 80, 
                borderRadius: '50%', 
                background: 'linear-gradient(135deg, #B8F03C, #059669)', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center', 
                fontSize: '32px', 
                fontWeight: 'bold', 
                color: '#0D0F11',
                boxShadow: '0 4px 12px rgba(184, 240, 60, 0.2)'
              }}
            >
              {initial}
            </div>
          )}
          <div style={{ flex: 1 }}>
            <h1 style={{ margin: '0 0 8px 0', fontSize: '24px', fontWeight: '800' }}>
              {user.first_name || user.username}
            </h1>
            <div style={{ color: 'var(--fg-dim)', fontSize: '14px', display: 'flex', gap: '16px', alignItems: 'center', flexWrap: 'wrap' }}>
              <span>ID: <strong>{user.telegram_id}</strong></span>
              <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                Balans: <strong style={{ color: 'var(--brand)', fontFamily: 'var(--mono)', fontSize: '16px' }}>{user.balance?.toLocaleString()} B</strong>
                <Link to="/hamyon" style={{
                  padding: '2px 8px',
                  borderRadius: '6px',
                  background: 'rgba(184, 240, 60, 0.15)',
                  color: 'var(--brand)',
                  fontSize: '12px',
                  fontWeight: '700',
                  textDecoration: 'none',
                  border: '1px solid rgba(184, 240, 60, 0.3)'
                }}>
                  + To'ldirish
                </Link>
              </span>
            </div>
          </div>
          <button className="btn-secondary" onClick={logout} style={{ padding: '8px 16px', borderRadius: '10px' }}>
            Chiqish
          </button>
        </div>

        <div className="tabs" style={{ display: 'flex', gap: '16px', marginBottom: '24px', borderBottom: '1px solid var(--border)' }}>
          <button 
            className={`tab-btn ${activeTab === 'channels' ? 'active' : ''}`} 
            onClick={() => setActiveTab('channels')}
            style={{ padding: '12px 16px', background: 'none', border: 'none', color: activeTab === 'channels' ? 'var(--brand)' : 'var(--fg)', borderBottom: activeTab === 'channels' ? '2px solid var(--brand)' : '2px solid transparent', cursor: 'pointer', fontWeight: '600' }}
          >
            Mening kanallarim {listings?.length ? `(${listings.length})` : ''}
          </button>
          <button 
            className={`tab-btn ${activeTab === 'payments' ? 'active' : ''}`} 
            onClick={() => setActiveTab('payments')}
            style={{ padding: '12px 16px', background: 'none', border: 'none', color: activeTab === 'payments' ? 'var(--brand)' : 'var(--fg)', borderBottom: activeTab === 'payments' ? '2px solid var(--brand)' : '2px solid transparent', cursor: 'pointer', fontWeight: '600' }}
          >
            To'lovlar
          </button>
          <button 
            className={`tab-btn ${activeTab === 'settings' ? 'active' : ''}`} 
            onClick={() => setActiveTab('settings')}
            style={{ padding: '12px 16px', background: 'none', border: 'none', color: activeTab === 'settings' ? 'var(--brand)' : 'var(--fg)', borderBottom: activeTab === 'settings' ? '2px solid var(--brand)' : '2px solid transparent', cursor: 'pointer', fontWeight: '600' }}
          >
            Sozlamalar
          </button>
        </div>

        <div className="tab-content">
          {activeTab === 'channels' && (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <h2 style={{ margin: 0, fontSize: '18px', fontWeight: '700' }}>Kanallar ro'yxati</h2>
                <button 
                  className="btn-primary" 
                  onClick={() => setIsAddModalOpen(true)}
                  style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
                >
                  <span>+</span> Yangi qo'shish
                </button>
              </div>

              {isLoading ? (
                <div style={{ padding: '40px', textAlign: 'center', color: 'var(--fg-dim)' }}>Yuklanmoqda...</div>
              ) : isError ? (
                <div className="empty-state" style={{ padding: '40px 20px', textAlign: 'center', background: 'var(--bg-elevated)', borderRadius: '16px', border: '1px solid rgba(255, 100, 100, 0.2)' }}>
                  <p style={{ margin: '0 0 16px 0', color: '#ff6b6b' }}>Kanallarni yuklashda xatolik yuz berdi.</p>
                  <button 
                    className="btn-primary" 
                    onClick={() => refetch()}
                  >
                    Qayta urinish
                  </button>
                </div>
              ) : listings && listings.length > 0 ? (
                <div className="listings-list" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {listings.map((l: any) => (
                    <ChannelCard key={l.id} listing={l} onLogoUpdated={refetch} />
                  ))}
                </div>
              ) : (
                <div className="empty-state" style={{ padding: '60px 20px', textAlign: 'center', background: 'var(--bg-elevated)', borderRadius: '16px', border: '1px dashed rgba(255, 255, 255, 0.1)' }}>
                  <p style={{ margin: '0 0 16px 0', color: 'var(--fg-dim)' }}>Hali birorta ham kanal qo'shmagansiz.</p>
                  <button 
                    className="btn-primary" 
                    onClick={() => setIsAddModalOpen(true)}
                  >
                    Birinchi kanalni qo'shish
                  </button>
                </div>
              )}
            </div>
          )}

          {activeTab === 'payments' && (
            <div className="empty-state" style={{ padding: '60px 20px', textAlign: 'center', background: 'var(--bg-elevated)', borderRadius: '16px' }}>
              To'lovlar tarixi tez kunda qo'shiladi.
            </div>
          )}

          {activeTab === 'settings' && (
            <div className="empty-state" style={{ padding: '60px 20px', textAlign: 'center', background: 'var(--bg-elevated)', borderRadius: '16px' }}>
              Profil sozlamalari tez kunda qo'shiladi.
            </div>
          )}
        </div>
      </div>
      
      {isAddModalOpen && (
        <AddListingModal onClose={() => setIsAddModalOpen(false)} />
      )}
    </section>
  );
}
