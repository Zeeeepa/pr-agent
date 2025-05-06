/**
 * PR-Agent Dashboard Tab Initializer
 * 
 * This file handles the initialization of tabs in the PR-Agent dashboard.
 * It sets up the tab navigation, handles tab switching, and manages tab state.
 */

// Tab Configuration
const TAB_CONFIG = {
    // Default active tab
    defaultTab: 'home',
    
    // Whether to persist active tab in URL hash
    persistTabInHash: true,
    
    // Whether to persist active tab in localStorage
    persistTabInStorage: true,
    
    // localStorage key for active tab
    storageKey: 'pr-agent-active-tab',
    
    // Tab definitions
    tabs: [
        {
            id: 'home',
            label: 'Home',
            icon: 'house',
            badge: false
        },
        {
            id: 'triggers',
            label: 'Event Triggers',
            icon: 'lightning',
            badge: false
        },
        {
            id: 'workflows',
            label: 'GitHub Workflows',
            icon: 'diagram-3',
            badge: false
        },
        {
            id: 'chat',
            label: 'AI Assistant',
            icon: 'chat-dots',
            badge: false
        },
        {
            id: 'settings',
            label: 'Settings',
            icon: 'gear',
            badge: false
        }
    ]
};

// Initialize tabs when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tab navigation
    initializeTabNavigation();
    
    // Set active tab based on URL hash or localStorage
    setInitialActiveTab();
    
    // Set up event listeners for tab switching
    setupTabEventListeners();
});

/**
 * Initialize tab navigation
 */
function initializeTabNavigation() {
    // Get the tab navigation container
    const tabNavContainer = document.getElementById('dashboard-tabs');
    if (!tabNavContainer) {
        console.error('Tab navigation container not found');
        return;
    }
    
    // Create tab navigation HTML
    const tabNavHtml = createTabNavigationHtml();
    
    // Set tab navigation HTML
    tabNavContainer.innerHTML = tabNavHtml;
    
    // Create tab content containers
    createTabContentContainers();
}

/**
 * Create tab navigation HTML
 * @returns {string} - HTML string for tab navigation
 */
function createTabNavigationHtml() {
    // Create tab navigation HTML
    let html = '<ul class="nav nav-tabs" role="tablist">';
    
    // Add tabs
    TAB_CONFIG.tabs.forEach((tab, index) => {
        const isActive = index === 0; // First tab is active by default
        
        html += `
            <li class="nav-item" role="presentation">
                <button class="nav-link ${isActive ? 'active' : ''}" 
                        id="${tab.id}-tab" 
                        data-bs-toggle="tab" 
                        data-bs-target="#${tab.id}" 
                        type="button" 
                        role="tab" 
                        aria-controls="${tab.id}" 
                        aria-selected="${isActive ? 'true' : 'false'}">
                    ${tab.icon ? `<i class="bi bi-${tab.icon} me-1"></i>` : ''}
                    ${tab.label}
                    ${tab.badge ? `<span class="badge bg-danger ms-1" id="${tab.id}-badge">0</span>` : ''}
                </button>
            </li>
        `;
    });
    
    html += '</ul>';
    
    return html;
}

/**
 * Create tab content containers
 */
function createTabContentContainers() {
    // Get the tab content container
    const tabContentContainer = document.getElementById('dashboard-tab-content');
    if (!tabContentContainer) {
        console.error('Tab content container not found');
        return;
    }
    
    // Create tab content HTML
    let html = '<div class="tab-content">';
    
    // Add tab content panes
    TAB_CONFIG.tabs.forEach((tab, index) => {
        const isActive = index === 0; // First tab is active by default
        
        html += `
            <div class="tab-pane fade ${isActive ? 'show active' : ''}" 
                 id="${tab.id}" 
                 role="tabpanel" 
                 aria-labelledby="${tab.id}-tab">
                <div class="tab-loading-indicator text-center py-5">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-3">Loading ${tab.label} content...</p>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    
    // Set tab content HTML
    tabContentContainer.innerHTML = html;
}

/**
 * Set initial active tab based on URL hash or localStorage
 */
function setInitialActiveTab() {
    let activeTabId = TAB_CONFIG.defaultTab;
    
    // Check URL hash
    if (TAB_CONFIG.persistTabInHash && window.location.hash) {
        const hashTabId = window.location.hash.substring(1);
        if (isValidTabId(hashTabId)) {
            activeTabId = hashTabId;
        }
    }
    // Check localStorage
    else if (TAB_CONFIG.persistTabInStorage) {
        const storedTabId = localStorage.getItem(TAB_CONFIG.storageKey);
        if (isValidTabId(storedTabId)) {
            activeTabId = storedTabId;
        }
    }
    
    // Activate the tab
    activateTab(activeTabId);
}

/**
 * Check if a tab ID is valid
 * @param {string} tabId - Tab ID to check
 * @returns {boolean} - Whether the tab ID is valid
 */
function isValidTabId(tabId) {
    return TAB_CONFIG.tabs.some(tab => tab.id === tabId);
}

/**
 * Activate a tab
 * @param {string} tabId - ID of the tab to activate
 */
function activateTab(tabId) {
    // Get the tab button
    const tabButton = document.getElementById(`${tabId}-tab`);
    if (!tabButton) {
        console.error(`Tab button not found for tab: ${tabId}`);
        return;
    }
    
    // Create a new Bootstrap tab instance and show it
    const tab = new bootstrap.Tab(tabButton);
    tab.show();
}

/**
 * Set up event listeners for tab switching
 */
function setupTabEventListeners() {
    // Get all tab buttons
    const tabButtons = document.querySelectorAll('[data-bs-toggle="tab"]');
    
    // Add event listeners to tab buttons
    tabButtons.forEach(button => {
        button.addEventListener('shown.bs.tab', function(event) {
            // Get the target tab ID
            const targetTabId = event.target.getAttribute('data-bs-target').replace('#', '');
            
            // Persist active tab in URL hash
            if (TAB_CONFIG.persistTabInHash) {
                window.location.hash = targetTabId;
            }
            
            // Persist active tab in localStorage
            if (TAB_CONFIG.persistTabInStorage) {
                localStorage.setItem(TAB_CONFIG.storageKey, targetTabId);
            }
            
            // Trigger tab content loading
            if (typeof window.loadTabContent === 'function') {
                window.loadTabContent(targetTabId);
            }
        });
    });
}

/**
 * Update badge count for a tab
 * @param {string} tabId - ID of the tab to update badge for
 * @param {number} count - Badge count
 */
function updateTabBadge(tabId, count) {
    // Get the tab badge
    const tabBadge = document.getElementById(`${tabId}-badge`);
    if (!tabBadge) {
        return;
    }
    
    // Update badge count
    tabBadge.textContent = count;
    
    // Show/hide badge based on count
    if (count > 0) {
        tabBadge.classList.remove('d-none');
    } else {
        tabBadge.classList.add('d-none');
    }
    
    // Update tab configuration
    const tabIndex = TAB_CONFIG.tabs.findIndex(tab => tab.id === tabId);
    if (tabIndex !== -1) {
        TAB_CONFIG.tabs[tabIndex].badge = count > 0;
    }
}

/**
 * Switch to a specific tab
 * @param {string} tabId - ID of the tab to switch to
 */
function switchToTab(tabId) {
    // Check if tab ID is valid
    if (!isValidTabId(tabId)) {
        console.error(`Invalid tab ID: ${tabId}`);
        return;
    }
    
    // Activate the tab
    activateTab(tabId);
}

// Export functions for use in other scripts
window.switchToTab = switchToTab;
window.updateTabBadge = updateTabBadge;

