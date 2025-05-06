import React, { useState } from 'react';
import { useSettings } from '../contexts/SettingsContext';

interface SettingsDialogProps {
  onClose: () => void;
}

const SettingsDialog: React.FC<SettingsDialogProps> = ({ onClose }) => {
  const { settings, saveSettings, validateSettings } = useSettings();
  
  const [githubToken, setGithubToken] = useState(settings.GITHUB_TOKEN || '');
  const [supabaseUrl, setSupabaseUrl] = useState(settings.SUPABASE_URL || '');
  const [supabaseKey, setSupabaseKey] = useState(settings.SUPABASE_ANON_KEY || '');
  
  const [validationMessage, setValidationMessage] = useState('');
  const [validationStatus, setValidationStatus] = useState<'success' | 'error' | ''>('');
  const [isValidating, setIsValidating] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const handleValidate = async () => {
    if (!supabaseUrl || !supabaseKey) {
      setValidationMessage('Error: Supabase URL and API key are required');
      setValidationStatus('error');
      return;
    }
    
    setIsValidating(true);
    setValidationMessage('Validating settings...');
    setValidationStatus('');
    
    try {
      const result = await validateSettings({
        GITHUB_TOKEN: githubToken,
        SUPABASE_URL: supabaseUrl,
        SUPABASE_ANON_KEY: supabaseKey
      });
      
      if (result.valid) {
        setValidationMessage('Verified! All credentials are valid');
        setValidationStatus('success');
      } else {
        setValidationMessage(`Error: ${result.message || 'Invalid credentials'}`);
        setValidationStatus('error');
      }
    } catch (err) {
      console.error('Error validating settings:', err);
      setValidationMessage('Error: An unexpected error occurred');
      setValidationStatus('error');
    } finally {
      setIsValidating(false);
    }
  };

  const handleSave = async () => {
    if (!supabaseUrl || !supabaseKey) {
      setValidationMessage('Error: Supabase URL and API key are required');
      setValidationStatus('error');
      return;
    }
    
    setIsSaving(true);
    setValidationMessage('Saving settings...');
    setValidationStatus('');
    
    try {
      const success = await saveSettings({
        GITHUB_TOKEN: githubToken,
        SUPABASE_URL: supabaseUrl,
        SUPABASE_ANON_KEY: supabaseKey
      });
      
      if (success) {
        setValidationMessage('Settings saved successfully');
        setValidationStatus('success');
        
        // Close dialog after a short delay
        setTimeout(() => {
          onClose();
        }, 1500);
      } else {
        setValidationMessage('Error: Failed to save settings');
        setValidationStatus('error');
      }
    } catch (err) {
      console.error('Error saving settings:', err);
      setValidationMessage('Error: An unexpected error occurred');
      setValidationStatus('error');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div 
      className="settings-dialog" 
      style={{ 
        display: 'flex',
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        zIndex: 2000,
        justifyContent: 'center',
        alignItems: 'center'
      }}
      onClick={onClose}
    >
      <div 
        className="settings-dialog-content"
        style={{
          backgroundColor: 'var(--card-bg)',
          color: 'var(--text-color)',
          borderRadius: '10px',
          padding: '20px',
          width: '90%',
          maxWidth: '500px',
          boxShadow: '0 4px 8px rgba(0, 0, 0, 0.2)'
        }}
        onClick={e => e.stopPropagation()}
      >
        <div className="settings-dialog-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h4 style={{ margin: 0 }}>Settings</h4>
          <span 
            className="settings-dialog-close" 
            style={{ cursor: 'pointer', fontSize: '1.5rem' }}
            onClick={onClose}
          >
            &times;
          </span>
        </div>
        
        <div className="settings-form-group" style={{ marginBottom: '15px' }}>
          <label htmlFor="github-api-key" style={{ display: 'block', marginBottom: '5px', fontWeight: 500 }}>
            GitHub API Key
          </label>
          <input 
            type="password" 
            id="github-api-key" 
            className="form-control" 
            placeholder="Enter GitHub token (starts with ghp_ or github_pat_)"
            value={githubToken}
            onChange={e => setGithubToken(e.target.value)}
          />
          <small style={{ color: 'var(--secondary-color)' }}>
            Personal access token with 'repo' scope
          </small>
        </div>
        
        <div className="settings-form-group" style={{ marginBottom: '15px' }}>
          <label htmlFor="supabase-url" style={{ display: 'block', marginBottom: '5px', fontWeight: 500 }}>
            Supabase URL
          </label>
          <input 
            type="text" 
            id="supabase-url" 
            className="form-control" 
            placeholder="Enter Supabase URL (https://...)"
            value={supabaseUrl}
            onChange={e => setSupabaseUrl(e.target.value)}
          />
          <small style={{ color: 'var(--secondary-color)' }}>
            URL from your Supabase project settings
          </small>
        </div>
        
        <div className="settings-form-group" style={{ marginBottom: '15px' }}>
          <label htmlFor="supabase-api-key" style={{ display: 'block', marginBottom: '5px', fontWeight: 500 }}>
            Supabase API Key
          </label>
          <input 
            type="password" 
            id="supabase-api-key" 
            className="form-control" 
            placeholder="Enter Supabase anon key (starts with ey...)"
            value={supabaseKey}
            onChange={e => setSupabaseKey(e.target.value)}
          />
          <small style={{ color: 'var(--secondary-color)' }}>
            Anon key from your Supabase project settings
          </small>
        </div>
        
        {validationMessage && (
          <div 
            className={`validation-message ${validationStatus ? `validation-${validationStatus}` : ''}`}
            style={{
              marginTop: '10px',
              padding: '8px',
              borderRadius: '4px',
              display: 'block',
              backgroundColor: validationStatus === 'success' 
                ? 'rgba(40, 167, 69, 0.2)' 
                : validationStatus === 'error'
                  ? 'rgba(220, 53, 69, 0.2)'
                  : 'transparent',
              color: validationStatus === 'success'
                ? 'var(--success-color)'
                : validationStatus === 'error'
                  ? 'var(--danger-color)'
                  : 'var(--text-color)',
              border: validationStatus 
                ? `1px solid var(--${validationStatus === 'success' ? 'success' : 'danger'}-color)` 
                : 'none'
            }}
          >
            {validationMessage}
          </div>
        )}
        
        <div className="settings-dialog-footer" style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '20px' }}>
          <button 
            className="btn btn-info"
            onClick={handleValidate}
            disabled={isValidating || isSaving}
          >
            {isValidating ? (
              <>
                <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                Validating...
              </>
            ) : 'Validate'}
          </button>
          <button 
            className="btn btn-primary"
            onClick={handleSave}
            disabled={isValidating || isSaving}
          >
            {isSaving ? (
              <>
                <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
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

