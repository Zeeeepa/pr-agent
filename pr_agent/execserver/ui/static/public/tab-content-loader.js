/**
 * PR-Agent Dashboard Tab Content Loader
 * 
 * This file handles the dynamic loading of content for each tab in the dashboard.
 * It ensures that tab content is loaded only when needed, improving performance.
 */

// Tab Content Configuration
const TAB_CONTENT_CONFIG = {
    // Default tab to load on page load
    defaultTab: 'home',
    
    // Whether to preload all tabs on page load
    preloadAllTabs: false,
    
    // Whether to cache tab content
    cacheTabContent: true,
    
    // Tab content cache
    contentCache: {},
    
    // Tab loading states
    loadingStates: {},
    
    // API endpoints for each tab
    endpoints: {
        'home': '/api/v1/dashboard/home',
        'triggers': '/api/v1/triggers',
        'workflows': '/api/v1/workflows',
        'chat': '/api/v1/chat/history',
        'settings': '/api/v1/settings'
    }
};

// Initialize the tab content loader
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tabs
    initializeTabs();
    
    // Load default tab content
    loadTabContent(TAB_CONTENT_CONFIG.defaultTab);
    
    // Preload all tabs if configured
    if (TAB_CONTENT_CONFIG.preloadAllTabs) {
        preloadAllTabs();
    }
});

/**
 * Initialize tabs and set up event listeners
 */
function initializeTabs() {
    // Get all tab buttons
    const tabButtons = document.querySelectorAll('[data-bs-toggle="tab"]');
    
    // Add event listeners to tab buttons
    tabButtons.forEach(button => {
        button.addEventListener('shown.bs.tab', function(event) {
            // Get the target tab ID
            const targetTab = event.target.getAttribute('data-bs-target').replace('#', '');
            
            // Load the tab content
            loadTabContent(targetTab);
            
            // Update URL hash for bookmarking
            window.location.hash = targetTab;
        });
    });
    
    // Check if URL has a hash and activate that tab
    if (window.location.hash) {
        const tabId = window.location.hash.substring(1);
        const tabButton = document.querySelector(`[data-bs-target="#${tabId}"]`);
        
        if (tabButton) {
            // Create a new Bootstrap tab instance and show it
            const tab = new bootstrap.Tab(tabButton);
            tab.show();
        }
    }
}

/**
 * Load content for a specific tab
 * @param {string} tabId - ID of the tab to load content for
 */
function loadTabContent(tabId) {
    // Check if tab content is already loaded and cached
    if (TAB_CONTENT_CONFIG.cacheTabContent && TAB_CONTENT_CONFIG.contentCache[tabId]) {
        return;
    }
    
    // Check if tab is already loading
    if (TAB_CONTENT_CONFIG.loadingStates[tabId]) {
        return;
    }
    
    // Set loading state
    TAB_CONTENT_CONFIG.loadingStates[tabId] = true;
    
    // Show loading indicator
    showTabLoading(tabId);
    
    // Get the tab content container
    const tabContent = document.getElementById(tabId);
    if (!tabContent) {
        console.error(`Tab content container not found for tab: ${tabId}`);
        TAB_CONTENT_CONFIG.loadingStates[tabId] = false;
        return;
    }
    
    // Get the API endpoint for this tab
    const endpoint = TAB_CONTENT_CONFIG.endpoints[tabId];
    if (!endpoint) {
        console.warn(`No API endpoint configured for tab: ${tabId}`);
        loadStaticTabContent(tabId);
        return;
    }
    
    // Fetch tab content from API
    fetch(endpoint)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Failed to load tab content: ${response.status} ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            // Process and render the tab content
            renderTabContent(tabId, data);
            
            // Cache the tab content if caching is enabled
            if (TAB_CONTENT_CONFIG.cacheTabContent) {
                TAB_CONTENT_CONFIG.contentCache[tabId] = data;
            }
            
            // Hide loading indicator
            hideTabLoading(tabId);
            
            // Reset loading state
            TAB_CONTENT_CONFIG.loadingStates[tabId] = false;
        })
        .catch(error => {
            console.error(`Error loading tab content for ${tabId}:`, error);
            
            // Show error message in tab
            showTabError(tabId, error.message);
            
            // Hide loading indicator
            hideTabLoading(tabId);
            
            // Reset loading state
            TAB_CONTENT_CONFIG.loadingStates[tabId] = false;
        });
}

/**
 * Show loading indicator for a tab
 * @param {string} tabId - ID of the tab to show loading indicator for
 */
function showTabLoading(tabId) {
    const tabContent = document.getElementById(tabId);
    if (!tabContent) return;
    
    // Create loading indicator if it doesn't exist
    let loadingIndicator = tabContent.querySelector('.tab-loading');
    if (!loadingIndicator) {
        loadingIndicator = document.createElement('div');
        loadingIndicator.className = 'tab-loading';
        loadingIndicator.innerHTML = `
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p>Loading content...</p>
        `;
        tabContent.appendChild(loadingIndicator);
    } else {
        loadingIndicator.style.display = 'flex';
    }
}

/**
 * Hide loading indicator for a tab
 * @param {string} tabId - ID of the tab to hide loading indicator for
 */
function hideTabLoading(tabId) {
    const tabContent = document.getElementById(tabId);
    if (!tabContent) return;
    
    // Hide loading indicator
    const loadingIndicator = tabContent.querySelector('.tab-loading');
    if (loadingIndicator) {
        loadingIndicator.style.display = 'none';
    }
}

/**
 * Show error message in a tab
 * @param {string} tabId - ID of the tab to show error message in
 * @param {string} errorMessage - Error message to show
 */
function showTabError(tabId, errorMessage) {
    const tabContent = document.getElementById(tabId);
    if (!tabContent) return;
    
    // Create error message element
    const errorElement = document.createElement('div');
    errorElement.className = 'alert alert-danger';
    errorElement.innerHTML = `
        <strong>Error loading content:</strong> ${errorMessage}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Add error message to tab content
    tabContent.appendChild(errorElement);
}

/**
 * Render content for a tab
 * @param {string} tabId - ID of the tab to render content for
 * @param {object} data - Data to render in the tab
 */
function renderTabContent(tabId, data) {
    const tabContent = document.getElementById(tabId);
    if (!tabContent) return;
    
    // Clear existing content (except loading indicator)
    const loadingIndicator = tabContent.querySelector('.tab-loading');
    tabContent.innerHTML = '';
    if (loadingIndicator) {
        tabContent.appendChild(loadingIndicator);
    }
    
    // Render content based on tab ID
    switch (tabId) {
        case 'home':
            renderHomeTab(tabContent, data);
            break;
        case 'triggers':
            renderTriggersTab(tabContent, data);
            break;
        case 'workflows':
            renderWorkflowsTab(tabContent, data);
            break;
        case 'chat':
            renderChatTab(tabContent, data);
            break;
        case 'settings':
            renderSettingsTab(tabContent, data);
            break;
        default:
            console.warn(`No render function defined for tab: ${tabId}`);
            tabContent.innerHTML = `<div class="alert alert-warning">No content renderer defined for this tab.</div>`;
    }
}

/**
 * Load static content for a tab
 * @param {string} tabId - ID of the tab to load static content for
 */
function loadStaticTabContent(tabId) {
    const tabContent = document.getElementById(tabId);
    if (!tabContent) return;
    
    // Clear existing content (except loading indicator)
    const loadingIndicator = tabContent.querySelector('.tab-loading');
    tabContent.innerHTML = '';
    if (loadingIndicator) {
        tabContent.appendChild(loadingIndicator);
    }
    
    // Load static content based on tab ID
    switch (tabId) {
        case 'home':
            tabContent.innerHTML = `
                <div class="card">
                    <div class="card-header">Welcome to PR-Agent Dashboard</div>
                    <div class="card-body">
                        <p>This is the PR-Agent dashboard home page. Here you can monitor and manage your PR-Agent instance.</p>
                        <p>Use the tabs above to navigate to different sections of the dashboard.</p>
                    </div>
                </div>
            `;
            break;
        case 'settings':
            tabContent.innerHTML = `
                <div class="card">
                    <div class="card-header">Dashboard Settings</div>
                    <div class="card-body">
                        <form id="settings-form">
                            <div class="mb-3">
                                <label for="auto-refresh" class="form-label">Auto-refresh</label>
                                <div class="form-check form-switch">
                                    <input class="form-check-input" type="checkbox" id="auto-refresh" checked>
                                    <label class="form-check-label" for="auto-refresh">Enable auto-refresh</label>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label for="refresh-interval" class="form-label">Refresh interval (seconds)</label>
                                <input type="number" class="form-control" id="refresh-interval" value="30" min="5" max="300">
                            </div>
                            <button type="submit" class="btn btn-primary">Save Settings</button>
                        </form>
                    </div>
                </div>
            `;
            break;
        default:
            tabContent.innerHTML = `
                <div class="alert alert-info">
                    <p>No static content defined for this tab.</p>
                    <p>This tab requires API data to display content.</p>
                </div>
            `;
    }
    
    // Hide loading indicator
    hideTabLoading(tabId);
    
    // Reset loading state
    TAB_CONTENT_CONFIG.loadingStates[tabId] = false;
}

/**
 * Preload all tabs
 */
function preloadAllTabs() {
    // Get all tab IDs
    const tabIds = Object.keys(TAB_CONTENT_CONFIG.endpoints);
    
    // Load content for each tab
    tabIds.forEach(tabId => {
        setTimeout(() => {
            loadTabContent(tabId);
        }, 100 * tabIds.indexOf(tabId)); // Stagger loading to avoid overwhelming the API
    });
}

/**
 * Render content for the home tab
 * @param {HTMLElement} container - Container element to render content in
 * @param {object} data - Data to render
 */
function renderHomeTab(container, data) {
    // Create recent events card
    const eventsCard = document.createElement('div');
    eventsCard.className = 'card mb-4';
    eventsCard.innerHTML = `
        <div class="card-header d-flex justify-content-between align-items-center">
            Recent Events
            <button class="btn btn-sm btn-outline-secondary refresh-data-btn" data-refresh-target="events">
                <i class="bi bi-arrow-clockwise"></i> Refresh
            </button>
        </div>
        <div class="card-body">
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>Event</th>
                            <th>Source</th>
                            <th>Status</th>
                            <th>Time</th>
                        </tr>
                    </thead>
                    <tbody id="events-table-body">
                        ${renderEventsTableRows(data.events || [])}
                    </tbody>
                </table>
            </div>
        </div>
    `;
    
    // Create system status card
    const statusCard = document.createElement('div');
    statusCard.className = 'card mb-4';
    statusCard.innerHTML = `
        <div class="card-header d-flex justify-content-between align-items-center">
            System Status
            <button class="btn btn-sm btn-outline-secondary refresh-data-btn" data-refresh-target="status">
                <i class="bi bi-arrow-clockwise"></i> Refresh
            </button>
        </div>
        <div class="card-body">
            <div class="row">
                <div class="col-md-6">
                    <div class="card mb-3">
                        <div class="card-body">
                            <h5 class="card-title">API Status</h5>
                            <p class="card-text">
                                <span class="status-indicator status-active"></span>
                                <span class="status-text">Online</span>
                            </p>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card mb-3">
                        <div class="card-body">
                            <h5 class="card-title">Active Triggers</h5>
                            <p class="card-text">${data.activeTriggers || 0} active triggers</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Add cards to container
    container.appendChild(eventsCard);
    container.appendChild(statusCard);
    
    // Set up event handlers for refresh buttons
    const refreshButtons = container.querySelectorAll('.refresh-data-btn');
    refreshButtons.forEach(button => {
        button.addEventListener('click', function() {
            const dataType = this.getAttribute('data-refresh-target');
            refreshData(dataType);
        });
    });
}

/**
 * Render table rows for events
 * @param {Array} events - Array of event objects
 * @returns {string} - HTML string for table rows
 */
function renderEventsTableRows(events) {
    if (!events || events.length === 0) {
        return '<tr><td colspan="4" class="text-center">No events to display</td></tr>';
    }
    
    return events.map(event => `
        <tr>
            <td>${event.type || 'Unknown'}</td>
            <td>${event.source || 'Unknown'}</td>
            <td>
                <span class="status-${event.status === 'success' ? 'active' : event.status === 'pending' ? 'pending' : 'inactive'}">
                    ${event.status || 'Unknown'}
                </span>
            </td>
            <td>${new Date(event.timestamp).toLocaleString()}</td>
        </tr>
    `).join('');
}

// Export functions for use in other scripts
window.loadTabContent = loadTabContent;
window.refreshData = refreshData;

