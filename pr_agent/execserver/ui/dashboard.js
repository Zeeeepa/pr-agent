/**
 * PR-Agent Dashboard Main UI Module
 * 
 * This module serves as the main entry point for the dashboard UI.
 * It initializes the dashboard components and handles the main UI logic.
 */

// Import required modules
import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import axios from 'axios';

// Import components
import Dashboard from './components/Dashboard';
import NotFound from './components/NotFound';

// Set up axios defaults
axios.defaults.baseURL = '/api/v1';
axios.defaults.headers.common['Content-Type'] = 'application/json';

// Initialize the dashboard
const initDashboard = () => {
  const root = ReactDOM.createRoot(document.getElementById('root'));
  
  root.render(
    <React.StrictMode>
      <Router>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Router>
    </React.StrictMode>
  );
};

// Export the initialization function
export { initDashboard };

// Initialize the dashboard when the module is loaded
document.addEventListener('DOMContentLoaded', initDashboard);

