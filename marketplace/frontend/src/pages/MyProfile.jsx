import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getMyProfile, updateProfile, updateTypeData, updateVisibility, deleteProfile, getVisibility } from '../api';

const TYPE_COLORS = {
  professional: { bg: 'bg-blue-100', text: 'text-blue-800' },
  advisor: { bg: 'bg-purple-100', text: 'text-purple-800' },
  founder: { bg: 'bg-orange-100', text: 'text-orange-800' },
};

function ScoreBadge({ score }) {
  const tier = score >= 86 ? 'All-Star' : score >= 61 ? 'Strong' : score >= 31 ? 'Rising' : 'Getting Started';
  const color = score >= 61 ? 'text-green-700 bg-green-50' : score >= 31 ? 'text-yellow-700 bg-yellow-50' : 'text-gray-600 bg-gray-100';
  return (
    <span className={`text-xs font-medium px-2 py-0.5 rounded ${color}`}>
      {score}/100 — {tier}
    </span>
  );
}

function TypeDataDisplay({ profile }) {
  const { profile_type, professional_data, advisor_data, founder_data } = profile;
  const data = professional_data || advisor_data || founder_data;
  if (!data) return null;

  const fields = Object.entries(data).filter(([, v]) => v != null && v !== '' && !(Array.isArray(v) && v.length === 0));

  return (
    <div className="p-4">
      <h4 className="text-xs font-semibold text-gray-400 uppercase mb-2">{profile_type} Details</h4>
      <dl className="grid grid-cols-2 gap-x-4 gap-y-1 text-sm">
        {fields.map(([key, val]) => (
          <div key={key} className="contents">
            <dt className="text-gray-500">{key.replace(/_/g, ' ')}</dt>
            <dd className="text-gray-900">{Array.isArray(val) ? val.join(', ') : String(val)}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}

export default function MyProfile({ onProfileChange }) {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [editing, setEditing] = useState(false);
  const [editingType, setEditingType] = useState(false);
  const [editForm, setEditForm] = useState({});
  const [typeEditForm, setTypeEditForm] = useState({});
  const [visibility, setVisibility] = useState(null);
  const [actionMsg, setActionMsg] = useState('');

  const flash = (msg) => { setActionMsg(msg); setTimeout(() => setActionMsg(''), 3000); };

  const fetchProfile = async () => {
    setLoading(true);
    try {
      const res = await getMyProfile();
      setProfile(res.data);
      const vis = await getVisibility();
      setVisibility(vis.data);
    } catch (err) {
      if (err.response?.status === 404) setError('no_profile');
      else if (err.response?.status === 401) setError('not_logged_in');
      else setError(err.response?.data?.detail || 'Failed to load');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchProfile(); }, []);

  const handleUpdateBase = async () => {
    try {
      const res = await updateProfile(editForm);
      setProfile(res.data);
      setEditing(false);
      flash('Base profile updated!');
    } catch (err) { flash('Failed: ' + (err.response?.data?.detail || 'Error')); }
  };

  const handleUpdateType = async () => {
    try {
      const payload = {};
      payload[`${profile.profile_type}_data`] = typeEditForm;
      const res = await updateTypeData(payload);
      setProfile(res.data);
      setEditingType(false);
      flash('Type-specific data updated!');
    } catch (err) { flash('Failed: ' + (err.response?.data?.detail || 'Error')); }
  };

  const handleVisibility = async (updates) => {
    try {
      const res = await updateVisibility(updates);
      setVisibility(res.data);
      if ('is_public' in updates) {
        await fetchProfile();
        flash(updates.is_public ? 'Profile published!' : 'Profile unpublished');
      } else {
        flash('Visibility updated!');
      }
    } catch (err) { flash('Failed: ' + (err.response?.data?.detail || 'Error')); }
  };

  const handleDelete = async () => {
    if (!window.confirm('Delete your marketplace profile? This cannot be undone.')) return;
    try {
      await deleteProfile();
      setProfile(null);
      setError('no_profile');
      onProfileChange?.(false);
      flash('Profile deleted.');
    } catch (err) { flash('Delete failed'); }
  };

  if (loading) return <div className="text-center py-12 text-gray-400">Loading profile...</div>;

  if (error === 'not_logged_in') return (
    <div className="text-center py-12">
      <p className="text-gray-600 mb-4">Please login to view your profile.</p>
      <button onClick={() => navigate('/login')} className="bg-blue-600 text-white px-4 py-2 rounded text-sm">Login</button>
    </div>
  );

  if (error === 'no_profile') return (
    <div className="text-center py-12">
      <h2 className="text-xl font-bold mb-2">No Marketplace Profile Yet</h2>
      <p className="text-gray-500 mb-6">Create your profile to appear on the marketplace.</p>
      <div className="flex gap-3 justify-center">
        <button onClick={() => navigate('/create')} className="bg-blue-600 text-white px-4 py-2 rounded text-sm">Create Profile</button>
        <button onClick={() => navigate('/onboarding')} className="border border-blue-600 text-blue-600 px-4 py-2 rounded text-sm">Guided Onboarding</button>
      </div>
    </div>
  );

  if (!profile) return null;

  const tc = TYPE_COLORS[profile.profile_type] || TYPE_COLORS.professional;
  const typeData = profile.professional_data || profile.advisor_data || profile.founder_data || {};

  return (
    <div className="max-w-2xl mx-auto">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <h2 className="text-2xl font-bold">My Profile</h2>
          <div className="flex items-center gap-2 mt-1">
            <span className={`text-xs font-medium px-2 py-0.5 rounded ${tc.bg} ${tc.text}`}>{profile.profile_type}</span>
            <span className={`text-xs ${profile.is_public ? 'text-green-600' : 'text-gray-400'}`}>
              {profile.is_public ? 'Public' : 'Draft'}
            </span>
            <ScoreBadge score={profile.profile_score} />
            <span className="text-xs text-gray-400">{profile.profile_views} views</span>
          </div>
        </div>
        <div className="flex gap-2">
          <button onClick={() => handleVisibility({ is_public: !profile.is_public })}
            className={`text-xs px-3 py-1.5 rounded font-medium ${profile.is_public ? 'bg-yellow-100 text-yellow-800' : 'bg-green-600 text-white'}`}>
            {profile.is_public ? 'Unpublish' : 'Publish'}
          </button>
          <button onClick={handleDelete} className="text-xs bg-red-50 text-red-700 px-3 py-1.5 rounded">Delete</button>
        </div>
      </div>

      {actionMsg && <div className="bg-blue-50 text-blue-700 text-sm p-2 rounded mb-4">{actionMsg}</div>}

      {/* Profile card */}
      <div className="bg-white border rounded-lg divide-y">
        {/* Base info */}
        <div className="p-4">
          <div className="flex items-start justify-between">
            <div>
              <h3 className="text-lg font-semibold">{profile.headline || '(no headline)'}</h3>
              <p className="text-sm text-gray-600 mt-1">{profile.bio || '(no bio)'}</p>
            </div>
            <button onClick={() => { setEditing(!editing); setEditForm({}); }}
              className="text-xs bg-gray-100 px-3 py-1 rounded hover:bg-gray-200">
              {editing ? 'Cancel' : 'Edit'}
            </button>
          </div>

          {editing && (
            <div className="mt-4 space-y-3 border-t pt-4">
              <input type="text" placeholder="Headline" defaultValue={profile.headline}
                onChange={(e) => setEditForm({ ...editForm, headline: e.target.value })}
                className="w-full border rounded px-3 py-2 text-sm" />
              <textarea placeholder="Bio" defaultValue={profile.bio}
                onChange={(e) => setEditForm({ ...editForm, bio: e.target.value })}
                className="w-full border rounded px-3 py-2 text-sm" rows={3} />
              <div className="grid grid-cols-2 gap-3">
                <input type="text" placeholder="Location" defaultValue={profile.location}
                  onChange={(e) => setEditForm({ ...editForm, location: e.target.value })}
                  className="border rounded px-3 py-2 text-sm" />
                <input type="text" placeholder="Skills (comma-separated)" defaultValue={profile.skills?.join(', ')}
                  onChange={(e) => setEditForm({ ...editForm, skills: e.target.value.split(',').map(s => s.trim()).filter(Boolean) })}
                  className="border rounded px-3 py-2 text-sm" />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <input type="url" placeholder="LinkedIn URL" defaultValue={profile.linkedin_url}
                  onChange={(e) => setEditForm({ ...editForm, linkedin_url: e.target.value })}
                  className="border rounded px-3 py-2 text-sm" />
                <input type="url" placeholder="Website URL" defaultValue={profile.website_url}
                  onChange={(e) => setEditForm({ ...editForm, website_url: e.target.value })}
                  className="border rounded px-3 py-2 text-sm" />
              </div>
              <button onClick={handleUpdateBase} className="bg-blue-600 text-white px-4 py-2 rounded text-sm">Save Base Info</button>
            </div>
          )}
        </div>

        {/* Details */}
        <div className="p-4">
          <h4 className="text-xs font-semibold text-gray-400 uppercase mb-2">Details</h4>
          <dl className="grid grid-cols-2 gap-x-4 gap-y-1 text-sm">
            <dt className="text-gray-500">Location</dt><dd>{profile.location || '-'}</dd>
            <dt className="text-gray-500">Skills</dt><dd>{profile.skills?.join(', ') || '-'}</dd>
            <dt className="text-gray-500">LinkedIn</dt><dd className="truncate">{profile.linkedin_url || '-'}</dd>
            <dt className="text-gray-500">Website</dt><dd className="truncate">{profile.website_url || '-'}</dd>
          </dl>
        </div>

        {/* Type-specific data */}
        <div>
          <div className="flex items-center justify-between px-4 pt-4">
            <h4 className="text-xs font-semibold text-gray-400 uppercase">{profile.profile_type} Details</h4>
            <button onClick={() => { setEditingType(!editingType); setTypeEditForm({}); }}
              className="text-xs bg-gray-100 px-3 py-1 rounded hover:bg-gray-200">
              {editingType ? 'Cancel' : 'Edit'}
            </button>
          </div>

          {editingType ? (
            <div className="p-4 space-y-3">
              {Object.entries(typeData).map(([key, val]) => (
                <div key={key}>
                  <label className="block text-xs text-gray-500 mb-1">{key.replace(/_/g, ' ')}</label>
                  <input type="text" defaultValue={Array.isArray(val) ? val.join(', ') : val ?? ''}
                    onChange={(e) => {
                      let v = e.target.value;
                      if (Array.isArray(val)) v = v.split(',').map(s => s.trim()).filter(Boolean);
                      setTypeEditForm({ ...typeEditForm, [key]: v });
                    }}
                    className="w-full border rounded px-3 py-2 text-sm" />
                </div>
              ))}
              <button onClick={handleUpdateType} className="bg-blue-600 text-white px-4 py-2 rounded text-sm">Save {profile.profile_type} Data</button>
            </div>
          ) : (
            <TypeDataDisplay profile={profile} />
          )}
        </div>

        {/* Visibility settings */}
        {visibility && (
          <div className="p-4">
            <h4 className="text-xs font-semibold text-gray-400 uppercase mb-3">Visibility Settings</h4>
            <div className="grid grid-cols-2 gap-2">
              {['show_email', 'show_phone', 'show_linkedin', 'show_location', 'discoverable_in_search'].map(key => (
                <label key={key} className="flex items-center gap-2 text-sm">
                  <input type="checkbox" checked={visibility[key] || false}
                    onChange={(e) => handleVisibility({ [key]: e.target.checked })}
                    className="rounded" />
                  {key.replace(/_/g, ' ').replace(/^show /, 'Show ')}
                </label>
              ))}
            </div>
          </div>
        )}

        {/* Documents link */}
        <div className="p-4">
          <a href="/documents" className="text-sm text-blue-600 hover:underline">
            Manage Documents ({profile.documents?.length || 0})
          </a>
        </div>

        {/* Debug */}
        <details className="p-4">
          <summary className="text-xs text-gray-400 cursor-pointer">Raw API Response</summary>
          <pre className="text-xs bg-gray-50 rounded p-3 mt-2 overflow-auto max-h-64">
            {JSON.stringify(profile, null, 2)}
          </pre>
        </details>
      </div>
    </div>
  );
}
