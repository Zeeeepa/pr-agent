import React, { createContext, useContext, useState, useEffect } from 'react';
import { useApi } from './ApiContext';

interface Settings {
  githubToken: string;
  supabaseUrl: string;
  supabaseApiKey: string;
  refreshInterval: number;
  autoRefresh: boolean;
  theme: 'light' | 'dark';
}

interface SettingsContextType {
  settings: Settings;
  updateSettings: (newSettings: Partial<Settings>) => void;
  saveSettings: () => Promise<void>;
  validateSettings: () => Promise<{ valid: boolean; message?: string }>;
  isLoading: boolean;
  error: string | null;
}

const defaultSettings: Settings = {
  githubToken: '',
  supabaseUrl: '',
  supabaseApiKey: '',
  refreshInterval: 30000,
  autoRefresh: true,
  theme: 'light',
};

const SettingsContext = createContext<SettingsContextType | undefined>(undefined);

export const SettingsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [settings, setSettings] = useState<Settings>(defaultSettings);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { api } = useApi();

  // Load settings from localStorage on mount
  useEffect(() => {
    const loadSettings = () => {
      try {
        const savedSettings = localStorage.getItem('pr-agent-settings');
        if (savedSettings) {
          const parsedSettings = JSON.parse(savedSettings);
          setSettings(prevSettings => ({
            ...prevSettings,
            ...parsedSettings,
          }));
        }
      } catch (err) {
        console.error('Error loading settings:', err);
        setError('Failed to load settings from local storage');
      }
    };

    loadSettings();
  }, []);

  const updateSettings = (newSettings: Partial<Settings>) => {
    setSettings(prevSettings => ({
      ...prevSettings,
      ...newSettings,
    }));
  };

  const saveSettings = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Save to localStorage
      localStorage.setItem('pr-agent-settings', JSON.stringify(settings));

      // Save to server
      await api.post('/api/v1/settings', {
        GITHUB_TOKEN: settings.githubToken,
        SUPABASE_URL: settings.supabaseUrl,
        SUPABASE_ANON_KEY: settings.supabaseApiKey,
        REFRESH_INTERVAL: settings.refreshInterval,
        AUTO_REFRESH: settings.autoRefresh,
      });

      return Promise.resolve();
    } catch (err) {
      console.error('Error saving settings:', err);
      setError('Failed to save settings');
      return Promise.reject(err);
    } finally {
      setIsLoading(false);
    }
  };

  const validateSettings = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await api.post('/api/v1/settings/validate', {
        GITHUB_TOKEN: settings.githubToken,
        SUPABASE_URL: settings.supabaseUrl,
        SUPABASE_ANON_KEY: settings.supabaseApiKey,
      });

      return response.data;
    } catch (err) {
      console.error('Error validating settings:', err);
      setError('Failed to validate settings');
      return { valid: false, message: 'Failed to validate settings' };
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <SettingsContext.Provider
      value={{
        settings,
        updateSettings,
        saveSettings,
        validateSettings,
        isLoading,
        error,
      }}
    >
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

