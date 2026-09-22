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
