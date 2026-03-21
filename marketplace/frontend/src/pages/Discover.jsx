import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { discoverProfiles } from '../api';

const TYPE_STYLES = {
  professional: { bg: 'bg-blue-100', text: 'text-blue-800', border: 'border-blue-200' },
  advisor: { bg: 'bg-purple-100', text: 'text-purple-800', border: 'border-purple-200' },
  founder: { bg: 'bg-orange-100', text: 'text-orange-800', border: 'border-orange-200' },
};

function ProfileCard({ profile }) {
  const style = TYPE_STYLES[profile.profile_type] || TYPE_STYLES.professional;

  return (
    <Link to={`/profile/${profile.id}`}
      className="bg-white border rounded-lg p-5 hover:shadow-md transition block">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          {profile.avatar_url ? (
            <img src={profile.avatar_url} alt="" className="w-12 h-12 rounded-full object-cover" />
          ) : (
            <div className={`w-12 h-12 rounded-full ${style.bg} flex items-center justify-center`}>
              <span className={`text-lg font-bold ${style.text}`}>
                {profile.headline?.[0]?.toUpperCase() || '?'}
              </span>
            </div>
          )}
          <div>
            <h3 className="font-semibold text-sm">{profile.headline || 'Untitled'}</h3>
            <div className="flex items-center gap-2 mt-0.5">
              <span className={`text-xs font-medium px-1.5 py-0.5 rounded ${style.bg} ${style.text}`}>
                {profile.profile_type}
              </span>
              {profile.location && (
                <span className="text-xs text-gray-400">{profile.location}</span>
              )}
            </div>
          </div>
        </div>
        <span className="text-xs text-gray-400 font-medium">{profile.profile_score}/100</span>
      </div>

      {profile.bio && (
        <p className="text-sm text-gray-600 mt-3 line-clamp-2">{profile.bio}</p>
      )}

      {profile.skills?.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-3">
          {profile.skills.slice(0, 6).map((skill, i) => (
            <span key={i} className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">{skill}</span>
          ))}
          {profile.skills.length > 6 && (
            <span className="text-xs text-gray-400">+{profile.skills.length - 6} more</span>
          )}
        </div>
      )}

      {(profile.primary_role || profile.availability_status) && (
        <div className="flex gap-3 mt-3 text-xs text-gray-500">
          {profile.primary_role && <span>{profile.primary_role}</span>}
          {profile.availability_status && (
            <span className={`${
              profile.availability_status === 'available' ? 'text-green-600' :
              profile.availability_status === 'open_to_offers' ? 'text-yellow-600' :
              'text-gray-400'
            }`}>
              {profile.availability_status.replace(/_/g, ' ')}
            </span>
          )}
        </div>
      )}
    </Link>
  );
}

export default function Discover() {
  const [profiles, setProfiles] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Filters
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [skillsFilter, setSkillsFilter] = useState('');
  const [locationFilter, setLocationFilter] = useState('');
  const [page, setPage] = useState(1);

  const fetchProfiles = async () => {
    setLoading(true);
    setError('');
    try {
      const params = { page, page_size: 20 };
      if (search) params.q = search;
      if (typeFilter) params.profile_type = typeFilter;
      if (skillsFilter) params.skills = skillsFilter;
      if (locationFilter) params.location = locationFilter;

      const res = await discoverProfiles(params);
      setProfiles(res.data.items);
      setTotal(res.data.total);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load profiles');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchProfiles(); }, [page, typeFilter]);

  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1);
    fetchProfiles();
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold">Discover</h2>
          <p className="text-sm text-gray-500">Browse professionals, advisors, and founders on the marketplace</p>
        </div>
        <span className="text-sm text-gray-400">{total} profiles</span>
      </div>

      {/* Search & Filters */}
      <form onSubmit={handleSearch} className="bg-white border rounded-lg p-4 mb-6">
        <div className="flex gap-3">
          <input type="text" placeholder="Search by name, skill, or keyword..."
            value={search} onChange={(e) => setSearch(e.target.value)}
            className="flex-1 border rounded px-3 py-2 text-sm" />
          <button type="submit"
            className="bg-blue-600 text-white px-4 py-2 rounded text-sm font-medium hover:bg-blue-700">
            Search
          </button>
        </div>

        <div className="flex gap-3 mt-3">
          {/* Type filter */}
          <div className="flex gap-1.5">
            {['', 'professional', 'advisor', 'founder'].map(type => (
              <button key={type} type="button"
                onClick={() => { setTypeFilter(type); setPage(1); }}
                className={`text-xs px-3 py-1.5 rounded-full font-medium transition ${
                  typeFilter === type
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}>
                {type || 'All'}
              </button>
            ))}
          </div>

          <input type="text" placeholder="Filter by skills (comma-sep)"
            value={skillsFilter} onChange={(e) => setSkillsFilter(e.target.value)}
            className="border rounded px-3 py-1.5 text-xs w-48" />

          <input type="text" placeholder="Location"
            value={locationFilter} onChange={(e) => setLocationFilter(e.target.value)}
            className="border rounded px-3 py-1.5 text-xs w-36" />
        </div>
      </form>

      {error && <div className="bg-red-50 text-red-700 text-sm p-3 rounded mb-4">{error}</div>}

      {/* Results */}
      {loading ? (
        <div className="text-center py-12 text-gray-400">Loading...</div>
      ) : profiles.length === 0 ? (
        <div className="text-center py-12 bg-white border rounded-lg">
          <p className="text-gray-500">No profiles found.</p>
          <p className="text-xs text-gray-400 mt-1">Try adjusting your filters or search terms.</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {profiles.map(p => <ProfileCard key={p.id} profile={p} />)}
        </div>
      )}

      {/* Pagination */}
      {total > 20 && (
        <div className="flex justify-center gap-2 mt-6">
          <button onClick={() => setPage(Math.max(1, page - 1))} disabled={page === 1}
            className="text-sm px-3 py-1 border rounded disabled:opacity-30">Prev</button>
          <span className="text-sm text-gray-500 py-1">Page {page}</span>
          <button onClick={() => setPage(page + 1)} disabled={profiles.length < 20}
            className="text-sm px-3 py-1 border rounded disabled:opacity-30">Next</button>
        </div>
      )}
    </div>
  );
}
