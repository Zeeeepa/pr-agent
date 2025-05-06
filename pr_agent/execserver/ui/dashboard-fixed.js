/**
 * PR-Agent Dashboard Fixed UI Elements
 * 
 * This module handles the fixed UI elements for the dashboard.
 * It provides utilities for working with fixed UI elements like headers, footers, and sidebars.
 */

// Fixed UI element handlers
const fixedUIHandlers = {
  /**
   * Initialize the fixed header
   * @param {Object} options - Header options
   */
  initHeader: (options = {}) => {
    // Default options
    const defaultOptions = {
      title: 'PR-Agent Dashboard',
      showThemeToggle: true,
      showNotifications: true,
      showSettings: true
    };
    
    // Merge options
    const headerOptions = { ...defaultOptions, ...options };
    
    // Get header element
    const headerElement = document.querySelector('.dashboard-header');
    if (!headerElement) {
      console.error('Dashboard header element not found');
      return;
    }
    
    // Set header title
    const titleElement = headerElement.querySelector('.dashboard-title');
    if (titleElement) {
      titleElement.textContent = headerOptions.title;
    }
    
    // Toggle theme button visibility
    const themeToggleButton = document.getElementById('theme-toggle');
    if (themeToggleButton) {
      themeToggleButton.style.display = headerOptions.showThemeToggle ? 'block' : 'none';
    }
    
    // Toggle notifications visibility
    const notificationBadge = document.querySelector('.notification-badge');
    if (notificationBadge) {
      notificationBadge.style.display = headerOptions.showNotifications ? 'block' : 'none';
    }
    
    // Toggle settings button visibility
    const settingsButton = document.getElementById('settings-btn');
    if (settingsButton) {
      settingsButton.style.display = headerOptions.showSettings ? 'block' : 'none';
    }
  },
  
  /**
   * Initialize the fixed sidebar
   * @param {Object} options - Sidebar options
   */
  initSidebar: (options = {}) => {
    // Default options
    const defaultOptions = {
      show: false,
      position: 'left', // left, right
      width: '250px',
      items: []
    };
    
    // Merge options
    const sidebarOptions = { ...defaultOptions, ...options };
    
    // If sidebar is not enabled, return
    if (!sidebarOptions.show) {
      return;
    }
    
    // Get or create sidebar element
    let sidebarElement = document.querySelector('.dashboard-sidebar');
    if (!sidebarElement) {
      // Create sidebar container
      const container = document.querySelector('.container');
      if (!container) {
        console.error('Container element not found');
        return;
      }
      
      // Create sidebar wrapper
      const sidebarWrapper = document.createElement('div');
      sidebarWrapper.className = 'dashboard-sidebar-wrapper';
      sidebarWrapper.style.display = 'flex';
      
      // Create sidebar element
      sidebarElement = document.createElement('div');
      sidebarElement.className = `dashboard-sidebar ${sidebarOptions.position}`;
      sidebarElement.style.width = sidebarOptions.width;
      sidebarElement.style.position = 'fixed';
      sidebarElement.style.top = '0';
      sidebarElement.style[sidebarOptions.position] = '0';
      sidebarElement.style.height = '100vh';
      sidebarElement.style.backgroundColor = 'var(--card-bg)';
      sidebarElement.style.borderRight = sidebarOptions.position === 'left' ? '1px solid var(--border-color)' : 'none';
      sidebarElement.style.borderLeft = sidebarOptions.position === 'right' ? '1px solid var(--border-color)' : 'none';
      sidebarElement.style.zIndex = '1030';
      sidebarElement.style.overflowY = 'auto';
      sidebarElement.style.transition = 'transform 0.3s ease';
      
      // Create sidebar content
      sidebarElement.innerHTML = `
        <div class="sidebar-header p-3 border-bottom">
          <h5 class="m-0">${sidebarOptions.title || 'Menu'}</h5>
          <button type="button" class="btn-close sidebar-close" aria-label="Close"></button>
        </div>
        <div class="sidebar-content p-3">
          <ul class="nav flex-column">
            ${sidebarOptions.items.map(item => `
              <li class="nav-item">
                <a class="nav-link ${item.active ? 'active' : ''}" href="${item.href || '#'}">
                  ${item.icon ? `<i class="bi bi-${item.icon} me-2"></i>` : ''}
                  ${item.text}
                </a>
              </li>
            `).join('')}
          </ul>
        </div>
      `;
      
      // Add sidebar to wrapper
      sidebarWrapper.appendChild(sidebarElement);
      
      // Add sidebar toggle button
      const sidebarToggle = document.createElement('button');
      sidebarToggle.className = 'btn btn-sm btn-outline-secondary sidebar-toggle';
      sidebarToggle.innerHTML = `<i class="bi bi-list"></i>`;
      sidebarToggle.style.position = 'fixed';
      sidebarToggle.style.top = '1rem';
      sidebarToggle.style[sidebarOptions.position] = '1rem';
      sidebarToggle.style.zIndex = '1031';
      
      // Add sidebar toggle button to wrapper
      sidebarWrapper.appendChild(sidebarToggle);
      
      // Add wrapper before container
      container.parentNode.insertBefore(sidebarWrapper, container);
      
      // Adjust container margin
      container.style[`margin${sidebarOptions.position.charAt(0).toUpperCase() + sidebarOptions.position.slice(1)}`] = sidebarOptions.width;
      
      // Add event listeners
      const sidebarCloseButton = sidebarElement.querySelector('.sidebar-close');
      if (sidebarCloseButton) {
        sidebarCloseButton.addEventListener('click', () => {
          sidebarElement.style.transform = sidebarOptions.position === 'left' ? 'translateX(-100%)' : 'translateX(100%)';
          sidebarToggle.style.display = 'block';
        });
      }
      
      sidebarToggle.addEventListener('click', () => {
        sidebarElement.style.transform = 'translateX(0)';
        sidebarToggle.style.display = 'none';
      });
    }
  },
  
  /**
   * Initialize the fixed footer
   * @param {Object} options - Footer options
   */
  initFooter: (options = {}) => {
    // Default options
    const defaultOptions = {
      show: false,
      text: '© 2025 PR-Agent',
      links: []
    };
    
    // Merge options
    const footerOptions = { ...defaultOptions, ...options };
    
    // If footer is not enabled, return
    if (!footerOptions.show) {
      return;
    }
    
    // Get or create footer element
    let footerElement = document.querySelector('.dashboard-footer');
    if (!footerElement) {
      // Create footer element
      footerElement = document.createElement('footer');
      footerElement.className = 'dashboard-footer mt-5 py-3 border-top';
      
      // Create footer content
      footerElement.innerHTML = `
        <div class="container">
          <div class="d-flex justify-content-between align-items-center">
            <div class="footer-text">
              ${footerOptions.text}
            </div>
            <div class="footer-links">
              ${footerOptions.links.map(link => `
                <a href="${link.href}" class="text-decoration-none me-3">${link.text}</a>
              `).join('')}
            </div>
          </div>
        </div>
      `;
      
      // Add footer to document
      document.body.appendChild(footerElement);
    }
  }
};

// Export fixed UI handlers
export default fixedUIHandlers;

