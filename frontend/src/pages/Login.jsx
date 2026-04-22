import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { loginUser } from '../api';

export default function Login({ setUser }) {
  const [username, setUsername] = useState('');
  const [password, setPassword]  = useState('');
  const [error, setError]   = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await loginUser(username, password);
      if (res.ok) {
        setUser(username);
        navigate('/');
      } else {
        const data = await res.json().catch(() => ({}));
        setError(data.error || 'Invalid username or password. Please try again.');
      }
    } catch (error) {
      console.error("Login Error Details:", error);
      setError(`Network error: ${error.message || String(error)}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-wrapper">
      {/* Left panel */}
      <div className="auth-panel">
        <Link to="/" className="auth-logo">
          <div className="brand-icon">🌱</div>
          <span style={{ fontWeight: 700, fontSize: '1rem' }}>Smart Farming</span>
        </Link>

        <div style={{ marginBottom: '2rem' }}>
          <h1 className="auth-title">Welcome back</h1>
          <p className="auth-subtitle">Sign in to your account to continue</p>
        </div>

        {error && (
          <div className="alert alert-error">
            <span>⚠️</span>
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Username</label>
            <input
              id="login-username"
              className="form-input"
              type="text"
              placeholder="Enter your username"
              value={username}
              onChange={e => setUsername(e.target.value)}
              required
              autoFocus
            />
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <input
              id="login-password"
              className="form-input"
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
            />
          </div>

          <button
            id="login-submit"
            type="submit"
            className="btn btn-primary btn-lg btn-full"
            disabled={loading}
          >
            {loading ? <><div className="spinner" /> Signing in…</> : 'Sign In →'}
          </button>
        </form>

        <div className="auth-switch">
          Don't have an account?{' '}
          <Link to="/register">Create one free</Link>
        </div>
      </div>

      {/* Right decorative panel */}
      <div className="auth-visual">
        <div className="auth-visual-content">
          <div style={{ fontSize: '5rem', marginBottom: '1.5rem' }}>🌿</div>
          <h2 style={{ fontSize: '1.8rem', fontWeight: 800, marginBottom: '0.75rem' }}>
            AI-Powered<br />
            <span style={{ color: 'var(--accent-green)' }}>Smart Farming</span>
          </h2>
          <p className="text-secondary" style={{ maxWidth: '320px', margin: '0 auto', lineHeight: 1.7 }}>
            Get personalised crop recommendations, fertilizer guidance, and
            instant plant disease detection powered by machine learning.
          </p>

          <div
            style={{
              display: 'flex',
              gap: '1rem',
              justifyContent: 'center',
              marginTop: '2.5rem',
              flexWrap: 'wrap',
            }}
          >
            {['🌾 Crops', '🧪 Fertilizers', '🔬 Diseases'].map(f => (
              <div
                key={f}
                style={{
                  padding: '0.5rem 1rem',
                  background: 'rgba(255,255,255,0.05)',
                  border: '1px solid rgba(255,255,255,0.08)',
                  borderRadius: '99px',
                  fontSize: '0.8rem',
                  color: 'var(--text-secondary)',
                }}
              >
                {f}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
