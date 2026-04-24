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

const LOCATIONS = {
  "Ahmednagar": ["Akole", "Jamkhed", "Karjat", "Kopargaon", "Nagar", "Nevasa", "Parner", "Pathardi", "Rahata", "Rahuri", "Sangamner", "Shevgaon", "Shrirampur", "Shrigonda"],
  "Akola": ["Akola", "Akot", "Balapur", "Barshitakli", "Murtijapur", "Patur", "Telhara"],
  "Amravati": ["Achalpur", "Amravati", "Anjangaon Surji", "Chandur Bazar", "Chandur Railway", "Chikhaldara", "Daryapur", "Dhamangaon Railway", "Dharni", "Morshi", "Nandgaon Khandeshwar", "Teosa", "Warud"],
  "Aurangabad": ["Aurangabad", "Chitegaon", "Gangapur", "Kannad", "Khuldabad", "Paithan", "Phulambri", "Sillod", "Soegaon", "Vaijapur"],
  "Beed": ["Ambejogai", "Ashti", "Beed", "Dharur", "Gevrai", "Kaij", "Majalgaon", "Parli", "Patoda", "Shirur", "Wadwani"],
  "Bhandara": ["Bhandara", "Lakhandur", "Lakhani", "Mohadi", "Pauni", "Sakoli", "Tumsar"],
  "Buldhana": ["Buldhana", "Chikhli", "Deulgaon Raja", "Jalgaon Jamod", "Khamgaon", "Lonar", "Malkapur", "Mehkar", "Motala", "Nandura", "Sangrampur", "Shegaon", "Sindkhed Raja"],
  "Chandrapur": ["Ballarpur", "Brahmapuri", "Chandrapur", "Chimur", "Gondpipri", "Jiwati", "Korpana", "Mul", "Nagbhir", "Pombhurna", "Rajura", "Sawali", "Sindewahi", "Warora"],
  "Dhule": ["Dhule", "Sakri", "Shirpur", "Shindkheda"],
  "Gadchiroli": ["Aheri", "Armori", "Bhamragad", "Chamorshi", "Desaiganj", "Dhanora", "Etapalli", "Gadchiroli", "Korchi", "Kurkheda", "Mulchera", "Sironcha"],
  "Gondia": ["Amgaon", "Arjuni Morgaon", "Deori", "Gondia", "Goregaon", "Sadak Arjuni", "Salekasa", "Tirora"],
  "Hingoli": ["Aundha Nagnath", "Basmath", "Hingoli", "Kalamnuri", "Sengaon"],
  "Jalgaon": ["Amalner", "Bhadgaon", "Bhusawal", "Bodwad", "Chalisgaon", "Chopda", "Dharangaon", "Erandol", "Jalgaon", "Jamner", "Muktainagar", "Pachora", "Parola", "Raver", "Yawal"],
  "Jalna": ["Ambad", "Badnapur", "Bhokardan", "Ghansawangi", "Jalna", "Jafrabad", "Mantha", "Partur"],
  "Kolhapur": ["Ajara", "Bawada", "Chandgad", "Gadhiglaj", "Hatkanangle", "Kagal", "Karveer", "Panhala", "Radhanagari", "Shahuwadi", "Shirol"],
  "Latur": ["Ahmadpur", "Ausa", "Chakaur", "Deoni", "Jalkot", "Latur", "Nilanga", "Renapur", "Shirur Anantpal", "Udgir"],
  "Mumbai": ["Mumbai City", "Mumbai Suburban"],
  "Nagpur": ["Hingna", "Kamptee", "Kanhan", "Katol", "Kuhi", "Mauda", "Nagpur Urban", "Nagpur Rural", "Narkhed", "Parseoni", "Ramtek", "Savner", "Umred"],
  "Nanded": ["Ardhapur", "Bhokar", "Biloli", "Deglur", "Dharmabad", "Hadgaon", "Himayatnagar", "Kandhar", "Kinwat", "Loha", "Mahoor", "Mudkhed", "Mukhed", "Naigaon", "Nanded", "Umri"],
  "Nandurbar": ["Akkalkuwa", "Akrani", "Nandurbar", "Navapur", "Shahada", "Taloda"],
  "Nashik": ["Baglan", "Chandwad", "Deola", "Dindori", "Igatpuri", "Kalwan", "Malegaon", "Nandgaon", "Nashik", "Niphad", "Peint", "Sinnar", "Surgana", "Trimbakeshwar", "Yeola"],
  "Osmanabad": ["Bhum", "Kalamb", "Lohara", "Osmanabad", "Paranda", "Tuljapur", "Umarga", "Washi"],
  "Palghar": ["Dahanu", "Jawhar", "Mokhada", "Palghar", "Talasari", "Vada", "Vikramgad", "Vasai-Virar"],
  "Parbhani": ["Gangakhed", "Jintur", "Manwath", "Palam", "Parbhani", "Pathri", "Purna", "Sailu", "Sonpeth"],
  "Pune": ["Ambegaon", "Baramati", "Bhor", "Daund", "Haveli", "Indapur", "Junnar", "Khed", "Maval", "Mulshi", "Pune City", "Purandar", "Shirur", "Velhe"],
  "Raigad": ["Alibag", "Karjat", "Khalapur", "Mahad", "Mangaon", "Mhasala", "Murud", "Panvel", "Pen", "Poladpur", "Roha", "Shrivardhan", "Sudhagad", "Tala", "Uran"],
  "Ratnagiri": ["Chiplun", "Dapoli", "Guhagar", "Khed", "Lanja", "Mandangad", "Rajapur", "Ratnagiri", "Sangameshwar"],
  "Sangli": ["Atpadi", "Jat", "Kavathe Mahankal", "Khanapur", "Miraj", "Palus", "Shirala", "Tasgaon", "Walwa"],
  "Satara": ["Jaoli", "Karad", "Khandala", "Khatav", "Koregaon", "Mahabaleshwar", "Man", "Patan", "Phaltan", "Satara", "Wai"],
  "Sindhudurg": ["Devgad", "Kankavli", "Kudal", "Malvan", "Sawantwadi", "Vaibhavwadi", "Vengurla", "Dodamarg"],
  "Solapur": ["Akkalkot", "Barshi", "Karmala", "Madha", "Malshiras", "Mangalvedhe", "Mohol", "Pandharpur", "Sangola", "Solapur North", "Solapur South"],
  "Thane": ["Ambarnath", "Bhivandi", "Kalyan", "Murbad", "Shahapur", "Thane", "Ulhasnagar"],
  "Wardha": ["Arvi", "Ashti", "Deoli", "Hinganghat", "Karanjha", "Seloo", "Samudrapur", "Wardha"],
  "Washim": ["Karanja", "Mangrulpir", "Manora", "Risod", "Washim"],
  "Yavatmal": ["Arni", "Babulgaon", "Darwha", "Digras", "Ghatanji", "Kalamb", "Kelapur", "Mahagaon", "Maregaon", "Ner", "Pusad", "Ralegaon", "Umarkhed", "Wani", "Yavatmal", "Zari-Jamani"],
};

export default function CropRecommendation() {
  const { t } = useTranslation();
  const [values, setValues] = useState({});
  const [results, setResults] = useState([]);
  const [error, setError]   = useState('');
  const [loading, setLoading] = useState(false);
  
  // New Location Features
  const [inputMode, setInputMode] = useState('manual'); // 'manual' or 'location'
  const [selectedDistrict, setSelectedDistrict] = useState('');
  const [selectedTaluka, setSelectedTaluka] = useState('');
  const [weatherLoading, setWeatherLoading] = useState(false);
  const [weatherSuccess, setWeatherSuccess] = useState(false);

  const set = k => e => setValues(v => ({ ...v, [k]: e.target.value }));

  const fetchWeather = async () => {
    if (!selectedDistrict || !selectedTaluka) {
      setError(t('common.select_location') || 'Please select District and Taluka');
      return;
    }

    setWeatherLoading(true);
    setWeatherSuccess(false);
    setError('');

    try {
      const res = await fetch(`/api/weather/?district=${selectedDistrict}&taluka=${selectedTaluka}`);
      const data = await res.json();
      
      if (!res.ok) throw new Error(data.error || 'Failed to fetch');

      setValues(v => ({
        ...v,
        temperature: data.temperature,
        humidity: data.humidity,
        rainfall: data.rainfall
      }));

      setWeatherLoading(false);
      setWeatherSuccess(true);

    } catch (err) {
      setError(err.message || t('common.weather_error'));
      setWeatherLoading(false);
    }
  };

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setResults([]);
    setLoading(true);
    try {
      const res = await predictCrop(values);
      if (res.ok) {
        const data = await res.json();
        setResults(data.results || []);
      } else {
        const data = await res.json().catch(() => ({}));
        setError(data.error || t('common.error_msg'));
      }
    } catch (err) {
      console.error(err);
      setError(t('common.network_error'));
    } finally {
      setLoading(false);
    }
  }

  function reset() { 
    setResults([]); 
    setValues({}); 
    setError(''); 
    setInputMode('manual');
    setSelectedDistrict('');
    setSelectedTaluka('');
    setWeatherSuccess(false);
  }

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

          {/* Mode Selection */}
          <div className="mode-selection mb-6" style={{ 
            display: 'flex', 
            gap: '1rem', 
            background: 'rgba(255,255,255,0.03)', 
            padding: '1rem', 
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--border)'
          }}>
            <label className="flex items-center gap-2 pointer">
              <input type="radio" name="inputMode" value="manual" 
                checked={inputMode === 'manual'} onChange={() => setInputMode('manual')} />
              <span>{t('crop.manual')}</span>
            </label>
            <label className="flex items-center gap-2 pointer">
              <input type="radio" name="inputMode" value="location" 
                checked={inputMode === 'location'} onChange={() => setInputMode('location')} />
              <span>{t('crop.location')}</span>
            </label>
          </div>

          <form onSubmit={handleSubmit}>
            {/* Location Dropdowns */}
            {inputMode === 'location' && (
              <div className="location-group mb-6 p-4 animate-fade-up" style={{ 
                background: 'rgba(34,197,94,0.05)', 
                borderRadius: 'var(--radius-md)',
                border: '1px dotted var(--accent-green)'
              }}>
                <div className="form-row">
                  <div className="form-group">
                    <label className="form-label">{t('crop.district')}</label>
                    <select 
                      className="form-input" 
                      value={selectedDistrict} 
                      onChange={(e) => { setSelectedDistrict(e.target.value); setSelectedTaluka(''); }}
                    >
                      <option value="">{t('common.select')}</option>
                      {Object.keys(LOCATIONS).sort().map(d => (
                        <option key={d} value={d}>{d}</option>
                      ))}
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">{t('crop.taluka')}</label>
                    <select 
                      className="form-input" 
                      value={selectedTaluka} 
                      onChange={(e) => setSelectedTaluka(e.target.value)}
                      disabled={!selectedDistrict}
                    >
                      <option value="">{t('common.select')}</option>
                      {(LOCATIONS[selectedDistrict] || []).sort().map(t => (
                        <option key={t} value={t}>{t}</option>
                      ))}
                    </select>
                  </div>
                </div>
                <button 
                  type="button" 
                  className="btn btn-outline btn-full mt-3"
                  onClick={fetchWeather}
                  disabled={weatherLoading || !selectedTaluka}
                >
                  {weatherLoading ? <div className="spinner" /> : `🌦 ${t('crop.fetch_weather')}`}
                </button>
                {weatherSuccess && (
                  <p style={{ fontSize: '0.75rem', color: 'var(--accent-green)', marginTop: '0.5rem', textAlign: 'center' }}>
                    ✅ {t('crop.weather_note')}
                  </p>
                )}
              </div>
            )}

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
