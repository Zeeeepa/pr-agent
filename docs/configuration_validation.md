# Configuration Validation

This document describes the configuration validation system for the PR Review Automator.

## Overview

The PR Review Automator includes a comprehensive configuration validation system that ensures all settings are valid before they are applied. This helps prevent configuration errors that could cause the application to malfunction.

## Validation Categories

The configuration validation system validates the following categories of settings:

### 1. Notification Settings

Validates settings related to notifications, including:

- `ENABLE_NOTIFICATIONS`: Boolean flag to enable/disable notifications
- `NOTIFICATION_WEBHOOK_URL`: URL for sending webhook notifications (must be a valid URL)

### 2. Comment Settings

Validates settings related to PR comments, including:

- `COMMENT_TEMPLATE`: Template for PR comments (must include required placeholders)
- `COMMENT_STYLE`: Style of PR comments (must be one of: 'detailed', 'concise', 'minimal')
- `MAX_COMMENT_LENGTH`: Maximum length of PR comments (must be a reasonable integer)

### 3. Environment Configuration

Validates environment-specific settings, including:

- `ENVIRONMENT`: Application environment (must be one of: 'development', 'testing', 'production')
- `LOG_LEVEL`: Logging level (must be one of: 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
- `LOG_FORMAT`: Logging format (must be one of: 'CONSOLE', 'JSON')
- `UI_PORT`: Port for the UI server (must be a valid port number)
- `API_PORT`: Port for the API server (must be a valid port number)
- `CORS_ORIGINS`: CORS origins (in production, must not include wildcard '*')
- `WEBHOOK_SECRET`: Secret for webhook validation (required in production)

### 4. Settings Persistence

Validates settings related to settings persistence, including:

- `SETTINGS_FILE_PATH`: Path to the settings file (must be writable)

### 5. UI Components

Validates settings related to UI components, including:

- `UI_THEME`: UI theme (must be one of: 'light', 'dark', 'system')
- `UI_LANGUAGE`: UI language (must be one of: 'en', 'es', 'fr', 'de', 'ja', 'zh')
- `UI_CUSTOM_CSS`: Custom CSS for the UI (must be a valid CSS object)

### 6. Other Settings

The system also validates other settings, including:

- `SUPABASE_URL` and `SUPABASE_ANON_KEY`: Supabase connection settings
- `GITHUB_TOKEN`: GitHub API token

## API Endpoints

The configuration validation system exposes the following API endpoints:

### Validate Settings

```
POST /api/v1/settings/validate
```

Validates the provided settings without saving them. Returns detailed validation results for each category.

Example response:

```json
{
  "valid": true,
  "message": "Settings validated successfully",
  "validation_results": {
    "notification_settings": {
      "valid": true,
      "error": null
    },
    "comment_settings": {
      "valid": true,
      "error": null
    },
    "environment_config": {
      "valid": true,
      "error": null
    },
    "settings_persistence": {
      "valid": true,
      "error": null
    },
    "ui_components": {
      "valid": true,
      "error": null
    },
    "other_settings": {
      "valid": true,
      "error": null
    }
  }
}
```

### Save Settings

```
POST /api/v1/settings
```

Validates and saves the provided settings. Returns an error if any settings are invalid.

Example response:

```json
{
  "status": "success",
  "message": "Settings saved successfully"
}
```

### Get Settings

```
GET /api/v1/settings
```

Gets the current settings. Sensitive values are masked.

Example response:

```json
{
  "ENABLE_NOTIFICATIONS": false,
  "UI_THEME": "dark",
  "UI_LANGUAGE": "en",
  "ENVIRONMENT": "development",
  "LOG_LEVEL": "INFO",
  "LOG_FORMAT": "CONSOLE",
  "UI_PORT": 8000,
  "API_PORT": 8001,
  "GITHUB_TOKEN": "********"
}
```

## Implementation

The configuration validation system is implemented in the following files:

- `pr_agent/execserver/services/config_validation_service.py`: Implements the validation logic for each category of settings
- `pr_agent/execserver/services/settings_service.py`: Manages loading, saving, and validating settings
- `pr_agent/execserver/api/routes.py`: Exposes API endpoints for validating and saving settings

## Testing

The configuration validation system includes comprehensive tests in:

- `tests/test_config_validation.py`: Tests for the configuration validation service

## Best Practices

When adding new configuration options, follow these best practices:

1. Add validation for the new option in the appropriate category in `config_validation_service.py`
2. Add tests for the new validation in `test_config_validation.py`
3. Document the new option in this document
4. Provide sensible defaults in `settings.json`

