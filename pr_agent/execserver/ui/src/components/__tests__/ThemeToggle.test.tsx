import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '../../test/test-utils';
import ThemeToggle from '../ThemeToggle';

describe('ThemeToggle', () => {
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

  // Mock matchMedia
  const matchMediaMock = vi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  }));

  // Mock document.documentElement
  const documentElementMock = {
    setAttribute: vi.fn(),
  };

  beforeEach(() => {
    vi.resetAllMocks();
    Object.defineProperty(window, 'localStorage', { value: localStorageMock });
    Object.defineProperty(window, 'matchMedia', { value: matchMediaMock });
    Object.defineProperty(document, 'documentElement', { value: documentElementMock });
  });

  it('renders correctly with default light theme', () => {
    render(<ThemeToggle />);
    
    const button = screen.getByRole('button', { name: /switch to dark theme/i });
    expect(button).toBeInTheDocument();
    expect(screen.getByText('🌙')).toBeInTheDocument();
  });

  it('loads theme from localStorage if available', () => {
    localStorageMock.getItem.mockReturnValueOnce('dark');
    
    render(<ThemeToggle />);
    
    expect(localStorageMock.getItem).toHaveBeenCalledWith('theme');
    expect(documentElementMock.setAttribute).toHaveBeenCalledWith('data-theme', 'dark');
    expect(screen.getByText('☀️')).toBeInTheDocument();
  });

  it('toggles theme when clicked', async () => {
    const { user } = render(<ThemeToggle />);
    
    const button = screen.getByRole('button', { name: /switch to dark theme/i });
    await user.click(button);
    
    expect(localStorageMock.setItem).toHaveBeenCalledWith('theme', 'dark');
    expect(documentElementMock.setAttribute).toHaveBeenCalledWith('data-theme', 'dark');
  });

  it('applies custom className if provided', () => {
    render(<ThemeToggle className="custom-class" />);
    
    const button = screen.getByRole('button');
    expect(button).toHaveClass('custom-class');
  });
});

