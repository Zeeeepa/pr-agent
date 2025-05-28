/**
 * Event System Interconnection
 * 
 * This file handles the event system interconnection for the PR-Agent dashboard.
 * It provides functionality for:
 * - Fetching and displaying recent events
 * - Managing event triggers
 * - Visualizing event flow
 * - Connecting triggers to actions
 * - Managing settings
 */

// Event System Configuration
const EVENT_SYSTEM = {
    apiBaseUrl: '/api/v1',
    refreshInterval: 30000, // 30 seconds
    maxEventsToShow: 10,
    autoRefresh: true
};

// Event Types and their display names
const EVENT_TYPES = {
    'push': 'Push',
    'pull_request': 'Pull Request',
    'pull_request_review': 'PR Review',
    'pull_request_review_comment': 'PR Review Comment',
    'issues': 'Issues',
    'issue_comment': 'Issue Comment',
    'create': 'Create',
    'delete': 'Delete',
    'release': 'Release',
    'workflow_run': 'Workflow Run'
};

// Action Types and their display names
const ACTION_TYPES = {
    'codefile': 'Execute Code File',
    'github_action': 'GitHub Action',
    'github_workflow': 'GitHub Workflow',
    'pr_comment': 'PR Comment'
};

// Initialize the event system
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're using the React app
    if (document.getElementById('root')) {
        console.log('React app detected, skipping legacy event system initialization');
        return;
    }
    
    // Initialize the dashboard
    initializeEventSystem();
    
    // Set up event handlers
    setupEventHandlers();
    
    // Start auto-refresh if enabled
    if (EVENT_SYSTEM.autoRefresh) {
        startAutoRefresh();
    }
    
    // Initialize settings
    initializeSettings();
});

/**
 * Initialize the event system
 */
function initializeEventSystem() {
    // Fetch initial data
    fetchRecentEvents();
    fetchTriggers();
    updateSystemStatus();
    
    // Update last updated timestamp
    updateLastUpdated();
}

/**
 * Set up event handlers for the UI
 */
function setupEventHandlers() {
    // Event refresh button
    const refreshButton = document.getElementById('refresh-events');
    if (refreshButton) {
        refreshButton.addEventListener('click', fetchRecentEvents);
    }
    
    // Load more events button
    const loadMoreButton = document.getElementById('load-more-events');
    if (loadMoreButton) {
        loadMoreButton.addEventListener('click', loadMoreEvents);
    }
    
    // Create trigger button
    const createTriggerButton = document.getElementById('create-trigger-btn');
    if (createTriggerButton) {
        createTriggerButton.addEventListener('click', showCreateTriggerModal);
    }
    
    // View connections button
    const viewConnectionsButton = document.getElementById('view-connections');
    if (viewConnectionsButton) {
        viewConnectionsButton.addEventListener('click', showConnectionsDiagram);
    }
    
    // Filter buttons
    const applyFiltersButton = document.getElementById('apply-filters');
    if (applyFiltersButton) {
        applyFiltersButton.addEventListener('click', applyTriggerFilters);
    }
    
    const resetFiltersButton = document.getElementById('reset-filters');
    if (resetFiltersButton) {
        resetFiltersButton.addEventListener('click', resetTriggerFilters);
    }
    
    // Settings button
    const settingsBtn = document.getElementById('settings-btn');
    if (settingsBtn) {
        settingsBtn.addEventListener('click', showSettingsDialog);
    }
    
    // Settings dialog close button
    const settingsCloseBtn = document.querySelector('.settings-dialog-close');
    if (settingsCloseBtn) {
        settingsCloseBtn.addEventListener('click', hideSettingsDialog);
    }
    
    // Settings dialog background click
    const settingsDialog = document.getElementById('settings-dialog');
    if (settingsDialog) {
        settingsDialog.addEventListener('click', function(e) {
            if (e.target === settingsDialog) {
                hideSettingsDialog();
            }
        });
    }
    
    // Validate settings button
    const validateBtn = document.getElementById('validate-settings');
    if (validateBtn) {
        validateBtn.addEventListener('click', validateSettings);
    }
    
    // Save settings button
    const saveBtn = document.getElementById('save-settings');
    if (saveBtn) {
        saveBtn.addEventListener('click', saveSettings);
    }
}

/**
 * Start auto-refresh for events
 */
function startAutoRefresh() {
    setInterval(function() {
        if (document.visibilityState === 'visible') {
            fetchRecentEvents(true); // Silent refresh (no UI feedback)
            updateSystemStatus();
        }
    }, EVENT_SYSTEM.refreshInterval);
}

/**
 * Update the last updated timestamp
 */
function updateLastUpdated() {
    const lastUpdatedElement = document.getElementById('last-updated');
    if (lastUpdatedElement) {
        lastUpdatedElement.textContent = new Date().toLocaleString();
    }
}

/**
 * Fetch recent events from the API
 * @param {boolean} silent - Whether to show UI feedback
 */
function fetchRecentEvents(silent = false) {
    if (!silent) {
        showLoading('events-table-body');
    }
    
    // Fetch events from API
    fetch(`${EVENT_SYSTEM.apiBaseUrl}/events?limit=${EVENT_SYSTEM.maxEventsToShow}`)
        .then(response => response.json())
        .then(data => {
            updateEventsTable(data);
            if (!silent) {
                updateLastUpdated();
            }
        })
        .catch(error => {
            console.error('Error fetching events:', error);
            if (!silent) {
                showError('events-table-body', 'Failed to fetch events');
            }
        });
}

/**
 * Load more events from the API
 */
function loadMoreEvents() {
    const currentCount = document.querySelectorAll('#events-table-body tr').length;
    
    fetch(`${EVENT_SYSTEM.apiBaseUrl}/events?limit=${EVENT_SYSTEM.maxEventsToShow}&offset=${currentCount}`)
        .then(response => response.json())
        .then(data => {
            appendEventsToTable(data);
        })
        .catch(error => {
            console.error('Error loading more events:', error);
            showError('events-table-body', 'Failed to load more events');
        });
}

/**
 * Update the events table with new data
 * @param {Array} events - Array of event objects
 */
function updateEventsTable(events) {
    const tableBody = document.getElementById('events-table-body');
    if (!tableBody) return;
    
    // Clear the table
    tableBody.innerHTML = '';
    
    // Add events to the table
    if (events && events.length > 0) {
        appendEventsToTable(events);
    } else {
        tableBody.innerHTML = '<tr><td colspan="5" class="text-center">No events found</td></tr>';
    }
}

/**
 * Append events to the events table
 * @param {Array} events - Array of event objects
 */
function appendEventsToTable(events) {
    const tableBody = document.getElementById('events-table-body');
    if (!tableBody || !events || events.length === 0) return;
    
    events.forEach(event => {
        const row = document.createElement('tr');
        
        // Format the timestamp
        const timestamp = new Date(event.created_at).toLocaleString();
        
        // Create the row content
        row.innerHTML = `
            <td>${EVENT_TYPES[event.event_type] || event.event_type}</td>
            <td>${event.repository}</td>
            <td>${timestamp}</td>
            <td><span class="${event.processed ? 'status-active' : 'status-inactive'}">${event.processed ? 'Yes' : 'No'}</span></td>
            <td>
                <button class="btn btn-sm btn-outline-info" onclick="viewEventDetails('${event.id}')">View Details</button>
            </td>
        `;
        
        tableBody.appendChild(row);
    });
}

/**
 * Fetch triggers from the API
 */
function fetchTriggers() {
    fetch(`${EVENT_SYSTEM.apiBaseUrl}/triggers`)
        .then(response => response.json())
        .then(data => {
            updateTriggersTable(data);
        })
        .catch(error => {
            console.error('Error fetching triggers:', error);
        });
}

/**
 * Update the triggers table with new data
 * @param {Array} triggers - Array of trigger objects
 */
function updateTriggersTable(triggers) {
    const tableBody = document.querySelector('#triggers-table tbody');
    if (!tableBody) return;
    
    // Clear the table
    tableBody.innerHTML = '';
    
    // Add triggers to the table
    if (triggers && triggers.length > 0) {
        triggers.forEach(trigger => {
            const row = document.createElement('tr');
            
            // Get the first condition and action for display
            const condition = trigger.conditions && trigger.conditions.length > 0 ? trigger.conditions[0] : null;
            const action = trigger.actions && trigger.actions.length > 0 ? trigger.actions[0] : null;
            
            // Create the action cell content with connections
            let actionContent = action ? ACTION_TYPES[action.action_type] || action.action_type : 'No action';
            
            // Add connections if this trigger has multiple actions
            if (trigger.actions && trigger.actions.length > 1) {
                actionContent += `
                    <div class="trigger-connection mt-2">
                        <span class="connection-dot"></span> Triggers: ${trigger.actions.length - 1} more action(s)
                    </div>
                `;
            }
            
            // Create the row content
            row.innerHTML = `
                <td>${trigger.name}</td>
                <td>${trigger.project_id}</td>
                <td>${condition ? condition.event_type : 'N/A'}</td>
                <td>${actionContent}</td>
                <td><span class="${trigger.enabled ? 'status-active' : 'status-inactive'}">${trigger.enabled ? 'Active' : 'Inactive'}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="editTrigger('${trigger.id}')">Edit</button>
                    <button class="btn btn-sm btn-outline-${trigger.enabled ? 'danger' : 'success'}" onclick="toggleTrigger('${trigger.id}', ${trigger.enabled})">
                        ${trigger.enabled ? 'Disable' : 'Enable'}
                    </button>
                </td>
            `;
            
            tableBody.appendChild(row);
        });
    } else {
        tableBody.innerHTML = '<tr><td colspan="6" class="text-center">No triggers found</td></tr>';
    }
}

/**
 * Show loading state in a container
 * @param {string} containerId - ID of the container element
 */
function showLoading(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = '<tr><td colspan="5" class="text-center">Loading...</td></tr>';
}

/**
 * Show error message in a container
 * @param {string} containerId - ID of the container element
 * @param {string} message - Error message to display
 */
function showError(containerId, message) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = `<tr><td colspan="5" class="text-center text-danger">${message}</td></tr>`;
}

/**
 * Update system status
 */
function updateSystemStatus() {
    fetch(`${EVENT_SYSTEM.apiBaseUrl}/database/status`)
        .then(response => response.json())
        .then(data => {
            const statusElement = document.querySelector('.status-active');
            if (statusElement) {
                if (data.status === 'connected') {
                    statusElement.textContent = '● All systems operational';
                    statusElement.className = 'status-active';
                } else {
                    statusElement.textContent = '● Database disconnected';
                    statusElement.className = 'status-inactive';
                }
            }
        })
        .catch(error => {
            console.error('Error updating system status:', error);
        });
}

/**
 * View event details
 * @param {string} eventId - ID of the event to view
 */
function viewEventDetails(eventId) {
    alert(`View details for event ${eventId}`);
}

/**
 * Edit a trigger
 * @param {string} triggerId - ID of the trigger to edit
 */
function editTrigger(triggerId) {
    alert(`Edit trigger ${triggerId}`);
}

/**
 * Toggle a trigger's enabled state
 * @param {string} triggerId - ID of the trigger to toggle
 * @param {boolean} currentEnabled - Current enabled state
 */
function toggleTrigger(triggerId, currentEnabled) {
    fetch(`${EVENT_SYSTEM.apiBaseUrl}/triggers/${triggerId}`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            enabled: !currentEnabled
        })
    })
    .then(response => response.json())
    .then(data => {
        // Refresh triggers
        fetchTriggers();
    })
    .catch(error => {
        console.error('Error toggling trigger:', error);
        alert('Failed to toggle trigger');
    });
}

/**
 * Show create trigger modal
 */
function showCreateTriggerModal() {
    alert('Create trigger modal');
}

/**
 * Show connections diagram
 */
function showConnectionsDiagram() {
    alert('Show connections diagram');
}

/**
 * Apply trigger filters
 */
function applyTriggerFilters() {
    alert('Apply trigger filters');
}

/**
 * Reset trigger filters
 */
function resetTriggerFilters() {
    alert('Reset trigger filters');
}

/**
 * Initialize settings
 */
function initializeSettings() {
    const themeToggleBtn = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    
    if (themeToggleBtn && themeIcon) {
        const savedTheme = localStorage.getItem('theme') || 
            (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
        
        if (savedTheme === 'dark') {
            document.documentElement.setAttribute('data-theme', 'dark');
            themeIcon.textContent = '☀️';
        }
        
        themeToggleBtn.addEventListener('click', function() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            
            if (newTheme === 'dark') {
                themeIcon.textContent = '☀️';
            } else {
                themeIcon.textContent = '🌙';
            }
        });
    }
    
    // Load settings from localStorage
    const githubApiKey = localStorage.getItem('github-api-key') || '';
    const supabaseUrl = localStorage.getItem('supabase-url') || '';
    const supabaseApiKey = localStorage.getItem('supabase-api-key') || '';
    
    const githubApiKeyInput = document.getElementById('github-api-key');
    const supabaseUrlInput = document.getElementById('supabase-url');
    const supabaseApiKeyInput = document.getElementById('supabase-api-key');
    
    if (githubApiKeyInput) githubApiKeyInput.value = githubApiKey;
    if (supabaseUrlInput) supabaseUrlInput.value = supabaseUrl;
    if (supabaseApiKeyInput) supabaseApiKeyInput.value = supabaseApiKey;
}

/**
 * Show settings dialog
 */
function showSettingsDialog() {
    const settingsDialog = document.getElementById('settings-dialog');
    if (settingsDialog) {
        settingsDialog.style.display = 'flex';
    }
}

/**
 * Hide settings dialog
 */
function hideSettingsDialog() {
    const settingsDialog = document.getElementById('settings-dialog');
    if (settingsDialog) {
        settingsDialog.style.display = 'none';
    }
}

/**
 * Validate settings
 */
function validateSettings() {
    const githubApiKey = document.getElementById('github-api-key')?.value || '';
    const supabaseUrl = document.getElementById('supabase-url')?.value || '';
    const supabaseApiKey = document.getElementById('supabase-api-key')?.value || '';
    const validationMessage = document.getElementById('validation-message');
    const validateSpinner = document.getElementById('validate-spinner');
    
    if (!validationMessage || !validateSpinner) return;
    
    // Show loading state
    validationMessage.textContent = 'Validating settings...';
    validationMessage.className = 'validation-message';
    validationMessage.style.display = 'block';
    validateSpinner.classList.remove('d-none');
    
    // Check if required fields are filled
    if (!supabaseUrl || !supabaseApiKey) {
        validationMessage.textContent = 'Error: Supabase URL and API key are required';
        validationMessage.className = 'validation-message validation-error';
        validationMessage.style.display = 'block';
        validateSpinner.classList.add('d-none');
        return;
    }
    
    // Validate settings with API
    fetch(`${EVENT_SYSTEM.apiBaseUrl}/settings/validate`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            GITHUB_TOKEN: githubApiKey,
            SUPABASE_URL: supabaseUrl,
            SUPABASE_ANON_KEY: supabaseApiKey
        })
    })
    .then(response => response.json())
    .then(data => {
        validateSpinner.classList.add('d-none');
        
        if (data.valid) {
            validationMessage.textContent = 'Verified! All credentials are valid';
            validationMessage.className = 'validation-message validation-success';
            
            // Check database status and migrations
            checkDatabaseStatus();
            checkMigrationStatus();
        } else {
            validationMessage.textContent = data.message || 'Error: Invalid credentials';
            validationMessage.className = 'validation-message validation-error';
        }
        validationMessage.style.display = 'block';
    })
    .catch(error => {
        console.error('Error validating settings:', error);
        validationMessage.textContent = 'Error: Failed to validate settings';
        validationMessage.className = 'validation-message validation-error';
        validationMessage.style.display = 'block';
        validateSpinner.classList.add('d-none');
    });
}

/**
 * Save settings
 */
function saveSettings() {
    const githubApiKey = document.getElementById('github-api-key')?.value || '';
    const supabaseUrl = document.getElementById('supabase-url')?.value || '';
    const supabaseApiKey = document.getElementById('supabase-api-key')?.value || '';
    const validationMessage = document.getElementById('validation-message');
    const saveSpinner = document.getElementById('save-spinner');
    
    if (!validationMessage || !saveSpinner) return;
    
    // Show loading state
    validationMessage.textContent = 'Saving settings...';
    validationMessage.className = 'validation-message';
    validationMessage.style.display = 'block';
    saveSpinner.classList.remove('d-none');
    
    // Check if required fields are filled
    if (!supabaseUrl || !supabaseApiKey) {
        validationMessage.textContent = 'Error: Supabase URL and API key are required';
        validationMessage.className = 'validation-message validation-error';
        validationMessage.style.display = 'block';
        saveSpinner.classList.add('d-none');
        return;
    }
    
    // Save to localStorage
    localStorage.setItem('github-api-key', githubApiKey);
    localStorage.setItem('supabase-url', supabaseUrl);
    localStorage.setItem('supabase-api-key', supabaseApiKey);
    
    // Save to server
    fetch(`${EVENT_SYSTEM.apiBaseUrl}/settings`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            GITHUB_TOKEN: githubApiKey,
            SUPABASE_URL: supabaseUrl,
            SUPABASE_ANON_KEY: supabaseApiKey
        })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.detail?.message || 'Failed to save settings');
            });
        }
        return response.json();
    })
    .then(data => {
        saveSpinner.classList.add('d-none');
        validationMessage.textContent = 'Settings saved successfully';
        validationMessage.className = 'validation-message validation-success';
        validationMessage.style.display = 'block';
        
        // Check database status
        checkDatabaseStatus();
        
        // Check migration status
        checkMigrationStatus();
        
        setTimeout(() => {
            validationMessage.style.display = 'none';
        }, 2000);
    })
    .catch(error => {
        console.error('Error saving settings:', error);
        saveSpinner.classList.add('d-none');
        validationMessage.textContent = `Error: ${error.message || 'Failed to save settings'}`;
        validationMessage.className = 'validation-message validation-error';
        validationMessage.style.display = 'block';
    });
}

/**
 * Check database status
 */
function checkDatabaseStatus() {
    fetch(`${EVENT_SYSTEM.apiBaseUrl}/database/status`)
        .then(response => response.json())
        .then(data => {
            const statusElement = document.querySelector('.status-active');
            if (statusElement) {
                if (data.status === 'connected') {
                    statusElement.textContent = '● All systems operational';
                    statusElement.className = 'status-active';
                } else {
                    statusElement.textContent = '● Database disconnected';
                    statusElement.className = 'status-inactive';
                }
            }
        })
        .catch(error => {
            console.error('Error checking database status:', error);
        });
}

/**
 * Check migration status
 */
function checkMigrationStatus() {
    const migrationStatus = document.getElementById('migration-status');
    const migrationInfo = document.getElementById('migration-info');
    const applyMigrationsBtn = document.getElementById('apply-migrations');
    
    if (!migrationStatus || !migrationInfo || !applyMigrationsBtn) return;
    
    fetch(`${EVENT_SYSTEM.apiBaseUrl}/database/migrations`)
        .then(response => response.json())
        .then(data => {
            migrationStatus.classList.remove('d-none');
            
            if (data.status === 'success') {
                const migrations = data.migrations;
                
                // Create migration status HTML
                let html = '';
                
                if (migrations.pending_count > 0) {
                    html += `<div class="alert alert-warning">
                        <strong>Pending Migrations:</strong> ${migrations.pending_count} migrations need to be applied.
                    </div>`;
                    
                    // Show apply migrations button
                    applyMigrationsBtn.classList.remove('d-none');
                    
                    // Add event listener for apply migrations button
                    applyMigrationsBtn.onclick = applyMigrations;
                } else {
                    html += `<div class="alert alert-success">
                        <strong>Database Up to Date:</strong> All migrations have been applied.
                    </div>`;
                    
                    // Hide apply migrations button
                    applyMigrationsBtn.classList.add('d-none');
                }
                
                if (migrations.failed_count > 0) {
                    html += `<div class="alert alert-danger">
                        <strong>Failed Migrations:</strong> ${migrations.failed_count} migrations failed to apply.
                    </div>`;
                }
                
                migrationInfo.innerHTML = html;
            } else {
                migrationInfo.innerHTML = `<div class="alert alert-danger">
                    <strong>Error:</strong> ${data.message || 'Failed to check migration status'}
                </div>`;
                
                // Hide apply migrations button
                applyMigrationsBtn.classList.add('d-none');
            }
        })
        .catch(error => {
            console.error('Error checking migration status:', error);
            migrationStatus.classList.remove('d-none');
            migrationInfo.innerHTML = `<div class="alert alert-danger">
                <strong>Error:</strong> Failed to check migration status
            </div>`;
            
            // Hide apply migrations button
            applyMigrationsBtn.classList.add('d-none');
        });
}

/**
 * Apply migrations
 */
function applyMigrations() {
    const migrationInfo = document.getElementById('migration-info');
    const migrationSpinner = document.getElementById('migration-spinner');
    
    if (!migrationInfo || !migrationSpinner) return;
    
    // Show loading state
    migrationSpinner.classList.remove('d-none');
    
    fetch(`${EVENT_SYSTEM.apiBaseUrl}/database/migrations/apply`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        migrationSpinner.classList.add('d-none');
        
        if (data.status === 'success') {
            migrationInfo.innerHTML = `<div class="alert alert-success">
                <strong>Success:</strong> ${data.message}
            </div>`;
            
            // Hide apply migrations button after successful application
            document.getElementById('apply-migrations')?.classList.add('d-none');
            
            // Refresh database status
            checkDatabaseStatus();
        } else {
            migrationInfo.innerHTML = `<div class="alert alert-danger">
                <strong>Error:</strong> ${data.message}
            </div>`;
        }
    })
    .catch(error => {
        console.error('Error applying migrations:', error);
        migrationSpinner.classList.add('d-none');
        migrationInfo.innerHTML = `<div class="alert alert-danger">
            <strong>Error:</strong> Failed to apply migrations
        </div>`;
    });
}

// Export functions for use in other scripts
window.viewEventDetails = viewEventDetails;
window.editTrigger = editTrigger;
window.toggleTrigger = toggleTrigger;
window.showCreateTriggerModal = showCreateTriggerModal;
window.showConnectionsDiagram = showConnectionsDiagram;
window.showSettingsDialog = showSettingsDialog;
window.hideSettingsDialog = hideSettingsDialog;
window.validateSettings = validateSettings;
window.saveSettings = saveSettings;
window.applyMigrations = applyMigrations;

