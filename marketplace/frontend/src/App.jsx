import { Routes, Route, Link, useNavigate, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { getMe, getMyProfile } from './api';
import Login from './pages/Login';
import CreateProfile from './pages/CreateProfile';
import MyProfile from './pages/MyProfile';
import Onboarding from './pages/Onboarding';
import ViewProfile from './pages/ViewProfile';
import Documents from './pages/Documents';
import Discover from './pages/Discover';

function ProtectedRoute({ token, children }) {
  if (!token) return <Navigate to="/login" replace />;
  return children;
}

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [user, setUser] = useState(null);
  const [hasProfile, setHasProfile] = useState(null); // null = loading, true/false

  const navigate = useNavigate();

  const handleLogin = (newToken, userData) => {
    localStorage.setItem('token', newToken);
    setToken(newToken);
    setUser(userData);
    setHasProfile(null); // re-check
    navigate('/');
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    setHasProfile(null);
    navigate('/login');
  };

  // Check user + profile existence on token change
  useEffect(() => {
    if (!token) { setUser(null); setHasProfile(null); return; }

    getMe().then(res => setUser(res.data)).catch(() => {
      localStorage.removeItem('token');
      setToken(null);
    });

    getMyProfile()
      .then(() => setHasProfile(true))
      .catch(() => setHasProfile(false));
  }, [token]);

  // Called by child pages when profile is created or deleted
  const onProfileChange = (exists) => setHasProfile(exists);

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b border-gray-200 px-6 py-3 sticky top-0 z-10">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <Link to="/" className="text-lg font-bold text-gray-900">OnlyFounders Marketplace</Link>
          <div className="flex gap-4 items-center">
            {token ? (
              <>
                <Link to="/discover" className="text-sm text-gray-600 hover:text-gray-900">Discover</Link>
                {hasProfile ? (
                  <>
                    <Link to="/" className="text-sm text-gray-600 hover:text-gray-900">My Profile</Link>
                    <Link to="/documents" className="text-sm text-gray-600 hover:text-gray-900">Documents</Link>
                  </>
                ) : (
                  <>
                    <Link to="/create" className="text-sm text-gray-600 hover:text-gray-900">Create Profile</Link>
                    <Link to="/onboarding" className="text-sm text-gray-600 hover:text-gray-900">Onboarding</Link>
                  </>
                )}
                {user && (
                  <span className="text-xs text-gray-400 border-l pl-4">
                    {user.first_name} {user.last_name}
                  </span>
                )}
                <button onClick={handleLogout} className="text-sm text-red-600 hover:text-red-800">
                  Logout
                </button>
              </>
            ) : (
              <Link to="/login" className="text-sm bg-blue-600 text-white px-3 py-1.5 rounded hover:bg-blue-700">
                Login
              </Link>
            )}
          </div>
        </div>
      </nav>

      <main className="max-w-5xl mx-auto px-6 py-8">
        <Routes>
          <Route path="/login" element={<Login onLogin={handleLogin} />} />
          <Route path="/" element={
            <ProtectedRoute token={token}><MyProfile onProfileChange={onProfileChange} /></ProtectedRoute>
          } />
          <Route path="/create" element={
            <ProtectedRoute token={token}><CreateProfile onProfileChange={onProfileChange} /></ProtectedRoute>
          } />
          <Route path="/onboarding" element={
            <ProtectedRoute token={token}><Onboarding onProfileChange={onProfileChange} /></ProtectedRoute>
          } />
          <Route path="/discover" element={
            <ProtectedRoute token={token}><Discover /></ProtectedRoute>
          } />
          <Route path="/documents" element={
            <ProtectedRoute token={token}><Documents /></ProtectedRoute>
          } />
          <Route path="/profile/:profileId" element={
            <ProtectedRoute token={token}><ViewProfile /></ProtectedRoute>
          } />
        </Routes>
      </main>
    </div>
  );
}

export default App;
