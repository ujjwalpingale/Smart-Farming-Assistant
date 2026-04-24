import { useState, useRef } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { predictDisease } from '../api';

export default function DiseaseDetection() {
  const { t } = useTranslation();
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
    if (!imageFile) { setError(t('disease.image_required') || 'Please upload a plant image.'); return; }
    setError('');
    setResult(null);
    setLoading(true);
    try {
      const res = await predictDisease({ crop_name: cropName, symptoms }, imageFile);
      if (res.ok) {
        const data = await res.json();
        setResult({
          disease: data.disease,
          prevention: data.prevention
        });
      } else {
        const data = await res.json().catch(() => ({}));
        setError(data.error || t('disease.detection_failed') || 'Detection failed.');
      }
    } catch {
      setError(t('common.network_error'));
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
            <div className="result-label">{t('disease.result_title')}</div>
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
                🛡 {t('disease.prevention')}
              </div>
              <p className="text-secondary text-sm" style={{ lineHeight: 1.7 }}>
                {result.prevention}
              </p>
            </div>

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
      <div className="container" style={{ maxWidth: 620 }}>
        <div className="page-header animate-fade-up">
          <div className="page-header-icon" style={{ background: 'rgba(244,63,94,0.12)' }}>🔬</div>
          <div>
            <div className="page-header-title">{t('disease.title')}</div>
            <div className="page-header-desc">
              {t('disease.desc')}
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
              <label className="form-label">{t('disease.crop_name')}</label>
              <select
                id="disease-crop"
                className="form-select"
                value={cropName}
                onChange={e => setCropName(e.target.value)}
                required
              >
                <option value="" disabled>{t('disease.select_crop')}</option>
                {['Apple', 'Cherry', 'Corn', 'Grape', 'Peach', 'Pepper', 'Potato', 'Tomato'].map(c => (
                  <option key={c} value={c}>{t(`disease.crops.${c}`)}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">{t('disease.symptoms')} <span className="unit">({t('common.optional')})</span></label>
              <textarea
                id="disease-symptoms"
                className="form-textarea"
                placeholder={t('disease.symptoms_placeholder')}
                value={symptoms}
                onChange={e => setSymptoms(e.target.value)}
                rows={3}
              />
            </div>

            <div className="form-group">
              <label className="form-label">{t('disease.image')} <span className="unit">{t('disease.image_hint')}</span></label>
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
                      {t('disease.drop_text')}
                    </div>
                    <div className="file-drop-hint">{t('disease.drop_hint')}</div>
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
                ? <><div className="spinner" /> {t('common.loading')}</>
                : t('common.detect')}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
