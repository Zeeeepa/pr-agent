import { describe, it, expect } from 'vitest';
import { render, screen } from '../../test/test-utils';
import Dashboard from '../Dashboard';

describe('Dashboard', () => {
  it('renders the dashboard with correct title', () => {
    render(<Dashboard />);
    expect(screen.getByText('PR-Agent Dashboard')).toBeInTheDocument();
  });

  it('renders all navigation tabs', () => {
    render(<Dashboard />);
    expect(screen.getByRole('tab', { name: 'Home' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'Event Triggers' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'GitHub Workflows' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'AI Assistant' })).toBeInTheDocument();
  });

  it('shows home content by default', () => {
    render(<Dashboard />);
    expect(screen.getByText('Active Triggers')).toBeInTheDocument();
    expect(screen.getByText('System Status')).toBeInTheDocument();
    expect(screen.getByText('You have 5 active triggers')).toBeInTheDocument();
    expect(screen.getByText('All systems operational')).toBeInTheDocument();
  });

  it('switches to events tab when clicked', async () => {
    const { user } = render(<Dashboard />);
    
    await user.click(screen.getByRole('tab', { name: 'Event Triggers' }));
    
    expect(screen.getByText('Manage your event triggers here')).toBeInTheDocument();
    expect(screen.queryByText('You have 5 active triggers')).not.toBeInTheDocument();
  });

  it('switches to workflows tab when clicked', async () => {
    const { user } = render(<Dashboard />);
    
    await user.click(screen.getByRole('tab', { name: 'GitHub Workflows' }));
    
    expect(screen.getByText('Manage your GitHub workflows here')).toBeInTheDocument();
    expect(screen.queryByText('You have 5 active triggers')).not.toBeInTheDocument();
  });

  it('switches to assistant tab when clicked', async () => {
    const { user } = render(<Dashboard />);
    
    await user.click(screen.getByRole('tab', { name: 'AI Assistant' }));
    
    expect(screen.getByText('Chat with the AI assistant here')).toBeInTheDocument();
    expect(screen.queryByText('You have 5 active triggers')).not.toBeInTheDocument();
  });

  it('opens settings dialog when settings button is clicked', async () => {
    const { user } = render(<Dashboard />);
    
    await user.click(screen.getByRole('button', { name: 'Settings' }));
    
    expect(screen.getByText('GitHub Token')).toBeInTheDocument();
    expect(screen.getByText('API URL')).toBeInTheDocument();
  });

  it('closes settings dialog when close button is clicked', async () => {
    const { user } = render(<Dashboard />);
    
    // Open settings
    await user.click(screen.getByRole('button', { name: 'Settings' }));
    expect(screen.getByText('GitHub Token')).toBeInTheDocument();
    
    // Close settings
    await user.click(screen.getByRole('button', { name: 'Close settings' }));
    expect(screen.queryByText('GitHub Token')).not.toBeInTheDocument();
  });
});

