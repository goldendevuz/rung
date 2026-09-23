import { useQuery } from '@tanstack/react-query';
import React, { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { createTopup, fetchTopupStatus, fetchWalletHistory, TransactionItem } from '../api/client';

const QUICK_AMOUNTS = [1, 5, 10, 25, 50, 100];
const B_UNIT_UZS = 1000;

export function Wallet() {
  const { user, isLoading: authLoading, mutate: refreshUser } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const orderIdFromUrl = searchParams.get('order_id');
  const amountFromUrl = searchParams.get('amount');

  const initialAmount = React.useMemo(() => {
    if (amountFromUrl) {
      const parsed = parseInt(amountFromUrl, 10);
      if (!isNaN(parsed) && parsed >= 1) return parsed;
    }
    return 5;
  }, [amountFromUrl]);

  const [bAmount, setBAmount] = useState<number>(initialAmount);
  const [customInput, setCustomInput] = useState<string>(String(initialAmount));
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Return state polling
  const [pollOrderId, setPollOrderId] = useState<string | null>(orderIdFromUrl);
  const [pollStatus, setPollStatus] = useState<'pending' | 'completed' | 'failed' | null>(null);
  const [pollData, setPollData] = useState<any>(null);

  // Handle URL order_id polling
  useEffect(() => {
    if (!pollOrderId) return;

    let isCancelled = false;
    let timerId: number | undefined;

    setPollStatus('pending');

    const poll = async () => {
      try {
        const data = await fetchTopupStatus(pollOrderId);
        if (isCancelled) return;

        setPollData(data);
        if (data.status === 'completed' || data.status === 'failed') {
          setPollStatus(data.status);
          if (data.status === 'completed') {
            refreshUser();
          }
          return;
        }
      } catch (err) {
        console.error('Error polling topup status:', err);
      }

      if (!isCancelled) {
        timerId = window.setTimeout(poll, 2000);
      }
    };

    timerId = window.setTimeout(poll, 200);

    return () => {
      isCancelled = true;
      if (timerId) window.clearTimeout(timerId);
    };
  }, [pollOrderId]);

  const handleAmountSelect = (val: number) => {
    setBAmount(val);
    setCustomInput(String(val));
    setErrorMessage(null);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const raw = e.target.value.replace(/[^0-9]/g, '');
    setCustomInput(raw);
    const parsed = parseInt(raw, 10);
    if (!isNaN(parsed) && parsed >= 1) {
      setBAmount(parsed);
      setErrorMessage(null);
    } else {
      setBAmount(0);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;
    if (bAmount < 1) {
      setErrorMessage("Minimal to'ldirish miqdori 1 B");
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);

    try {
      const res = await createTopup(bAmount);
      if (res.pay_url) {
        // Redirect to inPAY hosted checkout
        window.location.href = res.pay_url;
      } else {
        throw new Error("To'lov havolasi olinmadi");
      }
    } catch (err: any) {
      setErrorMessage(err.message || "To'lovni boshlashda xatolik yuz berdi");
      setIsSubmitting(false);
    }
  };

  const clearPolling = () => {
    setPollOrderId(null);
    setPollStatus(null);
    setPollData(null);
    // Remove query params without page reload
    setSearchParams({});
  };

  if (authLoading) {
    return (
      <div className="wrap" style={{ padding: '60px 20px', textAlign: 'center', color: 'var(--fg-dim)' }}>
        Yuklanmoqda...
      </div>
    );
  }

  if (!user) {
    return (
      <div className="wrap" style={{ padding: '60px 20px', maxWidth: '480px', margin: '0 auto', textAlign: 'center' }}>
        <div style={{
          background: 'var(--bg-elevated)',
          border: '1px solid var(--border)',
          borderRadius: '20px',
          padding: '40px 24px',
          boxShadow: '0 8px 32px rgba(0,0,0,0.2)'
        }}>
          <div style={{
            width: '64px',
            height: '64px',
            borderRadius: '50%',
            background: 'rgba(184, 240, 60, 0.1)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 20px',
            color: 'var(--brand)',
            fontSize: '28px'
          }}>
            💳
          </div>
          <h1 style={{ fontSize: '24px', fontWeight: '800', marginBottom: '12px' }}>Hamyon</h1>
          <p style={{ color: 'var(--fg-dim)', fontSize: '15px', marginBottom: '24px', lineHeight: '1.5' }}>
            Hamyonni to'ldirish va B tangalarini sotib olish uchun tizimga kiring.
          </p>
          <Link to="/kirish" className="btn-primary" style={{ display: 'inline-block', width: '100%', padding: '12px 20px', borderRadius: '12px', textAlign: 'center', textDecoration: 'none' }}>
            Kirish
          </Link>
        </div>
      </div>
    );
  }

  const uzsTotal = bAmount * B_UNIT_UZS;

  return (
    <div className="wrap" style={{ padding: '40px 20px 80px', maxWidth: '640px', margin: '0 auto' }}>
      {/* Return state / Polling Modal or Banner */}
      {pollOrderId && (
        <div style={{
          background: 'var(--bg-elevated)',
          border: pollStatus === 'completed'
            ? '1px solid #10B981'
            : pollStatus === 'failed'
            ? '1px solid #EF4444'
            : '1px solid var(--brand)',
          borderRadius: '20px',
          padding: '28px 24px',
          marginBottom: '32px',
          boxShadow: '0 8px 32px rgba(0,0,0,0.3)',
          textAlign: 'center'
        }}>
          {pollStatus === 'pending' && (
            <div>
              <div style={{
                display: 'inline-block',
                width: '44px',
                height: '44px',
                border: '3px solid rgba(184, 240, 60, 0.2)',
                borderTopColor: 'var(--brand)',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite',
                marginBottom: '16px'
              }} />
              <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
              <h2 style={{ fontSize: '20px', fontWeight: '700', margin: '0 0 8px' }}>Tekshirilyapti...</h2>
              <p style={{ color: 'var(--fg-dim)', fontSize: '14px', margin: '0 0 8px' }}>
                To'lov tizimidan tasdiqlash kutilmoqda. Iltimos kuting.
              </p>
              <span style={{ fontSize: '12px', color: 'var(--fg-muted)', fontFamily: 'var(--mono)' }}>
                Buyurtma: {pollOrderId}
              </span>
            </div>
          )}

          {pollStatus === 'completed' && (
            <div>
              <div style={{
                width: '52px',
                height: '52px',
                borderRadius: '50%',
                background: 'rgba(16, 185, 129, 0.15)',
                color: '#10B981',
                fontSize: '28px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 16px'
              }}>
                ✓
              </div>
              <h2 style={{ fontSize: '20px', fontWeight: '700', color: '#10B981', margin: '0 0 8px' }}>
                To'lov muvaffaqiyatli amalga oshirildi!
              </h2>
              <p style={{ color: 'var(--fg)', fontSize: '15px', margin: '0 0 16px' }}>
                Hamyoningizga <strong style={{ color: 'var(--brand)' }}>{pollData?.b_amount ?? bAmount} B</strong> qo'shildi.
              </p>
              <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
                <button onClick={clearPolling} className="btn-secondary" style={{ padding: '8px 20px', borderRadius: '10px' }}>
                  Yopish
                </button>
              </div>
            </div>
          )}

          {pollStatus === 'failed' && (
            <div>
              <div style={{
                width: '52px',
                height: '52px',
                borderRadius: '50%',
                background: 'rgba(239, 68, 68, 0.15)',
                color: '#EF4444',
                fontSize: '28px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 16px'
              }}>
                ✕
              </div>
              <h2 style={{ fontSize: '20px', fontWeight: '700', color: '#EF4444', margin: '0 0 8px' }}>
                To'lov amalga oshmadi
              </h2>
              <p style={{ color: 'var(--fg-dim)', fontSize: '14px', margin: '0 0 16px' }}>
                To'lov bekor qilindi yoki xatolik yuz berdi.
              </p>
              <button onClick={clearPolling} className="btn-secondary" style={{ padding: '8px 20px', borderRadius: '10px' }}>
                Qayta urinish
              </button>
            </div>
          )}
        </div>
      )}

      {/* Main Wallet Card */}
      <div style={{
        background: 'var(--bg-elevated)',
        border: '1px solid var(--border)',
        borderRadius: '24px',
        padding: '32px 28px',
        boxShadow: '0 12px 40px rgba(0,0,0,0.25)'
      }}>
        {/* Header & Balance */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '28px', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <h1 style={{ fontSize: '26px', fontWeight: '800', margin: '0 0 6px', letterSpacing: '-0.02em' }}>
              Hamyon
            </h1>
            <p style={{ color: 'var(--fg-dim)', fontSize: '14px', margin: 0 }}>
              B tangalari bilan kanallarni yuqori pog'onalarga ko'taring
            </p>
          </div>

          <div style={{
            background: 'rgba(184, 240, 60, 0.08)',
            border: '1px solid rgba(184, 240, 60, 0.25)',
            borderRadius: '16px',
            padding: '12px 18px',
            textAlign: 'right'
          }}>
            <div style={{ fontSize: '12px', color: 'var(--fg-dim)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Joriy balans
            </div>
            <div style={{ fontSize: '24px', fontWeight: '800', color: 'var(--brand)', fontFamily: 'var(--mono)' }}>
              {user.balance?.toLocaleString() ?? 0} B
            </div>
          </div>
        </div>

        {/* Top-up Form */}
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '24px' }}>
            <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', marginBottom: '10px', color: 'var(--fg)' }}>
              Miqdorni tanlang (B tanga)
            </label>

            {/* Quick-pick chips */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(80px, 1fr))', gap: '10px', marginBottom: '16px' }}>
              {QUICK_AMOUNTS.map((amt) => {
                const isSelected = bAmount === amt && customInput === String(amt);
                return (
                  <button
                    key={amt}
                    type="button"
                    onClick={() => handleAmountSelect(amt)}
                    style={{
                      padding: '12px 8px',
                      borderRadius: '12px',
                      border: isSelected ? '2px solid var(--brand)' : '1px solid var(--border)',
                      background: isSelected ? 'rgba(184, 240, 60, 0.12)' : 'var(--bg)',
                      color: isSelected ? 'var(--brand)' : 'var(--fg)',
                      fontWeight: '700',
                      fontSize: '15px',
                      cursor: 'pointer',
                      transition: 'all 0.15s ease'
                    }}
                  >
                    {amt} B
                  </button>
                );
              })}
            </div>

            {/* Custom Input */}
            <div style={{ position: 'relative' }}>
              <input
                type="text"
                inputMode="numeric"
                value={customInput}
                onChange={handleInputChange}
                placeholder="Boshqa miqdor"
                style={{
                  width: '100%',
                  padding: '14px 44px 14px 16px',
                  borderRadius: '12px',
                  border: '1px solid var(--border)',
                  background: 'var(--bg)',
                  color: 'var(--fg)',
                  fontSize: '16px',
                  fontWeight: '600',
                  boxSizing: 'border-box'
                }}
              />
              <span style={{
                position: 'absolute',
                right: '16px',
                top: '50%',
                transform: 'translateY(-50%)',
                color: 'var(--fg-dim)',
                fontWeight: '700',
                fontFamily: 'var(--mono)'
              }}>
                B
              </span>
            </div>
          </div>

          {/* Rate & Total Display */}
          <div style={{
            background: 'var(--bg)',
            border: '1px solid var(--border)',
            borderRadius: '14px',
            padding: '16px 20px',
            marginBottom: '24px'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '13px', color: 'var(--fg-dim)' }}>
              <span>Kurs:</span>
              <span>1 B = 1,000 so'm</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '15px', fontWeight: '700' }}>
              <span style={{ color: 'var(--fg)' }}>Jami to'lov:</span>
              <span style={{ color: 'var(--brand)', fontFamily: 'var(--mono)', fontSize: '18px' }}>
                {uzsTotal.toLocaleString()} so'm
              </span>
            </div>
            <div style={{ marginTop: '8px', fontSize: '12px', color: 'var(--fg-muted)', textAlign: 'right' }}>
              to'lov: Karta, Click, Payme, Paynet, Alif, AnorBank, Visa/MC (inPAY.uz xavfsiz to'lov)
            </div>
          </div>

          {errorMessage && (
            <div style={{
              background: 'rgba(239, 68, 68, 0.1)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              color: '#EF4444',
              padding: '12px 16px',
              borderRadius: '10px',
              fontSize: '14px',
              marginBottom: '20px'
            }}>
              {errorMessage}
            </div>
          )}

          {/* Submit button */}
          <button
            type="submit"
            disabled={isSubmitting || bAmount < 1}
            className="btn-primary"
            style={{
              width: '100%',
              padding: '16px 24px',
              borderRadius: '14px',
              fontSize: '16px',
              fontWeight: '700',
              cursor: isSubmitting || bAmount < 1 ? 'not-allowed' : 'pointer',
              opacity: isSubmitting || bAmount < 1 ? 0.6 : 1,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '10px'
            }}
          >
            {isSubmitting ? (
              <>
                <span style={{
                  display: 'inline-block',
                  width: '18px',
                  height: '18px',
                  border: '2px solid rgba(0,0,0,0.3)',
                  borderTopColor: '#000',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite'
                }} />
                Yuklanmoqda...
              </>
            ) : (
              `To'ldirish (${uzsTotal.toLocaleString()} so'm)`
            )}
          </button>
        </form>
      </div>
      <WalletHistory />
    </div>
  );
}


function WalletHistory() {
  const [page, setPage] = useState(1);
  const { data, isLoading, isError } = useQuery({
    queryKey: ['wallet-history', page],
    queryFn: () => fetchWalletHistory(page),
  });

  if (isLoading) return (
    <div style={{ textAlign: 'center', color: 'var(--fg-dim)', padding: '24px', fontSize: '14px' }}>
      Tarix yuklanmoqda...
    </div>
  );
  if (isError || !data) return null;
  if (data.total === 0) return (
    <div style={{ textAlign: 'center', color: 'var(--fg-dim)', padding: '24px', fontSize: '14px' }}>
      Hali tranzaksiyalar yo'q
    </div>
  );

  return (
    <div style={{ marginTop: '24px' }}>
      <h2 style={{ fontSize: '18px', fontWeight: '700', margin: '0 0 16px', letterSpacing: '-0.01em' }}>
        Tranzaksiyalar tarixi
      </h2>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {data.items.map((item: TransactionItem) => {
          const isCredit = item.delta_b > 0;
          const date = new Date(item.created_at);
          const dateStr = date.toLocaleDateString('uz-UZ', { day: '2-digit', month: '2-digit', year: 'numeric' });
          const timeStr = date.toLocaleTimeString('uz-UZ', { hour: '2-digit', minute: '2-digit' });
          return (
            <div
              key={item.id}
              style={{
                background: 'var(--bg-elevated)',
                border: '1px solid var(--border)',
                borderRadius: '14px',
                padding: '14px 18px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: '12px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flex: 1, minWidth: 0 }}>
                <div style={{
                  width: '38px',
                  height: '38px',
                  borderRadius: '50%',
                  background: isCredit ? 'rgba(184, 240, 60, 0.12)' : 'rgba(239, 68, 68, 0.12)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '18px',
                  flexShrink: 0,
                }}>
                  {isCredit ? '💳' : '🏆'}
                </div>
                <div style={{ minWidth: 0 }}>
                  <div style={{ fontSize: '14px', fontWeight: '600', color: 'var(--fg)', marginBottom: '2px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {item.description}
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--fg-dim)' }}>
                    {dateStr} {timeStr}
                  </div>
                </div>
              </div>
              <div style={{ textAlign: 'right', flexShrink: 0 }}>
                <div style={{
                  fontSize: '16px',
                  fontWeight: '800',
                  color: isCredit ? 'var(--brand)' : '#EF4444',
                  fontFamily: 'var(--mono)',
                }}>
                  {isCredit ? '+' : ''}{item.delta_b} B
                </div>
                <div style={{ fontSize: '11px', color: 'var(--fg-dim)' }}>
                  Balans: {item.balance_after_b} B
                </div>
              </div>
            </div>
          );
        })}
      </div>
      {data.total > data.page_size && (
        <div style={{ display: 'flex', gap: '8px', justifyContent: 'center', marginTop: '16px' }}>
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            style={{ padding: '8px 16px', borderRadius: '8px', border: '1px solid var(--border)', background: 'none', color: 'var(--fg)', cursor: page === 1 ? 'not-allowed' : 'pointer', opacity: page === 1 ? 0.5 : 1 }}
          >← Oldingi</button>
          <span style={{ padding: '8px 12px', fontSize: '13px', color: 'var(--fg-dim)' }}>
            {page} / {Math.ceil(data.total / data.page_size)}
          </span>
          <button
            onClick={() => setPage(p => p + 1)}
            disabled={page >= Math.ceil(data.total / data.page_size)}
            style={{ padding: '8px 16px', borderRadius: '8px', border: '1px solid var(--border)', background: 'none', color: 'var(--fg)', cursor: 'pointer' }}
          >Keyingi →</button>
        </div>
      )}
    </div>
  );
}
