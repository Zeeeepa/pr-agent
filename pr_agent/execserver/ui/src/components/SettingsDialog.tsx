import React, { useState } from 'react';
import { useSettings } from '../contexts/SettingsContext';

interface SettingsDialogProps {
  onClose: () => void;
}

const SettingsDialog: React.FC<SettingsDialogProps> = ({ onClose }) => {
  const { settings, updateSettings, saveSettings, validateSettings, isLoading } = useSettings();
  const [validationMessage, setValidationMessage] = useState<{ text: string; type: 'success' | 'error' | 'info' } | null>(null);

  const handleSave = async () => {
    setValidationMessage({ text: 'Saving settings...', type: 'info' });
    
    try {
      await saveSettings();
      setValidationMessage({ text: 'Settings saved successfully!', type: 'success' });
      
      // Clear success message after a delay
      setTimeout(() => {
        setValidationMessage(null);
        onClose();
      }, 1500);
    } catch (err) {
      setValidationMessage({ text: 'Failed to save settings', type: 'error' });
    }
  };

  const handleValidate = async () => {
    setValidationMessage({ text: 'Validating settings...', type: 'info' });
    
    try {
      const result = await validateSettings();
      
      if (result.valid) {
        setValidationMessage({ text: 'Validation successful! All credentials are valid.', type: 'success' });
      } else {
        setValidationMessage({ 
          text: result.message || 'Validation failed. Please check your credentials.', 
          type: 'error' 
        });
      }
    } catch (err) {
      setValidationMessage({ text: 'Failed to validate settings', type: 'error' });
    }
  };

  return (
    <div className="modal" style={{ display: 'block', backgroundColor: 'rgba(0,0,0,0.5)' }}>
      <div className="modal-dialog modal-lg">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">Settings</h5>
            <button type="button" className="btn-close" onClick={onClose}></button>
          </div>
          <div className="modal-body">
            <div className="mb-3">
              <label htmlFor="github-token" className="form-label">GitHub API Token</label>
              <input
                type="password"
                className="form-control"
                id="github-token"
                value={settings.githubToken}
                onChange={(e) => updateSettings({ githubToken: e.target.value })}
                placeholder="Enter GitHub API token"
              />
              <div className="form-text">Used for GitHub API access. Requires repo and workflow permissions.</div>
            </div>
            
            <div className="mb-3">
              <label htmlFor="supabase-url" className="form-label">Supabase URL</label>
              <input
                type="text"
                className="form-control"
                id="supabase-url"
                value={settings.supabaseUrl}
                onChange={(e) => updateSettings({ supabaseUrl: e.target.value })}
                placeholder="https://your-project.supabase.co"
              />
            </div>
            
            <div className="mb-3">
              <label htmlFor="supabase-key" className="form-label">Supabase Anon Key</label>
              <input
                type="password"
                className="form-control"
                id="supabase-key"
                value={settings.supabaseApiKey}
                onChange={(e) => updateSettings({ supabaseApiKey: e.target.value })}
                placeholder="Enter Supabase anon key"
              />
            </div>
            
            <div className="mb-3">
              <label htmlFor="refresh-interval" className="form-label">Refresh Interval (ms)</label>
              <input
                type="number"
                className="form-control"
                id="refresh-interval"
                value={settings.refreshInterval}
                onChange={(e) => updateSettings({ refreshInterval: parseInt(e.target.value) })}
                min="5000"
                step="1000"
              />
              <div className="form-text">How often to refresh data (minimum 5000ms)</div>
            </div>
            
            <div className="mb-3 form-check">
              <input
                type="checkbox"
                className="form-check-input"
                id="auto-refresh"
                checked={settings.autoRefresh}
                onChange={(e) => updateSettings({ autoRefresh: e.target.checked })}
              />
              <label className="form-check-label" htmlFor="auto-refresh">Enable auto-refresh</label>
            </div>
            
            {validationMessage && (
              <div className={`alert alert-${validationMessage.type === 'success' ? 'success' : validationMessage.type === 'error' ? 'danger' : 'info'}`}>
                {validationMessage.text}
              </div>
            )}
          </div>
          <div className="modal-footer">
            <button 
              type="button" 
              className="btn btn-outline-secondary" 
              onClick={onClose}
            >
              Cancel
            </button>
            <button 
              type="button" 
              className="btn btn-outline-primary me-2" 
              onClick={handleValidate}
              disabled={isLoading}
            >
              {isLoading && validationMessage?.text === 'Validating settings...' ? (
                <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              ) : null}
              Validate
            </button>
            <button 
              type="button" 
              className="btn btn-primary" 
              onClick={handleSave}
              disabled={isLoading}
            >
              {isLoading && validationMessage?.text === 'Saving settings...' ? (
                <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              ) : null}
              Save
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsDialog;

