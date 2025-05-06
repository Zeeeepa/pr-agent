// Main UI module for the dashboard
import { initializeTabs } from './dashboard-bootstrap';
import { setupFixedElements } from './dashboard-fixed';

/**
 * Dashboard UI module
 * Handles the main dashboard functionality and UI interactions
 */
export class DashboardUI {
  constructor() {
    this.tabs = [];
    this.activeTab = null;
    this.notificationCount = 0;
    this.darkMode = false;
  }

  /**
   * Initialize the dashboard UI
   */
  initialize() {
    // Initialize tabs
    initializeTabs();
    
    // Setup fixed UI elements
    setupFixedElements();
    
    // Setup theme
    this.setupTheme();
    
    // Setup event listeners
    this.setupEventListeners();
    
    // Initialize notifications
    this.initializeNotifications();
    
    console.log('Dashboard UI initialized');
  }

  /**
   * Setup theme based on user preference
   */
  setupTheme() {
    // Check for saved theme preference
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
      this.enableDarkMode();
    } else {
      this.disableDarkMode();
    }
  }

  /**
   * Enable dark mode
   */
  enableDarkMode() {
    document.body.classList.add('dark-mode');
    document.getElementById('theme-stylesheet')?.removeAttribute('disabled');
    this.darkMode = true;
    localStorage.setItem('theme', 'dark');
  }

  /**
   * Disable dark mode
   */
  disableDarkMode() {
    document.body.classList.remove('dark-mode');
    document.getElementById('theme-stylesheet')?.setAttribute('disabled', '');
    this.darkMode = false;
    localStorage.setItem('theme', 'light');
  }

  /**
   * Toggle between light and dark mode
   */
  toggleTheme() {
    if (this.darkMode) {
      this.disableDarkMode();
    } else {
      this.enableDarkMode();
    }
  }

  /**
   * Setup event listeners for dashboard interactions
   */
  setupEventListeners() {
    // Theme toggle
    const themeToggle = document.querySelector('.theme-toggle');
    if (themeToggle) {
      themeToggle.addEventListener('click', () => this.toggleTheme());
    }
    
    // Refresh button
    const refreshButton = document.querySelector('.refresh-button');
    if (refreshButton) {
      refreshButton.addEventListener('click', () => this.refreshData());
    }
    
    // Notification badge
    const notificationBadge = document.querySelector('.notification-badge');
    if (notificationBadge) {
      notificationBadge.addEventListener('click', () => this.toggleNotifications());
    }
  }

  /**
   * Initialize notifications
   */
  initializeNotifications() {
    // Get unread notifications count (would typically come from an API)
    this.notificationCount = 3;
    this.updateNotificationBadge();
  }

  /**
   * Update the notification badge with current count
   */
  updateNotificationBadge() {
    const badge = document.querySelector('.notification-badge .badge');
    if (badge) {
      if (this.notificationCount > 0) {
        badge.textContent = this.notificationCount;
        badge.style.display = 'flex';
      } else {
        badge.style.display = 'none';
      }
    }
  }

  /**
   * Toggle notifications panel
   */
  toggleNotifications() {
    const panel = document.querySelector('.notification-panel');
    if (panel) {
      panel.classList.toggle('visible');
    }
  }

  /**
   * Mark all notifications as read
   */
  markAllAsRead() {
    this.notificationCount = 0;
    this.updateNotificationBadge();
  }

  /**
   * Refresh dashboard data
   */
  refreshData() {
    console.log('Refreshing dashboard data...');
    
    // Show loading state
    const refreshButton = document.querySelector('.refresh-button');
    if (refreshButton) {
      refreshButton.disabled = true;
      refreshButton.textContent = 'Refreshing...';
    }
    
    // Simulate API call
    setTimeout(() => {
      // Reset button state
      if (refreshButton) {
        refreshButton.disabled = false;
        refreshButton.textContent = 'Refresh';
      }
      
      console.log('Dashboard data refreshed');
    }, 1000);
  }
}

// Create and export a singleton instance
const dashboardUI = new DashboardUI();
export default dashboardUI;

