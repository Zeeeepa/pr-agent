/**
 * Event System Interconnection
 * 
 * This file handles the event system interconnection for the PR-Agent dashboard.
 * It provides functionality for:
 * - Fetching and displaying recent events
 * - Managing event triggers
 * - Visualizing event flow
 * - Connecting triggers to actions
 * - Managing settings
 */

// Event System Configuration
const EVENT_SYSTEM = {
    apiBaseUrl: '/api/v1',
    refreshInterval: 30000, // 30 seconds
    maxEventsToShow: 10,
    autoRefresh: true
};

// Event Types and their display names
export const EVENT_TYPES = {
    'push': 'Push',
    'pull_request': 'Pull Request',
    'pull_request_review': 'PR Review',
    'pull_request_review_comment': 'PR Review Comment',
    'issues': 'Issues',
    'issue_comment': 'Issue Comment',
    'create': 'Create',
    'delete': 'Delete',
    'release': 'Release',
    'workflow_run': 'Workflow Run'
};

// Action Types and their display names
export const ACTION_TYPES = {
    'codefile': 'Execute Code File',
    'github_action': 'GitHub Action',
    'github_workflow': 'GitHub Workflow',
    'pr_comment': 'PR Comment'
};

// Initialize the event system
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're using the React app
    if (document.getElementById('root')) {
        console.log('React app detected, skipping legacy event system initialization');
        return;
    }
    
    // Initialize the legacy dashboard
    initializeLegacyEventSystem();
});

/**
 * Initialize the legacy event system
 */
function initializeLegacyEventSystem() {
    // Fetch initial data
    fetchRecentEvents();
    fetchTriggers();
    updateSystemStatus();
    
    // Update last updated timestamp
    updateLastUpdated();
    
    // Set up event handlers
    setupEventHandlers();
    
    // Start auto-refresh if enabled
    if (EVENT_SYSTEM.autoRefresh) {
        startAutoRefresh();
    }
    
    // Initialize settings
    initializeSettings();
}

/**
 * Set up event handlers for the UI
 */
function setupEventHandlers() {
    // Event refresh button
    const refreshButton = document.getElementById('refresh-events');
    if (refreshButton) {
        refreshButton.addEventListener('click', fetchRecentEvents);
    }
    
    // Load more events button
    const loadMoreButton = document.getElementById('load-more-events');
    if (loadMoreButton) {
        loadMoreButton.addEventListener('click', loadMoreEvents);
    }
    
    // Create trigger button
    const createTriggerButton = document.getElementById('create-trigger-btn');
    if (createTriggerButton) {
        createTriggerButton.addEventListener('click', showCreateTriggerModal);
    }
    
    // View connections button
    const viewConnectionsButton = document.getElementById('view-connections');
    if (viewConnectionsButton) {
        viewConnectionsButton.addEventListener('click', showConnectionsDiagram);
    }
    
    // Filter buttons
    const applyFiltersButton = document.getElementById('apply-filters');
    if (applyFiltersButton) {
        applyFiltersButton.addEventListener('click', applyTriggerFilters);
    }
    
    const resetFiltersButton = document.getElementById('reset-filters');
    if (resetFiltersButton) {
        resetFiltersButton.addEventListener('click', resetTriggerFilters);
    }
    
    // Settings button
    const settingsBtn = document.getElementById('settings-btn');
    if (settingsBtn) {
        settingsBtn.addEventListener('click', showSettingsDialog);
    }
    
    // Settings dialog close button
    const settingsCloseBtn = document.querySelector('.settings-dialog-close');
    if (settingsCloseBtn) {
        settingsCloseBtn.addEventListener('click', hideSettingsDialog);
    }
    
    // Settings dialog background click
    const settingsDialog = document.getElementById('settings-dialog');
    if (settingsDialog) {
        settingsDialog.addEventListener('click', function(e) {
            if (e.target === settingsDialog) {
                hideSettingsDialog();
            }
        });
    }
    
    // Validate settings button
    const validateBtn = document.getElementById('validate-settings');
    if (validateBtn) {
        validateBtn.addEventListener('click', validateSettings);
    }
    
    // Save settings button
    const saveBtn = document.getElementById('save-settings');
    if (saveBtn) {
        saveBtn.addEventListener('click', saveSettings);
    }
}

/**
 * Start auto-refresh for events
 */
function startAutoRefresh() {
    setInterval(function() {
        if (document.visibilityState === 'visible') {
            fetchRecentEvents(true); // Silent refresh (no UI feedback)
            updateSystemStatus();
        }
    }, EVENT_SYSTEM.refreshInterval);
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
 * Fetch recent events from the API
 * @param {boolean} silent - Whether to show UI feedback
 */
function fetchRecentEvents(silent = false) {
    if (!silent) {
        showLoading('events-table-body');
    }
    
    // Fetch events from API
    fetch(`${EVENT_SYSTEM.apiBaseUrl}/events?limit=${EVENT_SYSTEM.maxEventsToShow}`)
        .then(response => response.json())
        .then(data => {
            updateEventsTable(data);
            if (!silent) {
                updateLastUpdated();
            }
        })
        .catch(error => {
            console.error('Error fetching events:', error);
            if (!silent) {
                showError('events-table-body', 'Failed to fetch events');
            }
        });
}

/**
 * Show loading state in an element
 * @param {string} elementId - ID of the element to show loading in
 */
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '<tr><td colspan="5" class="text-center">Loading...</td></tr>';
    }
}

/**
 * Show error message in an element
 * @param {string} elementId - ID of the element to show error in
 * @param {string} message - Error message to display
 */
function showError(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `<tr><td colspan="5" class="text-center text-danger">${message}</td></tr>`;
    }
}

/**
 * Update system status
 */
function updateSystemStatus() {
    fetch(`${EVENT_SYSTEM.apiBaseUrl}/system/status`)
        .then(response => response.json())
        .then(data => {
            const statusElement = document.querySelector('.status-active');
            if (statusElement) {
                if (data.status === 'operational') {
                    statusElement.textContent = '● All systems operational';
                    statusElement.className = 'status-active';
                } else {
                    statusElement.textContent = '● System issues detected';
                    statusElement.className = 'status-inactive';
                }
            }
        })
        .catch(error => {
            console.error('Error updating system status:', error);
        });
}

/**
 * Initialize settings
 */
function initializeSettings() {
    // Load settings from localStorage
    const githubApiKey = localStorage.getItem('github-api-key') || '';
    const supabaseUrl = localStorage.getItem('supabase-url') || '';
    const supabaseApiKey = localStorage.getItem('supabase-api-key') || '';
    
    // Set input values
    const githubApiKeyInput = document.getElementById('github-api-key');
    const supabaseUrlInput = document.getElementById('supabase-url');
    const supabaseApiKeyInput = document.getElementById('supabase-api-key');
    
    if (githubApiKeyInput) githubApiKeyInput.value = githubApiKey;
    if (supabaseUrlInput) supabaseUrlInput.value = supabaseUrl;
    if (supabaseApiKeyInput) supabaseApiKeyInput.value = supabaseApiKey;
}

// Placeholder functions for legacy system
function loadMoreEvents() { console.log('loadMoreEvents not implemented'); }
function fetchTriggers() { console.log('fetchTriggers not implemented'); }
function updateEventsTable() { console.log('updateEventsTable not implemented'); }
function showCreateTriggerModal() { console.log('showCreateTriggerModal not implemented'); }
function showConnectionsDiagram() { console.log('showConnectionsDiagram not implemented'); }
function applyTriggerFilters() { console.log('applyTriggerFilters not implemented'); }
function resetTriggerFilters() { console.log('resetTriggerFilters not implemented'); }
function showSettingsDialog() { console.log('showSettingsDialog not implemented'); }
function hideSettingsDialog() { console.log('hideSettingsDialog not implemented'); }
function validateSettings() { console.log('validateSettings not implemented'); }
function saveSettings() { console.log('saveSettings not implemented'); }
function viewEventDetails() { console.log('viewEventDetails not implemented'); }
function editTrigger() { console.log('editTrigger not implemented'); }
function toggleTrigger() { console.log('toggleTrigger not implemented'); }

// Export functions for use in React components
export {
    EVENT_SYSTEM,
    fetchRecentEvents,
    updateSystemStatus,
    initializeSettings
};

// Export functions for legacy system
window.viewEventDetails = viewEventDetails;
window.editTrigger = editTrigger;
window.toggleTrigger = toggleTrigger;
window.showCreateTriggerModal = showCreateTriggerModal;
window.showConnectionsDiagram = showConnectionsDiagram;
window.showSettingsDialog = showSettingsDialog;
window.hideSettingsDialog = hideSettingsDialog;
window.validateSettings = validateSettings;
window.saveSettings = saveSettings;
