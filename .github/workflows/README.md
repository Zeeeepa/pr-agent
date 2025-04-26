# GitHub Actions Workflows

This directory contains GitHub Actions workflows for automating testing, building, and deployment of the PR-Agent application.

## Available Workflows

### CI Pipeline (`ci.yaml`)

This workflow runs on every push to the main branch and on pull requests. It performs the following tasks:

1. **Lint**: Runs pre-commit hooks and code linting tools to ensure code quality
2. **Test**: Builds a Docker test image and runs unit tests with code coverage
3. **Build Images**: Builds Docker images for different components of the application

Trigger this workflow manually:
- Go to Actions → CI Pipeline → Run workflow

### Deploy PR-Agent (`deploy.yaml`)

This workflow is triggered when a new release is published or can be run manually. It performs the following tasks:

1. **Set Version**: Determines the version to deploy (from release tag, manual input, or latest tag)
2. **Build and Push Docker Images**: Builds and pushes Docker images for all components to Docker Hub
3. **Publish to PyPI**: Builds and publishes the Python package to PyPI

Trigger this workflow manually:
- Go to Actions → Deploy PR-Agent → Run workflow
- Optionally specify a version, or leave blank to use the latest tag

## Required Secrets

For these workflows to function properly, you need to set up the following secrets in your GitHub repository:

- `DOCKERHUB_USERNAME`: Your Docker Hub username
- `DOCKERHUB_TOKEN`: Your Docker Hub access token
- `PYPI_API_TOKEN`: Your PyPI API token for publishing packages
- `CODECOV_TOKEN`: Your Codecov token for uploading coverage reports

## Adding New Workflows

When adding new workflows, please follow these guidelines:

1. Use descriptive names for workflow files and jobs
2. Include appropriate triggers (events that start the workflow)
3. Document the workflow in this README
4. Use existing GitHub Actions where possible
5. Test workflows thoroughly before merging
