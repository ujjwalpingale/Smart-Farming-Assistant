import { Link, NavLink, useNavigate } from 'react-router-dom';
import { logoutUser } from '../api';

export default function Navbar({ user, setUser }) {
  const navigate = useNavigate();

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
          <span>Smart Farming</span>
        </Link>

        <ul className="navbar-links">
          <li><NavLink to="/">Home</NavLink></li>
          {user && (
            <>
              <li><NavLink to="/crop">🌾 Crop</NavLink></li>
              <li><NavLink to="/fertilizer">🧪 Fertilizer</NavLink></li>
              <li><NavLink to="/disease">🔬 Disease</NavLink></li>
            </>
          )}
        </ul>

        <div className="navbar-auth">
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
                Sign out
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn btn-outline">Sign in</Link>
              <Link to="/register" className="btn btn-primary">Register</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
