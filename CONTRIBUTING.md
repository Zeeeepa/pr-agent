# Contributing to PR Static Analysis System

Thank you for your interest in contributing to the PR Static Analysis System! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md) to foster an inclusive and respectful community.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git

### Setting Up the Development Environment

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/pr-static-analysis.git
   cd pr-static-analysis
   ```
3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install the package in development mode:
   ```bash
   pip install -e .
   ```
5. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

## Development Workflow

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes
3. Run the tests to ensure your changes don't break existing functionality:
   ```bash
   pytest
   ```
4. Run the linter to ensure your code follows the project's style guidelines:
   ```bash
   flake8
   ```
5. Commit your changes:
   ```bash
   git commit -m "Add your meaningful commit message here"
   ```
6. Push your branch to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
7. Create a pull request from your fork to the main repository

## Pull Request Guidelines

- Follow the [conventional commits](https://www.conventionalcommits.org/) specification for commit messages
- Include tests for new features or bug fixes
- Update documentation as needed
- Ensure all tests pass and there are no linting errors
- Keep pull requests focused on a single change
- Link to relevant issues or discussions

## Testing

The project uses pytest for testing. To run the tests:

```bash
# Run all tests
pytest

# Run unit tests only
pytest pr_analysis_tests/unit_tests

# Run integration tests only
pytest pr_analysis_tests/integration_tests

# Run performance tests only
pytest pr_analysis_tests/integration_tests/test_performance.py

# Run tests with coverage
pytest --cov=pr_analysis
```

## Documentation

The project uses Markdown for documentation. When adding or updating features, please update the relevant documentation files in the `pr_analysis_docs` directory.

## Code Style

The project follows the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide for Python code. We use flake8 for linting:

```bash
flake8
```

## Releasing

The project follows [Semantic Versioning](https://semver.org/). To release a new version:

1. Update the version number in `setup.py`
2. Update the changelog in `CHANGELOG.md`
3. Create a new release on GitHub with release notes
4. The CI/CD pipeline will automatically publish the new version to PyPI

## Getting Help

If you need help with contributing to the project, you can:

- Open an issue on GitHub
- Join our community chat
- Contact the maintainers directly

## Thank You!

Thank you for contributing to the PR Static Analysis System! Your time and effort help make this project better for everyone.

