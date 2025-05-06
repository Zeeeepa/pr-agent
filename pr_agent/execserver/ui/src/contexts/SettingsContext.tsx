import React, { createContext, useContext, useState, useEffect } from 'react';
import { useApi } from './ApiContext';

interface Settings {
  githubToken: string;
  apiEndpoint: string;
  notificationsEnabled: boolean;
  refreshInterval: number;
  theme: 'light' | 'dark' | 'system';
}

interface SettingsContextType {
  settings: Settings;
  updateSettings: (newSettings: Partial<Settings>) => void;
  saveSettings: () => Promise<void>;
  resetSettings: () => void;
  isLoading: boolean;
  error: string | null;
}

const defaultSettings: Settings = {
  githubToken: '',
  apiEndpoint: '/api/v1',
  notificationsEnabled: true,
  refreshInterval: 30,
  theme: 'system',
};

const SettingsContext = createContext<SettingsContextType | undefined>(undefined);

export const SettingsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [settings, setSettings] = useState<Settings>(() => {
    // Load settings from localStorage if available
    const savedSettings = localStorage.getItem('pr-agent-settings');
    return savedSettings ? { ...defaultSettings, ...JSON.parse(savedSettings) } : defaultSettings;
  });
  
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { api } = useApi();

  // Save settings to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('pr-agent-settings', JSON.stringify(settings));
  }, [settings]);

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
      // Save settings to server (if needed)
      await api.post('/api/v1/settings', settings);
      setIsLoading(false);
      return Promise.resolve();
    } catch (err) {
      setIsLoading(false);
      setError('Failed to save settings to server');
      return Promise.reject(err);
    }
  };

  const resetSettings = () => {
    setSettings(defaultSettings);
  };

  return (
    <SettingsContext.Provider value={{ 
      settings, 
      updateSettings, 
      saveSettings, 
      resetSettings,
      isLoading,
      error
    }}>
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

