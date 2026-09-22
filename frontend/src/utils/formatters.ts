export function nf(x: number | string | undefined | null): string {
  if (x == null || Number.isNaN(x)) return "0";
  return String(x).replace(/\B(?=(\d{3})+(?!\d))/g, " ");
}

export function subs(x: number | undefined | null): string {
  if (x == null || Number.isNaN(x)) return "0";
  return x >= 1000 ? (Math.round(x / 100) / 10 + "").replace(".", ",") + " ming" : String(x);
}

export function initials(n: string | undefined | null): string {
  if (!n) return "R";
  const p = n.replace(/[^\p{L}\p{N} ]/gu, "").split(" ").filter(Boolean);
  return ((p[0] || "R")[0] + (p[1] ? p[1][0] : "")).toUpperCase();
}

export function formatB(units: number | undefined | null): string {
  if (units == null || Number.isNaN(units)) return "0";
  const b = units / 1000;
  return Number.isInteger(b) ? b.toString() : b.toString().replace('.', ',');
}

export function cleanTelegramHandle(handle?: string | null): string {
  if (!handle) return '';
  let clean = handle.trim();
  for (const prefix of [
    'https://t.me/', 'http://t.me/', 't.me/',
    'https://telegram.me/', 'http://telegram.me/', 'telegram.me/'
  ]) {
    if (clean.toLowerCase().startsWith(prefix)) {
      clean = clean.slice(prefix.length);
      break;
    }
  }
  clean = clean.replace(/^@/, '').replace(/\/+$/, '');
  return clean ? `@${clean}` : '';
}

export function getTelegramUrl(handle?: string | null, url?: string | null): string {
  if (url && (url.startsWith('http://') || url.startsWith('https://'))) {
    return url;
  }
  if (!handle) return 'https://t.me';
  const clean = handle.trim();
  if (clean.startsWith('http://') || clean.startsWith('https://')) {
    return clean;
  }
  if (clean.startsWith('t.me/')) {
    return `https://${clean}`;
  }
  if (clean.startsWith('telegram.me/')) {
    return `https://${clean}`;
  }
  return `https://t.me/${clean.replace(/^@/, '')}`;
}

export function formatDateSafe(dateStr?: string | null): string {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  if (isNaN(d.getTime())) return '';
  return d.toLocaleDateString('ru-RU');
}

