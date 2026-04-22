import { Link } from 'react-router-dom';

export default function Home({ user }) {
  return (
    <div className="main-content">
      {/* ── Hero ─────────────────────────────────────────────────────────── */}
      <div className="container">
        <div className="hero animate-fade-up">
          <div className="hero-badge">
            <span>✨</span>
            <span>AI-Powered Agricultural Intelligence</span>
          </div>
          <h1 className="hero-title">
            Grow Smarter with<br />
            <span className="gradient-text">Smart Farming AI</span>
          </h1>
          <p className="hero-subtitle">
            Harness the power of machine learning to get personalised crop
            recommendations, fertilizer guidance, and instant plant disease
            detection — all in one platform.
          </p>
          {!user && (
            <div className="flex gap-3 justify-center" style={{ flexWrap: 'wrap' }}>
              <Link to="/register" className="btn btn-primary btn-lg">
                Get Started Free →
              </Link>
              <Link to="/login" className="btn btn-outline btn-lg">
                Sign In
              </Link>
            </div>
          )}
          {user && (
            <div className="flex gap-3 justify-center" style={{ flexWrap: 'wrap' }}>
              <Link to="/crop" className="btn btn-primary btn-lg">
                Start Predicting →
              </Link>
            </div>
          )}
        </div>

        {/* ── Stats ──────────────────────────────────────────────────────── */}
        <div className="stats-strip animate-fade-up delay-1">
          {[
            { value: '22+', label: 'Crop Varieties' },
            { value: '10+', label: 'Fertilizer Types' },
            { value: '38+', label: 'Disease Classes' },
            { value: '99%', label: 'ML Accuracy' },
          ].map(({ value, label }) => (
            <div className="stat-item" key={label}>
              <div className="stat-value">{value}</div>
              <div className="stat-label">{label}</div>
            </div>
          ))}
        </div>

        {/* ── Feature Cards ───────────────────────────────────────────────── */}
        <div className="feature-grid animate-fade-up delay-2">
          <Link
            to={user ? '/crop' : '/login'}
            className="feature-card glass-card green"
          >
            <div className="feature-icon green">🌾</div>
            <div className="feature-title">Crop Recommendation</div>
            <p className="feature-desc">
              Input your soil's N-P-K ratios, temperature, humidity, pH, and
              rainfall. Our trained Random Forest model will recommend the
              optimal crop for maximum yield.
            </p>
            <div className="feature-cta">
              <span>Try it now</span>
              <span>→</span>
            </div>
          </Link>

          <Link
            to={user ? '/fertilizer' : '/login'}
            className="feature-card glass-card amber"
          >
            <div className="feature-icon amber">🧪</div>
            <div className="feature-title">Fertilizer Recommendation</div>
            <p className="feature-desc">
              Provide nutrient levels and soil type to get a tailored fertilizer
              suggestion. Reduce waste and maximise soil health with
              data-driven insights.
            </p>
            <div className="feature-cta">
              <span>Try it now</span>
              <span>→</span>
            </div>
          </Link>

          <Link
            to={user ? '/disease' : '/login'}
            className="feature-card glass-card rose"
          >
            <div className="feature-icon rose">🔬</div>
            <div className="feature-title">Disease Detection</div>
            <p className="feature-desc">
              Upload a photo of your plant and let our deep learning model
              identify diseases instantly. Get prevention advice before
              damage spreads.
            </p>
            <div className="feature-cta">
              <span>Try it now</span>
              <span>→</span>
            </div>
          </Link>
        </div>

        {/* ── How it works ─────────────────────────────────────────────────── */}
        <div style={{ textAlign: 'center', marginBottom: '4rem' }}>
          <h2
            className="animate-fade-up"
            style={{ fontSize: '1.8rem', fontWeight: 800, marginBottom: '0.5rem' }}
          >
            How It Works
          </h2>
          <p className="text-secondary animate-fade-up delay-1" style={{ marginBottom: '2.5rem' }}>
            Three simple steps to smarter farming
          </p>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
              gap: '1.5rem',
            }}
          >
            {[
              { step: '01', emoji: '✍️', title: 'Provide Data',     desc: 'Enter soil parameters or upload a plant image' },
              { step: '02', emoji: '🤖', title: 'AI Analyses',      desc: 'Our ML models process your inputs instantly' },
              { step: '03', emoji: '📋', title: 'Get Insights',     desc: 'Receive actionable recommendations to act on' },
            ].map(({ step, emoji, title, desc }, i) => (
              <div
                key={step}
                className={`glass-card animate-fade-up delay-${i + 1}`}
                style={{ padding: '1.75rem', textAlign: 'center' }}
              >
                <div
                  style={{
                    fontSize: '0.7rem',
                    fontWeight: 700,
                    letterSpacing: '0.12em',
                    color: 'var(--accent-green)',
                    marginBottom: '0.75rem',
                  }}
                >
                  STEP {step}
                </div>
                <div style={{ fontSize: '2rem', marginBottom: '0.75rem' }}>{emoji}</div>
                <div style={{ fontWeight: 700, marginBottom: '0.4rem' }}>{title}</div>
                <div className="text-secondary text-sm">{desc}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
