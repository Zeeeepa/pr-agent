/**
 * Settings Dialog Component
 * 
 * This file provides functionality for the settings dialog, allowing users to
 * configure Supabase credentials and other application settings.
 */

// Settings Dialog Configuration
const SETTINGS_CONFIG = {
    apiBaseUrl: '/api/v1',
    saveEndpoint: '/settings/supabase/save',
    validateEndpoint: '/settings/supabase/validate',
    statusEndpoint: '/settings/supabase/status'
};

// Initialize the settings dialog
document.addEventListener('DOMContentLoaded', function() {
    // Create the settings dialog if it doesn't exist
    createSettingsDialog();
    
    // Set up event handlers
    setupSettingsEventHandlers();
    
    // Check if Supabase is configured
    checkSupabaseStatus();
});

/**
 * Create the settings dialog HTML
 */
function createSettingsDialog() {
    // Check if the dialog already exists
    if (document.getElementById('settings-dialog')) {
        return;
    }
    
    // Create the dialog HTML
    const dialogHTML = `
    <div class="modal fade" id="settings-dialog" tabindex="-1" aria-labelledby="settings-dialog-label" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="settings-dialog-label">Settings</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <div class="mb-3">
                        <h6>Supabase Configuration</h6>
                        <div id="supabase-status" class="alert alert-info">
                            Checking Supabase connection status...
                        </div>
                        <div class="mb-3">
                            <label for="supabase-url" class="form-label">Supabase URL</label>
                            <input type="text" class="form-control" id="supabase-url" placeholder="https://your-project.supabase.co">
                        </div>
                        <div class="mb-3">
                            <label for="supabase-key" class="form-label">Supabase API Key</label>
                            <input type="password" class="form-control" id="supabase-key" placeholder="your-supabase-anon-key">
                        </div>
                        <div class="d-grid gap-2">
                            <button class="btn btn-outline-primary" id="validate-supabase-btn">Validate Connection</button>
                        </div>
                    </div>
                    <hr>
                    <div class="mb-3">
                        <h6>GitHub Configuration</h6>
                        <div class="mb-3">
                            <label for="github-token" class="form-label">GitHub API Token</label>
                            <input type="password" class="form-control" id="github-token" placeholder="github_pat_...">
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" id="save-settings-btn">Save</button>
                </div>
            </div>
        </div>
    </div>
    `;
    
    // Append the dialog to the body
    document.body.insertAdjacentHTML('beforeend', dialogHTML);
}

/**
 * Set up event handlers for the settings dialog
 */
function setupSettingsEventHandlers() {
    // Settings icon click
    const settingsIcon = document.getElementById('settings-icon');
    if (settingsIcon) {
        settingsIcon.addEventListener('click', showSettingsDialog);
    }
    
    // Validate button click
    const validateBtn = document.getElementById('validate-supabase-btn');
    if (validateBtn) {
        validateBtn.addEventListener('click', validateSupabaseConnection);
    }
    
    // Save button click
    const saveBtn = document.getElementById('save-settings-btn');
    if (saveBtn) {
        saveBtn.addEventListener('click', saveSettings);
    }
}

/**
 * Show the settings dialog
 */
function showSettingsDialog() {
    // Get the dialog element
    const dialog = document.getElementById('settings-dialog');
    if (!dialog) {
        console.error('Settings dialog not found');
        return;
    }
    
    // Show the dialog using Bootstrap
    const modal = new bootstrap.Modal(dialog);
    modal.show();
    
    // Check Supabase status
    checkSupabaseStatus();
}

/**
 * Check Supabase connection status
 */
function checkSupabaseStatus() {
    // Get the status element
    const statusElement = document.getElementById('supabase-status');
    if (!statusElement) {
        return;
    }
    
    // Show loading status
    statusElement.className = 'alert alert-info';
    statusElement.textContent = 'Checking Supabase connection status...';
    
    // Fetch status from API
    fetch(`${SETTINGS_CONFIG.apiBaseUrl}/settings/supabase`)
        .then(response => response.json())
        .then(data => {
            if (data.is_configured) {
                if (data.connection_status.is_connected) {
                    statusElement.className = 'alert alert-success';
                    statusElement.textContent = 'Connected to Supabase successfully.';
                } else {
                    statusElement.className = 'alert alert-warning';
                    statusElement.textContent = `Supabase is configured but not connected: ${data.connection_status.error}`;
                }
            } else {
                statusElement.className = 'alert alert-warning';
                statusElement.textContent = 'Supabase is not configured. Please enter your credentials.';
            }
        })
        .catch(error => {
            console.error('Error checking Supabase status:', error);
            statusElement.className = 'alert alert-danger';
            statusElement.textContent = 'Error checking Supabase status. Please try again.';
        });
}

/**
 * Validate Supabase connection
 */
function validateSupabaseConnection() {
    // Get the input values
    const url = document.getElementById('supabase-url').value.trim();
    const key = document.getElementById('supabase-key').value.trim();
    
    // Validate inputs
    if (!url || !key) {
        alert('Please enter both Supabase URL and API Key');
        return;
    }
    
    // Get the status element
    const statusElement = document.getElementById('supabase-status');
    if (!statusElement) {
        return;
    }
    
    // Show validating status
    statusElement.className = 'alert alert-info';
    statusElement.textContent = 'Validating Supabase connection...';
    
    // Validate connection
    fetch(`${SETTINGS_CONFIG.apiBaseUrl}/settings/supabase/validate`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            url: url,
            key: key
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.valid) {
            statusElement.className = 'alert alert-success';
            statusElement.textContent = 'Validation successful! You can now save these settings.';
        } else {
            statusElement.className = 'alert alert-danger';
            statusElement.textContent = `Validation failed: ${data.message}`;
        }
    })
    .catch(error => {
        console.error('Error validating Supabase connection:', error);
        statusElement.className = 'alert alert-danger';
        statusElement.textContent = 'Error validating connection. Please try again.';
    });
}

/**
 * Save settings
 */
function saveSettings() {
    // Get the input values
    const url = document.getElementById('supabase-url').value.trim();
    const key = document.getElementById('supabase-key').value.trim();
    
    // Validate inputs
    if (!url || !key) {
        alert('Please enter both Supabase URL and API Key');
        return;
    }
    
    // Get the status element
    const statusElement = document.getElementById('supabase-status');
    if (!statusElement) {
        return;
    }
    
    // Show saving status
    statusElement.className = 'alert alert-info';
    statusElement.textContent = 'Saving settings...';
    
    // Save settings
    fetch(`${SETTINGS_CONFIG.apiBaseUrl}/settings/supabase/save`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            url: url,
            key: key
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            statusElement.className = 'alert alert-success';
            statusElement.textContent = 'Settings saved successfully!';
            
            // Close the dialog after a delay
            setTimeout(() => {
                const dialog = document.getElementById('settings-dialog');
                if (dialog) {
                    const modal = bootstrap.Modal.getInstance(dialog);
                    if (modal) {
                        modal.hide();
                    }
                }
                
                // Refresh the page to apply settings
                window.location.reload();
            }, 1500);
        } else {
            statusElement.className = 'alert alert-danger';
            statusElement.textContent = `Failed to save settings: ${data.message}`;
        }
    })
    .catch(error => {
        console.error('Error saving settings:', error);
        statusElement.className = 'alert alert-danger';
        statusElement.textContent = 'Error saving settings. Please try again.';
    });
}

// Export functions for use in other scripts
window.showSettingsDialog = showSettingsDialog;
window.validateSupabaseConnection = validateSupabaseConnection;
window.saveSettings = saveSettings;
