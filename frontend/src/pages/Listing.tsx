import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { fetchListing } from '../api/client';
import { initials, subs, nf } from '../utils/formatters';

const ICON_V = (
  <span className="vbadge" title="Egasi tasdiqlangan" style={{ display: 'inline-flex', verticalAlign: 'middle', marginLeft: '6px' }}>
    <svg viewBox="0 0 24 24" style={{ width: '18px', height: '18px' }}>
      <path d="M12 2.6l2.3 1.7 2.8-.3 1 2.7 2.4 1.5-.9 2.7.9 2.7-2.4 1.5-1 2.7-2.8-.3L12 21.4 9.7 19.7l-2.8.3-1-2.7-2.4-1.5.9-2.7-.9-2.7 2.4-1.5 1-2.7 2.8.3z" opacity=".22" />
      <path d="M8.6 12.3l2.3 2.3 4.6-4.9" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ stroke: 'var(--violet-text)' }} />
    </svg>
  </span>
);

export const Listing = () => {
  const { id } = useParams<{ id: string }>();
  const [copied, setCopied] = useState(false);

  const { data, isLoading, error } = useQuery({
    queryKey: ['listing', id],
    queryFn: () => fetchListing(id!),
    retry: false,
  });

  if (isLoading) {
    return (
      <section id="page-listing" style={{ padding: '32px 16px', minHeight: '60vh' }}>
        <div className="wrap" style={{ maxWidth: '640px', margin: '0 auto' }}>
          <div style={{ padding: '40px 20px', textAlign: 'center', color: 'var(--ink-3)' }}>
            Yuklanmoqda...
          </div>
        </div>
      </section>
    );
  }

  if (error || !data) {
    return (
      <section id="page-listing" style={{ padding: '32px 16px', minHeight: '60vh' }}>
        <div className="wrap" style={{ maxWidth: '640px', margin: '0 auto' }}>
          <Link to="/" style={{ color: 'var(--ink-2)', textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: '6px', fontSize: '14px', marginBottom: '24px' }}>
            ← Bosh sahifaga qaytish
          </Link>
          <div className="card" style={{ padding: '32px 24px', textAlign: 'center' }}>
            <h1 style={{ fontSize: '22px', marginBottom: '12px' }}>Kanal topilmadi</h1>
            <p style={{ color: 'var(--ink-2)', fontSize: '14.5px', lineHeight: 1.6, maxWidth: '460px', margin: '0 auto 24px' }}>
              Bunday kanal mavjud emas yoki kanal egasi tomonidan o'chirilgan bo'lishi mumkin.
            </p>
            <Link to="/" className="btn-primary" style={{ display: 'inline-flex', alignItems: 'center', textDecoration: 'none' }}>
              Katalogga o'tish
            </Link>
          </div>
        </div>
      </section>
    );
  }

  const gradient = data.gradient_start && data.gradient_end
    ? `linear-gradient(135deg, ${data.gradient_start}, ${data.gradient_end})`
    : 'linear-gradient(135deg, #7C3AED, #2563EB)';

  const handleShare = async () => {
    const shareUrl = window.location.href;
    if (navigator.share) {
      try {
        await navigator.share({
          title: `${data.name} — Rung`,
          text: data.description || `${data.name} kanali Rung katalogida`,
          url: shareUrl,
        });
        return;
      } catch {
        // Fallback to copy
      }
    }
    navigator.clipboard.writeText(shareUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <section id="page-listing" style={{ padding: '24px 16px 60px', minHeight: '80vh' }}>
      <div className="wrap" style={{ maxWidth: '640px', margin: '0 auto' }}>
        {/* Navigation Breadcrumb */}
        <div style={{ marginBottom: '20px' }}>
          <Link 
            to="/" 
            style={{ 
              color: 'var(--ink-2)', 
              textDecoration: 'none', 
              display: 'inline-flex', 
              alignItems: 'center', 
              gap: '6px', 
              fontSize: '14px',
              fontWeight: '500',
              transition: 'color 0.15s'
            }}
          >
            <span style={{ fontSize: '16px' }}>←</span> Bosh sahifaga qaytish
          </Link>
        </div>

        {/* Channel Card */}
        <div 
          className="card" 
          style={{ 
            padding: '28px 24px', 
            borderRadius: '20px', 
            border: '1px solid var(--line-soft)',
            background: 'var(--surface)',
            boxShadow: '0 12px 36px rgba(0, 0, 0, 0.25)'
          }}
        >
          {/* Header Info */}
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '18px', flexWrap: 'wrap', marginBottom: '20px' }}>
            <div 
              style={{
                width: '68px',
                height: '68px',
                borderRadius: '18px',
                background: data.logo_url ? 'transparent' : gradient,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontWeight: '800',
                fontSize: '24px',
                color: '#fff',
                flexShrink: 0,
                boxShadow: '0 8px 20px rgba(0, 0, 0, 0.35)',
                overflow: 'hidden',
              }}
            >
              {data.logo_url ? (
                <img 
                  src={data.logo_url} 
                  alt={data.name} 
                  style={{ width: '100%', height: '100%', objectFit: 'cover' }} 
                  onError={(e) => {
                    e.currentTarget.style.display = 'none';
                    if (e.currentTarget.parentElement) {
                      e.currentTarget.parentElement.style.background = gradient;
                      e.currentTarget.parentElement.innerText = initials(data.name);
                    }
                  }}
                />
              ) : (
                initials(data.name)
              )}
            </div>

            <div style={{ flex: 1, minWidth: '220px' }}>
              <h1 style={{ fontSize: '22px', fontWeight: '800', margin: '0 0 8px', letterSpacing: '-0.02em', wordBreak: 'break-word' }}>
                {data.name}
                {data.verified && ICON_V}
              </h1>

              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                <span 
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '6px',
                    padding: '3px 10px',
                    borderRadius: '999px',
                    fontSize: '12px',
                    fontWeight: '600',
                    background: 'rgba(255, 255, 255, 0.06)',
                    color: 'var(--ink-2)',
                    border: '1px solid rgba(255, 255, 255, 0.08)'
                  }}
                >
                  <span className="sq" style={{ width: '7px', height: '7px', borderRadius: '2px', background: data.category_color || 'var(--lime)' }} />
                  {data.category_slug || 'Kategoriya'}
                </span>

                {data.free_label && (
                  <span className={`adlabel free ${data.free_label.includes("tasdiq") ? "unclaimed" : ""}`}>
                    {data.free_label}
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Description */}
          {data.description && (
            <div 
              style={{ 
                margin: '0 0 24px', 
                padding: '16px', 
                borderRadius: '14px', 
                background: 'rgba(255, 255, 255, 0.03)',
                border: '1px solid rgba(255, 255, 255, 0.05)',
                color: 'var(--ink-2)', 
                fontSize: '14.5px', 
                lineHeight: 1.6,
                wordBreak: 'break-word',
                whiteSpace: 'pre-wrap'
              }}
            >
              {data.description}
            </div>
          )}

          {/* Stats Bar */}
          <div 
            style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', 
              gap: '12px', 
              marginBottom: '28px',
              padding: '14px 16px',
              borderRadius: '14px',
              background: 'rgba(255, 255, 255, 0.02)',
              border: '1px solid rgba(255, 255, 255, 0.05)'
            }}
          >
            <div>
              <div style={{ fontSize: '11.5px', color: 'var(--ink-3)', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: '600', marginBottom: '2px' }}>
                Obunachilar
              </div>
              <div style={{ fontSize: '18px', fontWeight: '700', fontFamily: 'var(--mono)', color: 'var(--fg)' }}>
                {subs(data.subscribers)}
              </div>
            </div>

            <div>
              <div style={{ fontSize: '11.5px', color: 'var(--ink-3)', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: '600', marginBottom: '2px' }}>
                O'tishlar
              </div>
              <div style={{ fontSize: '18px', fontWeight: '700', fontFamily: 'var(--mono)', color: 'var(--fg)' }}>
                {nf(data.clickthroughs)}
              </div>
            </div>

            <div>
              <div style={{ fontSize: '11.5px', color: 'var(--ink-3)', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: '600', marginBottom: '2px' }}>
                Katalog holati
              </div>
              <div style={{ fontSize: '15px', fontWeight: '700', color: 'var(--lime-text)', marginTop: '2px' }}>
                ● Faol
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            <a
              href={`/go/${data.id}`}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-primary"
              style={{ 
                flex: '1 1 200px', 
                display: 'inline-flex', 
                alignItems: 'center', 
                justifyContent: 'center', 
                gap: '8px', 
                textDecoration: 'none',
                minHeight: '48px',
                fontSize: '15px'
              }}
            >
              {/* Telegram SVG Icon */}
              <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69.01-.03.01-.14-.07-.19-.08-.05-.19-.02-.27 0-.12.03-1.99 1.27-5.63 3.72-.53.36-1.01.54-1.44.53-.47-.01-1.38-.27-2.05-.49-.83-.27-1.49-.42-1.43-.88.03-.24.38-.49 1.03-.75 4.04-1.76 6.74-2.92 8.09-3.48 3.85-1.6 4.65-1.88 5.17-1.89.11 0 .37.03.54.17.14.12.18.28.2.45-.02.07-.02.21-.04.38z" />
              </svg>
              Telegramda ochish
            </a>

            <button
              onClick={handleShare}
              className="btn-ghost"
              style={{
                flex: '0 0 auto',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                minHeight: '48px',
                padding: '0 20px',
                fontSize: '14px'
              }}
            >
              {copied ? 'Havola nusxalandi! ✓' : 'Ulashish ↗'}
            </button>
          </div>
        </div>
      </div>
    </section>
  );
};
