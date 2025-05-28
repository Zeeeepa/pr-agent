/**
 * Global Error Handler for PR Review Automator UI
 * 
 * This file provides comprehensive error handling for client-side JavaScript,
 * including:
 * - Global error catching via window.onerror
 * - Resource loading error detection
 * - UI components for displaying errors to users
 * - Server-side error logging
 */

(function() {
  // Error UI container
  let errorContainer = null;
  
  // Create error UI container
  function createErrorContainer() {
    if (errorContainer) return;
    
    errorContainer = document.createElement('div');
    errorContainer.id = 'global-error-container';
    errorContainer.style.cssText = 'position: fixed; bottom: 20px; right: 20px; max-width: 400px; z-index: 9999; display: none;';
    document.body.appendChild(errorContainer);
  }
  
  // Show error message to user
  function showGlobalError(message, isWarning = false) {
    if (!errorContainer) createErrorContainer();
    
    const errorElement = document.createElement('div');
    errorElement.className = isWarning ? 'error-message warning' : 'error-message';
    errorElement.style.cssText = `
      background-color: ${isWarning ? '#fff3cd' : '#f8d7da'}; 
      color: ${isWarning ? '#856404' : '#721c24'}; 
      padding: 10px 15px; 
      margin-top: 10px; 
      border-radius: 4px; 
      box-shadow: 0 2px 5px rgba(0,0,0,0.2);
      position: relative;
    `;
    
    // Add close button
    const closeBtn = document.createElement('button');
    closeBtn.innerHTML = '&times;';
    closeBtn.style.cssText = 'position: absolute; right: 5px; top: 5px; background: none; border: none; font-size: 16px; cursor: pointer;';
    closeBtn.onclick = function() {
      errorElement.remove();
      if (errorContainer.children.length === 0) {
        errorContainer.style.display = 'none';
      }
    };
    
    errorElement.textContent = message;
    errorElement.appendChild(closeBtn);
    
    errorContainer.appendChild(errorElement);
    errorContainer.style.display = 'block';
    
    // Auto-remove after 10 seconds if it's just a warning
    if (isWarning) {
      setTimeout(() => {
        if (errorElement.parentNode) {
          errorElement.remove();
          if (errorContainer.children.length === 0) {
            errorContainer.style.display = 'none';
          }
        }
      }, 10000);
    }
    
    // Also log to console
    console.error(message);
  }
  
  // Global error handler
  window.onerror = function(message, source, lineno, colno, error) {
    const errorMsg = `JavaScript error: ${message} at ${source}:${lineno}:${colno}`;
    showGlobalError(errorMsg);
    
    // Log to server if available
    if (window.fetch) {
      fetch('/api/v1/log', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: 'js_error',
          message: message,
          source: source,
          lineno: lineno,
          colno: colno,
          stack: error ? error.stack : null,
          timestamp: new Date().toISOString()
        })
      }).catch(err => console.error('Failed to log error to server:', err));
    }
    
    return true; // Prevents the default error handling
  };
  
  // Resource loading error handler
  function logResourceLoadingErrors() {
    window.addEventListener('error', function(e) {
      if (e.target.tagName === 'LINK' || e.target.tagName === 'SCRIPT') {
        const resourceType = e.target.tagName === 'LINK' ? 'CSS' : 'JavaScript';
        const resourceUrl = e.target.src || e.target.href;
        const errorMsg = `Failed to load ${resourceType} resource: ${resourceUrl}`;
        
        showGlobalError(errorMsg, true);
        
        // Log to server if available
        if (window.fetch) {
          fetch('/api/v1/log', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              type: 'resource_error',
              resource_type: resourceType,
              resource_url: resourceUrl,
              timestamp: new Date().toISOString()
            })
          }).catch(err => console.error('Failed to log error to server:', err));
        }
      }
    }, true);
  }
  
  // Promise rejection handler
  window.addEventListener('unhandledrejection', function(event) {
    const errorMsg = `Unhandled Promise rejection: ${event.reason}`;
    showGlobalError(errorMsg);
    
    // Log to server if available
    if (window.fetch) {
      fetch('/api/v1/log', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: 'promise_error',
          message: event.reason ? (event.reason.message || String(event.reason)) : 'Unknown promise error',
          stack: event.reason && event.reason.stack ? event.reason.stack : null,
          timestamp: new Date().toISOString()
        })
      }).catch(err => console.error('Failed to log error to server:', err));
    }
  });
  
  // Initialize when DOM is ready
  document.addEventListener('DOMContentLoaded', function() {
    createErrorContainer();
    logResourceLoadingErrors();
    console.log('Error handling system initialized');
  });
  
  // Expose functions globally
  window.ErrorHandler = {
    showError: showGlobalError
  };
})();

