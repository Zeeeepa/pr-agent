import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '../../test/test-utils';
import SettingsDialog from '../SettingsDialog';
import { server } from '../../test/mocks/server';
import { rest } from 'msw';

describe('SettingsDialog', () => {
  // Mock localStorage
  const localStorageMock = (() => {
    let store: Record<string, string> = {};
    return {
      getItem: vi.fn((key: string) => store[key] || null),
      setItem: vi.fn((key: string, value: string) => {
        store[key] = value.toString();
      }),
      clear: vi.fn(() => {
        store = {};
      }),
    };
  })();

  beforeEach(() => {
    vi.resetAllMocks();
    Object.defineProperty(window, 'localStorage', { value: localStorageMock });
  });

  it('should not render when isOpen is false', () => {
    render(<SettingsDialog isOpen={false} onClose={() => {}} />);
    
    expect(screen.queryByText('Settings')).not.toBeInTheDocument();
  });

  it('should render when isOpen is true', () => {
    render(<SettingsDialog isOpen={true} onClose={() => {}} />);
    
    expect(screen.getByText('Settings')).toBeInTheDocument();
    expect(screen.getByLabelText('GitHub API Key')).toBeInTheDocument();
    expect(screen.getByLabelText('Supabase URL')).toBeInTheDocument();
    expect(screen.getByLabelText('Supabase API Key')).toBeInTheDocument();
  });

  it('should load settings from localStorage', () => {
    localStorageMock.getItem.mockImplementation((key) => {
      if (key === 'github-api-key') return 'github-token';
      if (key === 'supabase-url') return 'https://example.supabase.co';
      if (key === 'supabase-api-key') return 'supabase-key';
      return null;
    });

    render(<SettingsDialog isOpen={true} onClose={() => {}} />);
    
    expect(localStorageMock.getItem).toHaveBeenCalledWith('github-api-key');
    expect(localStorageMock.getItem).toHaveBeenCalledWith('supabase-url');
    expect(localStorageMock.getItem).toHaveBeenCalledWith('supabase-api-key');
    
    expect(screen.getByLabelText('GitHub API Key')).toHaveValue('github-token');
    expect(screen.getByLabelText('Supabase URL')).toHaveValue('https://example.supabase.co');
    expect(screen.getByLabelText('Supabase API Key')).toHaveValue('supabase-key');
  });

  it('should close when clicking the close button', async () => {
    const onCloseMock = vi.fn();
    const { user } = render(<SettingsDialog isOpen={true} onClose={onCloseMock} />);
    
    await user.click(screen.getByLabelText('Close settings'));
    
    expect(onCloseMock).toHaveBeenCalledTimes(1);
  });

  it('should close when clicking outside the dialog', async () => {
    const onCloseMock = vi.fn();
    const { user } = render(<SettingsDialog isOpen={true} onClose={onCloseMock} />);
    
    await user.click(screen.getByTestId('settings-dialog'));
    
    expect(onCloseMock).toHaveBeenCalledTimes(1);
  });

  it('should validate settings successfully', async () => {
    const { user } = render(<SettingsDialog isOpen={true} onClose={() => {}} />);
    
    // Fill in the form
    await user.type(screen.getByLabelText('GitHub API Key'), 'github-token');
    await user.type(screen.getByLabelText('Supabase URL'), 'https://example.supabase.co');
    await user.type(screen.getByLabelText('Supabase API Key'), 'supabase-key');
    
    // Click validate button
    await user.click(screen.getByText('Validate'));
    
    // Wait for validation to complete
    await waitFor(() => {
      expect(screen.getByTestId('validation-message')).toHaveTextContent('Verified! All credentials are valid');
    });
  });

  it('should show error when validation fails', async () => {
    // Override the default handler for validation
    server.use(
      rest.post('/api/v1/settings/validate', (req, res, ctx) => {
        return res(
          ctx.status(200),
          ctx.json({
            valid: false,
            message: 'Invalid GitHub token',
          })
        );
      })
    );
    
    const { user } = render(<SettingsDialog isOpen={true} onClose={() => {}} />);
    
    // Fill in the form
    await user.type(screen.getByLabelText('GitHub API Key'), 'invalid-token');
    await user.type(screen.getByLabelText('Supabase URL'), 'https://example.supabase.co');
    await user.type(screen.getByLabelText('Supabase API Key'), 'supabase-key');
    
    // Click validate button
    await user.click(screen.getByText('Validate'));
    
    // Wait for validation to complete
    await waitFor(() => {
      expect(screen.getByTestId('validation-message')).toHaveTextContent('Invalid GitHub token');
    });
  });

  it('should save settings successfully', async () => {
    const { user } = render(<SettingsDialog isOpen={true} onClose={() => {}} />);
    
    // Fill in the form
    await user.type(screen.getByLabelText('GitHub API Key'), 'github-token');
    await user.type(screen.getByLabelText('Supabase URL'), 'https://example.supabase.co');
    await user.type(screen.getByLabelText('Supabase API Key'), 'supabase-key');
    
    // Click save button
    await user.click(screen.getByText('Save'));
    
    // Wait for save to complete
    await waitFor(() => {
      expect(screen.getByTestId('validation-message')).toHaveTextContent('Settings saved successfully');
    });
    
    // Check localStorage was updated
    expect(localStorageMock.setItem).toHaveBeenCalledWith('github-api-key', 'github-token');
    expect(localStorageMock.setItem).toHaveBeenCalledWith('supabase-url', 'https://example.supabase.co');
    expect(localStorageMock.setItem).toHaveBeenCalledWith('supabase-api-key', 'supabase-key');
  });

  it('should show error when required fields are missing', async () => {
    const { user } = render(<SettingsDialog isOpen={true} onClose={() => {}} />);
    
    // Only fill GitHub token, leave Supabase fields empty
    await user.type(screen.getByLabelText('GitHub API Key'), 'github-token');
    
    // Click save button
    await user.click(screen.getByText('Save'));
    
    // Check error message
    expect(screen.getByTestId('validation-message')).toHaveTextContent('Error: Supabase URL and API key are required');
  });
});

