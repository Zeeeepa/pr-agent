import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Dashboard from './components/Dashboard'
import './App.css'

const App: React.FC = () => {
  const [darkMode, setDarkMode] = useState(false)

  useEffect(() => {
    // Check for user preference or system preference
    const savedTheme = localStorage.getItem('theme')
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    
    if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
      setDarkMode(true)
      document.getElementById('theme-stylesheet')?.removeAttribute('disabled')
    }
  }, [])

  const toggleTheme = () => {
    setDarkMode(!darkMode)
    if (darkMode) {
      document.getElementById('theme-stylesheet')?.setAttribute('disabled', '')
      localStorage.setItem('theme', 'light')
    } else {
      document.getElementById('theme-stylesheet')?.removeAttribute('disabled')
      localStorage.setItem('theme', 'dark')
    }
  }

  return (
    <Router>
      <div className={`app ${darkMode ? 'dark-mode' : ''}`}>
        <header className="app-header">
          <h1>PR Review Automator</h1>
          <button 
            className="theme-toggle" 
            onClick={toggleTheme}
            aria-label={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
          >
            {darkMode ? '☀️' : '🌙'}
          </button>
        </header>
        <Routes>
          <Route path="/" element={<Dashboard />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App

