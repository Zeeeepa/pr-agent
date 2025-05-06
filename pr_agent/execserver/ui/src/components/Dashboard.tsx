import React, { useState, useEffect } from 'react';
import ThemeToggle from './ThemeToggle';
import SettingsDialog from './SettingsDialog';

const Dashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('home');
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(new Date().toLocaleString());
  const [systemStatus, setSystemStatus] = useState<'active' | 'inactive'>('active');
  const [activeTriggerCount, setActiveTriggerCount] = useState(0);

  useEffect(() => {
    // Check database status
    const checkDatabaseStatus = async () => {
      try {
        const response = await fetch('/api/v1/database/status');
        const data = await response.json();
        
        setSystemStatus(data.status === 'connected' ? 'active' : 'inactive');
      } catch (error) {
        console.error('Error checking database status:', error);
        setSystemStatus('inactive');
      }
    };

    // Get trigger count
    const getTriggerCount = async () => {
      try {
        const response = await fetch('/api/v1/triggers');
        const data = await response.json();
        
        // Count active triggers
        const activeCount = data.filter((trigger: any) => trigger.enabled).length;
        setActiveTriggerCount(activeCount);
      } catch (error) {
        console.error('Error getting triggers:', error);
      }
    };

    checkDatabaseStatus();
    getTriggerCount();
    setLastUpdated(new Date().toLocaleString());

    // Set up auto-refresh
    const intervalId = setInterval(() => {
      checkDatabaseStatus();
      setLastUpdated(new Date().toLocaleString());
    }, 30000); // 30 seconds

    return () => clearInterval(intervalId);
  }, []);

  const handleTabClick = (tabId: string) => {
    setActiveTab(tabId);
  };

  return (
    <div className="container">
      <h1 className="mb-4">PR-Agent Dashboard</h1>
      
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div></div>
        <div>
          <ThemeToggle className="me-2" />
          <button 
            id="settings-btn" 
            className="btn btn-outline-secondary"
            onClick={() => setIsSettingsOpen(true)}
          >
            <span id="settings-icon">⚙️</span> Settings
          </button>
        </div>
      </div>
      
      <ul className="nav nav-tabs mb-4" id="myTab" role="tablist">
        <li className="nav-item" role="presentation">
          <button 
            className={`nav-link ${activeTab === 'home' ? 'active' : ''}`} 
            id="home-tab" 
            onClick={() => handleTabClick('home')}
            type="button" 
            role="tab" 
            aria-controls="home" 
            aria-selected={activeTab === 'home'}
          >
            Home
          </button>
        </li>
        <li className="nav-item" role="presentation">
          <button 
            className={`nav-link ${activeTab === 'triggers' ? 'active' : ''}`} 
            id="triggers-tab" 
            onClick={() => handleTabClick('triggers')}
            type="button" 
            role="tab" 
            aria-controls="triggers" 
            aria-selected={activeTab === 'triggers'}
          >
            Event Triggers
          </button>
        </li>
        <li className="nav-item" role="presentation">
          <button 
            className={`nav-link ${activeTab === 'workflows' ? 'active' : ''}`} 
            id="workflows-tab" 
            onClick={() => handleTabClick('workflows')}
            type="button" 
            role="tab" 
            aria-controls="workflows" 
            aria-selected={activeTab === 'workflows'}
          >
            GitHub Workflows
          </button>
        </li>
        <li className="nav-item" role="presentation">
          <button 
            className={`nav-link ${activeTab === 'chat' ? 'active' : ''}`} 
            id="chat-tab" 
            onClick={() => handleTabClick('chat')}
            type="button" 
            role="tab" 
            aria-controls="chat" 
            aria-selected={activeTab === 'chat'}
          >
            AI Assistant
          </button>
        </li>
      </ul>
      
      <div className="tab-content" id="myTabContent">
        <div 
          className={`tab-pane fade ${activeTab === 'home' ? 'show active' : ''}`} 
          id="home" 
          role="tabpanel" 
          aria-labelledby="home-tab"
        >
          <div className="row">
            <div className="col-md-6">
              <div className="card">
                <div className="card-header">
                  Active Triggers
                </div>
                <div className="card-body">
                  <p className="card-text">You have <strong>{activeTriggerCount}</strong> active triggers configured.</p>
                  <button 
                    className="btn btn-primary" 
                    onClick={() => handleTabClick('triggers')}
                  >
                    Manage Triggers
                  </button>
                </div>
              </div>
            </div>
            <div className="col-md-6">
              <div className="card">
                <div className="card-header">
                  System Status
                </div>
                <div className="card-body">
                  <p className="card-text">
                    <span className={`status-${systemStatus}`}>●</span> 
                    {systemStatus === 'active' ? 'All systems operational' : 'System issues detected'}
                  </p>
                  <p className="card-text">Last updated: <span id="last-updated">{lastUpdated}</span></p>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div 
          className={`tab-pane fade ${activeTab === 'triggers' ? 'show active' : ''}`} 
          id="triggers" 
          role="tabpanel" 
          aria-labelledby="triggers-tab"
        >
          <div className="card">
            <div className="card-header">Event Triggers</div>
            <div className="card-body">
              <p>Event triggers content will be displayed here.</p>
            </div>
          </div>
        </div>
        
        <div 
          className={`tab-pane fade ${activeTab === 'workflows' ? 'show active' : ''}`} 
          id="workflows" 
          role="tabpanel" 
          aria-labelledby="workflows-tab"
        >
          <div className="card">
            <div className="card-header">GitHub Workflows</div>
            <div className="card-body">
              <p>GitHub workflows content will be displayed here.</p>
            </div>
          </div>
        </div>
        
        <div 
          className={`tab-pane fade ${activeTab === 'chat' ? 'show active' : ''}`} 
          id="chat" 
          role="tabpanel" 
          aria-labelledby="chat-tab"
        >
          <div className="card">
            <div className="card-header">AI Assistant</div>
            <div className="card-body">
              <p>AI Assistant content will be displayed here.</p>
            </div>
          </div>
        </div>
      </div>
      
      <SettingsDialog 
        isOpen={isSettingsOpen} 
        onClose={() => setIsSettingsOpen(false)} 
      />
    </div>
  );
};

export default Dashboard;

