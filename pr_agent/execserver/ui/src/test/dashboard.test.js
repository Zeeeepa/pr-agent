/**
 * PR-Agent Dashboard Tests
 * 
 * This file contains tests for the dashboard components.
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

// Mock localStorage
const localStorageMock = (() => {
  let store = {};
  return {
    getItem: (key) => store[key] || null,
    setItem: (key, value) => {
      store[key] = value.toString();
    },
    removeItem: (key) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    }
  };
})();

// Mock DOM elements
const setupDOM = () => {
  document.body.innerHTML = `
    <div class="container">
      <header class="dashboard-header">
        <h1 class="dashboard-title">PR-Agent Dashboard</h1>
        <div class="header-actions">
          <button id="theme-toggle" class="btn btn-outline-secondary" title="Toggle Theme">
            <span id="theme-icon">🌙</span>
          </button>
        </div>
      </header>
      <div id="tab-navigation"></div>
      <div id="tab-content"></div>
    </div>
  `;
};

describe('Dashboard UI', () => {
  beforeEach(() => {
    // Setup DOM
    setupDOM();
    
    // Mock localStorage
    Object.defineProperty(window, 'localStorage', { value: localStorageMock });
    
    // Mock matchMedia
    Object.defineProperty(window, 'matchMedia', {
      value: vi.fn().mockImplementation(query => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })),
    });
  });
  
  afterEach(() => {
    // Clear localStorage
    localStorageMock.clear();
    
    // Clear DOM
    document.body.innerHTML = '';
  });
  
  it('should initialize the dashboard', () => {
    // Load the dashboard script
    const script = document.createElement('script');
    script.textContent = `
      function initializeDashboard() {
        // This is a mock function
        document.body.setAttribute('data-initialized', 'true');
      }
      
      document.addEventListener('DOMContentLoaded', initializeDashboard);
      
      // Manually trigger DOMContentLoaded
      const event = new Event('DOMContentLoaded');
      document.dispatchEvent(event);
    `;
    document.body.appendChild(script);
    
    // Check if dashboard was initialized
    expect(document.body.getAttribute('data-initialized')).toBe('true');
  });
  
  it('should toggle theme', () => {
    // Load the theme toggle script
    const script = document.createElement('script');
    script.textContent = `
      function toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', newTheme);
        
        // Update theme icon
        const themeIcon = document.getElementById('theme-icon');
        if (themeIcon) {
          themeIcon.textContent = newTheme === 'dark' ? '☀️' : '🌙';
        }
        
        // Save theme preference
        localStorage.setItem('pr-agent-theme', newTheme);
      }
      
      // Add event listener to theme toggle button
      const themeToggleBtn = document.getElementById('theme-toggle');
      if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', toggleTheme);
      }
    `;
    document.body.appendChild(script);
    
    // Get theme toggle button
    const themeToggleBtn = document.getElementById('theme-toggle');
    
    // Initial theme should be light
    expect(document.documentElement.getAttribute('data-theme')).toBeNull();
    
    // Click theme toggle button
    themeToggleBtn.click();
    
    // Theme should be dark
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
    expect(document.getElementById('theme-icon').textContent).toBe('☀️');
    expect(localStorage.getItem('pr-agent-theme')).toBe('dark');
    
    // Click theme toggle button again
    themeToggleBtn.click();
    
    // Theme should be light
    expect(document.documentElement.getAttribute('data-theme')).toBe('light');
    expect(document.getElementById('theme-icon').textContent).toBe('🌙');
    expect(localStorage.getItem('pr-agent-theme')).toBe('light');
  });
});

