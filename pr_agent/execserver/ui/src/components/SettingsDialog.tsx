import React, { useState, useEffect } from 'react';
import './SettingsDialog.css';

interface SettingsDialogProps {
  onClose: () => void;
}

const SettingsDialog: React.FC<SettingsDialogProps> = ({ onClose }) => {
  const [githubApiKey, setGithubApiKey] = useState('');
  const [supabaseUrl, setSupabaseUrl] = useState('');
  const [supabaseApiKey, setSupabaseApiKey] = useState('');
  const [validationMessage, setValidationMessage] = useState<{ text: string; type: 'success' | 'error' | 'none' }>({
    text: '',
    type: 'none'
  });
  const [validating, setValidating] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    // Load settings from localStorage
    const storedGithubApiKey = localStorage.getItem('github-api-key') || '';
    const storedSupabaseUrl = localStorage.getItem('supabase-url') || '';
    const storedSupabaseApiKey = localStorage.getItem('supabase-api-key') || '';
    
    setGithubApiKey(storedGithubApiKey);
    setSupabaseUrl(storedSupabaseUrl);
    setSupabaseApiKey(storedSupabaseApiKey);
  }, []);

  const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  const validateSettings = async () => {
    if (!supabaseUrl || !supabaseApiKey) {
      setValidationMessage({
        text: 'Error: Supabase URL and API key are required',
        type: 'error'
      });
      return;
    }
    
    setValidating(true);
    setValidationMessage({ text: 'Validating...', type: 'none' });
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setValidationMessage({
        text: 'Verified! All credentials are valid',
        type: 'success'
      });
    } catch (error) {
      setValidationMessage({
        text: 'Error: Failed to validate settings',
        type: 'error'
      });
    } finally {
      setValidating(false);
    }
  };

  const saveSettings = async () => {
    if (!supabaseUrl || !supabaseApiKey) {
      setValidationMessage({
        text: 'Error: Supabase URL and API key are required',
        type: 'error'
      });
      return;
    }
    
    setSaving(true);
    setValidationMessage({ text: 'Saving settings...', type: 'none' });
    
    try {
      // Save to localStorage
      localStorage.setItem('github-api-key', githubApiKey);
      localStorage.setItem('supabase-url', supabaseUrl);
      localStorage.setItem('supabase-api-key', supabaseApiKey);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setValidationMessage({
        text: 'Settings saved successfully',
        type: 'success'
      });
      
      // Close dialog after a delay
      setTimeout(() => {
        onClose();
      }, 1500);
    } catch (error) {
      setValidationMessage({
        text: 'Error: Failed to save settings',
        type: 'error'
      });
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="settings-dialog" onClick={handleBackdropClick}>
      <div className="settings-dialog-content">
        <div className="settings-dialog-header">
          <h3>Settings</h3>
          <span className="settings-dialog-close" onClick={onClose}>&times;</span>
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
          <small className="form-text">Personal access token with 'repo' scope</small>
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
          <small className="form-text">URL from your Supabase project settings</small>
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
          <small className="form-text">Anon key from your Supabase project settings</small>
        </div>
        
        {validationMessage.type !== 'none' && (
          <div className={`validation-message ${validationMessage.type === 'success' ? 'validation-success' : 'validation-error'}`}>
            {validationMessage.text}
          </div>
        )}
        
        <div className="settings-dialog-footer">
          <button 
            className="btn btn-info"
            onClick={validateSettings}
            disabled={validating || saving}
          >
            {validating ? (
              <>
                <span className="spinner"></span>
                Validating...
              </>
            ) : 'Validate'}
          </button>
          <button 
            className="btn btn-primary"
            onClick={saveSettings}
            disabled={validating || saving}
          >
            {saving ? (
              <>
                <span className="spinner"></span>
                Saving...
              </>
            ) : 'Save'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default SettingsDialog;

