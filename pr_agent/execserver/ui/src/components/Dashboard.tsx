import React, { useState } from 'react';
import ThemeToggle from './ThemeToggle';
import SettingsDialog from './SettingsDialog';

const Dashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('home');
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  const handleTabChange = (tab: string) => {
    setActiveTab(tab);
  };

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>PR-Agent Dashboard</h1>
        <div className="dashboard-actions">
          <ThemeToggle />
          <button onClick={() => setIsSettingsOpen(true)}>Settings</button>
        </div>
      </header>

      <div className="dashboard-tabs">
        <button 
          className={`tab ${activeTab === 'home' ? 'active' : ''}`}
          onClick={() => handleTabChange('home')}
          role="tab"
          aria-selected={activeTab === 'home'}
        >
          Home
        </button>
        <button 
          className={`tab ${activeTab === 'events' ? 'active' : ''}`}
          onClick={() => handleTabChange('events')}
          role="tab"
          aria-selected={activeTab === 'events'}
        >
          Event Triggers
        </button>
        <button 
          className={`tab ${activeTab === 'workflows' ? 'active' : ''}`}
          onClick={() => handleTabChange('workflows')}
          role="tab"
          aria-selected={activeTab === 'workflows'}
        >
          GitHub Workflows
        </button>
        <button 
          className={`tab ${activeTab === 'assistant' ? 'active' : ''}`}
          onClick={() => handleTabChange('assistant')}
          role="tab"
          aria-selected={activeTab === 'assistant'}
        >
          AI Assistant
        </button>
      </div>

      <div className="dashboard-content">
        {activeTab === 'home' && (
          <div className="home-content">
            <div className="card">
              <div className="card-header">
                <h2>Active Triggers</h2>
              </div>
              <div className="card-body">
                <p>You have 5 active triggers</p>
                <button onClick={() => handleTabChange('events')}>Manage Triggers</button>
              </div>
            </div>
            
            <div className="card">
              <div className="card-header">
                <h2>System Status</h2>
              </div>
              <div className="card-body">
                <p>All systems operational</p>
                <p>Last updated: {new Date().toLocaleTimeString()}</p>
              </div>
            </div>
          </div>
        )}
        
        {activeTab === 'events' && (
          <div className="events-content">
            <div className="card">
              <div className="card-header">
                <h2>Event Triggers</h2>
              </div>
              <div className="card-body">
                <p>Manage your event triggers here</p>
              </div>
            </div>
          </div>
        )}
        
        {activeTab === 'workflows' && (
          <div className="workflows-content">
            <div className="card">
              <div className="card-header">
                <h2>GitHub Workflows</h2>
              </div>
              <div className="card-body">
                <p>Manage your GitHub workflows here</p>
              </div>
            </div>
          </div>
        )}
        
        {activeTab === 'assistant' && (
          <div className="assistant-content">
            <div className="card">
              <div className="card-header">
                <h2>AI Assistant</h2>
              </div>
              <div className="card-body">
                <p>Chat with the AI assistant here</p>
              </div>
            </div>
          </div>
        )}
      </div>

      <SettingsDialog 
        isOpen={isSettingsOpen} 
        onClose={() => setIsSettingsOpen(false)} 
      />
    </div>
  );
};

export default Dashboard;

