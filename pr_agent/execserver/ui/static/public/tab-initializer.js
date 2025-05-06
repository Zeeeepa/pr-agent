/**
 * PR-Agent Dashboard Tab Initializer
 * 
 * This file handles the initialization of tabs in the dashboard.
 * It sets up tab navigation and ensures proper tab state persistence.
 */

// Tab Configuration
const TAB_CONFIG = {
    // Default tab to show on page load if no hash is present
    defaultTab: 'home',
    
    // Whether to persist tab state in localStorage
    persistTabState: true,
    
    // localStorage key for tab state
    tabStateKey: 'pr-agent-active-tab',
    
    // Tab definitions
    tabs: [
        {
            id: 'home',
            title: 'Dashboard',
            icon: 'house'
        },
        {
            id: 'triggers',
            title: 'Triggers',
            icon: 'lightning'
        },
        {
            id: 'workflows',
            title: 'Workflows',
            icon: 'diagram-3'
        },
        {
            id: 'chat',
            title: 'Chat History',
            icon: 'chat-dots'
        },
        {
            id: 'settings',
            title: 'Settings',
            icon: 'gear'
        }
    ]
};

// Initialize tabs when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tab navigation
    initializeTabs();
    
    // Set up event listeners for tab navigation
    setupTabEventListeners();
});

/**
 * Initialize tab navigation
 */
function initializeTabs() {
    // Get the tab container
    const tabContainer = document.getElementById('tab-navigation');
    if (!tabContainer) {
        console.error('Tab navigation container not found');
        return;
    }
    
    // Get the tab content container
    const tabContentContainer = document.getElementById('tab-content');
    if (!tabContentContainer) {
        console.error('Tab content container not found');
        return;
    }
    
    // Create tab navigation
    const tabNav = document.createElement('ul');
    tabNav.className = 'nav nav-tabs';
    tabNav.id = 'dashboard-tabs';
    tabNav.setAttribute('role', 'tablist');
    
    // Create tab content
    const tabContent = document.createElement('div');
    tabContent.className = 'tab-content';
    tabContent.id = 'dashboard-tab-content';
    
    // Create tabs
    TAB_CONFIG.tabs.forEach((tab, index) => {
        // Create tab button
        const tabButton = document.createElement('li');
        tabButton.className = 'nav-item';
        tabButton.setAttribute('role', 'presentation');
        
        const tabLink = document.createElement('button');
        tabLink.className = `nav-link ${index === 0 ? 'active' : ''}`;
        tabLink.id = `${tab.id}-tab`;
        tabLink.setAttribute('data-bs-toggle', 'tab');
        tabLink.setAttribute('data-bs-target', `#${tab.id}`);
        tabLink.setAttribute('type', 'button');
        tabLink.setAttribute('role', 'tab');
        tabLink.setAttribute('aria-controls', tab.id);
        tabLink.setAttribute('aria-selected', index === 0 ? 'true' : 'false');
        
        // Add icon if specified
        if (tab.icon) {
            tabLink.innerHTML = `<i class="bi bi-${tab.icon} me-1"></i> ${tab.title}`;
        } else {
            tabLink.textContent = tab.title;
        }
        
        tabButton.appendChild(tabLink);
        tabNav.appendChild(tabButton);
        
        // Create tab content pane
        const tabPane = document.createElement('div');
        tabPane.className = `tab-pane fade ${index === 0 ? 'show active' : ''}`;
        tabPane.id = tab.id;
        tabPane.setAttribute('role', 'tabpanel');
        tabPane.setAttribute('aria-labelledby', `${tab.id}-tab`);
        
        tabContent.appendChild(tabPane);
    });
    
    // Add tab navigation and content to containers
    tabContainer.appendChild(tabNav);
    tabContentContainer.appendChild(tabContent);
    
    // Restore active tab from localStorage or URL hash
    restoreActiveTab();
}

/**
 * Set up event listeners for tab navigation
 */
function setupTabEventListeners() {
    // Get all tab buttons
    const tabButtons = document.querySelectorAll('[data-bs-toggle="tab"]');
    
    // Add event listeners to tab buttons
    tabButtons.forEach(button => {
        button.addEventListener('shown.bs.tab', function(event) {
            // Get the target tab ID
            const targetTab = event.target.getAttribute('data-bs-target').replace('#', '');
            
            // Save active tab to localStorage if persistence is enabled
            if (TAB_CONFIG.persistTabState) {
                localStorage.setItem(TAB_CONFIG.tabStateKey, targetTab);
            }
            
            // Update URL hash for bookmarking
            window.location.hash = targetTab;
        });
    });
}

/**
 * Restore active tab from localStorage or URL hash
 */
function restoreActiveTab() {
    // Check URL hash first
    let activeTab = window.location.hash ? window.location.hash.substring(1) : null;
    
    // If no hash, check localStorage
    if (!activeTab && TAB_CONFIG.persistTabState) {
        activeTab = localStorage.getItem(TAB_CONFIG.tabStateKey);
    }
    
    // If no active tab found, use default
    if (!activeTab) {
        activeTab = TAB_CONFIG.defaultTab;
    }
    
    // Activate the tab
    const tabButton = document.querySelector(`[data-bs-target="#${activeTab}"]`);
    if (tabButton) {
        // Create a new Bootstrap tab instance and show it
        const tab = new bootstrap.Tab(tabButton);
        tab.show();
    }
}

/**
 * Switch to a specific tab programmatically
 * @param {string} tabId - ID of the tab to switch to
 */
function switchToTab(tabId) {
    const tabButton = document.querySelector(`[data-bs-target="#${tabId}"]`);
    if (tabButton) {
        // Create a new Bootstrap tab instance and show it
        const tab = new bootstrap.Tab(tabButton);
        tab.show();
    } else {
        console.warn(`Tab with ID "${tabId}" not found`);
    }
}

// Export functions for use in other scripts
window.switchToTab = switchToTab;

