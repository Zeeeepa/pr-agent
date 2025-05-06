/**
 * PR-Agent Dashboard Bootstrap Integration
 * 
 * This module handles the integration with Bootstrap for the dashboard UI.
 * It provides utilities for working with Bootstrap components programmatically.
 */

// Bootstrap component handlers
const bootstrapHandlers = {
  /**
   * Create and show a Bootstrap modal
   * @param {string} title - Modal title
   * @param {string} body - Modal body content (can be HTML)
   * @param {Object} options - Modal options
   * @returns {Object} - Modal instance and element
   */
  createModal: (title, body, options = {}) => {
    // Default options
    const defaultOptions = {
      size: 'medium', // small, medium, large
      backdrop: true,
      keyboard: true,
      focus: true,
      buttons: [
        {
          text: 'Close',
          type: 'secondary',
          dismiss: true
        }
      ]
    };
    
    // Merge options
    const modalOptions = { ...defaultOptions, ...options };
    
    // Create modal element
    const modalElement = document.createElement('div');
    modalElement.className = 'modal fade';
    modalElement.id = `modal-${Date.now()}`;
    modalElement.setAttribute('tabindex', '-1');
    modalElement.setAttribute('aria-hidden', 'true');
    
    // Set modal size
    let dialogClass = 'modal-dialog';
    if (modalOptions.size === 'small') {
      dialogClass += ' modal-sm';
    } else if (modalOptions.size === 'large') {
      dialogClass += ' modal-lg';
    } else if (modalOptions.size === 'extra-large') {
      dialogClass += ' modal-xl';
    }
    
    // Create modal content
    modalElement.innerHTML = `
      <div class="${dialogClass}">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">${title}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            ${body}
          </div>
          <div class="modal-footer">
            ${modalOptions.buttons.map(button => `
              <button type="button" class="btn btn-${button.type}" ${button.dismiss ? 'data-bs-dismiss="modal"' : ''}>
                ${button.text}
              </button>
            `).join('')}
          </div>
        </div>
      </div>
    `;
    
    // Add modal to document
    document.body.appendChild(modalElement);
    
    // Create Bootstrap modal instance
    const modalInstance = new bootstrap.Modal(modalElement, {
      backdrop: modalOptions.backdrop,
      keyboard: modalOptions.keyboard,
      focus: modalOptions.focus
    });
    
    // Add event listeners to buttons
    const buttonElements = modalElement.querySelectorAll('.modal-footer .btn');
    modalOptions.buttons.forEach((button, index) => {
      if (button.onClick && typeof button.onClick === 'function') {
        buttonElements[index].addEventListener('click', (event) => {
          button.onClick(event, modalInstance);
        });
      }
    });
    
    // Show modal
    modalInstance.show();
    
    // Return modal instance and element
    return {
      instance: modalInstance,
      element: modalElement
    };
  },
  
  /**
   * Create and show a Bootstrap toast notification
   * @param {string} title - Toast title
   * @param {string} message - Toast message
   * @param {Object} options - Toast options
   * @returns {Object} - Toast instance and element
   */
  createToast: (title, message, options = {}) => {
    // Default options
    const defaultOptions = {
      type: 'info', // info, success, warning, danger
      autohide: true,
      delay: 5000,
      position: 'top-right' // top-right, top-left, bottom-right, bottom-left
    };
    
    // Merge options
    const toastOptions = { ...defaultOptions, ...options };
    
    // Get or create toast container
    let toastContainer = document.querySelector(`.toast-container.${toastOptions.position}`);
    if (!toastContainer) {
      toastContainer = document.createElement('div');
      toastContainer.className = `toast-container ${toastOptions.position}`;
      
      // Set position styles
      if (toastOptions.position.includes('top')) {
        toastContainer.style.top = '1rem';
      } else {
        toastContainer.style.bottom = '1rem';
      }
      
      if (toastOptions.position.includes('right')) {
        toastContainer.style.right = '1rem';
      } else {
        toastContainer.style.left = '1rem';
      }
      
      toastContainer.style.position = 'fixed';
      toastContainer.style.zIndex = '1050';
      
      document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toastElement = document.createElement('div');
    toastElement.className = `toast bg-${toastOptions.type === 'info' ? 'light' : toastOptions.type}`;
    toastElement.setAttribute('role', 'alert');
    toastElement.setAttribute('aria-live', 'assertive');
    toastElement.setAttribute('aria-atomic', 'true');
    
    // Create toast content
    toastElement.innerHTML = `
      <div class="toast-header">
        <strong class="me-auto">${title}</strong>
        <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
      <div class="toast-body">
        ${message}
      </div>
    `;
    
    // Add toast to container
    toastContainer.appendChild(toastElement);
    
    // Create Bootstrap toast instance
    const toastInstance = new bootstrap.Toast(toastElement, {
      autohide: toastOptions.autohide,
      delay: toastOptions.delay
    });
    
    // Show toast
    toastInstance.show();
    
    // Return toast instance and element
    return {
      instance: toastInstance,
      element: toastElement
    };
  },
  
  /**
   * Create and show a Bootstrap alert
   * @param {string} message - Alert message
   * @param {string} type - Alert type (success, danger, warning, info)
   * @param {string} containerId - ID of the container element
   * @param {boolean} dismissible - Whether the alert can be dismissed
   * @returns {HTMLElement} - Alert element
   */
  createAlert: (message, type = 'info', containerId, dismissible = true) => {
    // Get container element
    const container = document.getElementById(containerId);
    if (!container) {
      console.error(`Alert container with ID "${containerId}" not found`);
      return null;
    }
    
    // Create alert element
    const alertElement = document.createElement('div');
    alertElement.className = `alert alert-${type} ${dismissible ? 'alert-dismissible fade show' : ''}`;
    alertElement.setAttribute('role', 'alert');
    
    // Create alert content
    alertElement.innerHTML = `
      ${message}
      ${dismissible ? '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>' : ''}
    `;
    
    // Add alert to container
    container.appendChild(alertElement);
    
    // Return alert element
    return alertElement;
  }
};

// Export bootstrap handlers
export default bootstrapHandlers;

