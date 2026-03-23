const R = 40
const CIRC = 2 * Math.PI * R

export function ScoreRing({
  value,
  label,
  color,
}: {
  value: number
  label: string
  color: string
}) {
  const offset = CIRC - Math.min(value, 1) * CIRC
  return (
    <div className="relative w-24 h-24">
      <svg className="w-24 h-24 -rotate-90" viewBox="0 0 96 96">
        <circle cx="48" cy="48" r={R} fill="none" stroke="rgba(6,182,212,0.08)" strokeWidth="5" />
        <circle cx="48" cy="48" r={R} fill="none" stroke={color}
          strokeWidth="5" strokeLinecap="round"
          strokeDasharray={CIRC} strokeDashoffset={offset}
          className="transition-all duration-1000" />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-2xl font-bold text-white">{Math.round(value * 100)}</span>
        <span className="text-[10px] text-zinc-500">{label}</span>
      </div>
    </div>
  )
}
