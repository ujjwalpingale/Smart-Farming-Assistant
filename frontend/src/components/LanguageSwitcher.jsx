import { useTranslation } from 'react-i18next';

export default function LanguageSwitcher() {
  const { i18n } = useTranslation();

  const changeLanguage = (lng) => {
    i18n.changeLanguage(lng);
  };

  return (
    <div className="language-switcher" style={{ display: 'flex', gap: '8px' }}>
      <button 
        className={`btn btn-sm ${i18n.language === 'en' ? 'btn-primary' : 'btn-outline'}`}
        onClick={() => changeLanguage('en')}
        style={{ padding: '4px 8px', fontSize: '0.75rem' }}
      >
        English
      </button>
      <button 
        className={`btn btn-sm ${i18n.language === 'mr' ? 'btn-primary' : 'btn-outline'}`}
        onClick={() => changeLanguage('mr')}
        style={{ padding: '4px 8px', fontSize: '0.75rem' }}
      >
        मराठी
      </button>
    </div>
  );
}
