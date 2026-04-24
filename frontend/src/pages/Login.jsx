import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { loginUser } from '../api';

export default function Login({ setUser }) {
  const { t } = useTranslation();
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
        setError(data.error || t('auth.login_failed') || 'Invalid username or password.');
      }
    } catch (error) {
      console.error("Login Error Details:", error);
      setError(t('common.network_error'));
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
          <span style={{ fontWeight: 700, fontSize: '1rem' }}>{t('nav.brand')}</span>
        </Link>

        <div style={{ marginBottom: '2rem' }}>
          <h1 className="auth-title">{t('auth.login_title')}</h1>
          <p className="auth-subtitle">{t('auth.login_subtitle')}</p>
        </div>

        {error && (
          <div className="alert alert-error">
            <span>⚠️</span>
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">{t('auth.username')}</label>
            <input
              id="login-username"
              className="form-input"
              type="text"
              placeholder={t('auth.username_placeholder')}
              value={username}
              onChange={e => setUsername(e.target.value)}
              required
              autoFocus
            />
          </div>

          <div className="form-group">
            <label className="form-label">{t('auth.password')}</label>
            <input
              id="login-password"
              className="form-input"
              type="password"
              placeholder={t('auth.password_placeholder')}
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
            {loading ? <><div className="spinner" /> {t('common.loading')}</> : `${t('common.sign_in')} →`}
          </button>
        </form>

        <div className="auth-switch">
          {t('auth.no_account')}{' '}
          <Link to="/register">{t('auth.create_free')}</Link>
        </div>
      </div>

      {/* Right decorative panel */}
      <div className="auth-visual">
        <div className="auth-visual-content">
          <div style={{ fontSize: '5rem', marginBottom: '1.5rem' }}>🌿</div>
          <h2 style={{ fontSize: '1.8rem', fontWeight: 800, marginBottom: '0.75rem' }}>
            {t('auth.ml_powered')}<br />
            <span style={{ color: 'var(--accent-green)' }}>{t('nav.brand')}</span>
          </h2>
          <p className="text-secondary" style={{ maxWidth: '320px', margin: '0 auto', lineHeight: 1.7 }}>
            {t('home.hero_desc')}
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
            {[
              { emoji: '🌾', label: 'common.crop' },
              { emoji: '🧪', label: 'common.fertilizer' },
              { emoji: '🔬', label: 'common.disease' },
            ].map(f => (
              <div
                key={f.label}
                style={{
                  padding: '0.5rem 1rem',
                  background: 'rgba(255,255,255,0.05)',
                  border: '1px solid rgba(255,255,255,0.08)',
                  borderRadius: '99px',
                  fontSize: '0.8rem',
                  color: 'var(--text-secondary)',
                }}
              >
                {f.emoji} {t(f.label)}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
