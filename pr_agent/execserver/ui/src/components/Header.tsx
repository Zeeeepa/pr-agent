import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import SettingsDialog from './SettingsDialog';
import './Header.css';

interface HeaderProps {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
}

const Header: React.FC<HeaderProps> = ({ theme, toggleTheme }) => {
  const [showSettings, setShowSettings] = useState(false);
  const location = useLocation();

  const isActive = (path: string) => {
    return location.pathname === path ? 'active' : '';
  };

  return (
    <header className="header">
      <div className="header-container">
        <h1 className="header-title">PR-Agent Dashboard</h1>
        
        <div className="header-actions">
          <button className="btn btn-outline-secondary" onClick={toggleTheme}>
            <span>{theme === 'dark' ? '☀️' : '🌙'}</span> Theme
          </button>
          <button className="btn btn-outline-secondary" onClick={() => setShowSettings(true)}>
            <span>⚙️</span> Settings
          </button>
        </div>
      </div>
      
      <nav className="nav-tabs">
        <Link to="/" className={`nav-link ${isActive('/')}`}>Home</Link>
        <Link to="/triggers" className={`nav-link ${isActive('/triggers')}`}>Event Triggers</Link>
        <Link to="/workflows" className={`nav-link ${isActive('/workflows')}`}>GitHub Workflows</Link>
        <Link to="/assistant" className={`nav-link ${isActive('/assistant')}`}>AI Assistant</Link>
      </nav>
      
      {showSettings && <SettingsDialog onClose={() => setShowSettings(false)} />}
    </header>
  );
};

export default Header;

