// Bootstrap integration for the dashboard
import { createTabElement, createTabContentElement } from './dashboard-fixed';

/**
 * Initialize tabs for the dashboard
 */
export function initializeTabs() {
  // Get saved tab from localStorage or default to first tab
  const savedTab = localStorage.getItem('activeTab') || 'overview';
  
  // Define available tabs
  const tabs = [
    { id: 'overview', label: 'Overview', dynamic: false },
    { id: 'prs', label: 'Pull Requests', dynamic: true },
    { id: 'reviews', label: 'Reviews', dynamic: true },
    { id: 'settings', label: 'Settings', dynamic: false }
  ];
  
  // Create tab elements
  const tabsContainer = document.querySelector('.tabs');
  if (tabsContainer) {
    tabs.forEach(tab => {
      const tabElement = createTabElement(tab.id, tab.label, tab.dynamic);
      tabsContainer.appendChild(tabElement);
      
      // Add click handler
      tabElement.addEventListener('click', () => {
        setActiveTab(tab.id);
        localStorage.setItem('activeTab', tab.id);
        
        // Load dynamic content if needed
        if (tab.dynamic) {
          loadTabContent(tab.id);
        }
      });
    });
  }
  
  // Create tab content containers
  const contentContainer = document.querySelector('.dashboard-content');
  if (contentContainer) {
    tabs.forEach(tab => {
      const contentElement = createTabContentElement(tab.id);
      contentContainer.appendChild(contentElement);
    });
  }
  
  // Set the active tab
  setActiveTab(savedTab);
  
  // Load dynamic content for the active tab if needed
  const activeTab = tabs.find(tab => tab.id === savedTab);
  if (activeTab && activeTab.dynamic) {
    loadTabContent(savedTab);
  }
}

/**
 * Set the active tab
 * @param {string} tabId - The ID of the tab to activate
 */
export function setActiveTab(tabId) {
  // Remove active class from all tabs
  document.querySelectorAll('.tab').forEach(tab => {
    tab.classList.remove('active');
  });
  
  // Add active class to selected tab
  const activeTab = document.querySelector(`.tab[data-tab="${tabId}"]`);
  if (activeTab) {
    activeTab.classList.add('active');
  }
  
  // Hide all tab content
  document.querySelectorAll('.tab-content').forEach(content => {
    content.classList.remove('active');
  });
  
  // Show selected tab content
  const activeContent = document.querySelector(`.tab-content[data-tab="${tabId}"]`);
  if (activeContent) {
    activeContent.classList.add('active');
  }
}

/**
 * Load content for a tab dynamically
 * @param {string} tabId - The ID of the tab to load content for
 */
export function loadTabContent(tabId) {
  const contentContainer = document.querySelector(`.tab-content[data-tab="${tabId}"]`);
  if (!contentContainer) return;
  
  // Show loading state
  contentContainer.innerHTML = '<div class="loading-spinner"></div>';
  
  // Simulate API call to load content
  setTimeout(() => {
    // This would typically be an API call
    let content = '';
    
    switch(tabId) {
      case 'prs':
        content = generatePullRequestsContent();
        break;
      case 'reviews':
        content = generateReviewsContent();
        break;
      default:
        content = '<p>No dynamic content available for this tab.</p>';
    }
    
    contentContainer.innerHTML = content;
  }, 500);
}

/**
 * Generate content for the Pull Requests tab
 * @returns {string} HTML content
 */
function generatePullRequestsContent() {
  // This would typically come from an API
  return `
    <h2>Pull Requests</h2>
    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>PR #</th>
            <th>Title</th>
            <th>Author</th>
            <th>Status</th>
            <th>Updated</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>#123</td>
            <td>Implement user authentication</td>
            <td>johndoe</td>
            <td>Open</td>
            <td>2 hours ago</td>
          </tr>
          <tr>
            <td>#122</td>
            <td>Fix navigation bug</td>
            <td>janedoe</td>
            <td>Merged</td>
            <td>5 hours ago</td>
          </tr>
          <tr>
            <td>#121</td>
            <td>Update documentation</td>
            <td>bobsmith</td>
            <td>Closed</td>
            <td>1 day ago</td>
          </tr>
        </tbody>
      </table>
    </div>
  `;
}

/**
 * Generate content for the Reviews tab
 * @returns {string} HTML content
 */
function generateReviewsContent() {
  // This would typically come from an API
  return `
    <h2>Review Activity</h2>
    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>PR #</th>
            <th>Reviewer</th>
            <th>Status</th>
            <th>Comments</th>
            <th>Submitted</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>#123</td>
            <td>AI Assistant</td>
            <td>Approved</td>
            <td>2</td>
            <td>1 hour ago</td>
          </tr>
          <tr>
            <td>#122</td>
            <td>AI Assistant</td>
            <td>Changes Requested</td>
            <td>5</td>
            <td>3 hours ago</td>
          </tr>
          <tr>
            <td>#120</td>
            <td>AI Assistant</td>
            <td>Approved</td>
            <td>0</td>
            <td>2 days ago</td>
          </tr>
        </tbody>
      </table>
    </div>
  `;
}

