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

  return (
    <section id="page-profile">
      <div className="wrap">
        <div className="profile-header" style={{ display: 'flex', alignItems: 'center', gap: '20px', marginBottom: '24px', padding: '24px', background: 'var(--bg-elevated)', borderRadius: '12px' }}>
          {user.photo_url ? (
            <img src={user.photo_url} alt="Avatar" style={{ width: 80, height: 80, borderRadius: '50%', objectFit: 'cover' }} />
          ) : (
            <div style={{ width: 80, height: 80, borderRadius: '50%', background: 'var(--brand)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '32px', fontWeight: 'bold', color: '#fff' }}>
              {(user.first_name || user.username || '?')[0].toUpperCase()}
            </div>
          )}
          <div style={{ flex: 1 }}>
            <h1 style={{ margin: '0 0 8px 0', fontSize: '24px' }}>{user.first_name || user.username}</h1>
            <div style={{ color: 'var(--fg-dim)', fontSize: '14px', display: 'flex', gap: '16px' }}>
              <span>ID: {user.telegram_id}</span>
              <span>Balans: <strong style={{ color: 'var(--brand)' }}>{user.balance?.toLocaleString()} so'm</strong></span>
            </div>
          </div>
          <button className="btn-secondary" onClick={logout}>Chiqish</button>
        </div>

        <div className="tabs" style={{ display: 'flex', gap: '16px', marginBottom: '24px', borderBottom: '1px solid var(--border)' }}>
          <button 
            className={`tab-btn ${activeTab === 'channels' ? 'active' : ''}`} 
            onClick={() => setActiveTab('channels')}
            style={{ padding: '12px 16px', background: 'none', border: 'none', color: activeTab === 'channels' ? 'var(--brand)' : 'var(--fg)', borderBottom: activeTab === 'channels' ? '2px solid var(--brand)' : '2px solid transparent', cursor: 'pointer', fontWeight: '500' }}
          >
            Mening kanallarim
          </button>
          <button 
            className={`tab-btn ${activeTab === 'payments' ? 'active' : ''}`} 
            onClick={() => setActiveTab('payments')}
            style={{ padding: '12px 16px', background: 'none', border: 'none', color: activeTab === 'payments' ? 'var(--brand)' : 'var(--fg)', borderBottom: activeTab === 'payments' ? '2px solid var(--brand)' : '2px solid transparent', cursor: 'pointer', fontWeight: '500' }}
          >
            To'lovlar
          </button>
          <button 
            className={`tab-btn ${activeTab === 'settings' ? 'active' : ''}`} 
            onClick={() => setActiveTab('settings')}
            style={{ padding: '12px 16px', background: 'none', border: 'none', color: activeTab === 'settings' ? 'var(--brand)' : 'var(--fg)', borderBottom: activeTab === 'settings' ? '2px solid var(--brand)' : '2px solid transparent', cursor: 'pointer', fontWeight: '500' }}
          >
            Sozlamalar
          </button>
        </div>

        <div className="tab-content">
          {activeTab === 'channels' && (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <h2 style={{ margin: 0, fontSize: '18px' }}>Kanallar ro'yxati</h2>
                <button 
                  className="btn-primary" 
                  onClick={() => setIsAddModalOpen(true)}
                >
                  + Yangi qo'shish
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
                <div className="empty-state" style={{ padding: '60px 20px', textAlign: 'center', background: 'var(--bg-elevated)', borderRadius: '12px' }}>
                  Hali birorta ham kanal qo'shmagansiz.
                </div>
              )}
            </div>
          )}

          {activeTab === 'payments' && (
            <div className="empty-state" style={{ padding: '60px 20px', textAlign: 'center', background: 'var(--bg-elevated)', borderRadius: '12px' }}>
              To'lovlar tarixi tez kunda qo'shiladi.
            </div>
          )}

          {activeTab === 'settings' && (
            <div className="empty-state" style={{ padding: '60px 20px', textAlign: 'center', background: 'var(--bg-elevated)', borderRadius: '12px' }}>
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
