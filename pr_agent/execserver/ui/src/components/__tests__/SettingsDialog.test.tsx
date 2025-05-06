import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '../../test/test-utils';
import SettingsDialog from '../SettingsDialog';

describe('SettingsDialog', () => {
  it('does not render when isOpen is false', () => {
    render(<SettingsDialog isOpen={false} onClose={() => {}} />);
    expect(screen.queryByText('Settings')).not.toBeInTheDocument();
  });

  it('renders when isOpen is true', () => {
    render(<SettingsDialog isOpen={true} onClose={() => {}} />);
    expect(screen.getByText('Settings')).toBeInTheDocument();
    expect(screen.getByLabelText('GitHub Token')).toBeInTheDocument();
    expect(screen.getByLabelText('API URL')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Save' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Cancel' })).toBeInTheDocument();
  });

  it('calls onClose when close button is clicked', async () => {
    const onClose = vi.fn();
    const { user } = render(<SettingsDialog isOpen={true} onClose={onClose} />);
    
    await user.click(screen.getByRole('button', { name: 'Close settings' }));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('calls onClose when cancel button is clicked', async () => {
    const onClose = vi.fn();
    const { user } = render(<SettingsDialog isOpen={true} onClose={onClose} />);
    
    await user.click(screen.getByRole('button', { name: 'Cancel' }));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('updates input values when typing', async () => {
    const { user } = render(<SettingsDialog isOpen={true} onClose={() => {}} />);
    
    const tokenInput = screen.getByLabelText('GitHub Token');
    const apiUrlInput = screen.getByLabelText('API URL');
    
    await user.type(tokenInput, 'test-token');
    await user.type(apiUrlInput, 'https://api.example.com');
    
    expect(tokenInput).toHaveValue('test-token');
    expect(apiUrlInput).toHaveValue('https://api.example.com');
  });

  it('disables save button while saving', async () => {
    // Mock timers for the setTimeout in handleSave
    vi.useFakeTimers();
    
    const { user } = render(<SettingsDialog isOpen={true} onClose={() => {}} />);
    
    const saveButton = screen.getByRole('button', { name: 'Save' });
    await user.click(saveButton);
    
    // Button should now be disabled and show "Saving..."
    expect(saveButton).toBeDisabled();
    expect(saveButton).toHaveTextContent('Saving...');
    
    // Fast-forward timers to complete the save operation
    vi.runAllTimers();
    
    // Restore real timers
    vi.useRealTimers();
  });
});

