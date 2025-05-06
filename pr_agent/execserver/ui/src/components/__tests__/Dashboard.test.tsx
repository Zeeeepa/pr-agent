import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '../../test/test-utils';
import Dashboard from '../Dashboard';
import { server } from '../../test/mocks/server';
import { rest } from 'msw';

describe('Dashboard', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    
    // Mock Date.toLocaleString
    const originalToLocaleString = Date.prototype.toLocaleString;
    Date.prototype.toLocaleString = vi.fn(() => '2023-01-01 12:34:56');
    
    return () => {
      Date.prototype.toLocaleString = originalToLocaleString;
    };
  });

  it('renders the dashboard with correct title', () => {
    render(<Dashboard />);
    
    expect(screen.getByText('PR-Agent Dashboard')).toBeInTheDocument();
  });

  it('renders the theme toggle and settings buttons', () => {
    render(<Dashboard />);
    
    expect(screen.getByText('Theme')).toBeInTheDocument();
    expect(screen.getByText('Settings')).toBeInTheDocument();
  });

  it('renders all navigation tabs', () => {
    render(<Dashboard />);
    
    expect(screen.getByRole('tab', { name: /home/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /event triggers/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /github workflows/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /ai assistant/i })).toBeInTheDocument();
  });

  it('shows the home tab by default', () => {
    render(<Dashboard />);
    
    expect(screen.getByRole('tab', { name: /home/i })).toHaveAttribute('aria-selected', 'true');
    expect(screen.getByText('Active Triggers')).toBeInTheDocument();
    expect(screen.getByText('System Status')).toBeInTheDocument();
  });

  it('switches tabs when clicked', async () => {
    const { user } = render(<Dashboard />);
    
    // Click on the triggers tab
    await user.click(screen.getByRole('tab', { name: /event triggers/i }));
    
    // Check that the triggers tab is now active
    expect(screen.getByRole('tab', { name: /event triggers/i })).toHaveAttribute('aria-selected', 'true');
    expect(screen.getByText('Event Triggers')).toBeInTheDocument();
  });

  it('opens settings dialog when settings button is clicked', async () => {
    const { user } = render(<Dashboard />);
    
    // Click on the settings button
    await user.click(screen.getByText('Settings'));
    
    // Check that the settings dialog is open
    expect(screen.getByText('GitHub API Key')).toBeInTheDocument();
  });

  it('fetches and displays system status', async () => {
    render(<Dashboard />);
    
    // Wait for the status to be fetched and displayed
    await waitFor(() => {
      expect(screen.getByText('All systems operational')).toBeInTheDocument();
    });
  });

  it('shows inactive status when database is disconnected', async () => {
    // Override the default handler for database status
    server.use(
      rest.get('/api/v1/database/status', (req, res, ctx) => {
        return res(
          ctx.status(200),
          ctx.json({
            status: 'disconnected',
          })
        );
      })
    );
    
    render(<Dashboard />);
    
    // Wait for the status to be fetched and displayed
    await waitFor(() => {
      expect(screen.getByText('System issues detected')).toBeInTheDocument();
    });
  });

  it('fetches and displays active trigger count', async () => {
    // Override the default handler for triggers
    server.use(
      rest.get('/api/v1/triggers', (req, res, ctx) => {
        return res(
          ctx.status(200),
          ctx.json([
            { id: '1', enabled: true },
            { id: '2', enabled: true },
            { id: '3', enabled: false },
          ])
        );
      })
    );
    
    render(<Dashboard />);
    
    // Wait for the trigger count to be fetched and displayed
    await waitFor(() => {
      expect(screen.getByText('You have 2 active triggers configured.')).toBeInTheDocument();
    });
  });

  it('navigates to triggers tab when manage triggers button is clicked', async () => {
    const { user } = render(<Dashboard />);
    
    // Click on the manage triggers button
    await user.click(screen.getByText('Manage Triggers'));
    
    // Check that the triggers tab is now active
    expect(screen.getByRole('tab', { name: /event triggers/i })).toHaveAttribute('aria-selected', 'true');
  });
});

