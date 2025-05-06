import React, { useState, useEffect } from 'react';

interface SettingsDialogProps {
  isOpen: boolean;
  onClose: () => void;
}

const SettingsDialog: React.FC<SettingsDialogProps> = ({ isOpen, onClose }) => {
  const [githubApiKey, setGithubApiKey] = useState('');
  const [supabaseUrl, setSupabaseUrl] = useState('');
  const [supabaseApiKey, setSupabaseApiKey] = useState('');
  const [validationMessage, setValidationMessage] = useState('');
  const [validationStatus, setValidationStatus] = useState<'success' | 'error' | ''>('');
  const [isValidating, setIsValidating] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    // Load settings from localStorage
    const loadSettings = () => {
      const githubKey = localStorage.getItem('github-api-key') || '';
      const sbUrl = localStorage.getItem('supabase-url') || '';
      const sbKey = localStorage.getItem('supabase-api-key') || '';
      
      setGithubApiKey(githubKey);
      setSupabaseUrl(sbUrl);
      setSupabaseApiKey(sbKey);
    };
    
    if (isOpen) {
      loadSettings();
    }
  }, [isOpen]);

  const validateSettings = async () => {
    if (!supabaseUrl || !supabaseApiKey) {
      setValidationMessage('Error: Supabase URL and API key are required');
      setValidationStatus('error');
      return;
    }

    setIsValidating(true);
    setValidationMessage('Validating settings...');
    setValidationStatus('');

    try {
      const response = await fetch('/api/v1/settings/validate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          GITHUB_TOKEN: githubApiKey,
          SUPABASE_URL: supabaseUrl,
          SUPABASE_ANON_KEY: supabaseApiKey
        }),
      });

      const data = await response.json();
      
      if (data.valid) {
        setValidationMessage('Verified! All credentials are valid');
        setValidationStatus('success');
      } else {
        setValidationMessage(data.message || 'Error: Invalid credentials');
        setValidationStatus('error');
      }
    } catch (error) {
      setValidationMessage('Error: Failed to validate settings');
      setValidationStatus('error');
    } finally {
      setIsValidating(false);
    }
  };

  const saveSettings = async () => {
    if (!supabaseUrl || !supabaseApiKey) {
      setValidationMessage('Error: Supabase URL and API key are required');
      setValidationStatus('error');
      return;
    }

    setIsSaving(true);
    setValidationMessage('Saving settings...');
    setValidationStatus('');

    try {
      // Save to localStorage
      localStorage.setItem('github-api-key', githubApiKey);
      localStorage.setItem('supabase-url', supabaseUrl);
      localStorage.setItem('supabase-api-key', supabaseApiKey);

      // Save to server
      const response = await fetch('/api/v1/settings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          GITHUB_TOKEN: githubApiKey,
          SUPABASE_URL: supabaseUrl,
          SUPABASE_ANON_KEY: supabaseApiKey
        }),
      });

      const data = await response.json();
      
      if (response.ok) {
        setValidationMessage('Settings saved successfully');
        setValidationStatus('success');
        
        setTimeout(() => {
          setValidationMessage('');
          setValidationStatus('');
        }, 2000);
      } else {
        setValidationMessage(data.message || 'Error: Failed to save settings');
        setValidationStatus('error');
      }
    } catch (error) {
      setValidationMessage('Error: Failed to save settings');
      setValidationStatus('error');
    } finally {
      setIsSaving(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div 
      className="settings-dialog" 
      style={{ display: 'flex' }}
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
      data-testid="settings-dialog"
    >
      <div className="settings-dialog-content">
        <div className="settings-dialog-header">
          <h4>Settings</h4>
          <span 
            className="settings-dialog-close" 
            onClick={onClose}
            aria-label="Close settings"
          >
            &times;
          </span>
        </div>
        
        <div className="settings-form-group">
          <label htmlFor="github-api-key">GitHub API Key</label>
          <input 
            type="password" 
            id="github-api-key" 
            className="form-control" 
            placeholder="Enter GitHub token (starts with ghp_ or github_pat_)"
            value={githubApiKey}
            onChange={(e) => setGithubApiKey(e.target.value)}
          />
          <small className="form-text text-muted">Personal access token with 'repo' scope</small>
        </div>
        
        <div className="settings-form-group">
          <label htmlFor="supabase-url">Supabase URL</label>
          <input 
            type="text" 
            id="supabase-url" 
            className="form-control" 
            placeholder="Enter Supabase URL (https://...)"
            value={supabaseUrl}
            onChange={(e) => setSupabaseUrl(e.target.value)}
          />
          <small className="form-text text-muted">URL from your Supabase project settings</small>
        </div>
        
        <div className="settings-form-group">
          <label htmlFor="supabase-api-key">Supabase API Key</label>
          <input 
            type="password" 
            id="supabase-api-key" 
            className="form-control" 
            placeholder="Enter Supabase anon key (starts with ey...)"
            value={supabaseApiKey}
            onChange={(e) => setSupabaseApiKey(e.target.value)}
          />
          <small className="form-text text-muted">Anon key from your Supabase project settings</small>
        </div>
        
        {validationMessage && (
          <div 
            className={`validation-message validation-${validationStatus}`} 
            style={{ display: 'block' }}
            data-testid="validation-message"
          >
            {validationMessage}
          </div>
        )}
        
        <div className="settings-dialog-footer">
          <button 
            id="validate-settings" 
            className="btn btn-info"
            onClick={validateSettings}
            disabled={isValidating}
          >
            {isValidating && (
              <span 
                className="spinner-border spinner-border-sm" 
                role="status" 
                aria-hidden="true"
              ></span>
            )}
            {' '}
            Validate
          </button>
          
          <button 
            id="save-settings" 
            className="btn btn-primary"
            onClick={saveSettings}
            disabled={isSaving}
          >
            {isSaving && (
              <span 
                className="spinner-border spinner-border-sm" 
                role="status" 
                aria-hidden="true"
              ></span>
            )}
            {' '}
            Save
          </button>
        </div>
      </div>
    </div>
  );
};

export default SettingsDialog;

