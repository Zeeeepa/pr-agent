# PR Static Analysis System - Usage Guide

This guide will walk you through how to use the PR Static Analysis System to analyze pull requests and interpret the results.

## Command Line Interface

The PR Static Analysis System provides a command-line interface (CLI) for analyzing pull requests.

### Analyzing a Pull Request

To analyze a pull request, use the `analyze` command:

```bash
pr-analysis analyze --repo "owner/repo" --pr 123
```

This will analyze pull request #123 in the specified repository and output the results to the console.

### Command Line Options

The CLI supports the following options:

- `--repo`, `-r`: The repository in the format "owner/repo" (required)
- `--pr`, `-p`: The pull request number (required)
- `--output`, `-o`: The output file to write the results to (optional)
- `--format`, `-f`: The output format (markdown, html, json) (default: markdown)
- `--comment`, `-c`: Whether to post the results as a comment on the PR (default: false)
- `--check`, `-k`: Whether to create a GitHub check run (default: false)
- `--config`, `-g`: Path to the configuration file (default: pr_analysis_config.yaml)
- `--verbose`, `-v`: Enable verbose output (default: false)
- `--help`, `-h`: Show help message and exit

### Examples

Analyze a pull request and output the results to a file:

```bash
pr-analysis analyze --repo "owner/repo" --pr 123 --output results.md
```

Analyze a pull request and post the results as a comment:

```bash
pr-analysis analyze --repo "owner/repo" --pr 123 --comment
```

Analyze a pull request and create a GitHub check run:

```bash
pr-analysis analyze --repo "owner/repo" --pr 123 --check
```

## Web Server

The PR Static Analysis System also provides a web server for handling GitHub webhooks.

### Starting the Web Server

To start the web server, use the `server` command:

```bash
pr-analysis server --host 0.0.0.0 --port 8000
```

This will start a web server listening on all interfaces on port 8000.

### Server Options

The server supports the following options:

- `--host`, `-h`: The host to bind to (default: 127.0.0.1)
- `--port`, `-p`: The port to listen on (default: 8000)
- `--config`, `-g`: Path to the configuration file (default: pr_analysis_config.yaml)
- `--verbose`, `-v`: Enable verbose output (default: false)
- `--help`, `-h`: Show help message and exit

### Webhook Endpoint

The web server provides a webhook endpoint at `/webhook` that accepts POST requests from GitHub. When a pull request is created or updated, GitHub will send a webhook event to this endpoint, and the system will automatically analyze the pull request.

## Interpreting Results

The PR Static Analysis System generates reports that highlight issues found in the pull request. The reports include:

### Summary

The summary section provides an overview of the analysis results:

- Number of errors
- Number of warnings
- Number of informational messages
- Total number of issues

### Issues

The issues section lists all the issues found in the pull request, grouped by severity:

- **Errors**: Critical issues that should be fixed before merging the PR
- **Warnings**: Potential issues that should be reviewed
- **Info**: Informational messages that may not require action

Each issue includes:

- Rule ID: The identifier of the rule that detected the issue
- Message: A description of the issue
- File: The file where the issue was found
- Line: The line number where the issue was found
- Column: The column number where the issue was found

### Example Report

Here's an example of a Markdown report:

```markdown
# PR Analysis Report for #123

**PR:** [Add new feature](https://github.com/owner/repo/pull/123)
**Base:** `main`
**Head:** `feature-branch`

## Summary

- **Errors:** 1
- **Warnings:** 2
- **Info:** 3
- **Total:** 6

## Issues

### :x: CI001: Syntax error in file1.py

**File:** `file1.py`
**Line:** 10
**Column:** 5

### :warning: CI002: Undefined reference to 'foo' in file2.py

**File:** `file2.py`
**Line:** 20
**Column:** 10

### :warning: PV001: Parameter type mismatch for 'bar' in file3.py

**File:** `file3.py`
**Line:** 30
**Column:** 15

### :information_source: IV001: Missing test for function 'baz' in file4.py

**File:** `file4.py`
**Line:** 40
**Column:** 1

### :information_source: IV002: Function 'qux' has low test coverage in file5.py

**File:** `file5.py`
**Line:** 50
**Column:** 1

### :information_source: IV003: Consider adding documentation for class 'Quux' in file6.py

**File:** `file6.py`
**Line:** 60
**Column:** 1
```

## GitHub Integration

When integrated with GitHub, the PR Static Analysis System can:

### Post Comments

The system can post the analysis results as a comment on the pull request:

![PR Comment Example](images/pr_comment_example.png)

### Create Check Runs

The system can create a GitHub check run with the analysis results:

![Check Run Example](images/check_run_example.png)

## Next Steps

Now that you know how to use the PR Static Analysis System, you can:

- [Customize the system](customization_guide.md) to fit your needs
- [Troubleshoot common issues](troubleshooting_guide.md) if you encounter problems
- [Extend the system](../dev_docs/extension_guide.md) with custom rules and formatters

