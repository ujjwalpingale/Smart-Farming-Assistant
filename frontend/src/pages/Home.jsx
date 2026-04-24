import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

export default function Home({ user }) {
  const { t } = useTranslation();

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
            {t('home.hero_title')}<br />
            <span className="gradient-text">{t('home.hero_accent')}</span>
          </h1>
          <p className="hero-subtitle">
            {t('home.hero_desc')}
          </p>
          {!user && (
            <div className="flex gap-3 justify-center" style={{ flexWrap: 'wrap' }}>
              <Link to="/register" className="btn btn-primary btn-lg">
                {t('common.register')}
              </Link>
              <Link to="/login" className="btn btn-outline btn-lg">
                {t('common.sign_in')}
              </Link>
            </div>
          )}
          {user && (
            <div className="flex gap-3 justify-center" style={{ flexWrap: 'wrap' }}>
              <Link to="/crop" className="btn btn-primary btn-lg">
                {t('home.get_started')}
              </Link>
            </div>
          )}
        </div>

        {/* ── Stats ──────────────────────────────────────────────────────── */}
        <div className="stats-strip animate-fade-up delay-1">
          {[
            { value: '22+', label: 'home.stats.crops' },
            { value: '10+', label: 'home.stats.ferts' },
            { value: '38+', label: 'home.stats.classes' },
            { value: '99%', label: 'home.stats.accuracy' },
          ].map(({ value, label }) => (
            <div className="stat-item" key={label}>
              <div className="stat-value">{value}</div>
              <div className="stat-label">{t(label)}</div>
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
            <div className="feature-title">{t('crop.title')}</div>
            <p className="feature-desc">
              {t('crop.desc')}
            </p>
            <div className="feature-cta">
              <span>{t('common.try_now')}</span>
              <span>→</span>
            </div>
          </Link>

          <Link
            to={user ? '/fertilizer' : '/login'}
            className="feature-card glass-card amber"
          >
            <div className="feature-icon amber">🧪</div>
            <div className="feature-title">{t('fert.title')}</div>
            <p className="feature-desc">
              {t('fert.desc')}
            </p>
            <div className="feature-cta">
              <span>{t('common.try_now')}</span>
              <span>→</span>
            </div>
          </Link>

          <Link
            to={user ? '/disease' : '/login'}
            className="feature-card glass-card rose"
          >
            <div className="feature-icon rose">🔬</div>
            <div className="feature-title">{t('disease.title')}</div>
            <p className="feature-desc">
              {t('disease.desc')}
            </p>
            <div className="feature-cta">
              <span>{t('common.try_now')}</span>
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
            {t('home.how_it_works.title')}
          </h2>
          <p className="text-secondary animate-fade-up delay-1" style={{ marginBottom: '2.5rem' }}>
            {t('home.how_it_works.subtitle')}
          </p>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
              gap: '1.5rem',
            }}
          >
            {[
              { step: '01', emoji: '✍️', title: 'home.how_it_works.step1_title', desc: 'home.how_it_works.step1_desc' },
              { step: '02', emoji: '🤖', title: 'home.how_it_works.step2_title', desc: 'home.how_it_works.step2_desc' },
              { step: '03', emoji: '📋', title: 'home.how_it_works.step3_title', desc: 'home.how_it_works.step3_desc' },
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
                  {t('common.step')} {step}
                </div>
                <div style={{ fontSize: '2rem', marginBottom: '0.75rem' }}>{emoji}</div>
                <div style={{ fontWeight: 700, marginBottom: '0.4rem' }}>{t(title)}</div>
                <div className="text-secondary text-sm">{t(desc)}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
