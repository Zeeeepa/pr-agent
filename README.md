# PR Static Analysis System

A comprehensive system for analyzing pull requests to detect errors, issues, wrongly implemented features, and parameter problems.

## Overview

The PR Static Analysis System is designed to analyze pull requests against the codebase to identify potential issues. It provides clear feedback on whether a PR provides a valid and error-free implementation.

Key features:

- **Code Integrity Analysis**: Detect syntax errors, undefined references, and other code integrity issues
- **Parameter Validation**: Identify parameter type mismatches, missing parameters, and incorrect parameter usage
- **Implementation Validation**: Check for feature completeness, test coverage, and other implementation issues
- **GitHub Integration**: Automatically analyze PRs when they are created or updated
- **Customizable Rules**: Easily extend the system with custom analysis rules
- **Comprehensive Reporting**: Generate detailed reports in various formats (Markdown, HTML, JSON)

## Installation

```bash
pip install pr-static-analysis
```

For detailed installation instructions, see the [Installation Guide](pr_analysis_docs/user_docs/installation_guide.md).

## Usage

### Command Line Interface

```bash
# Analyze a pull request
pr-analysis analyze --repo "owner/repo" --pr 123

# Start the webhook server
pr-analysis server --host 0.0.0.0 --port 8000
```

For detailed usage instructions, see the [Usage Guide](pr_analysis_docs/user_docs/usage_guide.md).

## Documentation

### User Documentation

- [Installation Guide](pr_analysis_docs/user_docs/installation_guide.md): How to install and configure the system
- [Usage Guide](pr_analysis_docs/user_docs/usage_guide.md): How to use the system to analyze PRs
- [Troubleshooting Guide](pr_analysis_docs/user_docs/troubleshooting_guide.md): Solutions to common issues

### Developer Documentation

- [Architecture Overview](pr_analysis_docs/dev_docs/architecture_overview.md): System architecture, components, and data flow
- [Extension Guide](pr_analysis_docs/dev_docs/extension_guide.md): How to extend the system with custom rules and formatters
- [API Reference](pr_analysis_docs/api_docs/index.md): Detailed API documentation

## Testing

The PR Static Analysis System includes comprehensive tests:

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test the system end-to-end
- **Performance Tests**: Test the system with large and complex PRs

To run the tests:

```bash
# Run unit tests
pytest pr_analysis_tests/unit_tests

# Run integration tests
pytest pr_analysis_tests/integration_tests

# Run performance tests
pytest pr_analysis_tests/integration_tests/test_performance.py
```

## Contributing

Contributions are welcome! Please see the [Contributing Guide](CONTRIBUTING.md) for more information.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

