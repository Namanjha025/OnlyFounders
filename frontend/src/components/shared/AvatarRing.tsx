import type { ReactNode } from 'react'

const CIRC = 2 * Math.PI * 37

export function AvatarRing({
  progress,
  color,
  children,
}: {
  progress: number
  color: string
  children: ReactNode
}) {
  return (
    <div className="relative w-[80px] h-[80px] mb-3">
      <svg className="absolute inset-0 w-full h-full -rotate-90" viewBox="0 0 80 80">
        <circle cx="40" cy="40" r="37" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="3" />
        <circle cx="40" cy="40" r="37" fill="none"
          stroke={color}
          strokeWidth="3" strokeLinecap="round"
          strokeDasharray={CIRC}
          strokeDashoffset={CIRC - Math.min(progress, 1) * CIRC}
          className="transition-all duration-700" />
      </svg>
      <div className="absolute inset-[6px] rounded-full overflow-hidden flex items-center justify-center">
        {children}
      </div>
    </div>
  )
}
