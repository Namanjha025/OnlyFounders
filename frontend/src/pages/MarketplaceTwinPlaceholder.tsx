import { Link, useParams } from 'react-router-dom'

/** Placeholder until Twin profile + chat per specs/marketplace. */
export function MarketplaceTwinPlaceholder() {
  const { twinId } = useParams<{ twinId: string }>()
  return (
    <div className="animate-fade-in -m-8 min-h-screen bg-black px-6 py-10 text-white">
      <Link to="/marketplace" className="text-sm text-zinc-400 hover:text-white">
        ← Back to TwinVerse
      </Link>
      <h1 className="mt-6 text-2xl font-semibold">Twin</h1>
      <p className="mt-2 text-zinc-400">ID: {twinId}</p>
      <p className="mt-4 max-w-md text-[15px] text-zinc-500">
        Profile and chat will connect to the marketplace API when ready.
      </p>
    </div>
  )
}
