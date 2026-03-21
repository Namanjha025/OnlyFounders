export function PlaceholderPage({ title }: { title: string }) {
  return (
    <div>
      <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
      <p className="mt-2 text-muted-foreground">
        Static placeholder — wire to OnlyFounders API and real pages when ready.
      </p>
    </div>
  )
}
