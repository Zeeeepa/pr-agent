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
                    <button class="btn btn-sm btn-outline-${trigger.enabled ? 'danger' : 'success'}" onclick="toggleTrigger('${trigger.id}', ${!trigger.enabled})">
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
 * Update the system status display
 */
function updateSystemStatus() {
    // This would fetch system status from the API
    // For now, we'll just update the timestamp
    updateLastUpdated();
}

/**
 * Show a loading indicator in a table
 * @param {string} tableBodyId - ID of the table body element
 */
function showLoading(tableBodyId) {
    const tableBody = document.getElementById(tableBodyId);
    if (!tableBody) return;
    
    tableBody.innerHTML = '<tr><td colspan="5" class="text-center">Loading...</td></tr>';
}

/**
 * Show an error message in a table
 * @param {string} tableBodyId - ID of the table body element
 * @param {string} message - Error message to display
 */
function showError(tableBodyId, message) {
    const tableBody = document.getElementById(tableBodyId);
    if (!tableBody) return;
    
    tableBody.innerHTML = `<tr><td colspan="5" class="text-center text-danger">${message}</td></tr>`;
}

/**
 * Show the create trigger modal
 */
function showCreateTriggerModal() {
    // This would show a modal for creating a new trigger
    alert('Create Trigger Modal would show here');
    // In a real implementation, this would open a modal with a form
}

/**
 * Show the connections diagram
 */
function showConnectionsDiagram() {
    // This would show a diagram of trigger connections
    alert('Connections Diagram would show here');
    // In a real implementation, this would open a modal with a visualization
}

/**
 * View event details
 * @param {string} eventId - ID of the event to view
 */
function viewEventDetails(eventId) {
    // This would show details for a specific event
    alert(`View details for event ${eventId}`);
    // In a real implementation, this would open a modal with event details
}

/**
 * Edit a trigger
 * @param {string} triggerId - ID of the trigger to edit
 */
function editTrigger(triggerId) {
    // This would open a form to edit a trigger
    alert(`Edit trigger ${triggerId}`);
    // In a real implementation, this would open a modal with a form
}

/**
 * Toggle a trigger's enabled status
 * @param {string} triggerId - ID of the trigger to toggle
 * @param {boolean} enabled - New enabled status
 */
function toggleTrigger(triggerId, enabled) {
    // This would update a trigger's enabled status
    fetch(`${EVENT_SYSTEM.apiBaseUrl}/triggers/${triggerId}`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ enabled: enabled })
    })
    .then(response => response.json())
    .then(data => {
        // Refresh the triggers table
        fetchTriggers();
    })
    .catch(error => {
        console.error('Error toggling trigger:', error);
        alert(`Failed to ${enabled ? 'enable' : 'disable'} trigger`);
    });
}

/**
 * Apply filters to the triggers table
 */
function applyTriggerFilters() {
    const repository = document.getElementById('filter-repository').value;
    const eventType = document.getElementById('filter-event-type').value;
    const status = document.getElementById('filter-status').value;
    
    // Build the query string
    let queryString = '';
    if (repository) queryString += `&repository=${repository}`;
    if (eventType) queryString += `&event_type=${eventType}`;
    if (status) queryString += `&enabled=${status === 'active'}`;
    
    // Fetch filtered triggers
    fetch(`${EVENT_SYSTEM.apiBaseUrl}/triggers?${queryString.substring(1)}`)
        .then(response => response.json())
        .then(data => {
            updateTriggersTable(data);
        })
        .catch(error => {
            console.error('Error applying filters:', error);
        });
}

/**
 * Reset filters on the triggers table
 */
function resetTriggerFilters() {
    // Reset filter inputs
    document.getElementById('filter-repository').value = '';
    document.getElementById('filter-event-type').value = '';
    document.getElementById('filter-status').value = '';
    
    // Fetch all triggers
    fetchTriggers();
}

/**
 * Initialize settings
 */
function initializeSettings() {
    // Load settings from localStorage
    const githubApiKey = localStorage.getItem('github-api-key') || '';
    const supabaseUrl = localStorage.getItem('supabase-url') || '';
    const supabaseApiKey = localStorage.getItem('supabase-api-key') || '';
    
    // Set input values
    document.getElementById('github-api-key').value = githubApiKey;
    document.getElementById('supabase-url').value = supabaseUrl;
    document.getElementById('supabase-api-key').value = supabaseApiKey;
    
    // If we have settings, send them to the server
    if (supabaseUrl && supabaseApiKey) {
        saveSettingsToServer({
            GITHUB_TOKEN: githubApiKey,
            SUPABASE_URL: supabaseUrl,
            SUPABASE_ANON_KEY: supabaseApiKey
        });
    }
}

/**
 * Show the settings dialog
 */
function showSettingsDialog() {
    const settingsDialog = document.getElementById('settings-dialog');
    if (settingsDialog) {
        settingsDialog.style.display = 'flex';
    }
}

/**
 * Hide the settings dialog
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
    const githubApiKey = document.getElementById('github-api-key').value;
    const supabaseUrl = document.getElementById('supabase-url').value;
    const supabaseApiKey = document.getElementById('supabase-api-key').value;
    const validationMessage = document.getElementById('validation-message');
    
    // Check if required fields are filled
    if (!supabaseUrl || !supabaseApiKey) {
        validationMessage.textContent = 'Error: Supabase URL and API key are required';
        validationMessage.className = 'validation-message validation-error';
        validationMessage.style.display = 'block';
        return;
    }
    
    // Validate settings with the server
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
        if (data.valid) {
            validationMessage.textContent = 'Verified! All credentials are valid';
            validationMessage.className = 'validation-message validation-success';
        } else {
            validationMessage.textContent = data.error || 'Error: Invalid credentials';
            validationMessage.className = 'validation-message validation-error';
        }
        validationMessage.style.display = 'block';
    })
    .catch(error => {
        console.error('Error validating settings:', error);
        validationMessage.textContent = 'Error: Failed to validate settings';
        validationMessage.className = 'validation-message validation-error';
        validationMessage.style.display = 'block';
    });
}

/**
 * Save settings
 */
function saveSettings() {
    const githubApiKey = document.getElementById('github-api-key').value;
    const supabaseUrl = document.getElementById('supabase-url').value;
    const supabaseApiKey = document.getElementById('supabase-api-key').value;
    const validationMessage = document.getElementById('validation-message');
    
    // Check if required fields are filled
    if (!supabaseUrl || !supabaseApiKey) {
        validationMessage.textContent = 'Error: Supabase URL and API key are required';
        validationMessage.className = 'validation-message validation-error';
        validationMessage.style.display = 'block';
        return;
    }
    
    // Save to localStorage
    localStorage.setItem('github-api-key', githubApiKey);
    localStorage.setItem('supabase-url', supabaseUrl);
    localStorage.setItem('supabase-api-key', supabaseApiKey);
    
    // Save to server
    saveSettingsToServer({
        GITHUB_TOKEN: githubApiKey,
        SUPABASE_URL: supabaseUrl,
        SUPABASE_ANON_KEY: supabaseApiKey
    });
    
    validationMessage.textContent = 'Settings saved successfully';
    validationMessage.className = 'validation-message validation-success';
    validationMessage.style.display = 'block';
    
    setTimeout(() => {
        validationMessage.style.display = 'none';
    }, 2000);
}

/**
 * Save settings to server
 * @param {Object} settings - Settings object
 */
function saveSettingsToServer(settings) {
    fetch(`${EVENT_SYSTEM.apiBaseUrl}/settings`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(settings)
    })
    .then(response => response.json())
    .catch(error => {
        console.error('Error saving settings to server:', error);
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
