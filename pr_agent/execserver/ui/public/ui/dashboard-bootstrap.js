/**
 * PR-Agent Dashboard Bootstrap Module
 * 
 * This file handles the initialization of the dashboard's visual components,
 * including theme setup, responsive design, and Bootstrap component initialization.
 */

// Bootstrap Configuration
const BOOTSTRAP_CONFIG = {
    // Theme configuration
    theme: {
        light: {
            primaryColor: '#0d6efd',
            secondaryColor: '#6c757d',
            successColor: '#28a745',
            dangerColor: '#dc3545',
            warningColor: '#ffc107',
            infoColor: '#17a2b8',
            backgroundColor: '#f8f9fa',
            textColor: '#212529'
        },
        dark: {
            primaryColor: '#4f8eff',
            secondaryColor: '#757575',
            successColor: '#4caf50',
            dangerColor: '#f44336',
            warningColor: '#ff9800',
            infoColor: '#03a9f4',
            backgroundColor: '#121212',
            textColor: '#e0e0e0'
        }
    },
    
    // Responsive breakpoints
    breakpoints: {
        xs: 0,
        sm: 576,
        md: 768,
        lg: 992,
        xl: 1200,
        xxl: 1400
    },
    
    // Bootstrap components to initialize
    components: {
        tooltips: true,
        popovers: true,
        toasts: true,
        modals: true,
        dropdowns: true
    }
};

/**
 * Initialize the dashboard theme
 * @param {string} theme - Theme to initialize ('light' or 'dark')
 */
function initializeTheme(theme) {
    console.log(`Initializing ${theme} theme...`);
    
    // Set theme attribute on document element
    document.documentElement.setAttribute('data-theme', theme);
    
    // Update theme toggle button icon
    const themeIcon = document.getElementById('theme-icon');
    if (themeIcon) {
        themeIcon.textContent = theme === 'dark' ? '☀️' : '🌙';
    }
    
    // Apply theme-specific CSS variables
    applyThemeVariables(theme);
    
    // Apply theme-specific class to body
    document.body.classList.remove('light-theme', 'dark-theme');
    document.body.classList.add(`${theme}-theme`);
    
    console.log(`${theme} theme initialized.`);
}

/**
 * Apply theme-specific CSS variables
 * @param {string} theme - Theme to apply ('light' or 'dark')
 */
function applyThemeVariables(theme) {
    // Get theme configuration
    const themeConfig = BOOTSTRAP_CONFIG.theme[theme];
    if (!themeConfig) {
        console.error(`Theme configuration not found for theme: ${theme}`);
        return;
    }
    
    // Apply CSS variables
    const root = document.documentElement;
    
    // Apply color variables
    root.style.setProperty('--primary-color', themeConfig.primaryColor);
    root.style.setProperty('--secondary-color', themeConfig.secondaryColor);
    root.style.setProperty('--success-color', themeConfig.successColor);
    root.style.setProperty('--danger-color', themeConfig.dangerColor);
    root.style.setProperty('--warning-color', themeConfig.warningColor);
    root.style.setProperty('--info-color', themeConfig.infoColor);
    root.style.setProperty('--bg-color', themeConfig.backgroundColor);
    root.style.setProperty('--text-color', themeConfig.textColor);
}

/**
 * Initialize Bootstrap components
 */
function initializeBootstrapComponents() {
    console.log('Initializing Bootstrap components...');
    
    // Initialize tooltips if enabled
    if (BOOTSTRAP_CONFIG.components.tooltips) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Initialize popovers if enabled
    if (BOOTSTRAP_CONFIG.components.popovers) {
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }
    
    // Initialize toasts if enabled
    if (BOOTSTRAP_CONFIG.components.toasts) {
        const toastElList = [].slice.call(document.querySelectorAll('.toast'));
        toastElList.map(function (toastEl) {
            return new bootstrap.Toast(toastEl);
        });
    }
    
    console.log('Bootstrap components initialized.');
}

/**
 * Set up responsive design
 */
function setupResponsiveDesign() {
    console.log('Setting up responsive design...');
    
    // Add viewport meta tag if not present
    if (!document.querySelector('meta[name="viewport"]')) {
        const meta = document.createElement('meta');
        meta.name = 'viewport';
        meta.content = 'width=device-width, initial-scale=1, shrink-to-fit=no';
        document.head.appendChild(meta);
    }
    
    // Add responsive classes to tables
    const tables = document.querySelectorAll('table:not(.table-responsive)');
    tables.forEach(table => {
        // Wrap table in responsive div if not already wrapped
        if (table.parentElement.classList.contains('table-responsive')) {
            return;
        }
        
        const wrapper = document.createElement('div');
        wrapper.className = 'table-responsive';
        table.parentNode.insertBefore(wrapper, table);
        wrapper.appendChild(table);
    });
    
    // Add responsive classes to images
    const images = document.querySelectorAll('img:not(.img-fluid)');
    images.forEach(img => {
        img.classList.add('img-fluid');
    });
    
    // Set up responsive breakpoint detection
    setupBreakpointDetection();
    
    console.log('Responsive design setup complete.');
}

/**
 * Set up breakpoint detection
 */
function setupBreakpointDetection() {
    // Create breakpoint detector element
    const detector = document.createElement('div');
    detector.className = 'd-none';
    detector.id = 'breakpoint-detector';
    document.body.appendChild(detector);
    
    // Add breakpoint classes
    Object.keys(BOOTSTRAP_CONFIG.breakpoints).forEach(breakpoint => {
        detector.classList.add(`d-${breakpoint}-block`);
    });
    
    // Set up resize listener
    window.addEventListener('resize', detectBreakpoint);
    
    // Initial detection
    detectBreakpoint();
}

/**
 * Detect current breakpoint
 */
function detectBreakpoint() {
    const detector = document.getElementById('breakpoint-detector');
    if (!detector) return;
    
    // Get computed style
    const style = window.getComputedStyle(detector);
    
    // Check display property to determine current breakpoint
    const display = style.display;
    
    // Determine current breakpoint
    let currentBreakpoint = 'xs';
    
    if (display === 'block') {
        // Find which breakpoint is active
        Object.keys(BOOTSTRAP_CONFIG.breakpoints).forEach(breakpoint => {
            if (detector.classList.contains(`d-${breakpoint}-block`)) {
                if (window.innerWidth >= BOOTSTRAP_CONFIG.breakpoints[breakpoint]) {
                    currentBreakpoint = breakpoint;
                }
            }
        });
    }
    
    // Dispatch breakpoint change event
    const event = new CustomEvent('breakpoint-change', {
        detail: {
            breakpoint: currentBreakpoint,
            width: window.innerWidth
        }
    });
    
    document.dispatchEvent(event);
    
    return currentBreakpoint;
}

/**
 * Initialize dashboard layout
 */
function initializeDashboardLayout() {
    console.log('Initializing dashboard layout...');
    
    // Set up responsive design
    setupResponsiveDesign();
    
    // Initialize Bootstrap components
    initializeBootstrapComponents();
    
    // Set up layout event listeners
    setupLayoutEventListeners();
    
    console.log('Dashboard layout initialized.');
}

/**
 * Set up layout event listeners
 */
function setupLayoutEventListeners() {
    // Listen for breakpoint changes
    document.addEventListener('breakpoint-change', function(event) {
        const { breakpoint, width } = event.detail;
        console.log(`Breakpoint changed to ${breakpoint} (${width}px)`);
        
        // Adjust layout based on breakpoint
        adjustLayoutForBreakpoint(breakpoint);
    });
    
    // Listen for theme changes
    document.addEventListener('theme-change', function(event) {
        const { theme } = event.detail;
        console.log(`Theme changed to ${theme}`);
        
        // Apply theme
        initializeTheme(theme);
    });
}

/**
 * Adjust layout for current breakpoint
 * @param {string} breakpoint - Current breakpoint
 */
function adjustLayoutForBreakpoint(breakpoint) {
    // Adjust card layouts
    adjustCardLayouts(breakpoint);
    
    // Adjust navigation
    adjustNavigation(breakpoint);
    
    // Adjust tables
    adjustTables(breakpoint);
}

/**
 * Adjust card layouts for current breakpoint
 * @param {string} breakpoint - Current breakpoint
 */
function adjustCardLayouts(breakpoint) {
    // Get all card decks
    const cardDecks = document.querySelectorAll('.card-deck');
    
    // Adjust card deck layout based on breakpoint
    cardDecks.forEach(deck => {
        // Remove existing column classes
        deck.classList.remove('row-cols-1', 'row-cols-sm-2', 'row-cols-md-3', 'row-cols-lg-4');
        
        // Add appropriate column classes based on breakpoint
        switch (breakpoint) {
            case 'xs':
                deck.classList.add('row-cols-1');
                break;
            case 'sm':
                deck.classList.add('row-cols-sm-2');
                break;
            case 'md':
                deck.classList.add('row-cols-md-3');
                break;
            case 'lg':
            case 'xl':
            case 'xxl':
                deck.classList.add('row-cols-lg-4');
                break;
        }
    });
}

/**
 * Adjust navigation for current breakpoint
 * @param {string} breakpoint - Current breakpoint
 */
function adjustNavigation(breakpoint) {
    // Get navigation elements
    const navbar = document.querySelector('.navbar');
    if (!navbar) return;
    
    // Adjust navigation based on breakpoint
    if (breakpoint === 'xs' || breakpoint === 'sm') {
        // Mobile navigation
        navbar.classList.remove('navbar-expand-lg');
        navbar.classList.add('navbar-expand-md');
    } else {
        // Desktop navigation
        navbar.classList.remove('navbar-expand-md');
        navbar.classList.add('navbar-expand-lg');
    }
}

/**
 * Adjust tables for current breakpoint
 * @param {string} breakpoint - Current breakpoint
 */
function adjustTables(breakpoint) {
    // Get all tables
    const tables = document.querySelectorAll('table');
    
    // Adjust table display based on breakpoint
    tables.forEach(table => {
        if (breakpoint === 'xs' || breakpoint === 'sm') {
            // Add responsive wrapper if not already present
            if (!table.parentElement.classList.contains('table-responsive')) {
                const wrapper = document.createElement('div');
                wrapper.className = 'table-responsive';
                table.parentNode.insertBefore(wrapper, table);
                wrapper.appendChild(table);
            }
        }
    });
}

/**
 * Create a toast notification
 * @param {string} title - Toast title
 * @param {string} message - Toast message
 * @param {string} type - Toast type ('success', 'danger', 'warning', 'info')
 * @param {number} duration - Toast duration in milliseconds
 */
function createToast(title, message, type = 'info', duration = 5000) {
    // Create toast container if it doesn't exist
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toastId = `toast-${Date.now()}`;
    const toastHtml = `
        <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header bg-${type} text-white">
                <strong class="me-auto">${title}</strong>
                <small>${new Date().toLocaleTimeString()}</small>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    // Add toast to container
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    // Initialize and show toast
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: duration
    });
    
    toast.show();
    
    // Remove toast from DOM after it's hidden
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
    
    return toast;
}

// Export functions
export {
    BOOTSTRAP_CONFIG,
    initializeTheme,
    initializeBootstrapComponents,
    setupResponsiveDesign,
    initializeDashboardLayout,
    createToast
};

