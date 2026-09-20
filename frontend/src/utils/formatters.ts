export function nf(x: number | string): string {
  return String(x).replace(/\B(?=(\d{3})+(?!\d))/g, " ");
}

export function subs(x: number): string {
  return x >= 1000 ? (Math.round(x / 100) / 10 + "").replace(".", ",") + " ming" : String(x);
}

export function initials(n: string): string {
  const p = n.replace(/[^\p{L}\p{N} ]/gu, "").split(" ").filter(Boolean);
  return ((p[0] || "R")[0] + (p[1] ? p[1][0] : "")).toUpperCase();
}

export function formatB(units: number): string {
  const b = units / 1000;
  return Number.isInteger(b) ? b.toString() : b.toString().replace('.', ',');
}
