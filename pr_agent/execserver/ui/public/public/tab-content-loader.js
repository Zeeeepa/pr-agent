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
            
            // Reset loading state
            TAB_CONTENT_CONFIG.loadingStates[tabId] = false;
        });
}

/**
 * Preload content for all tabs
 */
function preloadAllTabs() {
    // Get all tab IDs
    const tabIds = Object.keys(TAB_CONTENT_CONFIG.endpoints);
    
    // Load content for each tab
    tabIds.forEach(tabId => {
        // Skip the default tab as it's already loaded
        if (tabId !== TAB_CONTENT_CONFIG.defaultTab) {
            setTimeout(() => {
                loadTabContent(tabId);
            }, 1000); // Delay to prevent overwhelming the API
        }
    });
}

/**
 * Render content for a specific tab
 * @param {string} tabId - ID of the tab to render content for
 * @param {Object} data - Data to render in the tab
 */
function renderTabContent(tabId, data) {
    // Get the tab content container
    const tabContent = document.getElementById(tabId);
    if (!tabContent) {
        console.error(`Tab content container not found for tab: ${tabId}`);
        return;
    }
    
    // Render different content based on tab ID
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
 * Load static content for a tab that doesn't have an API endpoint
 * @param {string} tabId - ID of the tab to load static content for
 */
function loadStaticTabContent(tabId) {
    // Get the tab content container
    const tabContent = document.getElementById(tabId);
    if (!tabContent) {
        console.error(`Tab content container not found for tab: ${tabId}`);
        return;
    }
    
    // Hide loading indicator
    hideTabLoading(tabId);
    
    // Reset loading state
    TAB_CONTENT_CONFIG.loadingStates[tabId] = false;
}

/**
 * Show loading indicator for a tab
 * @param {string} tabId - ID of the tab to show loading indicator for
 */
function showTabLoading(tabId) {
    // Get the tab content container
    const tabContent = document.getElementById(tabId);
    if (!tabContent) return;
    
    // Create loading indicator if it doesn't exist
    let loadingIndicator = tabContent.querySelector('.tab-loading-indicator');
    if (!loadingIndicator) {
        loadingIndicator = document.createElement('div');
        loadingIndicator.className = 'tab-loading-indicator text-center py-5';
        loadingIndicator.innerHTML = `
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-3">Loading content...</p>
        `;
        tabContent.appendChild(loadingIndicator);
    } else {
        loadingIndicator.style.display = 'block';
    }
}

/**
 * Hide loading indicator for a tab
 * @param {string} tabId - ID of the tab to hide loading indicator for
 */
function hideTabLoading(tabId) {
    // Get the tab content container
    const tabContent = document.getElementById(tabId);
    if (!tabContent) return;
    
    // Hide loading indicator if it exists
    const loadingIndicator = tabContent.querySelector('.tab-loading-indicator');
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
    // Get the tab content container
    const tabContent = document.getElementById(tabId);
    if (!tabContent) return;
    
    // Hide loading indicator
    hideTabLoading(tabId);
    
    // Create error message element
    const errorElement = document.createElement('div');
    errorElement.className = 'alert alert-danger mt-3';
    errorElement.innerHTML = `
        <strong>Error loading content:</strong> ${errorMessage}
        <button type="button" class="btn btn-sm btn-outline-danger mt-2" onclick="loadTabContent('${tabId}')">
            Try Again
        </button>
    `;
    
    // Add error message to tab content
    tabContent.appendChild(errorElement);
}

/**
 * Render content for the Home tab
 * @param {HTMLElement} container - Container element to render content in
 * @param {Object} data - Data to render
 */
function renderHomeTab(container, data) {
    // Clear existing content
    container.innerHTML = '';
    
    // Create home tab content
    const homeContent = document.createElement('div');
    homeContent.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <span>Active Triggers</span>
                        <button class="btn btn-sm btn-outline-secondary refresh-data-btn" data-refresh-target="triggers">
                            <i class="bi bi-arrow-clockwise"></i> Refresh
                        </button>
                    </div>
                    <div class="card-body">
                        <p class="card-text">You have <strong>${data.activeTriggers || 0}</strong> active triggers configured.</p>
                        <a href="#" class="btn btn-primary" onclick="document.getElementById('triggers-tab').click();">Manage Triggers</a>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <span>System Status</span>
                        <button class="btn btn-sm btn-outline-secondary refresh-data-btn" data-refresh-target="status">
                            <i class="bi bi-arrow-clockwise"></i> Refresh
                        </button>
                    </div>
                    <div class="card-body">
                        <p class="card-text"><span class="status-active">●</span> ${data.systemStatus || 'All systems operational'}</p>
                        <p class="card-text">Last updated: <span id="last-updated">${new Date().toLocaleString()}</span></p>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <span>Recent Events</span>
                        <button class="btn btn-sm btn-outline-secondary refresh-data-btn" data-refresh-target="events">
                            <i class="bi bi-arrow-clockwise"></i> Refresh
                        </button>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>Event Type</th>
                                        <th>Repository</th>
                                        <th>Time</th>
                                        <th>Status</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody id="events-table-body">
                                    ${renderEventsTable(data.recentEvents || [])}
                                </tbody>
                            </table>
                        </div>
                        ${data.recentEvents && data.recentEvents.length > 0 ? 
                            `<button id="load-more-events" class="btn btn-outline-primary">Load More</button>` : 
                            `<p class="text-center text-muted">No recent events</p>`
                        }
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Add content to container
    container.appendChild(homeContent);
    
    // Set up event handlers for the home tab
    setupHomeTabEventHandlers();
}

/**
 * Render events table rows
 * @param {Array} events - Array of event objects
 * @returns {string} - HTML string of table rows
 */
function renderEventsTable(events) {
    if (!events || events.length === 0) {
        return '<tr><td colspan="5" class="text-center">No events found</td></tr>';
    }
    
    return events.map(event => {
        const timestamp = new Date(event.created_at).toLocaleString();
        return `
            <tr>
                <td>${event.event_type || 'Unknown'}</td>
                <td>${event.repository || 'N/A'}</td>
                <td>${timestamp}</td>
                <td><span class="${event.processed ? 'status-active' : 'status-inactive'}">${event.processed ? 'Processed' : 'Pending'}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-info" onclick="viewEventDetails('${event.id}')">View Details</button>
                </td>
            </tr>
        `;
    }).join('');
}

/**
 * Set up event handlers for the Home tab
 */
function setupHomeTabEventHandlers() {
    // Load more events button
    const loadMoreButton = document.getElementById('load-more-events');
    if (loadMoreButton) {
        loadMoreButton.addEventListener('click', loadMoreEvents);
    }
    
    // Refresh buttons
    const refreshButtons = document.querySelectorAll('.refresh-data-btn');
    refreshButtons.forEach(button => {
        button.addEventListener('click', function() {
            const dataType = this.getAttribute('data-refresh-target');
            refreshData(dataType);
        });
    });
}

/**
 * Load more events
 */
function loadMoreEvents() {
    // Get current number of events
    const currentCount = document.querySelectorAll('#events-table-body tr').length;
    
    // Show loading state
    const loadMoreButton = document.getElementById('load-more-events');
    if (loadMoreButton) {
        loadMoreButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';
        loadMoreButton.disabled = true;
    }
    
    // Fetch more events
    fetch(`/api/v1/events?limit=${TAB_CONTENT_CONFIG.maxEventsToShow}&offset=${currentCount}`)
        .then(response => response.json())
        .then(data => {
            // Append events to table
            const eventsTableBody = document.getElementById('events-table-body');
            if (eventsTableBody) {
                // Remove "No events found" row if it exists
                if (eventsTableBody.querySelector('tr td[colspan="5"]')) {
                    eventsTableBody.innerHTML = '';
                }
                
                // Append new events
                const newEventsHtml = renderEventsTable(data);
                eventsTableBody.innerHTML += newEventsHtml;
            }
            
            // Reset load more button
            if (loadMoreButton) {
                loadMoreButton.innerHTML = 'Load More';
                loadMoreButton.disabled = false;
                
                // Hide button if no more events
                if (!data || data.length === 0) {
                    loadMoreButton.style.display = 'none';
                }
            }
        })
        .catch(error => {
            console.error('Error loading more events:', error);
            
            // Reset load more button
            if (loadMoreButton) {
                loadMoreButton.innerHTML = 'Load More';
                loadMoreButton.disabled = false;
            }
            
            // Show error message
            const eventsTableBody = document.getElementById('events-table-body');
            if (eventsTableBody) {
                const lastRow = document.createElement('tr');
                lastRow.innerHTML = `<td colspan="5" class="text-center text-danger">Error loading more events. Please try again.</td>`;
                eventsTableBody.appendChild(lastRow);
            }
        });
}

/**
 * Render content for the Triggers tab
 * @param {HTMLElement} container - Container element to render content in
 * @param {Object} data - Data to render
 */
function renderTriggersTab(container, data) {
    // Implementation for Triggers tab
    // This would be similar to renderHomeTab but with triggers-specific content
}

/**
 * Render content for the Workflows tab
 * @param {HTMLElement} container - Container element to render content in
 * @param {Object} data - Data to render
 */
function renderWorkflowsTab(container, data) {
    // Implementation for Workflows tab
}

/**
 * Render content for the Chat tab
 * @param {HTMLElement} container - Container element to render content in
 * @param {Object} data - Data to render
 */
function renderChatTab(container, data) {
    // Implementation for Chat tab
}

/**
 * Render content for the Settings tab
 * @param {HTMLElement} container - Container element to render content in
 * @param {Object} data - Data to render
 */
function renderSettingsTab(container, data) {
    // Implementation for Settings tab
}

// Export functions for use in other scripts
window.loadTabContent = loadTabContent;
window.refreshData = refreshData;
window.viewEventDetails = function(eventId) {
    // Implementation for viewing event details
    console.log(`Viewing details for event: ${eventId}`);
    // This would typically open a modal with event details
};

