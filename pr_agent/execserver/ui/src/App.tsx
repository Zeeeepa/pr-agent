import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import EventTriggers from './components/EventTriggers';
import GitHubWorkflows from './components/GitHubWorkflows';
import AIAssistant from './components/AIAssistant';
import SettingsDialog from './components/SettingsDialog';
import { ThemeProvider } from './contexts/ThemeContext';
import { SettingsProvider } from './contexts/SettingsContext';
import { ApiProvider } from './contexts/ApiContext';

const App: React.FC = () => {
  const [showSettings, setShowSettings] = useState(false);

  return (
    <Router>
      <ApiProvider>
        <SettingsProvider>
          <ThemeProvider>
            <div className="container">
              <header className="mb-4">
                <h1>PR-Agent Dashboard</h1>
                <div className="d-flex justify-content-between align-items-center mb-4">
                  <div></div>
                  <div>
                    <ThemeToggle />
                    <button 
                      className="btn btn-outline-secondary ms-2" 
                      onClick={() => setShowSettings(true)}
                    >
                      ⚙️ Settings
                    </button>
                  </div>
                </div>

                <nav>
                  <ul className="nav nav-tabs mb-4">
                    <li className="nav-item">
                      <Link to="/" className="nav-link">Home</Link>
                    </li>
                    <li className="nav-item">
                      <Link to="/triggers" className="nav-link">Event Triggers</Link>
                    </li>
                    <li className="nav-item">
                      <Link to="/workflows" className="nav-link">GitHub Workflows</Link>
                    </li>
                    <li className="nav-item">
                      <Link to="/chat" className="nav-link">AI Assistant</Link>
                    </li>
                  </ul>
                </nav>
              </header>

              <main>
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/triggers" element={<EventTriggers />} />
                  <Route path="/workflows" element={<GitHubWorkflows />} />
                  <Route path="/chat" element={<AIAssistant />} />
                </Routes>
              </main>

              {showSettings && (
                <SettingsDialog onClose={() => setShowSettings(false)} />
              )}
            </div>
          </ThemeProvider>
        </SettingsProvider>
      </ApiProvider>
    </Router>
  );
};

// Theme toggle component
const ThemeToggle: React.FC = () => {
  const [theme, setTheme] = useState(() => {
    const savedTheme = localStorage.getItem('theme');
    return savedTheme || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prevTheme => prevTheme === 'dark' ? 'light' : 'dark');
  };

  return (
    <button className="btn btn-outline-secondary" onClick={toggleTheme}>
      <span>{theme === 'dark' ? '☀️' : '🌙'}</span> Theme
    </button>
  );
};

export default App;

