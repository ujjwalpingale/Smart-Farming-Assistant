import { useState } from 'react';
import { Link } from 'react-router-dom';
import { predictCrop } from '../api';

const FIELDS = [
  { key: 'nitrogen',    label: 'Nitrogen',     unit: 'mg/kg', min: 0, max: 200, step: 1,   placeholder: '0–200' },
  { key: 'phosphorus',  label: 'Phosphorus',   unit: 'mg/kg', min: 0, max: 200, step: 1,   placeholder: '0–200' },
  { key: 'potassium',   label: 'Potassium',    unit: 'mg/kg', min: 0, max: 200, step: 1,   placeholder: '0–200' },
  { key: 'temperature', label: 'Temperature',  unit: '°C',    min: 0, max: 60,  step: 0.1, placeholder: '0–60' },
  { key: 'humidity',    label: 'Humidity',     unit: '%',     min: 0, max: 100, step: 0.1, placeholder: '0–100' },
  { key: 'ph',          label: 'Soil pH',      unit: 'pH',    min: 0, max: 14,  step: 0.1, placeholder: '0–14' },
  { key: 'rainfall',    label: 'Rainfall',     unit: 'mm',    min: 0, max: 500, step: 0.1, placeholder: '0–500' },
];

export default function CropRecommendation() {
  const [values, setValues] = useState({});
  const [results, setResults] = useState([]); // Changed to list
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
      
      // Extract all H5 contents from the result list
      const matches = [...html.matchAll(/<h5[^>]*>([^<]+)<\/h5>/gi)];
      const found = matches.map(m => m[1].trim()).filter(t => t !== 'Recommended Crops');
      
      if (found.length > 0) {
        setResults(found);
      } else if (res.ok) {
        setResults(['Prediction received — check Django log.']);
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

  function reset() { setResults([]); setValues({}); setError(''); }

  if (results.length > 0) {
    return (
      <div className="main-content">
        <div className="container" style={{ maxWidth: 560, padding: '3rem 1.5rem' }}>
          <div className="glass-card result-card animate-fade-up">
            <div className="result-icon green">🌾</div>
            <div className="result-label">Recommended Crops</div>
            
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
                    {i === 0 ? '🥇 ' : i === 1 ? '🥈 ' : '🥉 '} {r}
                  </div>
                  <div style={{ fontSize: '0.8rem', opacity: 0.7 }}>
                    {i === 0 ? 'Best Match' : `Alternative Option ${i}`}
                  </div>
                </div>
              ))}
            </div>

            <p className="result-desc">
              Our AI has analyzed your conditions and identified these top choices for your farm.
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
      <div className="container" style={{ maxWidth: 680 }}>
        <div className="page-header animate-fade-up">
          <div className="page-header-icon" style={{ background: 'rgba(34,197,94,0.12)' }}>🌾</div>
          <div>
            <div className="page-header-title">Crop Recommendation</div>
            <div className="page-header-desc">
              Enter your soil and climate data to get an AI-powered crop suggestion.
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
                    {f.label}
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
                ? <><div className="spinner" /> Analysing…</>
                : '🌾  Predict Best Crop →'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
