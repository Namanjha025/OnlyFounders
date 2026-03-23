import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { User, Info, Heart, Briefcase, Eye, EyeOff, Trash2, Save, X, FileText, MapPin, Link2, Settings } from 'lucide-react'
import { cn } from '@/lib/utils'
import { marketplace, type MarketplaceProfile as ProfileType, type VisibilitySettings } from '@/lib/api'

function avatarGradient(seed: string): string {
  let h = 0
  for (let i = 0; i < seed.length; i++) h = (h + seed.charCodeAt(i) * (i + 1)) % 360
  return `linear-gradient(135deg, hsl(${h} 50% 35%), hsl(${(h + 50) % 360} 45% 25%))`
}
function nameInitials(s: string | null): string {
  if (!s) return '?'
  return (s.match(/[A-Za-z]+/g) ?? []).slice(0, 2).map(w => w[0]).join('').toUpperCase() || '?'
}

const inputClass = "w-full bg-background border border-border rounded-xl px-4 py-3 text-[15px] text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-white/20 transition"

const FIELD_LABELS: Record<string, string> = {
  primary_role: 'Primary Role', years_experience: 'Years Experience', hourly_rate: 'Hourly Rate ($)',
  availability_status: 'Availability', service_offerings: 'Services (comma-sep)', portfolio_url: 'Portfolio URL',
  cal_booking_link: 'Booking Link', certifications: 'Certifications (comma-sep)',
  domain_expertise: 'Expertise (comma-sep)', investment_thesis: 'Investment Thesis',
  portfolio_companies: 'Portfolio Companies', investment_stages: 'Investment Stages (comma-sep)',
  check_size_min: 'Min Check ($)', check_size_max: 'Max Check ($)', fee_structure: 'Fee Structure',
  availability: 'Availability', looking_for_roles: 'Looking For (comma-sep)',
  cofounder_brief: 'Co-founder Pitch', equity_offered: 'Equity Offered',
  startup_stage: 'Startup Stage', industry: 'Industry', commitment_level: 'Commitment',
  remote_ok: 'Remote OK', funding_stage: 'Funding Stage', employment_type_preference: 'Employment Type',
}

export function MarketplaceProfilePage() {
  const navigate = useNavigate()
  const [profile, setProfile] = useState<ProfileType | null>(null)
  const [visibility, setVisibility] = useState<VisibilitySettings | null>(null)
  const [loading, setLoading] = useState(true)
  const [noProfile, setNoProfile] = useState(false)
  const [editing, setEditing] = useState(false)
  const [editForm, setEditForm] = useState<Record<string, unknown>>({})
  const [typeEditForm, setTypeEditForm] = useState<Record<string, unknown>>({})
  const [msg, setMsg] = useState('')

  const flash = (m: string) => { setMsg(m); setTimeout(() => setMsg(''), 3000) }

  const fetchProfile = async () => {
    setLoading(true)
    try {
      const p = await marketplace.getMyProfile()
      setProfile(p)
      const v = await marketplace.getVisibility()
      setVisibility(v)
    } catch { setNoProfile(true) }
    finally { setLoading(false) }
  }

  useEffect(() => { fetchProfile() }, [])

  const handleSave = async () => {
    try {
      // Save base fields
      if (Object.keys(editForm).length > 0) {
        const p = await marketplace.updateProfile(editForm)
        setProfile(p)
      }
      // Save type-specific fields
      if (Object.keys(typeEditForm).length > 0 && profile) {
        const payload: Record<string, unknown> = {}
        payload[`${profile.profile_type}_data`] = typeEditForm
        const p = await marketplace.updateTypeData(payload)
        setProfile(p)
      }
      setEditing(false)
      flash('Changes saved!')
    } catch (err) { flash('Save failed: ' + (err instanceof Error ? err.message : 'Error')) }
  }

  const handleVisibility = async (updates: Partial<VisibilitySettings>) => {
    try {
      const v = await marketplace.updateVisibility(updates)
      setVisibility(v)
      if ('is_public' in updates) { await fetchProfile(); flash(updates.is_public ? 'Published!' : 'Unpublished') }
    } catch (err) { flash('Failed: ' + (err instanceof Error ? err.message : 'Error')) }
  }

  const handleDelete = async () => {
    if (!window.confirm('Delete your marketplace profile? This cannot be undone.')) return
    try { await marketplace.deleteProfile(); setProfile(null); setNoProfile(true) } catch { flash('Delete failed') }
  }

  if (loading) return (
    <div className="flex items-center justify-center py-20">
      <div className="w-8 h-8 border-2 border-white/30 border-t-zinc-300 rounded-full animate-spin" />
    </div>
  )

  if (noProfile) return (
    <div className="text-center py-20">
      <div className="w-20 h-20 rounded-full bg-white/10 flex items-center justify-center mx-auto mb-4">
        <User className="w-8 h-8 text-white/50" />
      </div>
      <h2 className="text-xl font-semibold text-white mb-2">No Profile Yet</h2>
      <p className="text-sm text-zinc-500 mb-6">Set up your marketplace profile to get discovered.</p>
      <button onClick={() => navigate('/login')}
        className="bg-white text-black px-6 py-2.5 rounded-xl text-sm font-semibold hover:bg-zinc-300 transition">
        Create Profile
      </button>
    </div>
  )

  if (!profile) return null
  const typeData = (profile.professional_data || profile.advisor_data || profile.founder_data || {}) as Record<string, unknown>

  return (
    <div className="max-w-3xl mx-auto">
      {/* Top bar (edit mode) */}
      {editing ? (
        <div className="flex items-center justify-between mb-6 bg-card border border-border rounded-xl px-4 py-3">
          <button onClick={() => { setEditing(false); setEditForm({}); setTypeEditForm({}) }}
            className="text-sm text-zinc-400 hover:text-zinc-200 flex items-center gap-1.5 transition">
            <X className="w-4 h-4" /> Cancel
          </button>
          <button onClick={handleSave}
            className="flex items-center gap-2 bg-white text-black px-4 py-1.5 rounded-lg text-sm font-semibold hover:bg-zinc-300 transition">
            <Save className="w-3.5 h-3.5" /> Save Changes
          </button>
        </div>
      ) : (
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-white">My Profile</h2>
          <div className="flex gap-2">
            <button onClick={() => setEditing(true)}
              className="text-sm text-zinc-400 hover:text-zinc-300 border border-white/[0.08] px-3 py-1.5 rounded-lg transition">
              Edit Profile
            </button>
            <button onClick={() => handleVisibility({ is_public: !profile.is_public })}
              className={cn('text-sm px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition',
                profile.is_public ? 'text-yellow-400 border border-yellow-500/20 hover:bg-yellow-500/10' : 'text-zinc-300 border border-white/20 hover:bg-white/10')}>
              {profile.is_public ? <><EyeOff className="w-3.5 h-3.5" /> Unpublish</> : <><Eye className="w-3.5 h-3.5" /> Publish</>}
            </button>
            <button onClick={handleDelete}
              className="text-sm text-red-400/70 border border-red-500/10 px-3 py-1.5 rounded-lg hover:bg-red-500/10 transition">
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      )}

      {msg && <div className="bg-white/10 border border-white/20 text-zinc-400 text-sm p-3 rounded-xl mb-4 animate-fade-in">{msg}</div>}

      {/* Avatar + Name header */}
      <div className="flex items-center gap-5 mb-6">
        <div
          className="w-20 h-20 rounded-xl shrink-0 flex items-center justify-center text-2xl font-bold text-white"
          style={{ background: avatarGradient(profile.headline || profile.id) }}
        >
          {nameInitials(profile.headline)}
        </div>
        <div>
          {editing ? (
            <input type="text" placeholder="Your headline" defaultValue={profile.headline || ''}
              onChange={e => setEditForm({ ...editForm, headline: e.target.value })}
              className="bg-transparent text-xl font-semibold text-white border-b border-white/20 pb-1 focus:outline-none focus:border-white/50 w-full" />
          ) : (
            <h3 className="text-xl font-semibold text-white">{profile.headline || '(no headline)'}</h3>
          )}
          <div className="flex items-center gap-3 mt-1">
            <span className="text-sm text-zinc-300 capitalize">{profile.profile_type}</span>
            <span className={cn('text-xs', profile.is_public ? 'text-emerald-400' : 'text-zinc-600')}>
              {profile.is_public ? 'Public' : 'Draft'}
            </span>
            <span className="text-xs text-zinc-600">{profile.profile_score}/100</span>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        {/* Basic Information */}
        <section className="rounded-2xl border border-border bg-card p-6">
          <h3 className="flex items-center gap-2 font-semibold text-[15px] mb-5">
            <User className="w-4 h-4 text-zinc-300" /> Basic Information
          </h3>
          {editing ? (
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-[11px] uppercase tracking-wider text-zinc-500 mb-1.5 block">Location</label>
                <input type="text" placeholder="City, Country" defaultValue={profile.location || ''}
                  onChange={e => setEditForm({ ...editForm, location: e.target.value })} className={inputClass} />
              </div>
              <div>
                <label className="text-[11px] uppercase tracking-wider text-zinc-500 mb-1.5 block">LinkedIn</label>
                <input type="url" placeholder="https://linkedin.com/in/..." defaultValue={profile.linkedin_url || ''}
                  onChange={e => setEditForm({ ...editForm, linkedin_url: e.target.value })} className={inputClass} />
              </div>
              <div>
                <label className="text-[11px] uppercase tracking-wider text-zinc-500 mb-1.5 block">Website</label>
                <input type="url" placeholder="https://..." defaultValue={profile.website_url || ''}
                  onChange={e => setEditForm({ ...editForm, website_url: e.target.value })} className={inputClass} />
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-y-3 gap-x-8 text-sm">
              <div className="flex items-center gap-2">
                <MapPin className="w-3.5 h-3.5 text-zinc-500 shrink-0" />
                <span className="text-zinc-300">{profile.location || '—'}</span>
              </div>
              <div className="flex items-center gap-2">
                <Link2 className="w-3.5 h-3.5 text-zinc-500 shrink-0" />
                {profile.linkedin_url ? (
                  <a href={profile.linkedin_url} target="_blank" rel="noopener" className="text-zinc-300 hover:underline truncate">{profile.linkedin_url.replace('https://linkedin.com/in/', '')}</a>
                ) : <span className="text-zinc-600">—</span>}
              </div>
            </div>
          )}
        </section>

        {/* About */}
        <section className="rounded-2xl border border-border bg-card p-6">
          <h3 className="flex items-center gap-2 font-semibold text-[15px] mb-4">
            <Info className="w-4 h-4 text-zinc-300" /> About
          </h3>
          {editing ? (
            <div className="space-y-4">
              <textarea placeholder="Tell others about yourself..." defaultValue={profile.bio || ''}
                onChange={e => setEditForm({ ...editForm, bio: e.target.value })}
                className={cn(inputClass, 'resize-none min-h-[120px]')} rows={5} />
              <div>
                <label className="text-[11px] uppercase tracking-wider text-zinc-500 mb-1.5 block">Skills</label>
                <input type="text" placeholder="python, react, strategy (comma-separated)" defaultValue={profile.skills?.join(', ') || ''}
                  onChange={e => setEditForm({ ...editForm, skills: e.target.value.split(',').map(s => s.trim()).filter(Boolean) })} className={inputClass} />
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="border-l-2 border-white/30 pl-4">
                <p className="text-sm text-zinc-300 leading-relaxed whitespace-pre-line">{profile.bio || 'No bio yet.'}</p>
              </div>
              {profile.skills?.length > 0 && (
                <div>
                  <p className="text-[11px] uppercase tracking-wider text-zinc-500 mb-2">Skills</p>
                  <div className="flex flex-wrap gap-1.5">
                    {profile.skills.map((s, i) => (
                      <span key={i} className="text-xs text-emerald-300/80 bg-emerald-500/10 border border-emerald-500/15 px-2.5 py-1 rounded-full">{s}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </section>

        {/* Type-specific details */}
        <section className="rounded-2xl border border-border bg-card p-6">
          <h3 className="flex items-center gap-2 font-semibold text-[15px] mb-5">
            {profile.profile_type === 'founder'
              ? <><Heart className="w-4 h-4 text-zinc-300" /> Co-founder Details</>
              : <><Briefcase className="w-4 h-4 text-zinc-300" /> {profile.profile_type === 'advisor' ? 'Advisory Details' : 'Professional Details'}</>
            }
          </h3>
          {editing ? (
            <div className="grid grid-cols-2 gap-3">
              {Object.entries(typeData).map(([key, val]) => (
                <div key={key} className={cn(key === 'cofounder_brief' || key === 'investment_thesis' ? 'col-span-2' : '')}>
                  <label className="text-[11px] uppercase tracking-wider text-zinc-500 mb-1.5 block">
                    {FIELD_LABELS[key] || key.replace(/_/g, ' ')}
                  </label>
                  {(key === 'cofounder_brief' || key === 'investment_thesis') ? (
                    <textarea defaultValue={String(val ?? '')}
                      onChange={e => setTypeEditForm({ ...typeEditForm, [key]: e.target.value })}
                      className={cn(inputClass, 'resize-none')} rows={3} />
                  ) : (
                    <input type="text"
                      defaultValue={Array.isArray(val) ? (val as string[]).join(', ') : String(val ?? '')}
                      onChange={e => {
                        const v = Array.isArray(val) ? e.target.value.split(',').map(s => s.trim()).filter(Boolean) : e.target.value
                        setTypeEditForm({ ...typeEditForm, [key]: v })
                      }}
                      className={inputClass} />
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-4">
              {Object.entries(typeData)
                .filter(([, v]) => v != null && v !== '' && !(Array.isArray(v) && (v as unknown[]).length === 0))
                .map(([key, val]) => (
                  <div key={key} className={cn(key === 'cofounder_brief' || key === 'investment_thesis' ? 'col-span-2' : '')}>
                    <p className="text-[11px] uppercase tracking-wider text-zinc-500 mb-1">
                      {FIELD_LABELS[key] || key.replace(/_/g, ' ')}
                    </p>
                    {key === 'cofounder_brief' || key === 'investment_thesis' ? (
                      <div className="border-l-2 border-white/30 pl-4">
                        <p className="text-sm text-zinc-300 leading-relaxed">{String(val)}</p>
                      </div>
                    ) : (
                      <p className="text-sm text-zinc-200 font-medium">
                        {Array.isArray(val) ? (val as string[]).join(', ') :
                         key.includes('rate') || key.includes('size') ? `$${Number(val).toLocaleString()}` :
                         String(val).replace(/_/g, ' ')}
                      </p>
                    )}
                  </div>
                ))}
            </div>
          )}
        </section>

        {/* Visibility Settings */}
        {visibility && (
          <section className="rounded-2xl border border-border bg-card p-6">
            <h3 className="flex items-center gap-2 font-semibold text-[15px] mb-4">
              <Settings className="w-4 h-4 text-zinc-300" /> Visibility
            </h3>
            <div className="grid grid-cols-2 gap-3">
              {(['show_email', 'show_phone', 'show_linkedin', 'show_location', 'discoverable_in_search'] as const).map(key => (
                <label key={key} className="flex items-center gap-2.5 text-sm text-zinc-400 cursor-pointer group">
                  <div className="relative">
                    <input type="checkbox" checked={visibility[key]}
                      onChange={e => handleVisibility({ [key]: e.target.checked })}
                      className="sr-only peer" />
                    <div className="w-9 h-5 bg-zinc-700 rounded-full peer-checked:bg-emerald-600 transition-colors duration-200" />
                    <div className="absolute top-[3px] left-[3px] w-[14px] h-[14px] bg-zinc-400 rounded-full shadow peer-checked:bg-white peer-checked:translate-x-4 transition-all duration-200" />
                  </div>
                  <span className="group-hover:text-zinc-200 transition capitalize">
                    {key.replace(/_/g, ' ').replace('show ', '')}
                  </span>
                </label>
              ))}
            </div>
          </section>
        )}

        {/* Documents */}
        <section className="rounded-2xl border border-border bg-card p-6">
          <button onClick={() => navigate('/marketplace/documents')}
            className="flex items-center gap-2 text-sm text-zinc-300 hover:text-zinc-400 transition w-full justify-center py-1">
            <FileText className="w-4 h-4" /> Manage Documents ({profile.documents?.length || 0})
          </button>
        </section>
      </div>
    </div>
  )
}
