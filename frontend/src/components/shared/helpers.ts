export function avatarGradient(seed: string): string {
  let h = 0
  for (let i = 0; i < seed.length; i++) h = (h + seed.charCodeAt(i) * (i + 1)) % 360
  return `linear-gradient(135deg, hsl(${h} 35% 28%), hsl(${(h + 45) % 360} 30% 20%))`
}

export function avatarGradientVivid(seed: string): string {
  let h = 0
  for (let i = 0; i < seed.length; i++) h = (h + seed.charCodeAt(i) * (i + 1)) % 360
  return `linear-gradient(135deg, hsl(${h} 50% 35%), hsl(${(h + 50) % 360} 45% 25%))`
}

export function nameInitials(s: string | null): string {
  if (!s) return '?'
  return (s.match(/[A-Za-z]+/g) ?? []).slice(0, 2).map(w => w[0]).join('').toUpperCase() || '?'
}

export function scoreToColor(score: number): string {
  const s = Math.min(Math.max(score, 0), 100) / 100
  const r = s < 0.5 ? 255 : Math.round(255 - (s - 0.5) * 2 * 255)
  const g = s < 0.5 ? Math.round(s * 2 * 200) : 200
  return `rgb(${r}, ${g}, 60)`
}
