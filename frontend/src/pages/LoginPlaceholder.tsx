import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Zap, ArrowRight, Check } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useAuth } from '@/lib/auth'
import { marketplace } from '@/lib/api'
import type { OnboardingStatus } from '@/lib/api'

// ── Step definitions per profile type ─────────────────────────────

const STEPS: Record<string, { num: number; name: string; fields: string[] }[]> = {
  professional: [
    { num: 1, name: 'Basics', fields: ['headline', 'bio', 'location'] },
    { num: 2, name: 'Skills', fields: ['skills', 'primary_role', 'years_experience'] },
    { num: 3, name: 'Services', fields: ['service_offerings', 'hourly_rate', 'availability_status'] },
    { num: 4, name: 'Links', fields: ['linkedin_url', 'website_url', 'portfolio_url', 'cal_booking_link'] },
  ],
  advisor: [
    { num: 1, name: 'Basics', fields: ['headline', 'bio', 'location'] },
    { num: 2, name: 'Expertise', fields: ['skills', 'domain_expertise', 'investment_thesis'] },
    { num: 3, name: 'Investment', fields: ['investment_stages', 'check_size_min', 'check_size_max', 'fee_structure'] },
    { num: 4, name: 'Links', fields: ['availability', 'cal_booking_link', 'linkedin_url', 'website_url'] },
  ],
  founder: [
    { num: 1, name: 'Basics', fields: ['headline', 'bio', 'location'] },
    { num: 2, name: 'Startup', fields: ['startup_stage', 'industry', 'funding_stage'] },
    { num: 3, name: 'Co-founder', fields: ['looking_for_roles', 'cofounder_brief', 'equity_offered', 'commitment_level'] },
    { num: 4, name: 'Links', fields: ['skills', 'linkedin_url', 'website_url'] },
  ],
}

const ARRAY_FIELDS = new Set(['skills', 'domain_expertise', 'investment_stages', 'looking_for_roles', 'service_offerings'])
const NUMBER_FIELDS = new Set(['years_experience', 'hourly_rate', 'check_size_min', 'check_size_max'])
const TEXTAREA_FIELDS = new Set(['bio', 'investment_thesis', 'cofounder_brief'])

const LABELS: Record<string, string> = {
  headline: 'Your professional headline', bio: 'Tell us about yourself', location: 'Where are you based?',
  skills: 'Skills (comma-separated)', primary_role: 'Primary Role', years_experience: 'Years of Experience',
  service_offerings: 'What services do you offer? (comma-sep)', hourly_rate: 'Hourly Rate ($)',
  availability_status: 'Availability (available / busy / open_to_offers)',
  linkedin_url: 'LinkedIn URL', website_url: 'Website URL', portfolio_url: 'Portfolio URL',
  cal_booking_link: 'Booking Link (Cal.com)', domain_expertise: 'Domain Expertise (comma-sep)',
  investment_thesis: 'Your investment thesis', investment_stages: 'Investment Stages (comma-sep)',
  check_size_min: 'Min Check Size ($)', check_size_max: 'Max Check Size ($)',
  fee_structure: 'Fee Structure (hourly / equity / retainer / pro_bono)',
  availability: 'Availability (hours/week)', startup_stage: 'Startup Stage (idea / pre_seed / seed)',
  industry: 'Industry (saas / fintech / healthtech)', funding_stage: 'Funding Stage',
  looking_for_roles: 'Roles you need (comma-sep)', cofounder_brief: 'Why should someone join you?',
  equity_offered: 'Equity Offered (e.g. 10-20%)', commitment_level: 'Commitment (full_time / part_time / flexible)',
}

// ── Phases: auth → pick type → onboarding steps → done ────────────

type Phase = 'auth' | 'pick_type' | 'onboarding' | 'done'

const inputClass = "w-full bg-black/50 border border-white/[0.08] rounded-lg px-3 py-2.5 text-sm text-white placeholder:text-zinc-600 focus:outline-none focus:border-white/20"

export function LoginPlaceholder() {
  const navigate = useNavigate()
  const { login, register, refreshProfile } = useAuth()

  // Auth state
  const [isRegister, setIsRegister] = useState(false)
  const [authForm, setAuthForm] = useState({ email: '', password: '', first_name: '', last_name: '' })

  // Flow state
  const [phase, setPhase] = useState<Phase>('auth')
  const [profileType, setProfileType] = useState('')
  const [onboardingStatus, setOnboardingStatus] = useState<OnboardingStatus | null>(null)
  const [currentStep, setCurrentStep] = useState(1)
  const [stepData, setStepData] = useState<Record<string, string>>({})

  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const setAuth = (f: string) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setAuthForm({ ...authForm, [f]: e.target.value })

  // ── Auth submit ──────────────────────────────────────────────────

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(''); setLoading(true)
    try {
      if (isRegister) {
        await register({
          email: authForm.email,
          password: authForm.password,
          first_name: authForm.first_name,
          last_name: authForm.last_name,
        })
        // New user → go to type selection
        setPhase('pick_type')
      } else {
        await login(authForm.email, authForm.password)
        // Existing user → check if they have a profile
        try {
          await marketplace.getMyProfile()
          navigate('/') // Has profile, go to app
        } catch {
          setPhase('pick_type') // No profile, onboard
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally { setLoading(false) }
  }

  // ── Type selection ───────────────────────────────────────────────

  const handleTypeSelect = async (type: string) => {
    setError(''); setLoading(true)
    try {
      const status = await marketplace.startOnboarding(type)
      setProfileType(type)
      setOnboardingStatus(status)
      setCurrentStep(1)
      setPhase('onboarding')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed')
    } finally { setLoading(false) }
  }

  // ── Step save ────────────────────────────────────────────────────

  const handleSaveStep = async () => {
    setError(''); setLoading(true)
    try {
      const processed: Record<string, unknown> = {}
      for (const [k, v] of Object.entries(stepData)) {
        if (!v && v !== 'false') continue
        if (ARRAY_FIELDS.has(k)) processed[k] = v.split(',').map(s => s.trim()).filter(Boolean)
        else if (NUMBER_FIELDS.has(k)) processed[k] = parseFloat(v)
        else processed[k] = v
      }

      const status = await marketplace.saveStep(currentStep, processed)
      setOnboardingStatus(status)
      setStepData({})

      if (status.is_complete) {
        // Publish profile automatically
        await marketplace.updateVisibility({ is_public: true })
        await refreshProfile()
        setPhase('done')
      } else if (currentStep < 4) {
        setCurrentStep(currentStep + 1)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed')
    } finally { setLoading(false) }
  }

  // ── Render: Auth phase ───────────────────────────────────────────

  if (phase === 'auth') return (
    <div className="min-h-screen bg-black flex flex-col items-center justify-center px-6">
      <div className="w-full max-w-sm">
        <div className="flex items-center gap-2 justify-center mb-8">
          <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-white text-black">
            <Zap className="w-4 h-4" strokeWidth={2.5} />
          </div>
          <span className="text-lg font-semibold text-white">OnlyFounders</span>
        </div>

        <div className="bg-[#1a1a1a] border border-white/[0.06] rounded-2xl p-6">
          <h2 className="text-lg font-semibold text-white mb-1">
            {isRegister ? 'Create Account' : 'Welcome Back'}
          </h2>
          <p className="text-sm text-zinc-500 mb-6">
            {isRegister ? 'Sign up and set up your marketplace profile' : 'Login to your workspace'}
          </p>

          <form onSubmit={handleAuth} className="space-y-3">
            {isRegister && (
              <div className="grid grid-cols-2 gap-2">
                <input type="text" placeholder="First Name" value={authForm.first_name} onChange={setAuth('first_name')}
                  className={inputClass} required />
                <input type="text" placeholder="Last Name" value={authForm.last_name} onChange={setAuth('last_name')}
                  className={inputClass} required />
              </div>
            )}
            <input type="email" placeholder="Email" value={authForm.email} onChange={setAuth('email')}
              className={inputClass} required />
            <input type="password" placeholder="Password" value={authForm.password} onChange={setAuth('password')}
              className={inputClass} required />

            {error && <div className="text-red-400 text-xs bg-red-500/10 rounded-lg p-2.5">{error}</div>}

            <button type="submit" disabled={loading}
              className="w-full bg-white text-black py-2.5 rounded-lg text-sm font-medium hover:bg-zinc-200 transition disabled:opacity-50 flex items-center justify-center gap-2">
              {loading ? 'Loading...' : isRegister ? <>Create Account <ArrowRight className="w-4 h-4" /></> : 'Login'}
            </button>
          </form>

          <p className="mt-4 text-sm text-zinc-500 text-center">
            {isRegister ? 'Already have an account?' : "Don't have an account?"}{' '}
            <button onClick={() => { setIsRegister(!isRegister); setError('') }}
              className="text-white hover:underline">
              {isRegister ? 'Login' : 'Register'}
            </button>
          </p>
        </div>
      </div>
    </div>
  )

  // ── Render: Pick type ────────────────────────────────────────────

  if (phase === 'pick_type') return (
    <div className="min-h-screen bg-black flex flex-col items-center justify-center px-6">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h2 className="text-xl font-semibold text-white">What describes you best?</h2>
          <p className="text-sm text-zinc-500 mt-1">This shapes your marketplace profile and what others see.</p>
        </div>

        <div className="space-y-3">
          {[
            { type: 'professional', label: 'Professional', desc: 'I offer skills and services to startups', icon: '💼' },
            { type: 'advisor', label: 'Advisor / Investor', desc: 'I mentor startups or invest in them', icon: '🎯' },
            { type: 'founder', label: 'Founder', desc: "I'm building a startup and looking for co-founders", icon: '🚀' },
          ].map(({ type, label, desc, icon }) => (
            <button key={type} onClick={() => handleTypeSelect(type)} disabled={loading}
              className="w-full text-left bg-[#1a1a1a] border border-white/[0.06] rounded-xl p-4 hover:bg-[#222] hover:border-white/[0.12] transition flex items-center gap-4">
              <span className="text-2xl">{icon}</span>
              <div>
                <span className="font-semibold text-white">{label}</span>
                <p className="text-xs text-zinc-500 mt-0.5">{desc}</p>
              </div>
              <ArrowRight className="w-4 h-4 text-zinc-600 ml-auto" />
            </button>
          ))}
        </div>

        {error && <div className="text-red-400 text-sm bg-red-500/10 rounded-xl p-3 mt-4">{error}</div>}
      </div>
    </div>
  )

  // ── Render: Onboarding steps ─────────────────────────────────────

  if (phase === 'onboarding') {
    const steps = STEPS[profileType] || []
    const step = steps.find(s => s.num === currentStep)

    return (
      <div className="min-h-screen bg-black flex flex-col items-center justify-center px-6">
        <div className="w-full max-w-md">
          {/* Progress */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-zinc-500 capitalize">{profileType} profile</span>
              <span className="text-xs text-zinc-600">Step {currentStep} of 4</span>
            </div>
            <div className="flex gap-1.5">
              {steps.map(s => (
                <div key={s.num} className={cn(
                  'flex-1 h-1.5 rounded-full transition-all',
                  s.num < currentStep ? 'bg-emerald-500' :
                  s.num === currentStep ? 'bg-white' :
                  'bg-zinc-800',
                )} />
              ))}
            </div>
          </div>

          {step && (
            <div className="bg-[#1a1a1a] border border-white/[0.06] rounded-2xl p-6">
              <h2 className="text-lg font-semibold text-white mb-1">{step.name}</h2>
              <p className="text-sm text-zinc-500 mb-5">
                {currentStep === 1 && 'Let people know who you are.'}
                {currentStep === 2 && 'What do you bring to the table?'}
                {currentStep === 3 && 'Details that help startups find you.'}
                {currentStep === 4 && 'Where can people reach you?'}
              </p>

              <div className="space-y-3">
                {step.fields.map(field => (
                  <div key={field}>
                    <label className="block text-xs text-zinc-500 mb-1.5">{LABELS[field] || field.replace(/_/g, ' ')}</label>
                    {TEXTAREA_FIELDS.has(field) ? (
                      <textarea value={stepData[field] || ''}
                        onChange={e => setStepData({ ...stepData, [field]: e.target.value })}
                        className={cn(inputClass, 'resize-none')} rows={3} placeholder={LABELS[field] || field} />
                    ) : (
                      <input type={NUMBER_FIELDS.has(field) ? 'number' : 'text'}
                        step={field.includes('rate') || field.includes('size') ? '0.01' : undefined}
                        value={stepData[field] || ''}
                        onChange={e => setStepData({ ...stepData, [field]: e.target.value })}
                        className={inputClass} placeholder={LABELS[field] || field} />
                    )}
                  </div>
                ))}
              </div>

              {error && <div className="text-red-400 text-xs bg-red-500/10 rounded-lg p-2.5 mt-3">{error}</div>}

              <div className="flex gap-2 mt-5">
                {currentStep > 1 && (
                  <button onClick={() => { setCurrentStep(currentStep - 1); setStepData({}); setError('') }}
                    className="border border-white/[0.1] text-zinc-300 px-4 py-2.5 rounded-lg text-sm hover:bg-white/[0.04] transition">
                    Back
                  </button>
                )}
                <button onClick={handleSaveStep} disabled={loading}
                  className="flex-1 bg-white text-black px-4 py-2.5 rounded-lg text-sm font-medium hover:bg-zinc-200 transition disabled:opacity-50 flex items-center justify-center gap-2">
                  {loading ? 'Saving...' : currentStep === 4 ? <>Complete <Check className="w-4 h-4" /></> : <>Continue <ArrowRight className="w-4 h-4" /></>}
                </button>
              </div>

              <button onClick={() => { handleSaveStep(); navigate('/') }}
                className="w-full text-center text-xs text-zinc-600 hover:text-zinc-400 mt-3 py-1">
                Skip for now
              </button>
            </div>
          )}
        </div>
      </div>
    )
  }

  // ── Render: Done ─────────────────────────────────────────────────

  return (
    <div className="min-h-screen bg-black flex flex-col items-center justify-center px-6">
      <div className="w-full max-w-sm text-center">
        <div className="w-16 h-16 rounded-full bg-emerald-500/20 flex items-center justify-center mx-auto mb-6">
          <Check className="w-8 h-8 text-emerald-400" />
        </div>
        <h2 className="text-xl font-semibold text-white mb-2">You're all set!</h2>
        <p className="text-sm text-zinc-500 mb-2">
          Profile score: <span className="text-white font-medium">{onboardingStatus?.profile_score || 0}/100</span>
        </p>
        <p className="text-xs text-zinc-600 mb-8">Your profile is live on the marketplace.</p>
        <button onClick={() => navigate('/')}
          className="bg-white text-black px-6 py-2.5 rounded-xl text-sm font-medium hover:bg-zinc-200 transition">
          Enter Workspace
        </button>
      </div>
    </div>
  )
}
