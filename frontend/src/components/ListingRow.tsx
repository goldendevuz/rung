import React from 'react';
import { initials, nf, subs, formatB, cleanTelegramHandle } from '../utils/formatters';
import { Link, useNavigate } from 'react-router-dom';

const ICON_V = (
  <span className="vbadge" title="Egasi tasdiqlangan">
    <svg viewBox="0 0 24 24">
      <path d="M12 2.6l2.3 1.7 2.8-.3 1 2.7 2.4 1.5-.9 2.7.9 2.7-2.4 1.5-1 2.7-2.8-.3L12 21.4 9.7 19.7l-2.8.3-1-2.7-2.4-1.5.9-2.7-.9-2.7 2.4-1.5 1-2.7 2.8.3z" opacity=".22" />
      <path d="M8.6 12.3l2.3 2.3 4.6-4.9" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ stroke: 'var(--violet-text)' }} />
    </svg>
  </span>
);

function Avatar({ ch, className = '' }: { ch: any, className?: string }) {
  const [imgError, setImgError] = React.useState(false);
  const logoUrl = ch.logo_url || ch.logo;
  const gradient = ch.g ? `linear-gradient(140deg, ${ch.g[0]}, ${ch.g[1]})` : 'var(--surface-2)';

  if (logoUrl && !imgError) {
    return (
      <div className={`${className} ava`} style={{ background: 'transparent', overflow: 'hidden' }}>
        <img 
          src={logoUrl} 
          alt={ch.n || ''} 
          onError={() => setImgError(true)}
          style={{ width: '100%', height: '100%', objectFit: 'cover' }}
        />
      </div>
    );
  }

  return (
    <div className={`${className} ava`} style={{ background: gradient }}>
      {initials(ch.n)}
    </div>
  );
}


export function SponsorRow({ item, isOwner }: { item: any, isOwner: boolean }) {
  const navigate = useNavigate();
  const ch = item?.ch || item || {};
  
  const cat = ch.category || { 
    n: ch.category_slug || ch.c || 'Kategoriya', 
    c: ch.category_color || 'var(--ink-2)',
    i: ch.category_icon
  };

  const handleRowClick = (e: React.MouseEvent) => {
    if ((e.target as HTMLElement).closest('button, a')) return;
    if (ch.id) navigate(`/p/${ch.id}`);
  };

  // REDUCED VIEW
  if (!isOwner) {
    return (
      <div className="row plain" style={{ cursor: 'pointer', background: 'var(--surface-2)', border: '1px solid rgba(245, 158, 11, 0.2)' }} onClick={handleRowClick}>
        <div className="rank num" style={{ width: '40px', display: 'flex', justifyContent: 'center' }}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="rgba(245, 158, 11, 0.5)">
             <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
          </svg>
        </div>
        <Avatar ch={ch} />
        <div className="mid">
          <p className="rtitle">
            <Link to={`/p/${ch.id}`} style={{ color: 'inherit', textDecoration: 'none' }}>
              {ch.n}
            </Link>
            {ch.v && ICON_V}
          </p>
          <p className="rdesc">{ch.d}</p>
        </div>
        <div className="rprice-wrap" style={{ display: 'flex', alignItems: 'center' }}>
          <span className="sponsor-badge" style={{ display: 'inline-flex', alignItems: 'center', gap: '5px', padding: '4px 10px', borderRadius: '999px', fontSize: '12px', fontWeight: 600, background: 'linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(217, 119, 6, 0.15))', border: '1px solid rgba(245, 158, 11, 0.35)', color: '#FBBF24' }}>
            Homiylik
          </span>
        </div>
      </div>
    );
  }

  // FULL VIEW (Owner)
  return (
    <div className="row plain" style={{ cursor: 'pointer', background: 'var(--surface-2)', border: '1px dashed rgba(245, 158, 11, 0.4)' }} onClick={handleRowClick}>
      <div className="rank num" style={{ width: '40px', display: 'flex', justifyContent: 'center' }}>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="rgba(245, 158, 11, 0.5)">
           <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
        </svg>
      </div>
      <Avatar ch={ch} />
      <div className="mid">
        <p className="rtitle">
          <Link to={`/p/${ch.id}`} style={{ color: 'inherit', textDecoration: 'none' }}>
            {ch.n}
          </Link>
          {ch.v && ICON_V}
        </p>
        <p className="rdesc">{ch.d}</p>
        <p className="rmeta">
          {cat.i ? <span style={{ marginRight: '4px' }}>{cat.i}</span> : <span className="sq" style={{ '--c': cat.c } as any} />}
          <b>{cat.n}</b>
          {ch.t ? <><span className="sep">·</span>{ch.t}</> : null}
          <span className="sep">·</span>
          <span className="num">{subs(ch.s)}</span> obunachi
          <span className="sep">·</span>
          <span className="num">{nf(ch.k)}</span> o'tish
        </p>
      </div>
      <div className="rprice-wrap" style={{ display: 'flex', flexFlow: 'column', alignItems: 'flex-end', gap: '4px' }}>
        <span className="sponsor-badge" style={{ display: 'inline-flex', alignItems: 'center', gap: '5px', padding: '4px 10px', borderRadius: '999px', fontSize: '12px', fontWeight: 600, background: 'linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(217, 119, 6, 0.15))', border: '1px solid rgba(245, 158, 11, 0.35)', color: '#FBBF24' }}>
          Sponsor (Sizniki)
        </span>
      </div>
    </div>
  );
}

export function ListingRow({ item, onClaim }: { item: any, onClaim?: () => void }) {
  const navigate = useNavigate();
  const ch = item?.ch || item || {};
  const rank = typeof item?.rank === 'number' ? item.rank : undefined;
  const tinted = rank != null && rank <= 9;
  
  const handleClean = cleanTelegramHandle(ch.h || ch.handle || '').toLowerCase();
    const isRung = handleClean === '@rung_uz' || ch.id === 'ba3b5499-4988-41c1-9f66-b721db1f66d8';
  const isSponsor = false; // Moved to SponsorRow

  const cat = ch.category || { 
    n: ch.category_slug || ch.c || 'Kategoriya', 
    c: ch.category_color || 'var(--ink-2)',
    i: ch.category_icon
  };

  const styles = tinted && rank != null ? { '--a': ((10 - rank) / 9).toFixed(2) } as React.CSSProperties : {};
  const className = `row ${tinted ? '' : 'plain'}`;

  const handleRowClick = (e: React.MouseEvent) => {
    // Do not navigate if user clicked on button or link
    if ((e.target as HTMLElement).closest('button, a')) {
      return;
    }
    if (ch.id) {
      navigate(`/p/${ch.id}`);
    }
  };

  return (
    <div 
      className={className} 
      style={{ ...styles, cursor: 'pointer' }} 
      data-top={tinted ? item.rank : undefined}
      onClick={handleRowClick}
    >
      <div className="rank num">{typeof item.rank === 'number' ? `#${item.rank}` : '—'}</div>
      <Avatar ch={ch} />
      
      <div className="mid">
        <p className="rtitle">
          <Link to={`/p/${ch.id}`} style={{ color: 'inherit', textDecoration: 'none' }}>
            {ch.n}
          </Link>
          {ch.v && ICON_V}
        </p>
        <p className="rdesc">{ch.d}</p>
        <p className="rmeta">
          {cat.i ? <span style={{ marginRight: '4px' }}>{cat.i}</span> : <span className="sq" style={{ '--c': cat.c } as any} />}
          <b>{cat.n}</b>
          {ch.t ? (
            <>
              <span className="sep">·</span>
              {ch.t}
            </>
          ) : null}
          <span className="sep">·</span>
          <span className="num">{subs(ch.s)}</span> obunachi
          <span className="sep">·</span>
          <span className="num">{nf(ch.k)}</span> o'tish
          {ch.free ? (
            <>
              <span className="sep">·</span>
              <span className={`adlabel free ${ch.free.includes("tasdiq") ? "unclaimed" : ""}`}>
                {ch.free}
              </span>
            </>
          ) : null}
        </p>
      </div>

      {!ch.free && !isRung && !isSponsor ? (
        <div className="rprice-wrap" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div className="rprice"><span className="num">{item.price}</span> B</div>
          {onClaim && (
            <button 
              className="claim-btn-mobile"
              title="Bu o'rinni olish"
              onClick={(e) => {
                e.stopPropagation();
                onClaim();
              }}
            >
              Olish
            </button>
          )}
          <button 
            className="claim-pill"
            onClick={(e) => {
              e.stopPropagation();
              if (onClaim) onClaim();
            }}
          >
            Bu o'rinni <span className="num">{formatB(item.priceUnits + 1000)} B</span> ga oling
          </button>
        </div>
      ) : isSponsor ? (
        <div className="rprice-wrap" style={{ display: 'flex', alignItems: 'center' }}>
          <span 
            className="sponsor-badge"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '5px',
              padding: '4px 10px',
              borderRadius: '999px',
              fontSize: '12px',
              fontWeight: 600,
              background: 'linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(217, 119, 6, 0.15))',
              border: '1px solid rgba(245, 158, 11, 0.35)',
              color: '#FBBF24',
              letterSpacing: '0.03em',
              boxShadow: '0 0 10px rgba(245, 158, 11, 0.12)',
              userSelect: 'none'
            }}
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor" style={{ opacity: 0.9 }}>
              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
            </svg>
            Sponsor
          </span>
        </div>
      ) : ch.free ? (
        <div className="rprice"><span style={{ color: 'var(--ink-3)', fontSize: '14px' }}>pulsiz</span></div>
      ) : null}
    </div>
  );
}

export function MiniListing({ item }: { item: any }) {
  const ch = item.ch;
  const handleClean = cleanTelegramHandle(ch?.h || ch?.handle || '').toLowerCase();
    const nameClean = (ch?.n || ch?.name || '').toLowerCase();
  const isRung = handleClean === '@rung_uz' || ch?.id === 'ba3b5499-4988-41c1-9f66-b721db1f66d8';
  const isSponsor = handleClean === '@sipagentbot' || handleClean === '@uz_cinema_rasmiy' || handleClean.includes('uz_cinema') || ch?.id === '2b2efff6-894d-4cdc-98e2-87ddc40a9ec8' || nameClean.includes('sipagentbot') || nameClean.includes('uzcinema') || nameClean.includes('uz cinema');

  return (
    <div className="mini">
      <div className="rank num">#{item.rank}</div>
      <Avatar ch={ch} />
      <div className="mini-n">{ch.n}</div>
      {!isRung && !isSponsor ? (
        <div className="mini-p"><span className="num">{item.price}</span> B</div>
      ) : isSponsor ? (
        <div className="mini-p" style={{ color: '#FBBF24', fontSize: '11px', fontWeight: 600 }}>Sponsor</div>
      ) : null}
    </div>
  );
}

export function EmptyRankSlot({ rank, onClaim }: { rank: number; onClaim?: () => void }) {
  return (
    <div className="row plain empty-slot" data-empty-rank={rank}>
      <div className="rank num" style={{ color: 'var(--ink-3)', opacity: 0.7 }}>
        #{rank}
      </div>
      <div className="ava empty-ava">
        <span>+</span>
      </div>
      <div className="mid">
        <p className="rtitle" style={{ color: 'var(--ink-3)', fontWeight: 600 }}>
          Bo'sh o'rin #{rank}
        </p>
        <p className="rdesc" style={{ color: 'var(--ink-3)', opacity: 0.8 }}>
          Kanalni qo'shib, reytingdagi ushbu pog'onani egallang
        </p>
      </div>
      <div className="rprice-wrap">
        <Link
          to="/qoshish"
          className="claim-empty-btn"
          onClick={(e) => {
            if (onClaim) {
              e.preventDefault();
              onClaim();
            }
          }}
        >
          Bu yerni egallang →
        </Link>
      </div>
    </div>
  );
}
