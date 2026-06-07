## Git Conventions
- Use conventional commits: feat:, fix:, docs:, test:, refactor:, chore:
- Subject lines under 72 characters, imperative mood
- Run `pytest` before every commit; do not commit if tests fail
- One logical change per commit
- Push to origin after each commit

## Code Conventions
- Python 3.11+, full type hints on public functions
- Docstrings (Google style) on all public functions and classes
- Black formatting, 100 char line limit
- Pure functions where possible; side effects isolated
