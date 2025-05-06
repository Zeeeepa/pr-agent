/**
 * PR-Agent Dashboard Main JavaScript
 * 
 * This file contains the core functionality for the PR-Agent dashboard.
 * It handles tab navigation, theme switching, real-time updates, and
 * notification management.
 */

// Dashboard Configuration
const DASHBOARD_CONFIG = {
    refreshInterval: 30000, // 30 seconds
    notificationCheckInterval: 15000, // 15 seconds
    maxEventsToShow: 10,
    autoRefresh: true,
    defaultTheme: 'light'
};

// Initialize the dashboard when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the dashboard components
    initializeDashboard();
    
    // Set up event handlers
    setupEventHandlers();
    
    // Start auto-refresh if enabled
    if (DASHBOARD_CONFIG.autoRefresh) {
        startAutoRefresh();
    }
    
    // Initialize notification system
    initializeNotifications();
});

/**
 * Initialize the dashboard components
 */
function initializeDashboard() {
    // Load user preferences
    loadUserPreferences();
    
    // Initialize tabs
    initializeTabs();
    
    // Apply theme
    applyTheme(getUserThemePreference());
    
    // Fetch initial data
    fetchDashboardData();
    
    // Update last updated timestamp
    updateLastUpdated();
}

/**
 * Set up event handlers for the dashboard
 */
function setupEventHandlers() {
    // Theme toggle button
    const themeToggleBtn = document.getElementById('theme-toggle');
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', toggleTheme);
    }
    
    // Refresh buttons
    const refreshButtons = document.querySelectorAll('.refresh-data-btn');
    refreshButtons.forEach(button => {
        button.addEventListener('click', function() {
            const dataType = this.getAttribute('data-refresh-target');
            refreshData(dataType);
        });
    });
    
    // Tab navigation
    const tabButtons = document.querySelectorAll('[data-bs-toggle="tab"]');
    tabButtons.forEach(button => {
        button.addEventListener('shown.bs.tab', function(event) {
            // Load tab-specific content when tab is shown
            const targetTab = event.target.getAttribute('data-bs-target').replace('#', '');
            loadTabContent(targetTab);
        });
    });
    
    // Notification clear button
    const clearNotificationsBtn = document.getElementById('clear-notifications');
    if (clearNotificationsBtn) {
        clearNotificationsBtn.addEventListener('click', clearAllNotifications);
    }
    
    // Settings button
    const settingsBtn = document.getElementById('settings-btn');
    if (settingsBtn) {
        settingsBtn.addEventListener('click', showSettingsDialog);
    }
}

/**
 * Start auto-refresh for dashboard data
 */
function startAutoRefresh() {
    // Refresh dashboard data at regular intervals
    setInterval(function() {
        if (document.visibilityState === 'visible') {
            // Only refresh if the page is visible
            fetchDashboardData(true); // Silent refresh
        }
    }, DASHBOARD_CONFIG.refreshInterval);
    
    // Check for new notifications at regular intervals
    setInterval(function() {
        if (document.visibilityState === 'visible') {
            checkForNewNotifications();
        }
    }, DASHBOARD_CONFIG.notificationCheckInterval);
}

/**
 * Fetch all dashboard data
 * @param {boolean} silent - Whether to show loading indicators
 */
function fetchDashboardData(silent = false) {
    // Fetch different types of data for the dashboard
    fetchRecentEvents(silent);
    fetchActiveTriggers(silent);
    fetchSystemStatus(silent);
    
    // Update last updated timestamp if not silent
    if (!silent) {
        updateLastUpdated();
    }
}

/**
 * Refresh specific data on the dashboard
 * @param {string} dataType - Type of data to refresh
 */
function refreshData(dataType) {
    switch (dataType) {
        case 'events':
            fetchRecentEvents();
            break;
        case 'triggers':
            fetchActiveTriggers();
            break;
        case 'status':
            fetchSystemStatus();
            break;
        case 'all':
            fetchDashboardData();
            break;
        default:
            console.warn(`Unknown data type: ${dataType}`);
    }
    
    // Update last updated timestamp
    updateLastUpdated();
}

/**
 * Update the last updated timestamp
 */
function updateLastUpdated() {
    const lastUpdatedElement = document.getElementById('last-updated');
    if (lastUpdatedElement) {
        lastUpdatedElement.textContent = new Date().toLocaleString();
    }
}

/**
 * Toggle between light and dark themes
 */
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    // Apply the new theme
    applyTheme(newTheme);
    
    // Save the theme preference
    saveUserThemePreference(newTheme);
}

/**
 * Apply a theme to the dashboard
 * @param {string} theme - Theme to apply ('light' or 'dark')
 */
function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    
    // Update theme toggle button icon
    const themeIcon = document.getElementById('theme-icon');
    if (themeIcon) {
        themeIcon.textContent = theme === 'dark' ? '☀️' : '🌙';
    }
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
    return DASHBOARD_CONFIG.defaultTheme;
}

/**
 * Save user's theme preference
 * @param {string} theme - Theme preference to save
 */
function saveUserThemePreference(theme) {
    localStorage.setItem('pr-agent-theme', theme);
}

/**
 * Load user preferences from localStorage
 */
function loadUserPreferences() {
    // Load theme preference
    const theme = getUserThemePreference();
    applyTheme(theme);
    
    // Load other preferences as needed
    DASHBOARD_CONFIG.autoRefresh = localStorage.getItem('pr-agent-auto-refresh') !== 'false';
}

/**
 * Initialize the notification system
 */
function initializeNotifications() {
    // Check for unread notifications
    updateNotificationCounter();
    
    // Set up notification panel
    setupNotificationPanel();
}

/**
 * Update the notification counter
 */
function updateNotificationCounter() {
    const counter = document.getElementById('notification-counter');
    if (!counter) return;
    
    // Get unread notifications count
    const unreadCount = getUnreadNotificationsCount();
    
    // Update the counter
    if (unreadCount > 0) {
        counter.textContent = unreadCount;
        counter.classList.remove('d-none');
    } else {
        counter.classList.add('d-none');
    }
}

/**
 * Get the count of unread notifications
 * @returns {number} - Count of unread notifications
 */
function getUnreadNotificationsCount() {
    // This would typically fetch from an API
    // For now, we'll use localStorage as a simple store
    const notifications = JSON.parse(localStorage.getItem('pr-agent-notifications') || '[]');
    return notifications.filter(notification => !notification.read).length;
}

/**
 * Check for new notifications
 */
function checkForNewNotifications() {
    // This would typically fetch from an API
    // For demonstration, we'll just update the counter
    updateNotificationCounter();
}

/**
 * Set up the notification panel
 */
function setupNotificationPanel() {
    const notificationPanel = document.getElementById('notification-panel');
    if (!notificationPanel) return;
    
    // Load notifications
    loadNotifications();
    
    // Set up notification panel toggle
    const notificationToggle = document.getElementById('notification-toggle');
    if (notificationToggle) {
        notificationToggle.addEventListener('click', function() {
            toggleNotificationPanel();
        });
    }
}

/**
 * Toggle the notification panel
 */
function toggleNotificationPanel() {
    const panel = document.getElementById('notification-panel');
    if (!panel) return;
    
    // Toggle panel visibility
    panel.classList.toggle('show');
    
    // Mark notifications as read when panel is opened
    if (panel.classList.contains('show')) {
        markAllNotificationsAsRead();
    }
}

/**
 * Load notifications into the notification panel
 */
function loadNotifications() {
    const notificationList = document.getElementById('notification-list');
    if (!notificationList) return;
    
    // Get notifications
    const notifications = JSON.parse(localStorage.getItem('pr-agent-notifications') || '[]');
    
    // Clear the list
    notificationList.innerHTML = '';
    
    // Add notifications to the list
    if (notifications.length > 0) {
        notifications.forEach(notification => {
            const item = document.createElement('div');
            item.className = `notification-item ${notification.read ? 'read' : 'unread'}`;
            item.innerHTML = `
                <div class="notification-title">${notification.title}</div>
                <div class="notification-message">${notification.message}</div>
                <div class="notification-time">${new Date(notification.time).toLocaleString()}</div>
            `;
            notificationList.appendChild(item);
        });
    } else {
        // No notifications
        notificationList.innerHTML = '<div class="no-notifications">No notifications</div>';
    }
}

/**
 * Mark all notifications as read
 */
function markAllNotificationsAsRead() {
    // Get notifications
    const notifications = JSON.parse(localStorage.getItem('pr-agent-notifications') || '[]');
    
    // Mark all as read
    notifications.forEach(notification => {
        notification.read = true;
    });
    
    // Save back to localStorage
    localStorage.setItem('pr-agent-notifications', JSON.stringify(notifications));
    
    // Update the counter
    updateNotificationCounter();
    
    // Update the notification list
    loadNotifications();
}

/**
 * Clear all notifications
 */
function clearAllNotifications() {
    // Clear notifications
    localStorage.setItem('pr-agent-notifications', '[]');
    
    // Update the counter
    updateNotificationCounter();
    
    // Update the notification list
    loadNotifications();
}

// Export functions for use in other scripts
window.toggleTheme = toggleTheme;
window.refreshData = refreshData;
window.clearAllNotifications = clearAllNotifications;

