import { useState } from 'react';
import { Link } from 'react-router-dom';
import { predictFertilizer } from '../api';

const SOIL_TYPES = [
  'Acidic Soil', 'Alkaline Soil', 'Loamy Soil', 'Neutral Soil', 'Peaty Soil',
];

export default function FertilizerRecommendation() {
  const [values, setValues] = useState({ nitrogen: '', phosphorus: '', potassium: '', soil: '' });
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
      const res = await predictFertilizer(values);
      const html = await res.text();
      
      const matches = [...html.matchAll(/<h5[^>]*>([^<]+)<\/h5>/gi)];
      const found = matches.map(m => m[1].trim()).filter(t => t !== 'Recommended Fertilizers');

      if (found.length > 0) {
        setResults(found);
      } else if (res.ok) {
        setResults(['Recommendation received — check response.']);
      } else {
        setError('Prediction failed. Please check your inputs.');
      }
    } catch (err) {
      console.error(err);
      setError('Network error. Make sure Django is running on port 8000.');
    } finally {
      setLoading(false);
    }
  }

  function reset() { setResults([]); setValues({ nitrogen: '', phosphorus: '', potassium: '', soil: '' }); setError(''); }

  if (results.length > 0) {
    return (
      <div className="main-content">
        <div className="container" style={{ maxWidth: 560, padding: '3rem 1.5rem' }}>
          <div className="glass-card result-card animate-fade-up">
            <div className="result-icon orange">🧪</div>
            <div className="result-label">Recommended Fertilizers</div>
            
            <div className="results-list" style={{ margin: '1.5rem 0' }}>
              {results.map((r, i) => (
                <div key={i} className={`result-item ${i === 0 ? 'primary' : 'secondary'}`} style={{
                  padding: i === 0 ? '1rem' : '0.75rem',
                  background: i === 0 ? 'rgba(249,115,22,0.1)' : 'rgba(255,255,255,0.05)',
                  borderRadius: '12px',
                  marginBottom: '0.75rem',
                  border: i === 0 ? '1px solid rgba(249,115,22,0.3)' : '1px solid rgba(255,255,255,0.1)',
                }}>
                  <div className="result-value" style={{ 
                    fontSize: i === 0 ? '1.8rem' : '1.2rem',
                    color: i === 0 ? 'var(--accent-orange)' : 'inherit',
                    fontWeight: 700 
                  }}>
                    {i === 0 ? '🥇 ' : i === 1 ? '🥈 ' : '🥉 '} {r}
                  </div>
                  <div style={{ fontSize: '0.8rem', opacity: 0.7 }}>
                    {i === 0 ? 'Best Match' : `Alternative Option ${i}`}
                  </div>
                </div>
              ))}
            </div>

            <p className="result-desc">
              These fertilizers are recommended to optimize your soil's nutrient balance.
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
