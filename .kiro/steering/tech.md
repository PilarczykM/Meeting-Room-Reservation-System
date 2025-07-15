# Technology Stack & Build System

## Tech Stack
- **Python**: 3.11+ (specified in pyproject.toml)
- **Package Manager**: uv (modern Python package manager)
- **CLI Framework**: Rich (for beautiful terminal output and tables)
- **Data Validation**: Pydantic v2 (for models and validation)
- **Testing**: pytest with pytest-mock
- **Code Quality**: Ruff (linting and formatting)
- **Pre-commit**: Automated code quality checks

## Build System
Uses `uv` as the primary package manager with `pyproject.toml` configuration.

## Common Commands

### Development Setup
```bash
# Install dependencies
make install
# or
uv sync
```

### Testing
```bash
# Run all tests
make test
# or
uv run pytest
```

### Code Quality
```bash
# Run linter
make lint
# or
uv run ruff check .

# Auto-fix formatting issues
make format
# or
uv run ruff check . --fix

# Run all quality checks
make all  # runs lint, format, and test
```

### Running the Application
```bash
# Via uv
uv run python main.py [command] [args]

# Direct execution
python main.py [command] [args]
```

## Configuration
- Environment-specific configs in `config/` directory (development.json, production.json, test.json)
- Supports `--env` flag to override environment
- Logging levels configurable via command line (`--verbose`, `--quiet`)

## Code Quality Standards
- Line length: 120 characters
- Target Python version: 3.10+
- Ruff handles both linting and formatting
- Docstrings required for public modules/classes (D100, D104, D107 ignored)
- Tests exempt from docstring requirements