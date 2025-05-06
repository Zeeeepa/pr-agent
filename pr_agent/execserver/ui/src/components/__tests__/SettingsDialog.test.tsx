import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent } from '../../test/test-utils';
import SettingsDialog from '../SettingsDialog';
import { act } from 'react-dom/test-utils';

describe('SettingsDialog', () => {
  beforeEach(() => {
    // Mock setTimeout
    vi.useFakeTimers();
  });

  afterEach(() => {
    // Restore timers
    vi.restoreAllMocks();
    vi.useRealTimers();
  });

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

  it('calls onClose when close button is clicked', () => {
    const onClose = vi.fn();
    render(<SettingsDialog isOpen={true} onClose={onClose} />);
    
    fireEvent.click(screen.getByRole('button', { name: 'Close settings' }));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('calls onClose when cancel button is clicked', () => {
    const onClose = vi.fn();
    render(<SettingsDialog isOpen={true} onClose={onClose} />);
    
    fireEvent.click(screen.getByRole('button', { name: 'Cancel' }));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('updates input values when typing', () => {
    render(<SettingsDialog isOpen={true} onClose={() => {}} />);
    
    const tokenInput = screen.getByLabelText('GitHub Token');
    const apiUrlInput = screen.getByLabelText('API URL');
    
    fireEvent.change(tokenInput, { target: { value: 'test-token' } });
    fireEvent.change(apiUrlInput, { target: { value: 'https://api.example.com' } });
    
    expect(tokenInput).toHaveValue('test-token');
    expect(apiUrlInput).toHaveValue('https://api.example.com');
  });

  it('shows saving state and calls onClose after save completes', () => {
    // Create a mock for the onClose function
    const onClose = vi.fn();
    
    // Render the component
    render(<SettingsDialog isOpen={true} onClose={onClose} />);
    
    // Get the save button
    const saveButton = screen.getByRole('button', { name: 'Save' });
    
    // Click the save button using act to handle state updates
    act(() => {
      fireEvent.click(saveButton);
    });
    
    // Verify button is disabled and shows "Saving..."
    expect(saveButton).toBeDisabled();
    expect(saveButton).toHaveTextContent('Saving...');
    
    // Advance timers by 600ms (more than the 500ms setTimeout in the component)
    act(() => {
      vi.advanceTimersByTime(600);
    });
    
    // Verify onClose was called after the timeout
    expect(onClose).toHaveBeenCalledTimes(1);
  });
});
