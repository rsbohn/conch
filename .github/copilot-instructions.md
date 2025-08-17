
# Copilot Instructions

## General Guidelines
- Be clear and concise in your prompts.
- Provide context when necessary.
- Specify the desired output format.

## Tools
- **pytest**: A testing framework for Python. Use the vscode task.
- **black**: A code formatter for Python. Use the vscode task.
- **uv**: Manages requirements, install, and script execution.
- **venv**: Always activate the local .venv.

### Windows PowerShell
- Use PowerShell commands when running on Windows.

## Preferred Libraries
The following libraries are preferred and commonly used in this codebase:

- **httpx**: For making HTTP requests.
- **textual**: For building terminal user interfaces (TUI).
- **pyperclip**: For clipboard access and manipulation.
- **pytest**: For writing and running tests.
- **black**: For code formatting.
- **sqlite3**: For lightweight database operations (pinning, indexing).
- **shlex** and **subprocess**: For shell command parsing and execution.
- **tempfile**: For creating temporary files and directories in tests and demos.
- **dataclasses**: For simple data structures (see `mvp.py`).

When adding new features, prefer these libraries for consistency and maintainability. If you need additional functionality, choose well-supported and widely adopted packages.

## Documentation and Journaling
- Document each 'reach' in ./devlog. Include the date in the filename.
- Use markdown for formatting.
- Instead of code snippets write links to the relevant code.
- Write a developer's guide for the project.
- Write a user guide for using the project.

## Code Style
- Follow PEP 8 guidelines for Python code.
- Use docstrings to document functions and classes.
- Keep lines shorter than 79 characters.
- Put imports at the top of the file.
- Use consistent naming conventions (e.g., snake_case for variables and functions).
- Use type hints for function parameters and return types.
- Periodically review and refactor code to improve readability and maintainability.

