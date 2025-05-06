/**
 * PR-Agent Dashboard Main UI Module
 * 
 * This file serves as the main entry point for the dashboard UI.
 * It initializes all dashboard components and coordinates their interactions.
 */

// Import dependencies
import { initializeTheme } from './dashboard-bootstrap.js';
import { setupFixedElements } from './dashboard-fixed.js';

// Dashboard Configuration
const DASHBOARD_CONFIG = {
    // API base URL
    apiBaseUrl: '/api/v1',
    
    // Refresh intervals (in milliseconds)
    refreshIntervals: {
        dashboard: 30000,      // 30 seconds
        notifications: 15000,  // 15 seconds
        systemStatus: 60000    // 1 minute
    },
    
    // Feature flags
    features: {
        darkMode: true,
        notifications: true,
        realTimeUpdates: true,
        responsiveDesign: true,
        tabNavigation: true
    },
    
    // Default settings
    defaults: {
        theme: 'light',
        activeTab: 'home',
        pageSize: 10
    }
};

// Initialize the dashboard when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the dashboard
    initializeDashboard();
});

/**
 * Initialize the dashboard
 */
function initializeDashboard() {
    console.log('Initializing PR-Agent Dashboard...');
    
    try {
        // Load user preferences
        loadUserPreferences();
        
        // Initialize theme
        initializeTheme(getUserThemePreference());
        
        // Set up fixed elements (header, footer, etc.)
        setupFixedElements();
        
        // Initialize tab navigation
        if (DASHBOARD_CONFIG.features.tabNavigation) {
            initializeTabNavigation();
        }
        
        // Initialize notifications
        if (DASHBOARD_CONFIG.features.notifications) {
            initializeNotifications();
        }
        
        // Set up real-time updates
        if (DASHBOARD_CONFIG.features.realTimeUpdates) {
            setupRealTimeUpdates();
        }
        
        // Load initial data
        loadInitialData();
        
        // Set up event handlers
        setupEventHandlers();
        
        console.log('Dashboard initialization complete.');
    } catch (error) {
        console.error('Error initializing dashboard:', error);
        showInitializationError(error);
    }
}

/**
 * Load user preferences from localStorage
 */
function loadUserPreferences() {
    console.log('Loading user preferences...');
    
    // Load theme preference
    const theme = localStorage.getItem('pr-agent-theme') || DASHBOARD_CONFIG.defaults.theme;
    DASHBOARD_CONFIG.defaults.theme = theme;
    
    // Load active tab preference
    const activeTab = localStorage.getItem('pr-agent-active-tab') || DASHBOARD_CONFIG.defaults.activeTab;
    DASHBOARD_CONFIG.defaults.activeTab = activeTab;
    
    // Load page size preference
    const pageSize = parseInt(localStorage.getItem('pr-agent-page-size')) || DASHBOARD_CONFIG.defaults.pageSize;
    DASHBOARD_CONFIG.defaults.pageSize = pageSize;
    
    console.log('User preferences loaded:', {
        theme,
        activeTab,
        pageSize
    });
}

/**
 * Get user's theme preference
 * @returns {string} - User's theme preference ('light' or 'dark')
 */
function getUserThemePreference() {
    // Check localStorage first
    const savedTheme = localStorage.getItem('pr-agent-theme');
    if (savedTheme) {
        return savedTheme;
    }
    
    // Check system preference
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        return 'dark';
    }
    
    // Default to light theme
    return DASHBOARD_CONFIG.defaults.theme;
}

/**
 * Initialize tab navigation
 */
function initializeTabNavigation() {
    console.log('Initializing tab navigation...');
    
    // This function would typically call functions from tab-initializer.js
    // For this implementation, we'll assume those functions are available globally
    
    // Initialize tabs
    if (typeof window.initializeTabs === 'function') {
        window.initializeTabs();
    } else {
        console.warn('Tab initialization function not found.');
    }
    
    // Set active tab
    const activeTab = DASHBOARD_CONFIG.defaults.activeTab;
    if (typeof window.switchToTab === 'function') {
        window.switchToTab(activeTab);
    } else {
        console.warn('Tab switching function not found.');
        
        // Fallback: manually activate the tab
        const tabButton = document.querySelector(`[data-bs-target="#${activeTab}"]`);
        if (tabButton) {
            tabButton.click();
        }
    }
}

/**
 * Initialize notifications
 */
function initializeNotifications() {
    console.log('Initializing notifications...');
    
    // Check for unread notifications
    checkForUnreadNotifications();
    
    // Set up notification refresh interval
    setInterval(function() {
        if (document.visibilityState === 'visible') {
            checkForUnreadNotifications();
        }
    }, DASHBOARD_CONFIG.refreshIntervals.notifications);
}

/**
 * Check for unread notifications
 */
function checkForUnreadNotifications() {
    // Fetch unread notifications count from API
    fetch(`${DASHBOARD_CONFIG.apiBaseUrl}/notifications/unread`)
        .then(response => response.json())
        .then(data => {
            // Update notification badge
            updateNotificationBadge(data.count || 0);
        })
        .catch(error => {
            console.error('Error checking for unread notifications:', error);
        });
}

/**
 * Update notification badge
 * @param {number} count - Number of unread notifications
 */
function updateNotificationBadge(count) {
    // Get notification badge element
    const badge = document.getElementById('notification-badge');
    if (!badge) return;
    
    // Update badge count
    badge.textContent = count;
    
    // Show/hide badge based on count
    if (count > 0) {
        badge.classList.remove('d-none');
    } else {
        badge.classList.add('d-none');
    }
}

/**
 * Set up real-time updates
 */
function setupRealTimeUpdates() {
    console.log('Setting up real-time updates...');
    
    // Set up dashboard refresh interval
    setInterval(function() {
        if (document.visibilityState === 'visible') {
            refreshDashboardData();
        }
    }, DASHBOARD_CONFIG.refreshIntervals.dashboard);
    
    // Set up system status refresh interval
    setInterval(function() {
        if (document.visibilityState === 'visible') {
            checkSystemStatus();
        }
    }, DASHBOARD_CONFIG.refreshIntervals.systemStatus);
}

/**
 * Refresh dashboard data
 */
function refreshDashboardData() {
    // Get active tab
    const activeTab = document.querySelector('.tab-pane.active');
    if (!activeTab) return;
    
    const tabId = activeTab.id;
    
    // Refresh data for active tab
    if (typeof window.refreshData === 'function') {
        window.refreshData(tabId);
    }
}

/**
 * Check system status
 */
function checkSystemStatus() {
    // Fetch system status from API
    fetch(`${DASHBOARD_CONFIG.apiBaseUrl}/system/status`)
        .then(response => response.json())
        .then(data => {
            // Update system status indicator
            updateSystemStatusIndicator(data.status || 'unknown');
        })
        .catch(error => {
            console.error('Error checking system status:', error);
            // Show system as offline if there's an error
            updateSystemStatusIndicator('offline');
        });
}

/**
 * Update system status indicator
 * @param {string} status - System status ('online', 'offline', 'degraded', 'maintenance', 'unknown')
 */
function updateSystemStatusIndicator(status) {
    // Get status indicator element
    const indicator = document.querySelector('.system-status-indicator');
    if (!indicator) return;
    
    // Update indicator based on status
    indicator.className = 'system-status-indicator';
    
    switch (status) {
        case 'online':
            indicator.classList.add('status-active');
            indicator.textContent = '● All systems operational';
            break;
        case 'offline':
            indicator.classList.add('status-inactive');
            indicator.textContent = '● System offline';
            break;
        case 'degraded':
            indicator.classList.add('status-warning');
            indicator.textContent = '● Degraded performance';
            break;
        case 'maintenance':
            indicator.classList.add('status-info');
            indicator.textContent = '● Maintenance in progress';
            break;
        default:
            indicator.classList.add('status-unknown');
            indicator.textContent = '● System status unknown';
    }
    
    // Update last updated timestamp
    const lastUpdated = document.getElementById('last-updated');
    if (lastUpdated) {
        lastUpdated.textContent = new Date().toLocaleString();
    }
}

/**
 * Load initial data for the dashboard
 */
function loadInitialData() {
    console.log('Loading initial dashboard data...');
    
    // Load data for active tab
    const activeTab = DASHBOARD_CONFIG.defaults.activeTab;
    if (typeof window.loadTabContent === 'function') {
        window.loadTabContent(activeTab);
    }
    
    // Check system status
    checkSystemStatus();
}

/**
 * Set up event handlers
 */
function setupEventHandlers() {
    console.log('Setting up event handlers...');
    
    // Theme toggle button
    const themeToggleBtn = document.getElementById('theme-toggle');
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', toggleTheme);
    }
    
    // Notification button
    const notificationBtn = document.getElementById('notification-toggle');
    if (notificationBtn) {
        notificationBtn.addEventListener('click', toggleNotificationPanel);
    }
    
    // Settings button
    const settingsBtn = document.getElementById('settings-btn');
    if (settingsBtn) {
        settingsBtn.addEventListener('click', openSettingsModal);
    }
    
    // Refresh buttons
    const refreshButtons = document.querySelectorAll('.refresh-data-btn');
    refreshButtons.forEach(button => {
        button.addEventListener('click', function() {
            const dataType = this.getAttribute('data-refresh-target');
            if (typeof window.refreshData === 'function') {
                window.refreshData(dataType);
            }
        });
    });
}

/**
 * Toggle between light and dark themes
 */
function toggleTheme() {
    // Get current theme
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
    
    // Toggle theme
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    // Apply new theme
    document.documentElement.setAttribute('data-theme', newTheme);
    
    // Update theme icon
    const themeIcon = document.getElementById('theme-icon');
    if (themeIcon) {
        themeIcon.textContent = newTheme === 'dark' ? '☀️' : '🌙';
    }
    
    // Save theme preference
    localStorage.setItem('pr-agent-theme', newTheme);
    
    console.log(`Theme switched to ${newTheme} mode.`);
}

/**
 * Toggle notification panel
 */
function toggleNotificationPanel() {
    // Get notification panel
    const panel = document.getElementById('notification-panel');
    if (!panel) return;
    
    // Toggle panel visibility
    panel.classList.toggle('show');
    
    // If panel is now visible, mark notifications as read
    if (panel.classList.contains('show')) {
        markNotificationsAsRead();
    }
}

/**
 * Mark notifications as read
 */
function markNotificationsAsRead() {
    // Send request to mark notifications as read
    fetch(`${DASHBOARD_CONFIG.apiBaseUrl}/notifications/mark-read`, {
        method: 'POST'
    })
        .then(response => response.json())
        .then(data => {
            // Update notification badge
            updateNotificationBadge(0);
        })
        .catch(error => {
            console.error('Error marking notifications as read:', error);
        });
}

/**
 * Open settings modal
 */
function openSettingsModal() {
    // Get settings modal
    const modal = document.getElementById('settings-modal');
    if (!modal) return;
    
    // Show modal
    const modalInstance = new bootstrap.Modal(modal);
    modalInstance.show();
}

/**
 * Show initialization error
 * @param {Error} error - Error object
 */
function showInitializationError(error) {
    // Create error alert
    const errorAlert = document.createElement('div');
    errorAlert.className = 'alert alert-danger';
    errorAlert.innerHTML = `
        <strong>Dashboard Initialization Error</strong>
        <p>${error.message}</p>
        <button class="btn btn-danger mt-2" onclick="location.reload()">Reload Dashboard</button>
    `;
    
    // Add error alert to page
    const container = document.querySelector('.container');
    if (container) {
        container.prepend(errorAlert);
    } else {
        document.body.prepend(errorAlert);
    }
}

// Export dashboard functions
export {
    DASHBOARD_CONFIG,
    toggleTheme,
    refreshDashboardData,
    checkSystemStatus,
    updateNotificationBadge,
    toggleNotificationPanel,
    markNotificationsAsRead,
    openSettingsModal
};

