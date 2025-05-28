import React, { useState } from 'react';
import { useSettings } from '../contexts/SettingsContext';

interface SettingsDialogProps {
  onClose: () => void;
}

const SettingsDialog: React.FC<SettingsDialogProps> = ({ onClose }) => {
  const { settings, updateSettings, saveSettings, resetSettings, isLoading, error } = useSettings();
  const [validationMessage, setValidationMessage] = useState<{ type: 'success' | 'error', message: string } | null>(null);
  
  // Create local state to track form values
  const [formValues, setFormValues] = useState({
    githubToken: settings.githubToken,
    apiEndpoint: settings.apiEndpoint,
    notificationsEnabled: settings.notificationsEnabled,
    refreshInterval: settings.refreshInterval,
    theme: settings.theme,
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target as HTMLInputElement;
    
    setFormValues(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value,
    }));
  };

  const handleSave = async () => {
    // Validate form values
    if (formValues.refreshInterval < 5) {
      setValidationMessage({
        type: 'error',
        message: 'Refresh interval must be at least 5 seconds',
      });
      return;
    }

    // Update settings with form values
    updateSettings(formValues);
    
    try {
      await saveSettings();
      setValidationMessage({
        type: 'success',
        message: 'Settings saved successfully',
      });
      
      // Close dialog after a short delay
      setTimeout(() => {
        onClose();
      }, 1500);
    } catch (err) {
      setValidationMessage({
        type: 'error',
        message: 'Failed to save settings',
      });
    }
  };

  const handleReset = () => {
    resetSettings();
    setFormValues({
      githubToken: '',
      apiEndpoint: '/api/v1',
      notificationsEnabled: true,
      refreshInterval: 30,
      theme: 'system',
    });
    setValidationMessage({
      type: 'success',
      message: 'Settings reset to defaults',
    });
  };

  return (
    <div className="modal d-block" tabIndex={-1} role="dialog" style={{ backgroundColor: 'rgba(0, 0, 0, 0.5)' }}>
      <div className="modal-dialog" role="document">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">Settings</h5>
            <button type="button" className="btn-close" onClick={onClose} aria-label="Close"></button>
          </div>
          <div className="modal-body">
            <form>
              <div className="mb-3">
                <label htmlFor="githubToken" className="form-label">GitHub Token</label>
                <input
                  type="password"
                  className="form-control"
                  id="githubToken"
                  name="githubToken"
                  value={formValues.githubToken}
                  onChange={handleInputChange}
                  placeholder="Enter your GitHub token"
                />
                <div className="form-text">Used for GitHub API access</div>
              </div>
              
              <div className="mb-3">
                <label htmlFor="apiEndpoint" className="form-label">API Endpoint</label>
                <input
                  type="text"
                  className="form-control"
                  id="apiEndpoint"
                  name="apiEndpoint"
                  value={formValues.apiEndpoint}
                  onChange={handleInputChange}
                />
              </div>
              
              <div className="mb-3">
                <label htmlFor="refreshInterval" className="form-label">Refresh Interval (seconds)</label>
                <input
                  type="number"
                  className="form-control"
                  id="refreshInterval"
                  name="refreshInterval"
                  value={formValues.refreshInterval}
                  onChange={handleInputChange}
                  min="5"
                />
              </div>
              
              <div className="mb-3 form-check">
                <input
                  type="checkbox"
                  className="form-check-input"
                  id="notificationsEnabled"
                  name="notificationsEnabled"
                  checked={formValues.notificationsEnabled}
                  onChange={handleInputChange}
                />
                <label className="form-check-label" htmlFor="notificationsEnabled">
                  Enable Notifications
                </label>
              </div>
              
              <div className="mb-3">
                <label htmlFor="theme" className="form-label">Theme</label>
                <select
                  className="form-select"
                  id="theme"
                  name="theme"
                  value={formValues.theme}
                  onChange={handleInputChange}
                >
                  <option value="light">Light</option>
                  <option value="dark">Dark</option>
                  <option value="system">System Default</option>
                </select>
              </div>
            </form>
            
            {validationMessage && (
              <div className={`alert alert-${validationMessage.type === 'success' ? 'success' : 'danger'} mt-3`}>
                {validationMessage.message}
              </div>
            )}
            
            {error && (
              <div className="alert alert-danger mt-3">
                {error}
              </div>
            )}
          </div>
          <div className="modal-footer">
            <button 
              type="button" 
              className="btn btn-secondary" 
              onClick={handleReset}
            >
              Reset to Defaults
            </button>
            <button 
              type="button" 
              className="btn btn-primary" 
              onClick={handleSave}
              disabled={isLoading}
            >
              {isLoading ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsDialog;

