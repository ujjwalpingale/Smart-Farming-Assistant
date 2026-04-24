import { Link, NavLink, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { logoutUser } from '../api';
import LanguageSwitcher from './LanguageSwitcher';

export default function Navbar({ user, setUser }) {
  const navigate = useNavigate();
  const { t } = useTranslation();

  async function handleLogout() {
    try { await logoutUser(); } catch (_) {}
    setUser(null);
    navigate('/login');
  }

  const initials = user ? user[0].toUpperCase() : '';

  return (
    <nav className="navbar">
      <div className="container navbar-inner">
        <Link to="/" className="navbar-brand">
          <div className="brand-icon">🌱</div>
          <span>{t('nav.brand')}</span>
        </Link>

        <ul className="navbar-links">
          <li><NavLink to="/">{t('common.home')}</NavLink></li>
          {user && (
            <>
              <li><NavLink to="/crop">🌾 {t('common.crop')}</NavLink></li>
              <li><NavLink to="/fertilizer">🧪 {t('common.fertilizer')}</NavLink></li>
              <li><NavLink to="/disease">🔬 {t('common.disease')}</NavLink></li>
            </>
          )}
        </ul>

        <div className="navbar-auth">
          <LanguageSwitcher />
          {user ? (
            <>
              <div className="user-chip">
                <div className="avatar">{initials}</div>
                <span>{user}</span>
              </div>
              <button
                className="btn btn-outline"
                style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem' }}
                onClick={handleLogout}
              >
                {t('common.sign_out')}
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn btn-outline">{t('common.sign_in')}</Link>
              <Link to="/register" className="btn btn-primary">{t('common.register')}</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
