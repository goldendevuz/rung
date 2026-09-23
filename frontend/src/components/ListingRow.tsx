import React from 'react';
import { initials, nf, subs, formatB } from '../utils/formatters';
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

export function ListingRow({ item, onClaim }: { item: any, onClaim?: () => void }) {
  const navigate = useNavigate();
  const ch = item?.ch || item || {};
  const rank = typeof item?.rank === 'number' ? item.rank : undefined;
  const tinted = rank != null && rank <= 9;
  
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

      {!ch.free ? (
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
      ) : (
        <div className="rprice"><span style={{ color: 'var(--ink-3)', fontSize: '14px' }}>pulsiz</span></div>
      )}
    </div>
  );
}

export function MiniListing({ item }: { item: any }) {
  const ch = item.ch;
  return (
    <div className="mini">
      <div className="rank num">#{item.rank}</div>
      <Avatar ch={ch} />
      <div className="mini-n">{ch.n}</div>
      <div className="mini-p"><span className="num">{item.price}</span> B</div>
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
