import React from 'react';
import { initials, nf, subs, formatB } from '../utils/formatters';
import { Link } from 'react-router-dom';

const ICON_V = (
  <span className="vbadge" title="Egasi tasdiqlangan">
    <svg viewBox="0 0 24 24">
      <path d="M12 2.6l2.3 1.7 2.8-.3 1 2.7 2.4 1.5-.9 2.7.9 2.7-2.4 1.5-1 2.7-2.8-.3L12 21.4 9.7 19.7l-2.8.3-1-2.7-2.4-1.5.9-2.7-.9-2.7 2.4-1.5 1-2.7 2.8.3z" opacity=".22" />
      <path d="M8.6 12.3l2.3 2.3 4.6-4.9" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ stroke: 'var(--violet-text)' }} />
    </svg>
  </span>
);

function Avatar({ ch, className = '' }: { ch: any, className?: string }) {
  const gradient = ch.g ? `linear-gradient(140deg, ${ch.g[0]}, ${ch.g[1]})` : 'var(--surface-2)';
  return (
    <div className={`${className} ava`} style={{ background: gradient }}>
      {initials(ch.n)}
    </div>
  );
}

export function ListingRow({ item, onClaim }: { item: any, onClaim?: () => void }) {
  const ch = item.ch;
  const tinted = item.rank <= 9;
  
  // Fake category data for now, you would look this up from a map or context in real implementation
  // Fallback to item category info if it exists
  const cat = ch.category || { n: ch.c || 'Kategoriya', c: 'var(--ink-2)' };

  const styles = tinted ? { '--a': ((10 - item.rank) / 9).toFixed(2) } as React.CSSProperties : {};
  const className = `row ${tinted ? '' : 'plain'}`;

  const hasHoverNone = window.matchMedia("(hover:none)").matches;

  return (
    <div 
      className={className} 
      style={styles} 
      data-top={tinted ? item.rank : undefined}
      onClick={() => {
        if (hasHoverNone && !ch.free && onClaim) {
          onClaim();
        }
      }}
    >
      <div className="rank num">{typeof item.rank === 'number' ? `#${item.rank}` : '—'}</div>
      <Avatar ch={ch} />
      
      <div className="mid">
        <p className="rtitle">
          <Link to={`/p/${ch.h.replace('@', '')}`} style={{ color: 'inherit', textDecoration: 'none' }}>
            {ch.n}
          </Link>
          {ch.v && ICON_V}
        </p>
        <p className="rdesc">{ch.d}</p>
        <p className="rmeta">
          {cat.i ? <span style={{ marginRight: '4px' }}>{cat.i}</span> : <span className="sq" style={{ '--c': cat.c } as any} />}
          <b>{cat.n}</b>
          <span className="sep">·</span>
          {ch.t} {/* Time added */}
          <span className="sep">·</span>
          <span className="num">{ch.h}</span>
          <span className="sep">·</span>
          <span className="num">{subs(ch.s)}</span> obunachi
          <span className="sep">·</span>
          <span className="num">{nf(ch.k)}</span> o'tish
          <span className="sep">·</span>
          {ch.free ? (
            <span className={`adlabel free ${ch.free.includes("tasdiq") ? "unclaimed" : ""}`}>
              {ch.free}
            </span>
          ) : (
            <span className="adlabel">
              Reklama · <span className="num">{item.price} B</span> to'langan
            </span>
          )}
        </p>
      </div>

      {!ch.free ? (
        <>
          <div className="rprice"><span className="num">{item.price}</span> B</div>
          <button 
            className="claim-pill"
            onClick={(e) => {
              e.stopPropagation();
              if (onClaim) onClaim();
            }}
          >
            Bu o'rinni <span className="num">{formatB(item.priceUnits + 1000)} B</span> ga oling
          </button>
        </>
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
