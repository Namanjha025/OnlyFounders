import { useState } from 'react';
import { login, register } from '../api';

export default function Login({ onLogin }) {
  const [isRegister, setIsRegister] = useState(false);
  const [form, setForm] = useState({ email: '', password: '', first_name: '', last_name: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const set = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (isRegister) {
        const res = await register(form);
        onLogin(res.data.access_token, res.data.user);
      } else {
        const res = await login(form.email, form.password);
        onLogin(res.data.access_token, null);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-sm mx-auto mt-12">
      <div className="bg-white rounded-lg border p-6">
        <h2 className="text-xl font-bold mb-1">{isRegister ? 'Create Account' : 'Welcome Back'}</h2>
        <p className="text-sm text-gray-500 mb-6">
          {isRegister ? 'Sign up to join the marketplace' : 'Login to your account'}
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          {isRegister && (
            <div className="grid grid-cols-2 gap-3">
              <input type="text" placeholder="First Name" value={form.first_name}
                onChange={set('first_name')} className="border rounded px-3 py-2 text-sm" required />
              <input type="text" placeholder="Last Name" value={form.last_name}
                onChange={set('last_name')} className="border rounded px-3 py-2 text-sm" required />
            </div>
          )}
          <input type="email" placeholder="Email" value={form.email}
            onChange={set('email')} className="w-full border rounded px-3 py-2 text-sm" required />
          <input type="password" placeholder="Password" value={form.password}
            onChange={set('password')} className="w-full border rounded px-3 py-2 text-sm" required />

          {error && <div className="bg-red-50 text-red-700 text-sm p-2 rounded">{error}</div>}

          <button type="submit" disabled={loading}
            className="w-full bg-blue-600 text-white py-2.5 rounded text-sm font-medium hover:bg-blue-700 disabled:opacity-50">
            {loading ? 'Loading...' : isRegister ? 'Register' : 'Login'}
          </button>
        </form>

        <p className="mt-4 text-sm text-gray-500 text-center">
          {isRegister ? 'Already have an account?' : "Don't have an account?"}{' '}
          <button onClick={() => { setIsRegister(!isRegister); setError(''); }}
            className="text-blue-600 hover:underline font-medium">
            {isRegister ? 'Login' : 'Register'}
          </button>
        </p>
      </div>
    </div>
  );
}
