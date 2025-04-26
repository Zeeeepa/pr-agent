# PR-Agent Upgrade Guide

This guide provides instructions for resolving dependency issues when running the PR-Agent execserver.

## Common Issues

### Import Error: ENABLE_NOTIFICATIONS

If you encounter the following error:
```
ImportError: cannot import name 'ENABLE_NOTIFICATIONS' from 'pr_agent.execserver.config'
```

This is because the `workflow_service.py` file is using the function `get_enable_notifications()` from the config module, not a direct variable.

### Pydantic Version Compatibility

If you see warnings about Pydantic configuration keys changing in V2:
```
UserWarning: Valid config keys have been renamed to 'json_schema_extra'
```

This is because the project was designed to work with Pydantic V1, but you're using Pydantic V2.

### GitHub App Configuration

If you see errors about missing GitHub configuration:
```
ConfigurationError: Required configuration 'GITHUB_APP_ID' not found
```

You need to set up the required GitHub App configuration in your environment.

## Solution

### Option 1: Use Compatible Dependencies

1. Create a new virtual environment:
   ```
   python -m venv pr_agent_env
   ```

2. Activate the virtual environment:
   - Windows: `pr_agent_env\Scripts\activate`
   - macOS/Linux: `source pr_agent_env/bin/activate`

3. Install dependencies from the compatible requirements file:
   ```
   pip install -r requirements-compatible.txt
   ```

4. Run the application:
   ```
   cd pr_agent/execserver
   python app.py
   ```

### Option 2: Set Up GitHub Configuration

If you want to use the GitHub integration, you need to set up the required environment variables:

1. Create a `.env` file in the project root with the following content:
   ```
   GITHUB_APP_ID=your_app_id
   GITHUB_APP_PRIVATE_KEY=your_private_key
   GITHUB_APP_INSTALLATION_ID=your_installation_id
   ```

   Or set these environment variables directly in your system.

2. If you don't need GitHub integration, you can modify the `github_service.py` file to make these configurations optional.

## Troubleshooting

If you continue to experience issues:

1. Make sure you're using a clean virtual environment
2. Check that all dependencies are installed correctly
3. Verify that your Python version is compatible (Python 3.8+ recommended)
4. Look for any error messages in the console output

For more information, refer to the [PR-Agent documentation](https://github.com/Codium-ai/pr-agent).
