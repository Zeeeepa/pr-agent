/**
 * PR-Agent Dashboard Fixed Elements Module
 * 
 * This file handles the fixed elements of the dashboard UI,
 * such as the header, footer, navigation, and notification panel.
 */

// Fixed Elements Configuration
const FIXED_ELEMENTS_CONFIG = {
    // Header configuration
    header: {
        fixed: true,
        height: '60px',
        zIndex: 1030
    },
    
    // Footer configuration
    footer: {
        fixed: true,
        height: '40px',
        zIndex: 1020
    },
    
    // Sidebar configuration
    sidebar: {
        fixed: true,
        width: '250px',
        collapsedWidth: '70px',
        zIndex: 1025,
        breakpoint: 'md' // Breakpoint at which sidebar collapses
    },
    
    // Notification panel configuration
    notificationPanel: {
        fixed: true,
        width: '320px',
        maxHeight: '400px',
        zIndex: 1035
    }
};

/**
 * Set up fixed elements
 */
function setupFixedElements() {
    console.log('Setting up fixed elements...');
    
    // Set up header
    setupHeader();
    
    // Set up footer
    setupFooter();
    
    // Set up sidebar
    setupSidebar();
    
    // Set up notification panel
    setupNotificationPanel();
    
    // Adjust content padding for fixed elements
    adjustContentPadding();
    
    // Set up resize listener
    window.addEventListener('resize', adjustContentPadding);
    
    console.log('Fixed elements setup complete.');
}

/**
 * Set up header
 */
function setupHeader() {
    // Get header element
    const header = document.querySelector('.dashboard-header');
    if (!header) return;
    
    // Apply fixed header styles
    if (FIXED_ELEMENTS_CONFIG.header.fixed) {
        header.style.position = 'fixed';
        header.style.top = '0';
        header.style.left = '0';
        header.style.right = '0';
        header.style.height = FIXED_ELEMENTS_CONFIG.header.height;
        header.style.zIndex = FIXED_ELEMENTS_CONFIG.header.zIndex;
        header.style.backgroundColor = 'var(--bg-color)';
        header.style.borderBottom = '1px solid var(--border-color)';
        header.style.padding = '0 1rem';
        header.style.display = 'flex';
        header.style.alignItems = 'center';
        header.style.justifyContent = 'space-between';
        header.style.transition = 'all 0.3s ease';
    }
}

/**
 * Set up footer
 */
function setupFooter() {
    // Get footer element
    const footer = document.querySelector('.dashboard-footer');
    if (!footer) return;
    
    // Apply fixed footer styles
    if (FIXED_ELEMENTS_CONFIG.footer.fixed) {
        footer.style.position = 'fixed';
        footer.style.bottom = '0';
        footer.style.left = '0';
        footer.style.right = '0';
        footer.style.height = FIXED_ELEMENTS_CONFIG.footer.height;
        footer.style.zIndex = FIXED_ELEMENTS_CONFIG.footer.zIndex;
        footer.style.backgroundColor = 'var(--bg-color)';
        footer.style.borderTop = '1px solid var(--border-color)';
        footer.style.padding = '0 1rem';
        footer.style.display = 'flex';
        footer.style.alignItems = 'center';
        footer.style.justifyContent = 'space-between';
        footer.style.fontSize = '0.875rem';
        footer.style.transition = 'all 0.3s ease';
    }
}

/**
 * Set up sidebar
 */
function setupSidebar() {
    // Get sidebar element
    const sidebar = document.querySelector('.dashboard-sidebar');
    if (!sidebar) return;
    
    // Apply fixed sidebar styles
    if (FIXED_ELEMENTS_CONFIG.sidebar.fixed) {
        sidebar.style.position = 'fixed';
        sidebar.style.top = FIXED_ELEMENTS_CONFIG.header.height;
        sidebar.style.left = '0';
        sidebar.style.bottom = FIXED_ELEMENTS_CONFIG.footer.height;
        sidebar.style.width = FIXED_ELEMENTS_CONFIG.sidebar.width;
        sidebar.style.zIndex = FIXED_ELEMENTS_CONFIG.sidebar.zIndex;
        sidebar.style.backgroundColor = 'var(--card-bg)';
        sidebar.style.borderRight = '1px solid var(--border-color)';
        sidebar.style.overflowY = 'auto';
        sidebar.style.transition = 'all 0.3s ease';
        
        // Add sidebar toggle button
        addSidebarToggle(sidebar);
        
        // Set up sidebar collapse on small screens
        setupSidebarCollapse(sidebar);
    }
}

/**
 * Add sidebar toggle button
 * @param {HTMLElement} sidebar - Sidebar element
 */
function addSidebarToggle(sidebar) {
    // Create toggle button
    const toggleButton = document.createElement('button');
    toggleButton.className = 'sidebar-toggle btn btn-sm btn-outline-secondary';
    toggleButton.innerHTML = '<i class="bi bi-chevron-left"></i>';
    toggleButton.style.position = 'absolute';
    toggleButton.style.top = '1rem';
    toggleButton.style.right = '-15px';
    toggleButton.style.zIndex = FIXED_ELEMENTS_CONFIG.sidebar.zIndex + 1;
    toggleButton.style.borderRadius = '50%';
    toggleButton.style.width = '30px';
    toggleButton.style.height = '30px';
    toggleButton.style.padding = '0';
    toggleButton.style.display = 'flex';
    toggleButton.style.alignItems = 'center';
    toggleButton.style.justifyContent = 'center';
    
    // Add toggle button to sidebar
    sidebar.appendChild(toggleButton);
    
    // Add click event listener
    toggleButton.addEventListener('click', function() {
        toggleSidebar(sidebar, toggleButton);
    });
}

/**
 * Toggle sidebar collapse
 * @param {HTMLElement} sidebar - Sidebar element
 * @param {HTMLElement} toggleButton - Toggle button element
 */
function toggleSidebar(sidebar, toggleButton) {
    // Check if sidebar is collapsed
    const isCollapsed = sidebar.classList.contains('collapsed');
    
    // Toggle collapsed state
    if (isCollapsed) {
        // Expand sidebar
        sidebar.classList.remove('collapsed');
        sidebar.style.width = FIXED_ELEMENTS_CONFIG.sidebar.width;
        toggleButton.innerHTML = '<i class="bi bi-chevron-left"></i>';
        
        // Show sidebar item text
        const sidebarItemTexts = sidebar.querySelectorAll('.sidebar-item-text');
        sidebarItemTexts.forEach(text => {
            text.style.display = 'inline';
        });
    } else {
        // Collapse sidebar
        sidebar.classList.add('collapsed');
        sidebar.style.width = FIXED_ELEMENTS_CONFIG.sidebar.collapsedWidth;
        toggleButton.innerHTML = '<i class="bi bi-chevron-right"></i>';
        
        // Hide sidebar item text
        const sidebarItemTexts = sidebar.querySelectorAll('.sidebar-item-text');
        sidebarItemTexts.forEach(text => {
            text.style.display = 'none';
        });
    }
    
    // Adjust content padding
    adjustContentPadding();
    
    // Save sidebar state
    localStorage.setItem('pr-agent-sidebar-collapsed', isCollapsed ? 'false' : 'true');
}

/**
 * Set up sidebar collapse on small screens
 * @param {HTMLElement} sidebar - Sidebar element
 */
function setupSidebarCollapse(sidebar) {
    // Get breakpoint
    const breakpoint = FIXED_ELEMENTS_CONFIG.sidebar.breakpoint;
    
    // Create media query
    const mediaQuery = window.matchMedia(`(max-width: ${getBreakpointWidth(breakpoint)}px)`);
    
    // Function to handle media query change
    function handleMediaQueryChange(e) {
        if (e.matches) {
            // Small screen - collapse sidebar
            sidebar.classList.add('collapsed');
            sidebar.style.width = FIXED_ELEMENTS_CONFIG.sidebar.collapsedWidth;
            
            // Hide sidebar item text
            const sidebarItemTexts = sidebar.querySelectorAll('.sidebar-item-text');
            sidebarItemTexts.forEach(text => {
                text.style.display = 'none';
            });
            
            // Update toggle button
            const toggleButton = sidebar.querySelector('.sidebar-toggle');
            if (toggleButton) {
                toggleButton.innerHTML = '<i class="bi bi-chevron-right"></i>';
            }
        } else {
            // Large screen - check saved state
            const isCollapsed = localStorage.getItem('pr-agent-sidebar-collapsed') === 'true';
            
            if (!isCollapsed) {
                // Expand sidebar
                sidebar.classList.remove('collapsed');
                sidebar.style.width = FIXED_ELEMENTS_CONFIG.sidebar.width;
                
                // Show sidebar item text
                const sidebarItemTexts = sidebar.querySelectorAll('.sidebar-item-text');
                sidebarItemTexts.forEach(text => {
                    text.style.display = 'inline';
                });
                
                // Update toggle button
                const toggleButton = sidebar.querySelector('.sidebar-toggle');
                if (toggleButton) {
                    toggleButton.innerHTML = '<i class="bi bi-chevron-left"></i>';
                }
            }
        }
        
        // Adjust content padding
        adjustContentPadding();
    }
    
    // Add listener for media query changes
    mediaQuery.addEventListener('change', handleMediaQueryChange);
    
    // Initial check
    handleMediaQueryChange(mediaQuery);
}

/**
 * Get width for a Bootstrap breakpoint
 * @param {string} breakpoint - Bootstrap breakpoint name
 * @returns {number} - Breakpoint width in pixels
 */
function getBreakpointWidth(breakpoint) {
    const breakpoints = {
        xs: 0,
        sm: 576,
        md: 768,
        lg: 992,
        xl: 1200,
        xxl: 1400
    };
    
    return breakpoints[breakpoint] || 768;
}

/**
 * Set up notification panel
 */
function setupNotificationPanel() {
    // Get notification panel element
    const panel = document.querySelector('.notification-panel');
    if (!panel) return;
    
    // Apply fixed notification panel styles
    if (FIXED_ELEMENTS_CONFIG.notificationPanel.fixed) {
        panel.style.position = 'fixed';
        panel.style.top = FIXED_ELEMENTS_CONFIG.header.height;
        panel.style.right = '1rem';
        panel.style.width = FIXED_ELEMENTS_CONFIG.notificationPanel.width;
        panel.style.maxHeight = FIXED_ELEMENTS_CONFIG.notificationPanel.maxHeight;
        panel.style.zIndex = FIXED_ELEMENTS_CONFIG.notificationPanel.zIndex;
        panel.style.backgroundColor = 'var(--card-bg)';
        panel.style.border = '1px solid var(--border-color)';
        panel.style.borderRadius = '0.5rem';
        panel.style.boxShadow = '0 0.5rem 1rem rgba(0, 0, 0, 0.15)';
        panel.style.overflowY = 'auto';
        panel.style.display = 'none';
        panel.style.transition = 'all 0.3s ease';
    }
    
    // Add click outside listener to close panel
    document.addEventListener('click', function(event) {
        // Check if click is outside notification panel and toggle button
        const isClickInsidePanel = panel.contains(event.target);
        const isClickOnToggle = event.target.closest('#notification-toggle');
        
        if (!isClickInsidePanel && !isClickOnToggle && panel.style.display === 'block') {
            panel.style.display = 'none';
        }
    });
    
    // Add notification toggle button click handler
    const toggleButton = document.getElementById('notification-toggle');
    if (toggleButton) {
        toggleButton.addEventListener('click', function(event) {
            event.stopPropagation();
            toggleNotificationPanel(panel);
        });
    }
}

/**
 * Toggle notification panel
 * @param {HTMLElement} panel - Notification panel element
 */
function toggleNotificationPanel(panel) {
    // Toggle panel visibility
    if (panel.style.display === 'none' || panel.style.display === '') {
        panel.style.display = 'block';
        
        // Mark notifications as read
        markNotificationsAsRead();
    } else {
        panel.style.display = 'none';
    }
}

/**
 * Mark notifications as read
 */
function markNotificationsAsRead() {
    // Update notification badge
    const badge = document.getElementById('notification-badge');
    if (badge) {
        badge.style.display = 'none';
    }
    
    // Mark notification items as read
    const unreadItems = document.querySelectorAll('.notification-item.unread');
    unreadItems.forEach(item => {
        item.classList.remove('unread');
    });
    
    // Send request to mark notifications as read
    // This would typically be an API call
    console.log('Marking notifications as read');
}

/**
 * Adjust content padding for fixed elements
 */
function adjustContentPadding() {
    // Get main content element
    const content = document.querySelector('.dashboard-content');
    if (!content) return;
    
    // Get fixed elements
    const header = document.querySelector('.dashboard-header');
    const footer = document.querySelector('.dashboard-footer');
    const sidebar = document.querySelector('.dashboard-sidebar');
    
    // Calculate padding
    let paddingTop = 0;
    let paddingBottom = 0;
    let paddingLeft = 0;
    
    // Add header height to top padding
    if (header && FIXED_ELEMENTS_CONFIG.header.fixed) {
        paddingTop = parseInt(FIXED_ELEMENTS_CONFIG.header.height);
    }
    
    // Add footer height to bottom padding
    if (footer && FIXED_ELEMENTS_CONFIG.footer.fixed) {
        paddingBottom = parseInt(FIXED_ELEMENTS_CONFIG.footer.height);
    }
    
    // Add sidebar width to left padding
    if (sidebar && FIXED_ELEMENTS_CONFIG.sidebar.fixed) {
        // Check if sidebar is collapsed
        const isCollapsed = sidebar.classList.contains('collapsed');
        paddingLeft = isCollapsed ? 
            parseInt(FIXED_ELEMENTS_CONFIG.sidebar.collapsedWidth) : 
            parseInt(FIXED_ELEMENTS_CONFIG.sidebar.width);
    }
    
    // Apply padding
    content.style.paddingTop = `${paddingTop}px`;
    content.style.paddingBottom = `${paddingBottom}px`;
    content.style.paddingLeft = `${paddingLeft}px`;
    content.style.minHeight = `calc(100vh - ${paddingTop + paddingBottom}px)`;
}

// Export functions
export {
    FIXED_ELEMENTS_CONFIG,
    setupFixedElements,
    toggleNotificationPanel,
    markNotificationsAsRead
};

