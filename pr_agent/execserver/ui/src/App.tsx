import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import EventTriggers from './components/EventTriggers';
import Workflows from './components/Workflows';
import AIAssistant from './components/AIAssistant';
import Header from './components/Header';
import './App.css';

const App: React.FC = () => {
  const [theme, setTheme] = useState<'light' | 'dark'>(() => {
    const savedTheme = localStorage.getItem('theme');
    return (savedTheme === 'dark' || 
      (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches)) 
      ? 'dark' 
      : 'light';
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prevTheme => prevTheme === 'dark' ? 'light' : 'dark');
  };

  return (
    <Router>
      <div className="app-container">
        <Header theme={theme} toggleTheme={toggleTheme} />
        <div className="container">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/triggers" element={<EventTriggers />} />
            <Route path="/workflows" element={<Workflows />} />
            <Route path="/assistant" element={<AIAssistant />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
};

export default App;

