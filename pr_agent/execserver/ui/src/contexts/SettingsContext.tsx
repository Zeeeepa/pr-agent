import React, { createContext, useState, useEffect, useContext } from 'react';
import { useApi } from './ApiContext';

interface Settings {
  GITHUB_TOKEN?: string;
  SUPABASE_URL?: string;
  SUPABASE_ANON_KEY?: string;
  [key: string]: string | undefined;
}

interface SettingsContextType {
  settings: Settings;
  saveSettings: (newSettings: Settings) => Promise<boolean>;
  validateSettings: (settingsToValidate: Settings) => Promise<{ valid: boolean; message?: string }>;
  loading: boolean;
  error: string | null;
}

const SettingsContext = createContext<SettingsContextType | undefined>(undefined);

export const SettingsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [settings, setSettings] = useState<Settings>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { api } = useApi();

  // Load settings from localStorage on initial render
  useEffect(() => {
    const loadLocalSettings = () => {
      const githubApiKey = localStorage.getItem('github-api-key') || '';
      const supabaseUrl = localStorage.getItem('supabase-url') || '';
      const supabaseApiKey = localStorage.getItem('supabase-api-key') || '';
      
      setSettings({
        GITHUB_TOKEN: githubApiKey,
        SUPABASE_URL: supabaseUrl,
        SUPABASE_ANON_KEY: supabaseApiKey
      });
    };

    loadLocalSettings();
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.get('/api/v1/settings');
      setSettings(response.data);
    } catch (err) {
      console.error('Error fetching settings:', err);
      setError('Failed to fetch settings');
    } finally {
      setLoading(false);
    }
  };

  const saveSettings = async (newSettings: Settings): Promise<boolean> => {
    setLoading(true);
    setError(null);
    
    try {
      // Save to localStorage
      if (newSettings.GITHUB_TOKEN) {
        localStorage.setItem('github-api-key', newSettings.GITHUB_TOKEN);
      }
      if (newSettings.SUPABASE_URL) {
        localStorage.setItem('supabase-url', newSettings.SUPABASE_URL);
      }
      if (newSettings.SUPABASE_ANON_KEY) {
        localStorage.setItem('supabase-api-key', newSettings.SUPABASE_ANON_KEY);
      }
      
      // Save to server
      await api.post('/api/v1/settings', newSettings);
      
      // Update state
      setSettings(prev => ({ ...prev, ...newSettings }));
      
      return true;
    } catch (err: any) {
      console.error('Error saving settings:', err);
      setError(err.response?.data?.message || 'Failed to save settings');
      return false;
    } finally {
      setLoading(false);
    }
  };

  const validateSettings = async (settingsToValidate: Settings): Promise<{ valid: boolean; message?: string }> => {
    try {
      const response = await api.post('/api/v1/settings/validate', settingsToValidate);
      return response.data;
    } catch (err: any) {
      console.error('Error validating settings:', err);
      return { 
        valid: false, 
        message: err.response?.data?.message || 'Failed to validate settings' 
      };
    }
  };

  return (
    <SettingsContext.Provider value={{ settings, saveSettings, validateSettings, loading, error }}>
      {children}
    </SettingsContext.Provider>
  );
};

export const useSettings = (): SettingsContextType => {
  const context = useContext(SettingsContext);
  if (context === undefined) {
    throw new Error('useSettings must be used within a SettingsProvider');
  }
  return context;
};

