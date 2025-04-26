# PR-Agent Upgrade Instructions

This document provides instructions for upgrading PR-Agent to fix compatibility issues with newer dependency versions.

## Issue

The PR-Agent application may encounter errors when running with newer versions of dependencies, particularly:

1. `ImportError: cannot import name 'ENABLE_NOTIFICATIONS' from 'pr_agent.execserver.config'`
2. Pydantic v2 compatibility issues (warnings about schema_extra renamed to json_schema_extra)
3. FastAPI version compatibility issues
4. PyGithub version compatibility issues

## Solution

### Option 1: Use Compatible Dependencies

The simplest solution is to install the compatible versions of dependencies:

```bash
# Create a new virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install compatible dependencies
pip install -r requirements-compatible.txt
```

### Option 2: Use the Fixed Code

If you want to use newer versions of dependencies, you can use the fixed code in this PR:

1. Update `workflow_service.py` to use `get_enable_notifications()` instead of importing `ENABLE_NOTIFICATIONS` directly
2. Make sure your code is compatible with Pydantic v2 if you're using it

## Running the Application

After installing the dependencies, you can run the application:

```bash
# Run the execserver
cd pr_agent/execserver
python app.py
```

## Troubleshooting

If you encounter issues with Python-dotenv parsing:

1. Check your `.env` file format
2. Make sure there are no spaces around the equal sign
3. Make sure there are no quotes around values unless they are part of the value

Example of a correct `.env` file:

```
GITHUB_TOKEN=your_token_here
ENABLE_NOTIFICATIONS=False
```

## Additional Notes

- The PR-Agent application is designed to work with specific versions of dependencies
- Using newer versions may cause compatibility issues
- If you need to use newer versions, you may need to update more code than just the changes in this PR
