export function CardSkeleton() {
  return (
    <div className="rounded-2xl bg-card border border-border p-6 flex flex-col items-center">
      <div className="w-[80px] h-[80px] rounded-full bg-secondary animate-pulse mb-3" />
      <div className="h-4 w-32 bg-secondary rounded animate-pulse mb-2" />
      <div className="h-3 w-20 bg-secondary rounded animate-pulse mb-3" />
      <div className="h-10 w-full bg-secondary rounded animate-pulse" />
    </div>
  )
}
