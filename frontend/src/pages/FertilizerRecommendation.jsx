import { useState } from 'react';
import { Link } from 'react-router-dom';
import { predictFertilizer } from '../api';

const SOIL_TYPES = [
  'Acidic Soil', 'Alkaline Soil', 'Loamy Soil', 'Neutral Soil', 'Peaty Soil',
];

export default function FertilizerRecommendation() {
  const [values, setValues] = useState({ nitrogen: '', phosphorus: '', potassium: '', soil: '' });
  const [result, setResult] = useState(null);
  const [error, setError]   = useState('');
  const [loading, setLoading] = useState(false);

  const set = k => e => setValues(v => ({ ...v, [k]: e.target.value }));

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setResult(null);
    setLoading(true);
    try {
      const res = await predictFertilizer(values);
      const html = await res.text();
      const m = html.match(/Recommended Fertilizer[\s\S]*?<h5[^>]*>([^<]+)<\/h5>/i)
             || html.match(/alert-success[^>]*>[\s\S]*?<h5[^>]*>\s*([^<]+)\s*<\/h5>/i);
      if (m) {
        setResult(m[1].trim());
      } else if (res.ok) {
        setResult('Recommendation received — check response.');
      } else {
        setError('Prediction failed. Please check your inputs.');
      }
    } catch {
      setError('Network error. Make sure Django is running on port 8000.');
    } finally {
      setLoading(false);
    }
  }

  function reset() { setResult(null); setValues({ nitrogen: '', phosphorus: '', potassium: '', soil: '' }); setError(''); }

  if (result) {
    return (
      <div className="main-content">
        <div className="container" style={{ maxWidth: 560, padding: '3rem 1.5rem' }}>
          <div className="glass-card result-card animate-fade-up">
            <div className="result-icon amber">🧪</div>
            <div className="result-label">Recommended Fertilizer</div>
            <div className="result-value" style={{ fontSize: '1.9rem' }}>{result}</div>
            <p className="result-desc">
              Based on your soil nutrients and type, this fertilizer is
              recommended to optimise plant growth and health.
            </p>
            <div className="flex gap-3 justify-center" style={{ flexWrap: 'wrap' }}>
              <button className="btn btn-primary" onClick={reset}>Try Another →</button>
              <Link to="/" className="btn btn-outline">Back to Home</Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="main-content">
      <div className="container" style={{ maxWidth: 580 }}>
        <div className="page-header animate-fade-up">
          <div className="page-header-icon" style={{ background: 'rgba(245,158,11,0.12)' }}>🧪</div>
          <div>
            <div className="page-header-title">Fertilizer Recommendation</div>
            <div className="page-header-desc">
              Enter soil nutrient levels and soil type to receive a targeted fertilizer suggestion.
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
              {[
                { key: 'nitrogen',   label: 'Nitrogen',   unit: 'mg/kg' },
                { key: 'phosphorus', label: 'Phosphorus', unit: 'mg/kg' },
                { key: 'potassium',  label: 'Potassium',  unit: 'mg/kg' },
              ].map(f => (
                <div className="form-group" key={f.key}>
                  <label className="form-label">
                    {f.label}
                    <span className="unit">{f.unit}</span>
                  </label>
                  <input
                    id={`fert-${f.key}`}
                    className="form-input"
                    type="number"
                    min={0} max={200}
                    placeholder="0–200"
                    value={values[f.key]}
                    onChange={set(f.key)}
                    required
                  />
                </div>
              ))}
            </div>

            <div className="form-group">
              <label className="form-label">Soil Type <span className="unit">(optional)</span></label>
              <select id="fert-soil" className="form-select" value={values.soil} onChange={set('soil')}>
                <option value="">— Select soil type —</option>
                {SOIL_TYPES.map(s => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>

            <button
              id="fert-submit"
              type="submit"
              className="btn btn-primary btn-lg btn-full mt-4"
              disabled={loading}
              style={{
                background: 'linear-gradient(135deg, #f59e0b, #ea580c)',
                boxShadow: loading ? 'none' : '0 0 24px rgba(245,158,11,0.3)',
              }}
            >
              {loading
                ? <><div className="spinner" /> Analysing…</>
                : '🧪  Recommend Fertilizer →'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
