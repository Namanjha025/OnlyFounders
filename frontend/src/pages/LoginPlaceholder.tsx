import { Link } from 'react-router-dom'

/** Minimal route so Sidebar logout matches Tenderulkar (`/login`). Replace with real auth UI later. */
export function LoginPlaceholder() {
  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center px-6">
      <p className="text-muted-foreground text-sm mb-4">Login (placeholder)</p>
      <Link to="/" className="text-primary underline-offset-4 hover:underline">
        Back to app shell
      </Link>
    </div>
  )
}
