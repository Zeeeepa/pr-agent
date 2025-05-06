# PR Static Analysis System - Troubleshooting Guide

This guide will help you troubleshoot common issues with the PR Static Analysis System.

## Common Issues

### Installation Issues

#### Package Not Found

**Issue**: `pip install pr-static-analysis` fails with "Package not found" error.

**Solution**:
- Verify that you're using the correct package name
- Check your internet connection
- Try using a different PyPI mirror: `pip install --index-url https://pypi.org/simple pr-static-analysis`

#### Dependency Conflicts

**Issue**: Installation fails due to dependency conflicts.

**Solution**:
- Create a virtual environment to isolate dependencies:
  ```bash
  python -m venv pr_analysis_env
  source pr_analysis_env/bin/activate  # On Windows: pr_analysis_env\Scripts\activate
  pip install pr-static-analysis
  ```
- Try installing with the `--no-dependencies` flag and then install dependencies manually:
  ```bash
  pip install --no-dependencies pr-static-analysis
  pip install -r requirements.txt
  ```

### Configuration Issues

#### GitHub Token Not Working

**Issue**: The system fails to authenticate with GitHub.

**Solution**:
- Verify that your token has the required permissions
- Check that the token is correctly set in the configuration file or environment variable
- Ensure the token is still valid (not expired or revoked)
- Try generating a new token

#### Webhook Not Receiving Events

**Issue**: The webhook endpoint is not receiving events from GitHub.

**Solution**:
- Verify that the webhook is correctly set up in GitHub
- Check that the webhook URL is publicly accessible
- Ensure the webhook secret matches between GitHub and your configuration
- Check GitHub's webhook delivery logs for errors
- Verify your server's firewall settings

### Analysis Issues

#### No Issues Found When There Should Be

**Issue**: The system reports no issues, but you know there are problems in the code.

**Solution**:
- Check that the appropriate rules are enabled in your configuration
- Verify that the severity threshold is not set too high
- Ensure the system is analyzing the correct files
- Check if the issues are in files that are excluded from analysis

#### False Positives

**Issue**: The system reports issues that are not actually problems.

**Solution**:
- Adjust the rule configuration to reduce false positives
- Add specific exclusions for the false positives
- Consider disabling problematic rules if they generate too many false positives

#### Analysis Takes Too Long

**Issue**: The analysis process takes too long to complete.

**Solution**:
- Limit the scope of analysis to specific files or directories
- Disable resource-intensive rules
- Increase the severity threshold to focus on more important issues
- Consider running the analysis asynchronously

### Reporting Issues

#### Markdown Formatting Issues

**Issue**: The Markdown report is not formatted correctly.

**Solution**:
- Check for special characters that might be interfering with Markdown syntax
- Verify that the report template is correct
- Try using a different output format (HTML or JSON)

#### HTML Report Not Rendering

**Issue**: The HTML report is not rendering correctly in the browser.

**Solution**:
- Check for HTML syntax errors in the report
- Verify that all required CSS and JavaScript files are included
- Try viewing the report in a different browser

#### GitHub Comment Too Large

**Issue**: The GitHub comment is too large and gets truncated.

**Solution**:
- Reduce the verbosity of the report
- Split the report into multiple comments
- Use a GitHub check run instead of a comment
- Link to an external report instead of posting the full report

## Debugging

### Enabling Verbose Output

To get more detailed information about what the system is doing, enable verbose output:

```bash
pr-analysis analyze --repo "owner/repo" --pr 123 --verbose
```

### Checking Logs

The system logs information to the following locations:

- **Linux/macOS**: `~/.pr_analysis/logs/`
- **Windows**: `C:\Users\<username>\.pr_analysis\logs\`

Check these logs for more detailed error information.

### Using the Debug Mode

For even more detailed debugging information, you can run the system in debug mode:

```bash
PR_ANALYSIS_DEBUG=1 pr-analysis analyze --repo "owner/repo" --pr 123
```

## Getting Help

If you're still having issues after trying the solutions in this guide, you can:

- Check the [GitHub Issues](https://github.com/your-organization/pr-static-analysis/issues) for similar problems
- Open a new issue with details about your problem
- Contact the maintainers for support

## Common Error Messages

### "Authentication failed"

**Cause**: The GitHub token is invalid or does not have the required permissions.

**Solution**: Generate a new token with the correct permissions and update your configuration.

### "Repository not found"

**Cause**: The specified repository does not exist or you don't have access to it.

**Solution**: Verify the repository name and ensure you have access to it.

### "Pull request not found"

**Cause**: The specified pull request does not exist or you don't have access to it.

**Solution**: Verify the pull request number and ensure you have access to it.

### "Rule not found"

**Cause**: A rule specified in the configuration does not exist.

**Solution**: Check the rule ID and ensure it's correctly specified in the configuration.

### "Failed to parse file"

**Cause**: The system could not parse a file due to syntax errors or encoding issues.

**Solution**: Check the file for syntax errors and ensure it uses a supported encoding (UTF-8 is recommended).

