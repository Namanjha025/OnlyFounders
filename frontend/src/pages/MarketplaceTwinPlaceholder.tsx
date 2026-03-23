import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, MapPin, Briefcase, Heart, Link2, GraduationCap, Mail, Users, ExternalLink } from 'lucide-react'
import { cn } from '@/lib/utils'
import { marketplace, type MarketplaceProfile } from '@/lib/api'

const TYPE_META: Record<string, { label: string; color: string }> = {
  professional: { label: 'Professional', color: 'text-zinc-300' },
  advisor: { label: 'Advisor / Investor', color: 'text-zinc-300' },
  founder: { label: 'Founder', color: 'text-zinc-300' },
}

function avatarGradient(seed: string): string {
  let h = 0
  for (let i = 0; i < seed.length; i++) h = (h + seed.charCodeAt(i) * (i + 1)) % 360
  return `linear-gradient(135deg, hsl(${h} 50% 35%), hsl(${(h + 50) % 360} 45% 25%))`
}

function nameInitials(headline: string | null): string {
  if (!headline) return '?'
  const words = headline.match(/[A-Za-z]+/g) ?? []
  return words.slice(0, 2).map(w => w[0]).join('').toUpperCase() || '?'
}

const FIELD_LABELS: Record<string, string> = {
  primary_role: 'Role', years_experience: 'Experience', hourly_rate: 'Rate',
  availability_status: 'Availability', service_offerings: 'Services', portfolio_url: 'Portfolio',
  cal_booking_link: 'Booking', certifications: 'Certifications',
  domain_expertise: 'Expertise', investment_thesis: 'Thesis', portfolio_companies: 'Portfolio',
  investment_stages: 'Stages', check_size_min: 'Min Check', check_size_max: 'Max Check',
  fee_structure: 'Fee', availability: 'Availability',
  looking_for_roles: 'Looking For', cofounder_brief: 'Pitch', equity_offered: 'Equity',
  startup_stage: 'Stage', industry: 'Industry', commitment_level: 'Commitment',
  remote_ok: 'Remote', funding_stage: 'Funding',
}

export function MarketplaceTwinPlaceholder() {
  const { twinId } = useParams<{ twinId: string }>()
  const [profile, setProfile] = useState<MarketplaceProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!twinId) return
    marketplace.getProfile(twinId)
      .then(setProfile)
      .catch(err => setError(err instanceof Error ? err.message : 'Not found'))
      .finally(() => setLoading(false))
  }, [twinId])

  if (loading) return (
    <div className="animate-fade-in -m-8 min-h-screen bg-background flex items-center justify-center">
      <div className="w-8 h-8 border-2 border-white/30 border-t-zinc-300 rounded-full animate-spin" />
    </div>
  )
  if (error) return (
    <div className="animate-fade-in -m-8 min-h-screen bg-background px-6 py-10">
      <div className="max-w-xl mx-auto text-center py-20">
        <p className="text-red-400 mb-4">{error}</p>
        <Link to="/marketplace" className="text-zinc-300 hover:underline text-sm">Back to marketplace</Link>
      </div>
    </div>
  )
  if (!profile) return null

  const meta = TYPE_META[profile.profile_type] || TYPE_META.professional
  const typeData = (profile.professional_data || profile.advisor_data || profile.founder_data || {}) as Record<string, unknown>
  const isSelf = 'visibility_settings' in profile

  // Split type data into highlighted fields and detail fields
  const highlightFields = ['primary_role', 'domain_expertise', 'looking_for_roles']
  const highlighted = Object.entries(typeData).filter(([k, v]) => highlightFields.includes(k) && v != null && v !== '')
  const details = Object.entries(typeData).filter(([k, v]) =>
    !highlightFields.includes(k) && v != null && v !== '' && !(Array.isArray(v) && (v as unknown[]).length === 0)
  )

  return (
    <div className="animate-fade-in -m-8 min-h-screen bg-background text-white">
      {/* Top bar */}
      <div className="border-b border-border bg-background/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-6 py-3 flex items-center justify-between">
          <Link to="/marketplace" className="flex items-center gap-2 text-sm text-zinc-400 hover:text-zinc-300 transition">
            <ArrowLeft className="w-4 h-4" /> Back to directory
          </Link>
          {!isSelf && (
            <button className="flex items-center gap-2 bg-white text-black px-4 py-1.5 rounded-lg text-sm font-semibold hover:bg-zinc-300 transition">
              <Users className="w-3.5 h-3.5" /> Connect
            </button>
          )}
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_340px] gap-6">

          {/* ── Left Column: Main Profile ──────────────────────── */}
          <div className="space-y-6">
            {/* Avatar + Name card */}
            <div className="rounded-2xl border border-border bg-card p-8">
              <div className="flex flex-col items-center">
                <div className="w-28 h-28 rounded-full border-[3px] border-white/40 p-1">
                  <div
                    className="w-full h-full rounded-full flex items-center justify-center text-3xl font-bold text-white"
                    style={{ background: avatarGradient(profile.headline || profile.id) }}
                  >
                    {nameInitials(profile.headline)}
                  </div>
                </div>
                <h1 className="text-2xl font-semibold mt-4">{profile.headline || 'Untitled'}</h1>
                <p className={cn('text-sm mt-1', meta.color)}>{meta.label}</p>
                {profile.location && (
                  <p className="flex items-center gap-1 text-sm text-zinc-500 mt-1">
                    <MapPin className="w-3.5 h-3.5" /> {profile.location}
                  </p>
                )}
              </div>
            </div>

            {/* About */}
            {/* About + Skills */}
            {(profile.bio || (profile.skills && profile.skills.length > 0)) && (
              <div className="rounded-2xl border border-border bg-card p-6">
                <h2 className="font-semibold text-[15px] text-foreground mb-3">About</h2>
                {profile.bio && (
                  <div className="border-l-2 border-white/30 pl-4 mb-4">
                    <p className="text-sm text-zinc-300 leading-relaxed whitespace-pre-line">{profile.bio}</p>
                  </div>
                )}
                {profile.skills && profile.skills.length > 0 && (
                  <div>
                    <p className="text-[11px] uppercase tracking-wider text-zinc-500 mb-2">Skills</p>
                    <div className="flex flex-wrap gap-1.5">
                      {profile.skills.map((skill, i) => (
                        <span key={i} className="text-xs text-emerald-300/80 bg-emerald-500/10 border border-emerald-500/15 px-2.5 py-1 rounded-full">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* How I Can Help / What I Offer */}
            {highlighted.length > 0 && (
              <div className="rounded-2xl border border-border bg-card p-6">
                <h2 className="flex items-center gap-2 font-semibold text-[15px] text-foreground mb-3">
                  <Heart className="w-4 h-4 text-zinc-400" />
                  {profile.profile_type === 'founder' ? 'Looking For' : 'How I Can Help'}
                </h2>
                {highlighted.map(([key, val]) => (
                  <div key={key} className="border-l-2 border-white/30 pl-4 mb-3 last:mb-0">
                    <p className="text-sm text-zinc-400">
                      {Array.isArray(val) ? (val as string[]).join(', ') : String(val)}
                    </p>
                  </div>
                ))}
              </div>
            )}

            {/* Professional / Type Details */}
            {details.length > 0 && (
              <div className="rounded-2xl border border-border bg-card p-6">
                <h2 className="flex items-center gap-2 font-semibold text-[15px] text-foreground mb-4">
                  <Briefcase className="w-4 h-4 text-zinc-300" />
                  {profile.profile_type === 'professional' ? 'Professional' :
                   profile.profile_type === 'advisor' ? 'Advisory Details' : 'Startup Details'}
                </h2>
                <div className="grid grid-cols-2 gap-4">
                  {details.map(([key, val]) => (
                    <div key={key}>
                      <p className="text-[11px] uppercase tracking-wider text-zinc-500 mb-1">
                        {FIELD_LABELS[key] || key.replace(/_/g, ' ')}
                      </p>
                      <p className="text-sm text-zinc-200">
                        {Array.isArray(val)
                          ? typeof (val as unknown[])[0] === 'object'
                            ? (val as { name?: string }[]).map(v => v.name || JSON.stringify(v)).join(', ')
                            : (val as string[]).join(', ')
                          : key.includes('rate') || key.includes('size')
                            ? `$${Number(val).toLocaleString()}`
                            : String(val).replace(/_/g, ' ')}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* ── Right Column: Sidebar ──────────────────────────── */}
          <div className="space-y-4">
            {/* Connect card */}
            <div className="rounded-2xl border border-border bg-card p-5">
              <h3 className="font-semibold text-[15px] text-foreground mb-3">Connect</h3>
              {isSelf && profile.linkedin_url ? (
                <div className="mb-3">
                  <p className="text-xs text-zinc-500 mb-1">Preferred contact:</p>
                  <a href={profile.linkedin_url} target="_blank" rel="noopener"
                    className="flex items-center gap-1.5 text-sm text-zinc-300 hover:underline">
                    <Link2 className="w-3.5 h-3.5" /> LinkedIn
                  </a>
                </div>
              ) : (
                <p className="text-xs text-zinc-500 mb-3">Contact info visible after connecting.</p>
              )}
              <button className="w-full flex items-center justify-center gap-2 border border-white/20 text-zinc-300 py-2.5 rounded-xl text-sm font-medium hover:bg-white/5 hover:border-white/30 transition">
                <Users className="w-4 h-4" /> Invite to Team
              </button>
            </div>

            {/* Quick Info card */}
            <div className="rounded-2xl border border-border bg-card p-5">
              <h3 className="font-semibold text-[15px] text-foreground mb-3">Quick Info</h3>
              <dl className="space-y-2.5">
                <div className="flex justify-between text-sm">
                  <dt className="text-zinc-500">Type</dt>
                  <dd className="text-zinc-200 font-medium capitalize">{profile.profile_type}</dd>
                </div>
                {profile.location && (
                  <div className="flex justify-between text-sm">
                    <dt className="text-zinc-500">Location</dt>
                    <dd className="text-zinc-200 font-medium">{profile.location}</dd>
                  </div>
                )}
                <div className="flex justify-between text-sm">
                  <dt className="text-zinc-500">Profile Score</dt>
                  <dd className="text-zinc-200 font-medium">{profile.profile_score}/100</dd>
                </div>
                {isSelf && profile.website_url && (
                  <div className="flex justify-between text-sm">
                    <dt className="text-zinc-500">Website</dt>
                    <dd>
                      <a href={profile.website_url} target="_blank" rel="noopener"
                        className="text-zinc-300 hover:underline flex items-center gap-1">
                        Visit <ExternalLink className="w-3 h-3" />
                      </a>
                    </dd>
                  </div>
                )}
              </dl>
            </div>

            {/* Score ring */}
            <div className="rounded-2xl border border-border bg-card p-5 flex flex-col items-center">
              <ScoreRing score={profile.profile_score} />
              <p className="text-xs text-zinc-500 mt-3">
                {profile.profile_score >= 80 ? 'All-Star Profile' :
                 profile.profile_score >= 60 ? 'Strong Profile' :
                 profile.profile_score >= 40 ? 'Rising Profile' : 'Getting Started'}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function ScoreRing({ score }: { score: number }) {
  const r = 40; const circ = 2 * Math.PI * r
  const offset = circ - (Math.min(score, 100) / 100) * circ
  const color = score >= 80 ? '#22d3ee' : score >= 60 ? '#34d399' : score >= 40 ? '#facc15' : '#52525b'
  return (
    <div className="relative w-24 h-24">
      <svg className="w-24 h-24 -rotate-90" viewBox="0 0 96 96">
        <circle cx="48" cy="48" r={r} fill="none" stroke="rgba(6,182,212,0.08)" strokeWidth="5" />
        <circle cx="48" cy="48" r={r} fill="none" stroke={color} strokeWidth="5"
          strokeLinecap="round" strokeDasharray={circ} strokeDashoffset={offset}
          className="transition-all duration-1000" />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-2xl font-bold text-white">{score}</span>
        <span className="text-[10px] text-zinc-500">/ 100</span>
      </div>
    </div>
  )
}
