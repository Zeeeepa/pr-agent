# PR-Agent GitHub Actions Workflows

This directory contains GitHub Actions workflows for testing, building, and deploying the PR-Agent application.

## Available Workflows

### PR-Agent CI/CD Pipeline (`pr-agent-ci-cd.yaml`)

A comprehensive CI/CD pipeline that handles:

1. **Linting**: Checks code quality using ruff and pre-commit hooks
2. **Testing**: Runs unit tests and ExecServer tests with code coverage reporting
3. **Building**: Builds Docker images for GitHub App and ExecServer
4. **Deployment**: Deploys to staging and production environments

#### Workflow Triggers

- **Push to main**: Automatically runs lint, test, build, and deploy to staging
- **Pull Requests to main**: Automatically runs lint and test
- **Manual Trigger**: Can be manually triggered with an option to deploy to production

#### Environment Requirements

For the workflow to function properly, the following secrets must be configured:

- `DOCKERHUB_USERNAME`: Docker Hub username for pushing images
- `DOCKERHUB_TOKEN`: Docker Hub token for authentication
- `CODECOV_TOKEN`: Token for uploading code coverage reports to Codecov
- `KUBE_CONFIG`: Kubernetes configuration for deployment

### Build and Test (`build-and-test.yaml`)

Basic workflow that builds the Docker image and runs unit tests.

### Code Coverage (`code_coverage.yaml`)

Generates and uploads code coverage reports to Codecov.

### Documentation CI (`docs-ci.yaml`)

Validates documentation changes.

### End-to-End Tests (`e2e_tests.yaml`)

Runs end-to-end tests for GitHub, GitLab, and Bitbucket integrations.

### PR-Agent Review (`pr-agent-review.yaml`)

Uses PR-Agent to review pull requests.

### Pre-commit (`pre-commit.yml`)

Runs pre-commit hooks to ensure code quality.

## Setting Up GitHub Environments

For the deployment stages to work properly, you need to set up the following GitHub environments:

1. **staging**: For staging deployments
2. **production**: For production deployments (with required reviewers for approval)

## Adding Required Secrets

Go to your repository settings → Secrets and variables → Actions, and add the following secrets:

- `DOCKERHUB_USERNAME`: Your Docker Hub username
- `DOCKERHUB_TOKEN`: Your Docker Hub access token
- `CODECOV_TOKEN`: Your Codecov token
- `KUBE_CONFIG`: Your Kubernetes configuration file content (base64 encoded)

## Manual Workflow Dispatch

To manually trigger the workflow:

1. Go to the Actions tab in your repository
2. Select "PR-Agent CI/CD Pipeline"
3. Click "Run workflow"
4. Choose whether to deploy to production
5. Click "Run workflow" to start the process
