// Tab navigation initialization
document.addEventListener('DOMContentLoaded', function() {
  initializeTabs();
});

function initializeTabs() {
  // Get saved tab from localStorage or default to first tab
  const savedTab = localStorage.getItem('activeTab') || 'overview';
  
  // Set the active tab
  setActiveTab(savedTab);
  
  // Add click handlers to tab buttons
  document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', function() {
      const tabId = this.getAttribute('data-tab');
      setActiveTab(tabId);
      localStorage.setItem('activeTab', tabId);
    });
  });
}

function setActiveTab(tabId) {
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

