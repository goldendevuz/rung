import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchMyListings } from '../api/client';
import { useAuth } from '../contexts/AuthContext';
import { ListingRow } from '../components/ListingRow';
import AddListingModal from '../components/AddListingModal';

export function Profile() {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState<'channels' | 'payments' | 'settings'>('channels');
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [avatarError, setAvatarError] = useState(false);

  const { data: listings, isLoading } = useQuery({
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
              <span>Balans: <strong style={{ color: 'var(--brand)', fontFamily: 'var(--mono)', fontSize: '16px' }}>{user.balance?.toLocaleString()} B</strong></span>
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
            Mening kanallarim
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
              ) : listings && listings.length > 0 ? (
                <div className="listings-list" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {listings.map((l: any) => (
                    <ListingRow key={l.id} item={l} />
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
