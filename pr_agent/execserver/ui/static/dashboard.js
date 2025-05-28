// Main dashboard functionality
document.addEventListener('DOMContentLoaded', function() {
  // Initialize dashboard components
  initializeNotifications();
  setupAutoRefresh();
  
  // Theme detection and initialization is handled in React
});

function initializeNotifications() {
  // Set up notification system
  const notificationBadge = document.querySelector('.notification-badge');
  if (notificationBadge) {
    notificationBadge.addEventListener('click', function() {
      // Toggle notification panel visibility
      const panel = document.querySelector('.notification-panel');
      if (panel) {
        panel.classList.toggle('visible');
      }
    });
  }
}

function setupAutoRefresh() {
  // Auto-refresh data every 5 minutes if enabled
  const autoRefreshEnabled = localStorage.getItem('autoRefresh') !== 'false';
  if (autoRefreshEnabled) {
    setInterval(function() {
      refreshDashboardData();
    }, 5 * 60 * 1000); // 5 minutes
  }
}

function refreshDashboardData() {
  // This function would typically make API calls to refresh data
  console.log('Refreshing dashboard data...');
  
  // Show loading indicators
  document.querySelectorAll('.refresh-indicator').forEach(indicator => {
    indicator.classList.add('loading');
  });
  
  // Simulate API call delay
  setTimeout(function() {
    // Hide loading indicators
    document.querySelectorAll('.refresh-indicator').forEach(indicator => {
      indicator.classList.remove('loading');
    });
    
    console.log('Dashboard data refreshed');
  }, 1000);
}

