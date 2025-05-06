// Fixed UI elements for the dashboard

/**
 * Create a tab element
 * @param {string} id - The ID of the tab
 * @param {string} label - The label text for the tab
 * @param {boolean} dynamic - Whether the tab has dynamic content
 * @returns {HTMLElement} The created tab element
 */
export function createTabElement(id, label, dynamic = false) {
  const tab = document.createElement('button');
  tab.className = 'tab';
  tab.setAttribute('data-tab', id);
  tab.textContent = label;
  
  if (dynamic) {
    tab.setAttribute('data-dynamic', 'true');
  }
  
  return tab;
}

/**
 * Create a tab content element
 * @param {string} id - The ID of the tab
 * @returns {HTMLElement} The created tab content element
 */
export function createTabContentElement(id) {
  const content = document.createElement('div');
  content.className = 'tab-content';
  content.setAttribute('data-tab', id);
  
  // Add default content based on tab ID
  switch(id) {
    case 'overview':
      content.innerHTML = createOverviewContent();
      break;
    case 'settings':
      content.innerHTML = createSettingsContent();
      break;
    default:
      content.innerHTML = '<div class="loading-spinner"></div>';
  }
  
  return content;
}

/**
 * Setup fixed UI elements
 */
export function setupFixedElements() {
  // Create notification panel
  createNotificationPanel();
  
  // Setup theme toggle
  setupThemeToggle();
}

/**
 * Create the notification panel
 */
function createNotificationPanel() {
  const panel = document.createElement('div');
  panel.className = 'notification-panel';
  
  const header = document.createElement('div');
  header.className = 'notification-header';
  header.innerHTML = `
    <h3>Notifications</h3>
    <button class="mark-read-button">Mark all as read</button>
  `;
  
  const content = document.createElement('div');
  content.className = 'notification-content';
  content.innerHTML = `
    <div class="notification-item unread">
      <div class="notification-icon">🔔</div>
      <div class="notification-details">
        <div class="notification-title">New PR Review</div>
        <div class="notification-message">PR #123 has been reviewed</div>
        <div class="notification-time">2 hours ago</div>
      </div>
    </div>
    <div class="notification-item unread">
      <div class="notification-icon">🔔</div>
      <div class="notification-details">
        <div class="notification-title">PR Merged</div>
        <div class="notification-message">PR #122 has been merged</div>
        <div class="notification-time">5 hours ago</div>
      </div>
    </div>
    <div class="notification-item unread">
      <div class="notification-icon">🔔</div>
      <div class="notification-details">
        <div class="notification-title">New Comment</div>
        <div class="notification-message">New comment on PR #121</div>
        <div class="notification-time">1 day ago</div>
      </div>
    </div>
  `;
  
  panel.appendChild(header);
  panel.appendChild(content);
  
  document.body.appendChild(panel);
  
  // Add event listener to mark all as read button
  const markReadButton = panel.querySelector('.mark-read-button');
  if (markReadButton) {
    markReadButton.addEventListener('click', () => {
      // Mark all notifications as read
      panel.querySelectorAll('.notification-item').forEach(item => {
        item.classList.remove('unread');
      });
      
      // Update badge
      const badge = document.querySelector('.notification-badge .badge');
      if (badge) {
        badge.style.display = 'none';
      }
    });
  }
}

/**
 * Setup theme toggle functionality
 */
function setupThemeToggle() {
  const themeToggle = document.querySelector('.theme-toggle');
  if (!themeToggle) return;
  
  // Check for saved theme preference
  const savedTheme = localStorage.getItem('theme');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  
  if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
    document.body.classList.add('dark-mode');
    document.getElementById('theme-stylesheet')?.removeAttribute('disabled');
    themeToggle.textContent = '☀️';
    themeToggle.setAttribute('aria-label', 'Switch to light mode');
  } else {
    document.body.classList.remove('dark-mode');
    document.getElementById('theme-stylesheet')?.setAttribute('disabled', '');
    themeToggle.textContent = '🌙';
    themeToggle.setAttribute('aria-label', 'Switch to dark mode');
  }
}

/**
 * Create content for the Overview tab
 * @returns {string} HTML content
 */
function createOverviewContent() {
  return `
    <h2>Dashboard Overview</h2>
    <div class="stats-container">
      <div class="stat-card">
        <h3>Open PRs</h3>
        <p class="stat-value">12</p>
      </div>
      <div class="stat-card">
        <h3>Pending Reviews</h3>
        <p class="stat-value">5</p>
      </div>
      <div class="stat-card">
        <h3>Completed Today</h3>
        <p class="stat-value">7</p>
      </div>
    </div>
    <div class="recent-activity mt-4">
      <h3>Recent Activity</h3>
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>Type</th>
              <th>Description</th>
              <th>Time</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>PR Review</td>
              <td>Reviewed PR #123: Implement user authentication</td>
              <td>2 hours ago</td>
            </tr>
            <tr>
              <td>PR Merge</td>
              <td>Merged PR #122: Fix navigation bug</td>
              <td>5 hours ago</td>
            </tr>
            <tr>
              <td>Comment</td>
              <td>Commented on PR #121: Update documentation</td>
              <td>1 day ago</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `;
}

/**
 * Create content for the Settings tab
 * @returns {string} HTML content
 */
function createSettingsContent() {
  return `
    <h2>Dashboard Settings</h2>
    <div class="settings-container">
      <div class="settings-group">
        <h3>Notification Settings</h3>
        <div class="setting-item">
          <label>
            <input type="checkbox" checked> Email notifications
          </label>
        </div>
        <div class="setting-item">
          <label>
            <input type="checkbox" checked> Browser notifications
          </label>
        </div>
      </div>
      <div class="settings-group">
        <h3>Display Settings</h3>
        <div class="setting-item">
          <label>
            <input type="checkbox" checked> Show closed PRs
          </label>
        </div>
        <div class="setting-item">
          <label>
            <input type="checkbox" checked> Auto-refresh (every 5 minutes)
          </label>
        </div>
      </div>
      <div class="settings-group">
        <h3>Theme Settings</h3>
        <div class="setting-item">
          <label>
            <input type="radio" name="theme" value="light" checked> Light theme
          </label>
        </div>
        <div class="setting-item">
          <label>
            <input type="radio" name="theme" value="dark"> Dark theme
          </label>
        </div>
        <div class="setting-item">
          <label>
            <input type="radio" name="theme" value="system"> Use system preference
          </label>
        </div>
      </div>
    </div>
  `;
}

