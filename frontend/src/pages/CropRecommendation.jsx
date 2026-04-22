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
      const res = await predictCrop(values);
      // Django renders a result page; parse the result from the HTML
      const html = await res.text();
      // Try to find "Recommended Crop" heading content
      const m = html.match(/Recommended Crop[\s\S]*?<h5[^>]*>([^<]+)<\/h5>/i)
             || html.match(/result"\}>([^<]+)<\/h5>/i)
             || html.match(/alert-success[^>]*>[\s\S]*?<h5[^>]*>\s*([^<]+)\s*<\/h5>/i);
      if (m) {
        setResult(m[1].trim());
      } else if (res.ok) {
        setResult('Prediction received — check Django HTML for result.');
      } else {
        setError('Prediction failed. Please check your inputs.');
      }
    } catch {
      setError('Network error. Make sure Django is running on port 8000.');
    } finally {
      setLoading(false);
    }
  }

  function reset() { setResult(null); setValues({}); setError(''); }

  if (result) {
    return (
      <div className="main-content">
        <div className="container" style={{ maxWidth: 560, padding: '3rem 1.5rem' }}>
          <div className="glass-card result-card animate-fade-up">
            <div className="result-icon green">🌾</div>
            <div className="result-label">Recommended Crop</div>
            <div className="result-value">{result}</div>
            <p className="result-desc">
              Based on your soil and climate parameters, this crop is predicted
              to deliver the best yield for your conditions.
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
