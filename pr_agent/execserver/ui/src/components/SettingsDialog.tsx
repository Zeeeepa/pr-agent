import React, { useState } from 'react';

interface SettingsDialogProps {
  isOpen: boolean;
  onClose: () => void;
}

const SettingsDialog: React.FC<SettingsDialogProps> = ({ isOpen, onClose }) => {
  const [githubToken, setGithubToken] = useState('');
  const [apiUrl, setApiUrl] = useState('');
  const [saving, setSaving] = useState(false);

  if (!isOpen) return null;

  const handleSave = () => {
    setSaving(true);
    
    // Simulate API call with a timeout
    setTimeout(() => {
      // In a real app, you would save the settings to the server
      // await fetch('/api/v1/settings', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ githubToken, apiUrl })
      // });
      
      setSaving(false);
      onClose();
    }, 500);
  };

  return (
    <div className="settings-dialog-overlay">
      <div className="settings-dialog-content">
        <div className="settings-dialog-header">
          <h2>Settings</h2>
          <button 
            className="settings-dialog-close" 
            onClick={onClose}
            aria-label="Close settings"
          >
            ×
          </button>
        </div>
        
        <div className="settings-dialog-body">
          <div className="form-group">
            <label htmlFor="github-token">GitHub Token</label>
            <input
              id="github-token"
              type="password"
              value={githubToken}
              onChange={(e) => setGithubToken(e.target.value)}
              placeholder="Enter your GitHub token"
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="api-url">API URL</label>
            <input
              id="api-url"
              type="text"
              value={apiUrl}
              onChange={(e) => setApiUrl(e.target.value)}
              placeholder="Enter API URL"
            />
          </div>
        </div>
        
        <div className="settings-dialog-footer">
          <button onClick={onClose}>Cancel</button>
          <button 
            onClick={handleSave} 
            disabled={saving}
          >
            {saving ? 'Saving...' : 'Save'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default SettingsDialog;
