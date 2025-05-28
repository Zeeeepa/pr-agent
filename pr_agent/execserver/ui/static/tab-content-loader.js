// Dynamic tab content loading
document.addEventListener('DOMContentLoaded', function() {
  setupDynamicContentLoading();
});

function setupDynamicContentLoading() {
  // Set up content loading for tabs that need dynamic data
  document.querySelectorAll('.tab[data-dynamic="true"]').forEach(tab => {
    tab.addEventListener('click', function() {
      const tabId = this.getAttribute('data-tab');
      loadTabContent(tabId);
    });
  });
  
  // Load content for the initial active tab if it's dynamic
  const activeTab = document.querySelector('.tab.active[data-dynamic="true"]');
  if (activeTab) {
    const tabId = activeTab.getAttribute('data-tab');
    loadTabContent(tabId);
  }
}

function loadTabContent(tabId) {
  const contentContainer = document.querySelector(`.tab-content[data-tab="${tabId}"]`);
  if (!contentContainer) return;
  
  // Show loading state
  contentContainer.innerHTML = '<div class="loading-spinner"></div>';
  
  // Simulate API call to load content
  setTimeout(function() {
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

