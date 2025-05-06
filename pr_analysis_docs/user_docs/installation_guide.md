# PR Static Analysis System - Installation Guide

This guide will walk you through the process of installing and configuring the PR Static Analysis System.

## Prerequisites

Before installing the PR Static Analysis System, ensure you have the following:

- Python 3.8 or higher
- pip (Python package installer)
- Git
- A GitHub account with access to the repositories you want to analyze
- A GitHub personal access token with the following permissions:
  - `repo` (Full control of private repositories)
  - `read:org` (Read organization information)
  - `read:user` (Read user information)

## Installation

### 1. Install from PyPI

The simplest way to install the PR Static Analysis System is via pip:

```bash
pip install pr-static-analysis
```

### 2. Install from Source

Alternatively, you can install from source:

```bash
git clone https://github.com/your-organization/pr-static-analysis.git
cd pr-static-analysis
pip install -e .
```

## Configuration

### 1. Create a Configuration File

Create a configuration file named `pr_analysis_config.yaml` in your project directory:

```yaml
# GitHub Configuration
github:
  token: "your-github-token"  # Your GitHub personal access token
  webhook_secret: "your-webhook-secret"  # Secret for GitHub webhook (optional)

# Analysis Configuration
analysis:
  rules:
    - "CI001"  # Syntax Error Check
    - "CI002"  # Undefined Reference Check
    - "PV001"  # Parameter Type Mismatch Check
    - "PV002"  # Missing Parameter Check
    - "IV001"  # Feature Completeness Check
    - "IV002"  # Test Coverage Check
  severity_threshold: "warning"  # Minimum severity to report (error, warning, info)

# Reporting Configuration
reporting:
  format: "markdown"  # Output format (markdown, html, json)
  comment_on_pr: true  # Whether to post results as a comment on the PR
  create_check_run: true  # Whether to create a GitHub check run
```

### 2. Set Environment Variables

You can also configure the system using environment variables:

```bash
export PR_ANALYSIS_GITHUB_TOKEN="your-github-token"
export PR_ANALYSIS_WEBHOOK_SECRET="your-webhook-secret"
export PR_ANALYSIS_RULES="CI001,CI002,PV001,PV002,IV001,IV002"
export PR_ANALYSIS_SEVERITY_THRESHOLD="warning"
export PR_ANALYSIS_REPORT_FORMAT="markdown"
export PR_ANALYSIS_COMMENT_ON_PR="true"
export PR_ANALYSIS_CREATE_CHECK_RUN="true"
```

## GitHub Integration

### 1. Set Up a GitHub Webhook

To automatically analyze PRs when they are created or updated, you need to set up a GitHub webhook:

1. Go to your repository on GitHub
2. Click on "Settings" > "Webhooks" > "Add webhook"
3. Set the Payload URL to your webhook endpoint (e.g., `https://your-server.com/webhook`)
4. Set the Content type to `application/json`
5. Set the Secret to your webhook secret
6. Select "Let me select individual events" and check "Pull requests"
7. Click "Add webhook"

### 2. Set Up a GitHub App (Optional)

For more advanced integration, you can create a GitHub App:

1. Go to your GitHub account settings
2. Click on "Developer settings" > "GitHub Apps" > "New GitHub App"
3. Fill in the required information
4. Set the Webhook URL to your webhook endpoint
5. Set the Webhook secret to your webhook secret
6. Set the required permissions:
   - Repository permissions:
     - Checks: Read & write
     - Contents: Read
     - Pull requests: Read & write
   - Organization permissions:
     - Members: Read
7. Subscribe to events:
   - Pull request
   - Push
8. Click "Create GitHub App"
9. Generate a private key for your app
10. Install the app on your repositories

## Verification

To verify that the installation was successful, run the following command:

```bash
pr-analysis --version
```

You should see the version number of the PR Static Analysis System.

## Next Steps

Now that you have installed and configured the PR Static Analysis System, you can:

- [Learn how to use the system](usage_guide.md)
- [Customize the system](customization_guide.md)
- [Troubleshoot common issues](troubleshooting_guide.md)

