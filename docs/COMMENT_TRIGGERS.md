# Comment Trigger Options

PR-Agent provides configurable triggers for when automated comments should be posted to PRs, allowing users to control the frequency and conditions of automated feedback.

## Configuration Options

The comment trigger options can be configured in your `settings.toml` file under the `pr_reviewer` section:

```toml
[pr_reviewer]
# ... other settings ...
comment_trigger = "ALWAYS" # Options: "ALWAYS", "ONCE_PER_PR", "AFTER_CHANGES"
# ... other settings ...
```

### Available Trigger Options

1. **ALWAYS** (default): Post comments on every PR review request, regardless of previous comments.
2. **ONCE_PER_PR**: Post a comment only once per PR, even if the PR is updated with new commits.
3. **AFTER_CHANGES**: Post a comment when the PR is first created and then only when new commits are added to the PR.

## How It Works

PR-Agent tracks comment history for each PR to implement these trigger strategies:

- When a comment is posted, PR-Agent records the PR ID and the latest commit SHA at the time of commenting.
- For subsequent review requests, PR-Agent checks the trigger configuration and comment history to determine if a new comment should be posted.

### Comment Tracking

Comment history is stored in a JSON file located at `~/.pr_agent/comment_history.json`. This ensures that comment tracking persists across application restarts.

The tracking data includes:
- Repository name
- PR ID
- Timestamp of each comment
- Commit SHA at the time of commenting

## Use Cases

1. **ALWAYS**: Use this option when you want comprehensive feedback on every review request, regardless of previous comments. This is useful for teams that want to track the evolution of a PR through multiple iterations.

2. **ONCE_PER_PR**: Use this option to reduce noise in PRs by providing feedback only once. This is useful for teams that prefer to have a single, comprehensive review comment per PR.

3. **AFTER_CHANGES**: Use this option to provide feedback when the PR is first created and then only when the PR is updated with new commits. This balances between providing timely feedback and reducing noise.

## Example Configuration

```toml
# settings.toml
[pr_reviewer]
require_score_review = false
require_tests_review = true
require_estimate_effort_to_review = true
persistent_comment = true
comment_trigger = "AFTER_CHANGES" # Only post comments on PR creation and when new commits are added
```

## Implementation Details

The comment trigger functionality is implemented through:

1. A `CommentTracker` class that manages comment history and determines when to post comments.
2. Integration with the PR reviewer tool to check the trigger configuration before posting comments.
3. A persistent storage mechanism to track comment history across application restarts.

The implementation ensures that comment triggers work consistently across different Git providers and PR workflows.

