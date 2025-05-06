import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

// Main dashboard component
const Dashboard = () => {
  return (
    <div className="container mt-4">
      <h1>PR-Agent Dashboard</h1>
      <div className="row mt-4">
        <div className="col-md-6">
          <div className="card">
            <div className="card-header">System Status</div>
            <div className="card-body">
              <p className="card-text">
                <span className="text-success">●</span> All systems operational
              </p>
              <p className="card-text">
                Last updated: {new Date().toLocaleString()}
              </p>
            </div>
          </div>
        </div>
        <div className="col-md-6">
          <div className="card">
            <div className="card-header">Quick Actions</div>
            <div className="card-body">
              <button className="btn btn-primary me-2">View Triggers</button>
              <button className="btn btn-secondary">Settings</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Settings page
const Settings = () => {
  return (
    <div className="container mt-4">
      <h1>Settings</h1>
      <div className="card mt-4">
        <div className="card-header">Application Settings</div>
        <div className="card-body">
          <form>
            <div className="mb-3">
              <label htmlFor="githubToken" className="form-label">
                GitHub Token
              </label>
              <input
                type="password"
                className="form-control"
                id="githubToken"
                placeholder="Enter GitHub token"
              />
            </div>
            <div className="mb-3">
              <label htmlFor="supabaseUrl" className="form-label">
                Supabase URL
              </label>
              <input
                type="text"
                className="form-control"
                id="supabaseUrl"
                placeholder="Enter Supabase URL"
              />
            </div>
            <div className="mb-3">
              <label htmlFor="supabaseKey" className="form-label">
                Supabase Key
              </label>
              <input
                type="password"
                className="form-control"
                id="supabaseKey"
                placeholder="Enter Supabase key"
              />
            </div>
            <button type="submit" className="btn btn-primary">
              Save Settings
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

// Not found page
const NotFound = () => {
  return (
    <div className="container mt-4 text-center">
      <h1>404 - Page Not Found</h1>
      <p>The page you are looking for does not exist.</p>
      <a href="/" className="btn btn-primary">
        Go to Dashboard
      </a>
    </div>
  );
};

// Main App component with routing
const App = () => {
  return (
    <Router>
      <div className="app">
        <nav className="navbar navbar-expand-lg navbar-dark bg-dark">
          <div className="container">
            <a className="navbar-brand" href="/">
              PR-Agent
            </a>
            <button
              className="navbar-toggler"
              type="button"
              data-bs-toggle="collapse"
              data-bs-target="#navbarNav"
              aria-controls="navbarNav"
              aria-expanded="false"
              aria-label="Toggle navigation"
            >
              <span className="navbar-toggler-icon"></span>
            </button>
            <div className="collapse navbar-collapse" id="navbarNav">
              <ul className="navbar-nav">
                <li className="nav-item">
                  <a className="nav-link" href="/">
                    Dashboard
                  </a>
                </li>
                <li className="nav-item">
                  <a className="nav-link" href="/settings">
                    Settings
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </nav>

        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;

