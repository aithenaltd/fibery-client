# Contributing to Fibery Client

First off, thank you for considering contributing to Fibery Client! It's people like you that make it a great tool for everyone.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* Use a clear and descriptive title
* Describe the exact steps which reproduce the problem
* Provide specific examples to demonstrate the steps
* Describe the behavior you observed after following the steps
* Explain which behavior you expected to see instead and why
* Include error messages and stack traces if any

### Suggesting Enhancements

If you have a suggestion for the library, we'd love to hear about it. Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* A clear and descriptive title
* A detailed description of the proposed functionality
* Explain why this enhancement would be useful
* List any alternative solutions or features you've considered

### Development Process

1. Fork the repo and create your branch from `main`
2. Install development dependencies:
   ```bash
   poetry install --with dev
   ```

3. Make your changes:
   * Write code
   * Write or update tests
   * Update documentation
   * Update type hints
   * Run static type checking with mypy
   * Run linting with ruff

4. Run the test suite:
   ```bash
   poetry run pytest
   ```

5. Run type checking:
   ```bash
   poetry run mypy src
   ```

6. Run linting:
   ```bash
   poetry run ruff check .
   ```

### Pull Request Process

1. Follow all instructions in the template
2. Update the README.md with details of changes if needed
3. Update the CHANGELOG.md following the existing format
4. The PR must pass all CI checks
5. You may merge the Pull Request once you have approval from a maintainer

## Styleguides

### Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line
* Consider starting the commit message with an applicable emoji:
    * 🎨 `:art:` when improving the format/structure of the code
    * 🐎 `:racehorse:` when improving performance
    * 📝 `:memo:` when writing docs
    * 🐛 `:bug:` when fixing a bug
    * 🔥 `:fire:` when removing code or files
    * ✅ `:white_check_mark:` when adding tests
    * 🔒 `:lock:` when dealing with security

### Python Styleguide

* Follow PEP 8
* Use type hints
* Use f-strings for string formatting
* Use meaningful variable names
* Write docstrings for all public methods
* Keep functions focused and small
* Use async/await consistently
* Handle errors appropriately
* Write unit tests for new functionality

### Documentation Styleguide

* Use Markdown for documentation
* Include code examples when relevant
* Keep line length to a reasonable limit
* Include type information in code examples
* Document exceptions and error cases
* Provide context and examples for complex features

## Testing

* Write unit tests for all new code
* Maintain or improve test coverage
* Tests should be independent and idempotent
* Mock external services appropriately
* Test both success and failure cases
* Include integration tests where appropriate

## Additional Notes

### Issue and Pull Request Labels

* `bug` - Something isn't working
* `enhancement` - New feature or request
* `documentation` - Documentation only changes
* `duplicate` - This issue or pull request already exists
* `good first issue` - Good for newcomers
* `help wanted` - Extra attention is needed
* `invalid` - This doesn't seem right
* `question` - Further information is requested
* `wontfix` - This will not be worked on

## Recognition

Contributors who submit a PR that is merged will be added to the Contributors list in the README.md file.

## Questions?

Feel free to open an issue for any questions about contributing. We're here to help!