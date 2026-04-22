import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { registerUser } from '../api';

const RULES = [
  { label: '12+ characters',           test: p => p.length >= 12 },
  { label: 'One uppercase letter',      test: p => /[A-Z]/.test(p) },
  { label: 'One special character',     test: p => /[!@#$%^&*(),.?":{}|<>]/.test(p) },
  { label: 'Not purely numeric',        test: p => !/^\d+$/.test(p) },
];

export default function Register({ setUser }) {
  const [form, setForm] = useState({ username: '', email: '', password: '', password_confirm: '' });
  const [errors, setErrors]   = useState([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const set = k => e => setForm(f => ({ ...f, [k]: e.target.value }));

  async function handleSubmit(e) {
    e.preventDefault();
    setErrors([]);

    // Client-side checks
    const errs = [];
    if (form.password !== form.password_confirm) errs.push('Passwords do not match.');
    RULES.forEach(r => { if (!r.test(form.password)) errs.push(r.label + ' required.'); });
    if (errs.length) { setErrors(errs); return; }

    setLoading(true);
    try {
      const res = await registerUser(form.username, form.email, form.password, form.password_confirm);
      if (res.ok) {
        setUser(form.username);
        navigate('/');
      } else {
        const data = await res.json().catch(() => ({}));
        setErrors([data.error || 'Registration failed. Please try again.']);
      }
    } catch (error) {
      console.error("Registration Error Details:", error);
      setErrors([`Network error: ${error.message || String(error)}`]);
    } finally {
      setLoading(false);
    }
  }

  const pwRuleStatus = RULES.map(r => ({ ...r, ok: r.test(form.password) }));

  return (
    <div className="auth-wrapper">
      {/* Left decorative panel */}
      <div className="auth-visual">
        <div className="auth-visual-content animate-fade-up">
          <div style={{ fontSize: '5rem', marginBottom: '1.5rem' }}>🚜</div>
          <h2 style={{ fontSize: '1.8rem', fontWeight: 800, marginBottom: '0.75rem' }}>
            Join thousands of<br />
            <span style={{ color: 'var(--accent-green)' }}>Smart Farmers</span>
          </h2>
          <p className="text-secondary" style={{ maxWidth: '320px', margin: '0 auto', lineHeight: 1.7 }}>
            Create your free account and start making data-driven decisions for
            your farm today.
          </p>

          <div style={{ marginTop: '2.5rem', display: 'flex', flexDirection: 'column', gap: '0.75rem', alignItems: 'center' }}>
            {['🌱 Free forever', '🤖 ML-Powered predictions', '📊 Track your history'].map(f => (
              <div
                key={f}
                style={{
                  padding: '0.5rem 1.25rem',
                  background: 'rgba(34,197,94,0.08)',
                  border: '1px solid rgba(34,197,94,0.2)',
                  borderRadius: '99px',
                  fontSize: '0.82rem',
                  color: 'var(--accent-green)',
                }}
              >
                {f}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Right form panel */}
      <div className="auth-panel" style={{ borderRight: 'none', borderLeft: '1px solid var(--border)' }}>
        <Link to="/" className="auth-logo">
          <div className="brand-icon">🌱</div>
          <span style={{ fontWeight: 700, fontSize: '1rem' }}>Smart Farming</span>
        </Link>

        <div style={{ marginBottom: '2rem' }}>
          <h1 className="auth-title">Create account</h1>
          <p className="auth-subtitle">It's free and only takes a minute</p>
        </div>

        {errors.length > 0 && (
          <div className="alert alert-error">
            <span>⚠️</span>
            <ul style={{ margin: 0, paddingLeft: '1rem' }}>
              {errors.map((e, i) => <li key={i}>{e}</li>)}
            </ul>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Username</label>
            <input id="reg-username" className="form-input" type="text"
              placeholder="Choose a username" value={form.username}
              onChange={set('username')} required autoFocus />
          </div>

          <div className="form-group">
            <label className="form-label">Email</label>
            <input id="reg-email" className="form-input" type="email"
              placeholder="your@email.com" value={form.email}
              onChange={set('email')} required />
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <input id="reg-password" className="form-input" type="password"
              placeholder="Create a strong password" value={form.password}
              onChange={set('password')} required />

            {/* Inline strength indicator */}
            {form.password && (
              <div style={{ marginTop: '0.5rem', display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                {pwRuleStatus.map(r => (
                  <span
                    key={r.label}
                    style={{
                      fontSize: '0.7rem',
                      padding: '0.2rem 0.5rem',
                      borderRadius: '99px',
                      background: r.ok ? 'rgba(34,197,94,0.12)' : 'rgba(255,255,255,0.05)',
                      color: r.ok ? 'var(--accent-green)' : 'var(--text-muted)',
                      border: `1px solid ${r.ok ? 'rgba(34,197,94,0.25)' : 'rgba(255,255,255,0.07)'}`,
                    }}
                  >
                    {r.ok ? '✓' : '○'} {r.label}
                  </span>
                ))}
              </div>
            )}
          </div>

          <div className="form-group">
            <label className="form-label">Confirm Password</label>
            <input id="reg-password-confirm" className="form-input" type="password"
              placeholder="Repeat your password" value={form.password_confirm}
              onChange={set('password_confirm')} required />
          </div>

          <button id="reg-submit" type="submit" className="btn btn-primary btn-lg btn-full" disabled={loading}>
            {loading ? <><div className="spinner" /> Creating account…</> : 'Create Account →'}
          </button>
        </form>

        <div className="auth-switch">
          Already have an account?{' '}
          <Link to="/login">Sign in</Link>
        </div>
      </div>
    </div>
  );
}
