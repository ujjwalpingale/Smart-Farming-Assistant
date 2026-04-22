import { useState, useRef } from 'react';
import { Link } from 'react-router-dom';
import { predictDisease } from '../api';

export default function DiseaseDetection() {
  const [cropName, setCropName]   = useState('');
  const [symptoms, setSymptoms]   = useState('');
  const [imageFile, setImageFile] = useState(null);
  const [preview, setPreview]     = useState(null);
  const [dragOver, setDragOver]   = useState(false);
  const [result, setResult]       = useState(null);
  const [error, setError]         = useState('');
  const [loading, setLoading]     = useState(false);
  const inputRef = useRef();

  function handleFile(file) {
    if (!file) return;
    setImageFile(file);
    setPreview(URL.createObjectURL(file));
  }

  function onDrop(e) {
    e.preventDefault();
    setDragOver(false);
    handleFile(e.dataTransfer.files[0]);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!imageFile) { setError('Please upload a plant image.'); return; }
    setError('');
    setResult(null);
    setLoading(true);
    try {
      const res = await predictDisease({ crop_name: cropName, symptoms }, imageFile);
      const html = await res.text();
      const diseaseMatch = html.match(/Detected Disease[\s\S]*?<h5[^>]*>([^<]+)<\/h5>/i)
                        || html.match(/alert-success[^>]*>[\s\S]*?<h5[^>]*>\s*([^<]+)\s*<\/h5>/i);
      const prevMatch    = html.match(/Prevention[\s\S]*?<p[^>]*class="text-muted"[^>]*>([^<]+)<\/p>/i)
                        || html.match(/<p class="text-muted">([^<]+)<\/p>/i);
      if (diseaseMatch) {
        setResult({
          disease:    diseaseMatch[1].trim(),
          prevention: prevMatch ? prevMatch[1].trim() : 'Consult an agricultural specialist for prevention advice.',
        });
      } else if (res.ok) {
        setResult({ disease: 'Unknown', prevention: 'Could not parse response from server.' });
      } else {
        setError('Detection failed. Please try with a different image.');
      }
    } catch {
      setError('Network error. Make sure Django is running on port 8000.');
    } finally {
      setLoading(false);
    }
  }

  function reset() {
    setResult(null); setCropName(''); setSymptoms('');
    setImageFile(null); setPreview(null); setError('');
  }

  if (result) {
    return (
      <div className="main-content">
        <div className="container" style={{ maxWidth: 600, padding: '3rem 1.5rem' }}>
          <div className="glass-card animate-fade-up" style={{ padding: '2.5rem', textAlign: 'center' }}>
            {preview && (
              <img
                src={preview}
                alt="Uploaded plant"
                style={{
                  width: 160, height: 160,
                  objectFit: 'cover',
                  borderRadius: 'var(--radius-lg)',
                  marginBottom: '1.5rem',
                  border: '2px solid var(--border)',
                }}
              />
            )}
            <div className="result-icon rose" style={{ margin: '0 auto 1.5rem' }}>🔬</div>
            <div className="result-label">Detected Disease</div>
            <div className="result-value" style={{ fontSize: '1.8rem', marginBottom: '1.25rem' }}>
              {result.disease}
            </div>

            <div
              className="glass-card"
              style={{ padding: '1.25rem 1.5rem', textAlign: 'left', marginBottom: '1.5rem' }}
            >
              <div
                style={{
                  fontSize: '0.72rem', fontWeight: 700, letterSpacing: '0.08em',
                  textTransform: 'uppercase', color: 'var(--accent-rose)', marginBottom: '0.5rem',
                }}
              >
                🛡 Prevention Advice
              </div>
              <p className="text-secondary text-sm" style={{ lineHeight: 1.7 }}>
                {result.prevention}
              </p>
            </div>

            <div className="flex gap-3 justify-center" style={{ flexWrap: 'wrap' }}>
              <button className="btn btn-primary" onClick={reset}>Analyse Another →</button>
              <Link to="/" className="btn btn-outline">Back to Home</Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="main-content">
      <div className="container" style={{ maxWidth: 620 }}>
        <div className="page-header animate-fade-up">
          <div className="page-header-icon" style={{ background: 'rgba(244,63,94,0.12)' }}>🔬</div>
          <div>
            <div className="page-header-title">Plant Disease Detection</div>
            <div className="page-header-desc">
              Upload a clear photo of your plant and let our deep learning model
              identify the disease.
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
            <div className="form-group">
              <label className="form-label">Crop Name</label>
              <select
                id="disease-crop"
                className="form-select"
                value={cropName}
                onChange={e => setCropName(e.target.value)}
                required
              >
                <option value="" disabled>Select a crop...</option>
                <option value="Apple">Apple</option>
                <option value="Cherry">Cherry</option>
                <option value="Corn">Corn</option>
                <option value="Grape">Grape</option>
                <option value="Peach">Peach</option>
                <option value="Pepper">Pepper</option>
                <option value="Potato">Potato</option>
                <option value="Tomato">Tomato</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Symptoms <span className="unit">(optional)</span></label>
              <textarea
                id="disease-symptoms"
                className="form-textarea"
                placeholder="Describe visible symptoms — yellowing, spots, wilting…"
                value={symptoms}
                onChange={e => setSymptoms(e.target.value)}
                rows={3}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Plant Image <span className="unit">required · JPG/PNG/BMP · max 5 MB</span></label>
              <div
                className={`file-drop${dragOver ? ' drag-over' : ''}`}
                onDragOver={e => { e.preventDefault(); setDragOver(true); }}
                onDragLeave={() => setDragOver(false)}
                onDrop={onDrop}
                onClick={() => inputRef.current?.click()}
              >
                <input
                  ref={inputRef}
                  id="disease-image"
                  type="file"
                  accept="image/*"
                  style={{ display: 'none' }}
                  onChange={e => handleFile(e.target.files[0])}
                />
                {preview ? (
                  <div>
                    <img
                      src={preview}
                      alt="Preview"
                      style={{
                        maxHeight: 160,
                        maxWidth: '100%',
                        borderRadius: 'var(--radius-md)',
                        marginBottom: '0.5rem',
                      }}
                    />
                    <div className="file-drop-text" style={{ color: 'var(--accent-green)' }}>
                      ✓ {imageFile?.name}
                    </div>
                    <div className="file-drop-hint">Click to change image</div>
                  </div>
                ) : (
                  <>
                    <div className="file-drop-icon">📷</div>
                    <div className="file-drop-text">
                      Drag & drop or <span style={{ color: 'var(--accent-green)' }}>browse</span>
                    </div>
                    <div className="file-drop-hint">Supports JPG, PNG, BMP, GIF</div>
                  </>
                )}
              </div>
            </div>

            <button
              id="disease-submit"
              type="submit"
              className="btn btn-primary btn-lg btn-full mt-4"
              disabled={loading}
              style={{
                background: 'linear-gradient(135deg, #f43f5e, #8b5cf6)',
                boxShadow: loading ? 'none' : '0 0 24px rgba(244,63,94,0.3)',
              }}
            >
              {loading
                ? <><div className="spinner" /> Detecting…</>
                : '🔬  Detect Disease →'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
