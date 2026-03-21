import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createProfile } from '../api';

const PROFILE_TYPES = [
  { value: 'professional', label: 'Professional', desc: 'Showcase your skills and find work with startups', color: 'blue' },
  { value: 'advisor', label: 'Advisor', desc: 'Offer expertise, mentorship, and investment to startups', color: 'purple' },
  { value: 'founder', label: 'Founder', desc: 'Find co-founders and build your team', color: 'orange' },
];

export default function CreateProfile({ onProfileChange }) {
  const navigate = useNavigate();
  const [profileType, setProfileType] = useState('professional');
  const [form, setForm] = useState({ headline: '', bio: '', location: '', skills: '', linkedin_url: '', website_url: '' });
  const [typeData, setTypeData] = useState({});
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const set = (field) => (e) => setForm({ ...form, [field]: e.target.value });
  const setTD = (field) => (e) => setTypeData({ ...typeData, [field]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const payload = {
        profile_type: profileType,
        headline: form.headline,
        bio: form.bio || undefined,
        location: form.location || undefined,
        skills: form.skills ? form.skills.split(',').map(s => s.trim()).filter(Boolean) : [],
        linkedin_url: form.linkedin_url || undefined,
        website_url: form.website_url || undefined,
      };

      if (profileType === 'professional') {
        payload.professional_data = {
          primary_role: typeData.primary_role || undefined,
          years_experience: typeData.years_experience ? parseInt(typeData.years_experience) : undefined,
          hourly_rate: typeData.hourly_rate ? parseFloat(typeData.hourly_rate) : undefined,
          availability_status: typeData.availability_status || undefined,
          service_offerings: typeData.service_offerings ? typeData.service_offerings.split(',').map(s => s.trim()) : undefined,
          portfolio_url: typeData.portfolio_url || undefined,
          cal_booking_link: typeData.cal_booking_link || undefined,
        };
      } else if (profileType === 'advisor') {
        payload.advisor_data = {
          domain_expertise: typeData.domain_expertise ? typeData.domain_expertise.split(',').map(s => s.trim()) : undefined,
          investment_thesis: typeData.investment_thesis || undefined,
          fee_structure: typeData.fee_structure || undefined,
          investment_stages: typeData.investment_stages ? typeData.investment_stages.split(',').map(s => s.trim()) : undefined,
          check_size_min: typeData.check_size_min ? parseFloat(typeData.check_size_min) : undefined,
          check_size_max: typeData.check_size_max ? parseFloat(typeData.check_size_max) : undefined,
          cal_booking_link: typeData.cal_booking_link || undefined,
        };
      } else if (profileType === 'founder') {
        payload.founder_data = {
          looking_for_roles: typeData.looking_for_roles ? typeData.looking_for_roles.split(',').map(s => s.trim()) : undefined,
          cofounder_brief: typeData.cofounder_brief || undefined,
          commitment_level: typeData.commitment_level || undefined,
          equity_offered: typeData.equity_offered || undefined,
          remote_ok: typeData.remote_ok === 'true' ? true : typeData.remote_ok === 'false' ? false : undefined,
        };
      }

      await createProfile(payload);
      onProfileChange?.(true);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create profile');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold mb-6">Create Marketplace Profile</h2>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Type selector */}
        <div className="grid grid-cols-3 gap-3">
          {PROFILE_TYPES.map(t => (
            <button key={t.value} type="button"
              onClick={() => { setProfileType(t.value); setTypeData({}); }}
              className={`p-3 rounded-lg border-2 text-left transition ${
                profileType === t.value ? `border-${t.color}-500 bg-${t.color}-50` : 'border-gray-200 hover:border-gray-300'
              }`}>
              <span className="font-semibold text-sm">{t.label}</span>
              <p className="text-xs text-gray-500 mt-1">{t.desc}</p>
            </button>
          ))}
        </div>

        {/* Base fields */}
        <div className="bg-white rounded-lg border p-4 space-y-3">
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide">Basic Info</h3>
          <input type="text" placeholder="Headline *" value={form.headline}
            onChange={set('headline')} className="w-full border rounded px-3 py-2 text-sm" required />
          <textarea placeholder="Bio — tell people about yourself" value={form.bio}
            onChange={set('bio')} className="w-full border rounded px-3 py-2 text-sm" rows={3} />
          <div className="grid grid-cols-2 gap-3">
            <input type="text" placeholder="Location" value={form.location} onChange={set('location')} className="border rounded px-3 py-2 text-sm" />
            <input type="text" placeholder="Skills (comma-separated)" value={form.skills} onChange={set('skills')} className="border rounded px-3 py-2 text-sm" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <input type="url" placeholder="LinkedIn URL" value={form.linkedin_url} onChange={set('linkedin_url')} className="border rounded px-3 py-2 text-sm" />
            <input type="url" placeholder="Website URL" value={form.website_url} onChange={set('website_url')} className="border rounded px-3 py-2 text-sm" />
          </div>
        </div>

        {/* Professional fields */}
        {profileType === 'professional' && (
          <div className="bg-white rounded-lg border p-4 space-y-3">
            <h3 className="text-sm font-semibold text-blue-600 uppercase tracking-wide">Professional Details</h3>
            <div className="grid grid-cols-2 gap-3">
              <input type="text" placeholder="Primary Role (e.g., Backend Developer)" value={typeData.primary_role || ''} onChange={setTD('primary_role')} className="border rounded px-3 py-2 text-sm" />
              <input type="number" placeholder="Years of Experience" value={typeData.years_experience || ''} onChange={setTD('years_experience')} className="border rounded px-3 py-2 text-sm" />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <input type="number" step="0.01" placeholder="Hourly Rate ($)" value={typeData.hourly_rate || ''} onChange={setTD('hourly_rate')} className="border rounded px-3 py-2 text-sm" />
              <select value={typeData.availability_status || ''} onChange={setTD('availability_status')} className="border rounded px-3 py-2 text-sm">
                <option value="">Availability Status</option>
                <option value="available">Available</option>
                <option value="busy">Busy</option>
                <option value="open_to_offers">Open to Offers</option>
                <option value="not_available">Not Available</option>
              </select>
            </div>
            <input type="text" placeholder="Service Offerings (comma-separated)" value={typeData.service_offerings || ''} onChange={setTD('service_offerings')} className="w-full border rounded px-3 py-2 text-sm" />
            <div className="grid grid-cols-2 gap-3">
              <input type="url" placeholder="Portfolio URL" value={typeData.portfolio_url || ''} onChange={setTD('portfolio_url')} className="border rounded px-3 py-2 text-sm" />
              <input type="url" placeholder="Cal.com Booking Link" value={typeData.cal_booking_link || ''} onChange={setTD('cal_booking_link')} className="border rounded px-3 py-2 text-sm" />
            </div>
          </div>
        )}

        {/* Advisor fields */}
        {profileType === 'advisor' && (
          <div className="bg-white rounded-lg border p-4 space-y-3">
            <h3 className="text-sm font-semibold text-purple-600 uppercase tracking-wide">Advisor Details</h3>
            <input type="text" placeholder="Domain Expertise (comma-separated)" value={typeData.domain_expertise || ''} onChange={setTD('domain_expertise')} className="w-full border rounded px-3 py-2 text-sm" />
            <textarea placeholder="Investment Thesis" value={typeData.investment_thesis || ''} onChange={setTD('investment_thesis')} className="w-full border rounded px-3 py-2 text-sm" rows={2} />
            <div className="grid grid-cols-2 gap-3">
              <input type="text" placeholder="Investment Stages (comma-separated)" value={typeData.investment_stages || ''} onChange={setTD('investment_stages')} className="border rounded px-3 py-2 text-sm" />
              <select value={typeData.fee_structure || ''} onChange={setTD('fee_structure')} className="border rounded px-3 py-2 text-sm">
                <option value="">Fee Structure</option>
                <option value="hourly">Hourly</option>
                <option value="retainer">Retainer</option>
                <option value="equity">Equity</option>
                <option value="pro_bono">Pro Bono</option>
                <option value="success_fee">Success Fee</option>
              </select>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <input type="number" placeholder="Min Check Size ($)" value={typeData.check_size_min || ''} onChange={setTD('check_size_min')} className="border rounded px-3 py-2 text-sm" />
              <input type="number" placeholder="Max Check Size ($)" value={typeData.check_size_max || ''} onChange={setTD('check_size_max')} className="border rounded px-3 py-2 text-sm" />
            </div>
            <input type="url" placeholder="Cal.com Booking Link" value={typeData.cal_booking_link || ''} onChange={setTD('cal_booking_link')} className="w-full border rounded px-3 py-2 text-sm" />
          </div>
        )}

        {/* Founder fields */}
        {profileType === 'founder' && (
          <div className="bg-white rounded-lg border p-4 space-y-3">
            <h3 className="text-sm font-semibold text-orange-600 uppercase tracking-wide">Co-founder Details</h3>
            <input type="text" placeholder="Looking for Roles (comma-separated, e.g., CTO, Designer)" value={typeData.looking_for_roles || ''} onChange={setTD('looking_for_roles')} className="w-full border rounded px-3 py-2 text-sm" />
            <textarea placeholder="Co-founder Brief — why should someone join you?" value={typeData.cofounder_brief || ''} onChange={setTD('cofounder_brief')} className="w-full border rounded px-3 py-2 text-sm" rows={3} />
            <div className="grid grid-cols-2 gap-3">
              <input type="text" placeholder="Equity Offered (e.g., 10-20%)" value={typeData.equity_offered || ''} onChange={setTD('equity_offered')} className="border rounded px-3 py-2 text-sm" />
              <select value={typeData.commitment_level || ''} onChange={setTD('commitment_level')} className="border rounded px-3 py-2 text-sm">
                <option value="">Commitment Level</option>
                <option value="full_time">Full Time</option>
                <option value="part_time">Part Time</option>
                <option value="flexible">Flexible</option>
                <option value="advisory">Advisory</option>
              </select>
            </div>
            <select value={typeData.remote_ok || ''} onChange={setTD('remote_ok')} className="w-full border rounded px-3 py-2 text-sm">
              <option value="">Remote OK?</option>
              <option value="true">Yes</option>
              <option value="false">No</option>
            </select>
          </div>
        )}

        {error && <div className="bg-red-50 text-red-700 text-sm p-3 rounded">{error}</div>}

        <button type="submit" disabled={loading}
          className="w-full bg-blue-600 text-white py-2.5 rounded text-sm font-medium hover:bg-blue-700 disabled:opacity-50">
          {loading ? 'Creating...' : 'Create Profile'}
        </button>
      </form>
    </div>
  );
}
