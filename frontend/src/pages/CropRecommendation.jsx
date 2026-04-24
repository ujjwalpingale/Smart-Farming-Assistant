import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { predictCrop } from '../api';

const FIELDS = [
  { key: 'nitrogen',    label: 'crop.nitrogen',    unit: 'mg/kg', min: 0, max: 200, step: 1,   placeholder: '0–200' },
  { key: 'phosphorus',  label: 'crop.phosphorus',  unit: 'mg/kg', min: 0, max: 200, step: 1,   placeholder: '0–200' },
  { key: 'potassium',   label: 'crop.potassium',   unit: 'mg/kg', min: 0, max: 200, step: 1,   placeholder: '0–200' },
  { key: 'temperature', label: 'crop.temperature', unit: '°C',    min: 0, max: 60,  step: 0.1, placeholder: '0–60' },
  { key: 'humidity',    label: 'crop.humidity',    unit: '%',     min: 0, max: 100, step: 0.1, placeholder: '0–100' },
  { key: 'ph',          label: 'crop.ph',          unit: 'pH',    min: 0, max: 14,  step: 0.1, placeholder: '0–14' },
  { key: 'rainfall',    label: 'crop.rainfall',    unit: 'mm',    min: 0, max: 500, step: 0.1, placeholder: '0–500' },
];

export default function CropRecommendation() {
  const { t } = useTranslation();
  const [values, setValues] = useState({});
  const [results, setResults] = useState([]);
  const [error, setError]   = useState('');
  const [loading, setLoading] = useState(false);

  const set = k => e => setValues(v => ({ ...v, [k]: e.target.value }));

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setResults([]);
    setLoading(true);
    try {
      const res = await predictCrop(values);
      const html = await res.text();
      
      const matches = [...html.matchAll(/<h5[^>]*>([^<]+)<\/h5>/gi)];
      const found = matches.map(m => m[1].trim()).filter(t => t !== 'Recommended Crops');
      
      if (found.length > 0) {
        setResults(found);
      } else if (res.ok) {
        setResults([t('common.success_msg') || 'Prediction received.']);
      } else {
        setError(t('common.error_msg') || 'Prediction failed. Please check your inputs.');
      }
    } catch (err) {
      console.error(err);
      setError(t('common.network_error'));
    } finally {
      setLoading(false);
    }
  }

  function reset() { setResults([]); setValues({}); setError(''); }

  if (results.length > 0) {
    return (
      <div className="main-content">
        <div className="container" style={{ maxWidth: 560, padding: '3rem 1.5rem' }}>
          <div className="glass-card result-card animate-fade-up">
            <div className="result-icon green">🌾</div>
            <div className="result-label">{t('crop.result_title')}</div>
            
            <div className="results-list" style={{ margin: '1.5rem 0' }}>
              {results.map((r, i) => (
                <div key={i} className={`result-item ${i === 0 ? 'primary' : 'secondary'}`} style={{
                  padding: i === 0 ? '1rem' : '0.75rem',
                  background: i === 0 ? 'rgba(34,197,94,0.1)' : 'rgba(255,255,255,0.05)',
                  borderRadius: '12px',
                  marginBottom: '0.75rem',
                  border: i === 0 ? '1px solid rgba(34,197,94,0.3)' : '1px solid rgba(255,255,255,0.1)',
                }}>
                  <div className="result-value" style={{ 
                    fontSize: i === 0 ? '1.8rem' : '1.2rem',
                    color: i === 0 ? 'var(--accent-green)' : 'inherit',
                    fontWeight: 700 
                  }}>
                    {i === 0 ? '🥇 ' : i === 1 ? '🥈 ' : '🥉 '} {t(`crop.result_crops.${r.toLowerCase()}`, r)}
                  </div>
                  <div style={{ fontSize: '0.8rem', opacity: 0.7 }}>
                    {i === 0 ? t('common.best_match') : `${t('common.alternative')} ${i}`}
                  </div>
                </div>
              ))}
            </div>

            <p className="result-desc">
              {t('crop.result_desc')}
            </p>
            <div className="flex gap-3 justify-center" style={{ flexWrap: 'wrap' }}>
              <button className="btn btn-primary" onClick={reset}>{t('common.try_another')}</button>
              <Link to="/" className="btn btn-outline">{t('common.back_home')}</Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="main-content">
      <div className="container" style={{ maxWidth: 680 }}>
        <div className="page-header animate-fade-up">
          <div className="page-header-icon" style={{ background: 'rgba(34,197,94,0.12)' }}>🌾</div>
          <div>
            <div className="page-header-title">{t('crop.title')}</div>
            <div className="page-header-desc">
              {t('crop.desc')}
            </div>
          </div>
        </div>

        <div className="glass-card animate-fade-up delay-1" style={{ padding: '2rem' }}>
          {error && (
            <div className="alert alert-error mb-4">
              <span>⚠️</span> {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="form-row">
              {FIELDS.map(f => (
                <div className="form-group" key={f.key}>
                  <label className="form-label">
                    {t(f.label)}
                    <span className="unit">{f.unit}</span>
                  </label>
                  <input
                    id={`crop-${f.key}`}
                    className="form-input"
                    type="number"
                    step={f.step}
                    min={f.min}
                    max={f.max}
                    placeholder={f.placeholder}
                    value={values[f.key] ?? ''}
                    onChange={set(f.key)}
                    required
                  />
                </div>
              ))}
            </div>

            <button
              id="crop-submit"
              type="submit"
              className="btn btn-primary btn-lg btn-full mt-4"
              disabled={loading}
            >
              {loading
                ? <><div className="spinner" /> {t('common.loading')}</>
                : t('common.predict')}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
