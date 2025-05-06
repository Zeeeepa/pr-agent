# PR Review Tools Tests

This directory contains unit tests for the PR review tools in the PR Agent.

## Tools Tested

1. **PR Reviewer** (`test_pr_reviewer.py`)
   - Tests the automated review generation with `PRReviewer`
   - Tests different review modes (standard, answer, auto)
   - Tests integration with different AI models

2. **Code Suggestions** (`test_pr_code_suggestions.py`)
   - Tests code improvement suggestions with `PRCodeSuggestions`
   - Tests proper formatting and applicability of suggestions
   - Tests integration with different AI models

3. **Question Answering** (`test_pr_questions.py` and `test_pr_line_questions.py`)
   - Tests PR question answering with `PRQuestions`
   - Tests line-specific questions with `PR_LineQuestions`
   - Tests accurate and relevant responses

4. **PR Description** (`test_pr_description.py`)
   - Tests automated PR description generation with `PRDescription`
   - Tests proper extraction of PR purpose and changes
   - Tests generation of appropriate labels

5. **Changelog Updates** (`test_pr_update_changelog.py`)
   - Tests automated changelog updates with `PRUpdateChangelog`
   - Tests proper formatting and categorization of changes
   - Tests integration with existing changelog files

## AI Handler Tests

The `tests/unittest/algo/test_ai_handlers.py` file tests the AI handler implementations:
- `LiteLLMAIHandler`
- `OpenAIAIHandler`
- `LangchainAIHandler`

## Token Handler Tests

The `tests/unittest/algo/test_token_handler.py` file tests the token management functionality:
- Token counting
- Token limit enforcement
- Token encoder initialization

## Running the Tests

To run all the tests:

```bash
python -m unittest discover tests/unittest
```

To run a specific test file:

```bash
python -m unittest tests/unittest/tools/test_pr_reviewer.py
```

To run a specific test case:

```bash
python -m unittest tests.unittest.tools.test_pr_reviewer.TestPRReviewer.test_initialization
```

## Test Coverage

These tests cover:
- Initialization of each tool
- Core functionality of each tool
- Integration with different AI models
- Proper handling of different modes and options
- Token management
- Formatting of outputs

