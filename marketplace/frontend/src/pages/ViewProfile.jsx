import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getProfile } from '../api';

export default function ViewProfile() {
  const { profileId } = useParams();
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const res = await getProfile(profileId);
        setProfile(res.data);
      } catch (err) {
        setError(err.response?.status === 404 ? 'Profile not found' : err.response?.data?.detail || 'Error');
      } finally {
        setLoading(false);
      }
    })();
  }, [profileId]);

  if (loading) return <div className="text-center py-12 text-gray-400">Loading...</div>;
  if (error) return <div className="text-center py-12 text-red-600">{error}</div>;
  if (!profile) return null;

  const isSelfView = 'visibility_settings' in profile;

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white border rounded-lg p-6">
        <div className="flex items-center gap-3 mb-4">
          {profile.avatar_url && (
            <img src={profile.avatar_url} alt="" className="w-14 h-14 rounded-full object-cover" />
          )}
          <div>
            <h2 className="text-xl font-bold">{profile.headline || 'Untitled Profile'}</h2>
            <div className="flex gap-2 mt-1">
              <span className="text-xs font-medium px-2 py-0.5 rounded bg-gray-100 text-gray-700">
                {profile.profile_type}
              </span>
              <span className="text-xs text-gray-400">Score: {profile.profile_score}</span>
            </div>
          </div>
        </div>

        {profile.bio && <p className="text-sm text-gray-600 mb-4">{profile.bio}</p>}

        {profile.skills?.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mb-4">
            {profile.skills.map((s, i) => (
              <span key={i} className="text-xs bg-gray-100 text-gray-700 px-2 py-0.5 rounded">{s}</span>
            ))}
          </div>
        )}

        <dl className="grid grid-cols-2 gap-2 text-sm">
          {profile.location && <><dt className="text-gray-500">Location</dt><dd>{profile.location}</dd></>}
          {profile.primary_role && <><dt className="text-gray-500">Role</dt><dd>{profile.primary_role}</dd></>}
          {profile.availability_status && <><dt className="text-gray-500">Availability</dt><dd>{profile.availability_status}</dd></>}
        </dl>

        {isSelfView && (
          <p className="text-xs text-gray-400 mt-4 border-t pt-3">
            You are viewing your own profile (self view). Other users see the public view.
          </p>
        )}
      </div>
    </div>
  );
}
