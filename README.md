<div align="center">

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://www.qodo.ai/wp-content/uploads/2025/02/PR-Agent-Purple-2.png">
  <source media="(prefers-color-scheme: light)" srcset="https://www.qodo.ai/wp-content/uploads/2025/02/PR-Agent-Purple-2.png">
  <img src="https://codium.ai/images/pr_agent/logo-light.png" alt="logo" width="330">

</picture>
<br/>

[Installation Guide](https://qodo-merge-docs.qodo.ai/installation/) |
[Usage Guide](https://qodo-merge-docs.qodo.ai/usage-guide/) |
[Tools Guide](https://qodo-merge-docs.qodo.ai/tools/) |
[Qodo Merge](https://qodo-merge-docs.qodo.ai/overview/pr_agent_pro/) 💎

PR-Agent aims to help efficiently review and handle pull requests, by providing AI feedback and suggestions
</div>

[![Static Badge](https://img.shields.io/badge/Chrome-Extension-violet)](https://chromewebstore.google.com/detail/qodo-merge-ai-powered-cod/ephlnjeghhogofkifjloamocljapahnl)
[![Static Badge](https://img.shields.io/badge/Pro-App-blue)](https://github.com/apps/qodo-merge-pro/)
[![Static Badge](https://img.shields.io/badge/OpenSource-App-red)](https://github.com/apps/qodo-merge-pro-for-open-source/)
[![Discord](https://badgen.net/badge/icon/discord?icon=discord&label&color=purple)](https://discord.com/invite/SgSxuQ65GF)
<a href="https://github.com/Codium-ai/pr-agent/commits/main">
<img alt="GitHub" src="https://img.shields.io/github/last-commit/Codium-ai/pr-agent/main?style=for-the-badge" height="20">
</a>
</div>

[//]: # (### [Documentation]&#40;https://qodo-merge-docs.qodo.ai/&#41;)

[//]: # ()
[//]: # (- See the [Installation Guide]&#40;https://qodo-merge-docs.qodo.ai/installation/&#41; for instructions on installing PR-Agent on different platforms.)

[//]: # ()
[//]: # (- See the [Usage Guide]&#40;https://qodo-merge-docs.qodo.ai/usage-guide/&#41; for instructions on running PR-Agent tools via different interfaces, such as CLI, PR Comments, or by automatically triggering them when a new PR is opened.)

[//]: # ()
[//]: # (- See the [Tools Guide]&#40;https://qodo-merge-docs.qodo.ai/tools/&#41; for a detailed description of the different tools, and the available configurations for each tool.)

## Table of Contents

- [News and Updates](#news-and-updates)
- [Overview](#overview)
- [Example results](#example-results)
- [Try it now](#try-it-now)
- [Qodo Merge](https://qodo-merge-docs.qodo.ai/overview/pr_agent_pro/)
- [How it works](#how-it-works)
- [Why use PR-Agent?](#why-use-pr-agent)

## News and Updates

## Apr 16, 2025

New tool for Qodo Merge 💎 - `/scan_repo_discussions`.

<img width="635" alt="image" src="https://codium.ai/images/pr_agent/scan_repo_discussions_2.png" />

Read more about it [here](https://qodo-merge-docs.qodo.ai/tools/scan_repo_discussions/).

## Apr 14, 2025

GPT-4.1 is out. And its quite good on coding tasks...

https://openai.com/index/gpt-4-1/

<img width="512" alt="image" src="https://github.com/user-attachments/assets/a8f4c648-a058-4bdc-9825-2a4bb71a23e5" />

## March 28, 2025

A new version, v0.28, was released. See release notes [here](https://github.com/qodo-ai/pr-agent/releases/tag/v0.28).

This version includes a new tool, [Help Docs](https://qodo-merge-docs.qodo.ai/tools/help_docs/), which can answer free-text questions based on a documentation folder.

`/help_docs` is now being used to provide immediate automatic feedback to any user who [opens an issue](https://github.com/qodo-ai/pr-agent/issues/1608#issue-2897328825) on PR-Agent's open-source project

### Feb 28, 2025

A new version, v0.27, was released. See release notes [here](https://github.com/qodo-ai/pr-agent/releases/tag/v0.27).

## Overview

<div style="text-align:left;">

Supported commands per platform:

|       |                                                                                                         | GitHub | GitLab | Bitbucket | Azure DevOps |
| ----- | ------------------------------------------------------------------------------------------------------- |:------:|:------:|:---------:|:------------:|
| TOOLS | [Review](https://qodo-merge-docs.qodo.ai/tools/review/)                                                 |   ✅   |   ✅   |    ✅     |      ✅      |
|       | [Describe](https://qodo-merge-docs.qodo.ai/tools/describe/)                                             |   ✅   |   ✅   |    ✅     |      ✅      |
|       | [Improve](https://qodo-merge-docs.qodo.ai/tools/improve/)                                               |   ✅   |   ✅   |    ✅     |      ✅      |
|       | [Ask](https://qodo-merge-docs.qodo.ai/tools/ask/)                                                       |   ✅   |   ✅   |    ✅     |      ✅      |
|       | ⮑ [Ask on code lines](https://qodo-merge-docs.qodo.ai/tools/ask/#ask-lines)                             |   ✅   |   ✅   |           |              |
|       | [Update CHANGELOG](https://qodo-merge-docs.qodo.ai/tools/update_changelog/)                             |   ✅   |   ✅   |    ✅     |      ✅      |
|       | [Help Docs](https://qodo-merge-docs.qodo.ai/tools/help_docs/?h=auto#auto-approval)                      |   ✅   |   ✅   |    ✅     |              |
|       | [Ticket Context](https://qodo-merge-docs.qodo.ai/core-abilities/fetching_ticket_context/) 💎            |   ✅   |   ✅   |    ✅     |              |
|       | [Utilizing Best Practices](https://qodo-merge-docs.qodo.ai/tools/improve/#best-practices) 💎            |   ✅   |   ✅   |    ✅     |              |
|       | [PR Chat](https://qodo-merge-docs.qodo.ai/chrome-extension/features/#pr-chat) 💎                        |   ✅   |        |           |              |
|       | [Suggestion Tracking](https://qodo-merge-docs.qodo.ai/tools/improve/#suggestion-tracking) 💎            |   ✅   |   ✅   |           |              |
|       | [CI Feedback](https://qodo-merge-docs.qodo.ai/tools/ci_feedback/) 💎                                    |   ���   |        |           |              |
|       | [PR Documentation](https://qodo-merge-docs.qodo.ai/tools/documentation/) 💎                             |   ✅   |   ✅   |           |              |
|       | [Custom Labels](https://qodo-merge-docs.qodo.ai/tools/custom_labels/) 💎                                |   ✅   |   ✅   |           |              |
|       | [Analyze](https://qodo-merge-docs.qodo.ai/tools/analyze/) 💎                                            |   ✅   |   ✅   |           |              |
|       | [Similar Code](https://qodo-merge-docs.qodo.ai/tools/similar_code/) 💎                                  |   ✅   |        |           |              |
|       | [Custom Prompt](https://qodo-merge-docs.qodo.ai/tools/custom_prompt/) 💎                                |   ✅   |   ✅   |    ✅     |              |
|       | [Test](https://qodo-merge-docs.qodo.ai/tools/test/) 💎                                                  |   ✅   |   ��   |           |              |
|       | [Implement](https://qodo-merge-docs.qodo.ai/tools/implement/) 💎                                        |   ✅   |   ✅   |    ✅     |              |
|       | [Scan Repo Discussions](https://qodo-merge-docs.qodo.ai/tools/scan_repo_discussions/) 💎                |   ✅   |        |           |              |
|       | [Auto-Approve](https://qodo-merge-docs.qodo.ai/tools/improve/?h=auto#auto-approval) 💎                  |   ✅   |   ✅   |    ✅     |              |
|       |                                                                                                         |        |        |           |              |
| USAGE | [CLI](https://qodo-merge-docs.qodo.ai/usage-guide/automations_and_usage/#local-repo-cli)                |   ✅   |   ✅   |    ✅     |      ✅      |
|       | [App / webhook](https://qodo-merge-docs.qodo.ai/usage-guide/automations_and_usage/#github-app)          |   ✅   |   ✅   |    ✅     |      ✅      |
|       | [Tagging bot](https://github.com/Codium-ai/pr-agent#try-it-now)                                         |   ✅   |        |           |              |
|       | [Actions](https://qodo-merge-docs.qodo.ai/installation/github/#run-as-a-github-action)                  |   ✅   |   ✅   |    ✅     |      ✅      |
|       |                                                                                                         |        |        |           |              |
| CORE  | [PR compression](https://qodo-merge-docs.qodo.ai/core-abilities/compression_strategy/)                  |   ✅   |   ✅   |    ✅     |      ✅      |
|       | Adaptive and token-aware file patch fitting                                                             |   ✅   |   ✅   |    ✅     |      ✅      |
|       | [Multiple models support](https://qodo-merge-docs.qodo.ai/usage-guide/changing_a_model/)                |   ✅   |   ✅   |    ✅     |      ✅      |
|       | [Local and global metadata](https://qodo-merge-docs.qodo.ai/core-abilities/metadata/)                   |   ✅   |   ✅   |    ✅     |      ✅      |
|       | [Dynamic context](https://qodo-merge-docs.qodo.ai/core-abilities/dynamic_context/)                      |   ✅   |   ✅   |    ✅     |      ✅      |
|       | [Self reflection](https://qodo-merge-docs.qodo.ai/core-abilities/self_reflection/)                      |   ✅   |   ✅   |    ✅     |      ✅      |
|       | [Static code analysis](https://qodo-merge-docs.qodo.ai/core-abilities/static_code_analysis/) 💎         |   ✅   |   ✅   |           |              |
|       | [Global and wiki configurations](https://qodo-merge-docs.qodo.ai/usage-guide/configuration_options/) 💎 |   ✅   |   ✅   |    ✅     |              |
|       | [PR interactive actions](https://www.qodo.ai/images/pr_agent/pr-actions.mp4) 💎                         |   ✅   |   ✅   |           |              |
|       | [Impact Evaluation](https://qodo-merge-docs.qodo.ai/core-abilities/impact_evaluation/) 💎               |   ✅   |   ✅   |           |              |

- 💎 means this feature is available only in [Qodo-Merge](https://www.qodo.ai/pricing/)

[//]: # (- Support for additional git providers is described in [here]&#40;./docs/Full_environments.md&#41;)
___

‣ **Auto Description ([`/describe`](https://qodo-merge-docs.qodo.ai/tools/describe/))**: Automatically generating PR description - title, type, summary, code walkthrough and labels.
\
‣ **Auto Review ([`/review`](https://qodo-merge-docs.qodo.ai/tools/review/))**: Adjustable feedback about the PR, possible issues, security concerns, review effort and more.
\
‣ **Code Suggestions ([`/improve`](https://qodo-merge-docs.qodo.ai/tools/improve/))**: Code suggestions for improving the PR.
\
‣ **Question Answering ([`/ask ...`](https://qodo-merge-docs.qodo.ai/tools/ask/))**: Answering free-text questions about the PR.
\
‣ **Update Changelog ([`/update_changelog`](https://qodo-merge-docs.qodo.ai/tools/update_changelog/))**: Automatically updating the CHANGELOG.md file with the PR changes.
\
‣ **Help Docs ([`/help_docs`](https://qodo-merge-docs.qodo.ai/tools/help_docs/))**: Answers a question on any repository by utilizing given documentation.
\
‣ **Add Documentation 💎  ([`/add_docs`](https://qodo-merge-docs.qodo.ai/tools/documentation/))**: Generates documentation to methods/functions/classes that changed in the PR.
\
‣ **Generate Custom Labels 💎 ([`/generate_labels`](https://qodo-merge-docs.qodo.ai/tools/custom_labels/))**: Generates custom labels for the PR, based on specific guidelines defined by the user.
\
‣ **Analyze 💎 ([`/analyze`](https://qodo-merge-docs.qodo.ai/tools/analyze/))**: Identify code components that changed in the PR, and enables to interactively generate tests, docs, and code suggestions for each component.
\
‣ **Test 💎 ([`/test`](https://qodo-merge-docs.qodo.ai/tools/test/))**: Generate tests for a selected component, based on the PR code changes.
\
‣ **Custom Prompt 💎 ([`/custom_prompt`](https://qodo-merge-docs.qodo.ai/tools/custom_prompt/))**: Automatically generates custom suggestions for improving the PR code, based on specific guidelines defined by the user.
\
‣ **Generate Tests 💎 ([`/test component_name`](https://qodo-merge-docs.qodo.ai/tools/test/))**: Generates unit tests for a selected component, based on the PR code changes.
\
‣ **CI Feedback 💎 ([`/checks ci_job`](https://qodo-merge-docs.qodo.ai/tools/ci_feedback/))**: Automatically generates feedback and analysis for a failed CI job.
\
‣ **Similar Code 💎 ([`/find_similar_component`](https://qodo-merge-docs.qodo.ai/tools/similar_code/))**: Retrieves the most similar code components from inside the organization's codebase, or from open-source code.
\
‣ **Implement 💎 ([`/implement`](https://qodo-merge-docs.qodo.ai/tools/implement/))**: Generates implementation code from review suggestions.
___

## Example results

</div>
<h4><a href="https://github.com/Codium-ai/pr-agent/pull/530">/describe</a></h4>
<div align="center">
<p float="center">
<img src="https://www.codium.ai/images/pr_agent/describe_new_short_main.png" width="512">
</p>
</div>
<hr>

<h4><a href="https://github.com/Codium-ai/pr-agent/pull/732#issuecomment-1975099151">/review</a></h4>
<div align="center">
<p float="center">
<kbd>
<img src="https://www.codium.ai/images/pr_agent/review_new_short_main.png" width="512">
</kbd>
</p>
</div>
<hr>

<h4><a href="https://github.com/Codium-ai/pr-agent/pull/732#issuecomment-1975099159">/improve</a></h4>
<div align="center">
<p float="center">
<kbd>
<img src="https://www.codium.ai/images/pr_agent/improve_new_short_main.png" width="512">
</kbd>
</p>
</div>

<div align="left">

</div>
<hr>

## Try it now

Try the Claude Sonnet powered PR-Agent instantly on _your public GitHub repository_. Just mention `@CodiumAI-Agent` and add the desired command in any PR comment. The agent will generate a response based on your command.
For example, add a comment to any pull request with the following text:

```
@CodiumAI-Agent /review
```

and the agent will respond with a review of your PR.

Note that this is a promotional bot, suitable only for initial experimentation.
It does not have 'edit' access to your repo, for example, so it cannot update the PR description or add labels (`@CodiumAI-Agent /describe` will publish PR description as a comment). In addition, the bot cannot be used on private repositories, as it does not have access to the files there.

---

## Qodo Merge 💎

[Qodo Merge](https://www.qodo.ai/pricing/) is a hosted version of PR-Agent, provided by Qodo. It is available for a monthly fee, and provides the following benefits:

1. **Fully managed** - We take care of everything for you - hosting, models, regular updates, and more. Installation is as simple as signing up and adding the Qodo Merge app to your GitHub\GitLab\BitBucket repo.
2. **Improved privacy** - No data will be stored or used to train models. Qodo Merge will employ zero data retention, and will use an OpenAI account with zero data retention.
3. **Improved support** - Qodo Merge users will receive priority support, and will be able to request new features and capabilities.
4. **Extra features** -In addition to the benefits listed above, Qodo Merge will emphasize more customization, and the usage of static code analysis, in addition to LLM logic, to improve results.
See [here](https://qodo-merge-docs.qodo.ai/overview/pr_agent_pro/) for a list of features available in Qodo Merge.

## How it works

The following diagram illustrates PR-Agent tools and their flow:

![PR-Agent Tools](https://www.qodo.ai/images/pr_agent/diagram-v0.9.png)

Check out the [PR Compression strategy](https://qodo-merge-docs.qodo.ai/core-abilities/#pr-compression-strategy) page for more details on how we convert a code diff to a manageable LLM prompt

## Why use PR-Agent?

A reasonable question that can be asked is: `"Why use PR-Agent? What makes it stand out from existing tools?"`

Here are some advantages of PR-Agent:

- We emphasize **real-life practical usage**. Each tool (review, improve, ask, ...) has a single LLM call, no more. We feel that this is critical for realistic team usage - obtaining an answer quickly (~30 seconds) and affordably.
- Our [PR Compression strategy](https://qodo-merge-docs.qodo.ai/core-abilities/#pr-compression-strategy)  is a core ability that enables to effectively tackle both short and long PRs.
- Our JSON prompting strategy enables to have **modular, customizable tools**. For example, the '/review' tool categories can be controlled via the [configuration](pr_agent/settings/configuration.toml) file. Adding additional categories is easy and accessible.
- We support **multiple git providers** (GitHub, Gitlab, Bitbucket), **multiple ways** to use the tool (CLI, GitHub Action, GitHub App, Docker, ...), and **multiple models** (GPT, Claude, Deepseek, ...)

## Data privacy

### Self-hosted PR-Agent

- If you host PR-Agent with your OpenAI API key, it is between you and OpenAI. You can read their API data privacy policy here:
https://openai.com/enterprise-privacy

### Qodo-hosted Qodo Merge 💎

- When using Qodo Merge 💎, hosted by Qodo, we will not store any of your data, nor will we use it for training. You will also benefit from an OpenAI account with zero data retention.

- For certain clients, Qodo-hosted Qodo Merge will use Qodo’s proprietary models — if this is the case, you will be notified.

- No passive collection of Code and Pull Requests’ data — Qodo Merge will be active only when you invoke it, and it will then extract and analyze only data relevant to the executed command and queried pull request.

### Qodo Merge Chrome extension

- The [Qodo Merge Chrome extension](https://chromewebstore.google.com/detail/qodo-merge-ai-powered-cod/ephlnjeghhogofkifjloamocljapahnl) serves solely to modify the visual appearance of a GitHub PR screen. It does not transmit any user's repo or pull request code. Code is only sent for processing when a user submits a GitHub comment that activates a PR-Agent tool, in accordance with the standard privacy policy of Qodo-Merge.

## Links

- Discord community: https://discord.gg/kG35uSHDBc
- Qodo site: https://www.qodo.ai/
- Blog: https://www.qodo.ai/blog/
- Troubleshooting: https://www.qodo.ai/blog/technical-faq-and-troubleshooting/
- Support: support@qodo.ai

# Event Server Executor for PR-Agent

A powerful extension for PR-Agent that captures GitHub events, stores them in a database, and executes custom code based on configured triggers.

## Overview

The Event Server Executor extension enhances PR-Agent with the following capabilities:

1. **Event Capture and Storage**: Automatically captures all GitHub webhook events and stores them in a database for later analysis and processing.

2. **Trigger Configuration**: Define custom triggers that execute code when specific GitHub events occur (PR creation, comments, pushes, etc.).

3. **Code Execution Engine**: Execute custom Python code, GitHub Actions, or PR-Agent commands in response to GitHub events.

4. **Notification System**: Receive Windows notifications when actions are triggered and completed.

## Features

- **Event Database**: Store all GitHub events with metadata for analysis and processing
- **Project-Based Organization**: Categorize events by GitHub repository
- **Flexible Trigger System**: Configure triggers based on event type, repository, and other criteria
- **Multiple Execution Options**: Run Python code, GitHub Actions, or PR-Agent commands
- **Web Dashboard**: Manage triggers and view event history through a web interface
- **Windows Notifications**: Receive desktop notifications for important events

## Installation

### Prerequisites

- Python 3.8+
- PR-Agent installed
- GitHub account with webhook access

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Zeeeepa/pr-agent.git
   cd pr-agent
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   ```bash
   # Create a .env file with the following variables
   GITHUB_TOKEN=your_github_token
   SUPABASE_URL=your_supabase_url  # Optional, for production use
   SUPABASE_ANON_KEY=your_supabase_anon_key  # Optional, for production use
   ```

4. Start the server:
   ```bash
   python -m pr_agent.event_server.run
   ```

## Usage

### Setting Up Webhooks

1. Go to your GitHub repository settings
2. Navigate to Webhooks
3. Add a new webhook with the URL of your Event Server
4. Select the events you want to capture
5. Save the webhook

### Configuring Triggers

1. Open the web dashboard at `http://localhost:3000/dashboard`
2. Click "Add Trigger"
3. Select the repository, event type, and action
4. Choose the execution type (Python code, GitHub Action, PR-Agent command)
5. Configure parameters and notifications
6. Save the trigger

### Example Trigger Configuration

```json
{
  "name": "Auto Review PR",
  "repository": "Zeeeepa/pr-agent",
  "event_type": "pull_request",
  "event_action": "opened",
  "execution_type": "pr_agent_command",
  "command": "/review",
  "notifications": {
    "windows": true,
    "email": false
  }
}
```

## Development

### Project Structure

```
pr_agent/
├── event_server/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── events.py
│   │   ├── triggers.py
│   │   └── executions.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── sqlite.py
│   │   └── supabase.py
│   ├── execution/
│   │   ├── __init__.py
│   │   ├── code_executor.py
│   │   ├── action_executor.py
│   │   └── command_executor.py
│   ├── notification/
│   │   ├── __init__.py
│   │   └── windows.py
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── dashboard.py
│   │   └── static/
│   └── run.py
```

### Adding New Event Types

To add support for new GitHub event types:

1. Update the event handler in `pr_agent/event_server/api/events.py`
2. Add the event type to the trigger configuration options
3. Implement any specific processing logic for the new event type

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Built on top of [PR-Agent](https://github.com/Zeeeepa/pr-agent)
- Uses [FastAPI](https://fastapi.tiangolo.com/) for the web server
- Uses [SQLite](https://www.sqlite.org/index.html) for local development
- Uses [Supabase](https://supabase.io/) for production database
