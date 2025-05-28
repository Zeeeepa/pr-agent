import React from 'react';

function App() {
  return (
    <div className="container">
      <h1 className="mb-4">PR-Agent Dashboard</h1>
      
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div></div>
        <div>
          <button id="settings-btn" className="btn btn-outline-secondary">
            <span id="settings-icon">⚙️</span> Settings
          </button>
        </div>
      </div>
      
      <div className="card">
        <div className="card-header">
          Welcome to PR-Agent
        </div>
        <div className="card-body">
          <p className="card-text">This is the PR-Agent Dashboard. The UI is currently in dark theme mode.</p>
        </div>
      </div>
    </div>
  );
}

export default App;

