import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { startOnboarding, saveOnboardingStep, getOnboardingStatus } from '../api';

const STEPS = {
  professional: [
    { num: 1, name: 'Basics', fields: ['headline', 'bio', 'avatar_url', 'location'] },
    { num: 2, name: 'Skills', fields: ['skills', 'primary_role', 'years_experience'] },
    { num: 3, name: 'Services', fields: ['service_offerings', 'hourly_rate', 'availability_status'] },
    { num: 4, name: 'Links', fields: ['linkedin_url', 'website_url', 'portfolio_url', 'cal_booking_link'] },
  ],
  advisor: [
    { num: 1, name: 'Basics', fields: ['headline', 'bio', 'avatar_url', 'location'] },
    { num: 2, name: 'Expertise', fields: ['skills', 'domain_expertise', 'investment_thesis'] },
    { num: 3, name: 'Investment', fields: ['investment_stages', 'check_size_min', 'check_size_max', 'fee_structure'] },
    { num: 4, name: 'Availability', fields: ['availability', 'cal_booking_link', 'linkedin_url', 'website_url'] },
  ],
  founder: [
    { num: 1, name: 'Basics', fields: ['headline', 'bio', 'avatar_url', 'location'] },
    { num: 2, name: 'Startup', fields: ['startup_stage', 'industry', 'funding_stage'] },
    { num: 3, name: 'Co-founder', fields: ['looking_for_roles', 'cofounder_brief', 'equity_offered', 'commitment_level'] },
    { num: 4, name: 'Links', fields: ['skills', 'linkedin_url', 'website_url'] },
  ],
};

// Fields that should be sent as arrays
const ARRAY_FIELDS = new Set(['skills', 'domain_expertise', 'investment_stages', 'looking_for_roles', 'service_offerings']);
// Fields that should be sent as numbers
const NUMBER_FIELDS = new Set(['years_experience', 'hourly_rate', 'check_size_min', 'check_size_max']);

const FIELD_LABELS = {
  headline: 'Headline',
  bio: 'Bio',
  avatar_url: 'Avatar URL',
  location: 'Location',
  skills: 'Skills (comma-separated)',
  primary_role: 'Primary Role',
  years_experience: 'Years of Experience',
  service_offerings: 'Service Offerings (comma-separated)',
  hourly_rate: 'Hourly Rate ($)',
  availability_status: 'Availability (available / busy / open_to_offers)',
  linkedin_url: 'LinkedIn URL',
  website_url: 'Website URL',
  portfolio_url: 'Portfolio URL',
  cal_booking_link: 'Cal.com Booking Link',
  domain_expertise: 'Domain Expertise (comma-separated)',
  investment_thesis: 'Investment Thesis',
  investment_stages: 'Investment Stages (comma-separated)',
  check_size_min: 'Min Check Size ($)',
  check_size_max: 'Max Check Size ($)',
  fee_structure: 'Fee Structure (hourly / retainer / equity / pro_bono)',
  availability: 'Availability (hours/week or open/closed)',
  startup_stage: 'Startup Stage (idea / pre_seed / seed / series_a)',
  industry: 'Industry (saas / fintech / ai_ml / ...)',
  funding_stage: 'Funding Stage',
  looking_for_roles: 'Looking for Roles (comma-separated)',
  cofounder_brief: 'Co-founder Brief',
  equity_offered: 'Equity Offered (e.g., 10-20%)',
  commitment_level: 'Commitment (full_time / part_time / flexible)',
};

export default function Onboarding({ onProfileChange }) {
  const navigate = useNavigate();
  const [profileType, setProfileType] = useState('');
  const [status, setStatus] = useState(null);
  const [currentStep, setCurrentStep] = useState(1);
  const [stepData, setStepData] = useState({});
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleStart = async (type) => {
    setLoading(true);
    setError('');
    try {
      const res = await startOnboarding(type);
      setProfileType(type);
      setStatus(res.data);
      setCurrentStep(1);
      onProfileChange?.(true);
    } catch (err) {
      if (err.response?.status === 409) {
        // Already has a profile — try to resume
        try {
          const res = await getOnboardingStatus();
          setStatus(res.data);
          setProfileType(res.data.profile_type);
        } catch {
          setError('Profile already exists. Go to My Profile to edit it.');
        }
      } else {
        setError(err.response?.data?.detail || 'Failed to start onboarding');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSaveStep = async () => {
    setLoading(true);
    setError('');
    try {
      // Convert field values to proper types
      const processed = {};
      for (const [key, val] of Object.entries(stepData)) {
        if (!val && val !== false) continue;
        if (ARRAY_FIELDS.has(key)) {
          processed[key] = val.split(',').map(s => s.trim()).filter(Boolean);
        } else if (NUMBER_FIELDS.has(key)) {
          processed[key] = parseFloat(val);
        } else {
          processed[key] = val;
        }
      }

      const res = await saveOnboardingStep(currentStep, processed);
      setStatus(res.data);
      setStepData({});

      if (res.data.is_complete) {
        // Done!
      } else if (currentStep < 4) {
        setCurrentStep(currentStep + 1);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save step');
    } finally {
      setLoading(false);
    }
  };

  const handleResume = async () => {
    setError('');
    try {
      const res = await getOnboardingStatus();
      setStatus(res.data);
      setProfileType(res.data.profile_type);
      const completed = res.data.completed_steps || [];
      setCurrentStep(completed.length < 4 ? Math.max(...completed, 0) + 1 : 4);
    } catch (err) {
      setError('No onboarding in progress. Start one above.');
    }
  };

  // Type selection screen
  if (!profileType) {
    return (
      <div className="max-w-lg mx-auto">
        <h2 className="text-2xl font-bold mb-2">Guided Onboarding</h2>
        <p className="text-sm text-gray-500 mb-6">Choose your profile type to begin the step-by-step setup.</p>

        <div className="space-y-3">
          {[
            { type: 'professional', icon: '💼', desc: 'Showcase your skills and find work with startups' },
            { type: 'advisor', icon: '🎯', desc: 'Offer expertise, mentorship, and investment' },
            { type: 'founder', icon: '🚀', desc: 'Find co-founders and build your team' },
          ].map(({ type, icon, desc }) => (
            <button key={type} onClick={() => handleStart(type)} disabled={loading}
              className="w-full text-left border rounded-lg p-4 hover:bg-gray-50 transition flex items-start gap-3">
              <span className="text-2xl">{icon}</span>
              <div>
                <span className="font-semibold capitalize">{type}</span>
                <p className="text-xs text-gray-500 mt-0.5">{desc}</p>
              </div>
            </button>
          ))}
        </div>

        <button onClick={handleResume} className="mt-4 text-sm text-blue-600 hover:underline">
          Resume existing onboarding
        </button>

        {error && <div className="bg-red-50 text-red-700 text-sm p-3 rounded mt-4">{error}</div>}
      </div>
    );
  }

  // Step-by-step wizard
  const steps = STEPS[profileType] || [];
  const step = steps.find(s => s.num === currentStep);
  const isComplete = status?.is_complete;

  return (
    <div className="max-w-lg mx-auto">
      <h2 className="text-2xl font-bold mb-1">Onboarding: <span className="capitalize">{profileType}</span></h2>
      <p className="text-sm text-gray-500 mb-4">
        {isComplete ? 'All steps complete! Your profile is ready.' : `Step ${currentStep} of 4`}
      </p>

      {/* Step indicators */}
      <div className="flex gap-2 mb-6">
        {steps.map(s => (
          <button key={s.num}
            onClick={() => { setCurrentStep(s.num); setStepData({}); setError(''); }}
            className={`flex-1 text-center py-2.5 rounded-lg text-xs font-medium transition ${
              s.num === currentStep
                ? 'bg-blue-600 text-white shadow-sm'
                : status?.completed_steps?.includes(s.num)
                ? 'bg-green-100 text-green-800 border border-green-200'
                : 'bg-gray-100 text-gray-500'
            }`}>
            {s.num}. {s.name}
            {status?.completed_steps?.includes(s.num) && s.num !== currentStep && ' ✓'}
          </button>
        ))}
      </div>

      {/* Completion banner */}
      {isComplete && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
          <p className="text-green-800 font-medium">Onboarding complete!</p>
          <p className="text-green-600 text-sm mt-1">
            Score: {status.profile_score}/100. Go to your profile to publish it.
          </p>
          <button onClick={() => navigate('/')}
            className="mt-3 bg-green-600 text-white px-4 py-2 rounded text-sm hover:bg-green-700">
            View My Profile
          </button>
        </div>
      )}

      {/* Step form */}
      {step && (
        <div className="bg-white border rounded-lg p-4 space-y-4">
          <h3 className="font-semibold">Step {step.num}: {step.name}</h3>
          {step.fields.map(field => (
            <div key={field}>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                {FIELD_LABELS[field] || field.replace(/_/g, ' ')}
              </label>
              {field === 'bio' || field === 'investment_thesis' || field === 'cofounder_brief' ? (
                <textarea value={stepData[field] || ''}
                  onChange={(e) => setStepData({ ...stepData, [field]: e.target.value })}
                  className="w-full border rounded px-3 py-2 text-sm" rows={3}
                  placeholder={FIELD_LABELS[field] || field} />
              ) : (
                <input type={NUMBER_FIELDS.has(field) ? 'number' : 'text'}
                  step={field.includes('rate') || field.includes('size') ? '0.01' : undefined}
                  value={stepData[field] || ''}
                  onChange={(e) => setStepData({ ...stepData, [field]: e.target.value })}
                  className="w-full border rounded px-3 py-2 text-sm"
                  placeholder={FIELD_LABELS[field] || field} />
              )}
            </div>
          ))}

          <div className="flex gap-3 pt-2">
            {currentStep > 1 && (
              <button onClick={() => { setCurrentStep(currentStep - 1); setStepData({}); }}
                className="border border-gray-300 text-gray-700 px-4 py-2 rounded text-sm hover:bg-gray-50">
                Back
              </button>
            )}
            <button onClick={handleSaveStep} disabled={loading}
              className="flex-1 bg-blue-600 text-white px-4 py-2 rounded text-sm font-medium hover:bg-blue-700 disabled:opacity-50">
              {loading ? 'Saving...' : currentStep === 4 ? 'Complete' : 'Save & Continue'}
            </button>
          </div>
        </div>
      )}

      {/* Status bar */}
      {status && (
        <div className="mt-4 bg-gray-50 rounded-lg p-3 flex items-center justify-between">
          <div className="text-xs text-gray-500">
            Score: <span className="font-medium text-gray-700">{status.profile_score}</span>/100
            &nbsp;&middot;&nbsp;
            Steps: {status.completed_steps?.join(', ') || 'none'}
          </div>
          <div className="w-32 bg-gray-200 rounded-full h-2">
            <div className="bg-blue-600 h-2 rounded-full transition-all"
              style={{ width: `${(status.completed_steps?.length || 0) * 25}%` }} />
          </div>
        </div>
      )}

      {error && <div className="bg-red-50 text-red-700 text-sm p-3 rounded mt-4">{error}</div>}
    </div>
  );
}
