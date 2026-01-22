<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->
# Developer Workflow

This document describes how to set up your development environment and run common development tasks.

## Environment Setup

Lynx uses UV for dependency management and virtual environment handling.

```bash
# Clone the repository
git clone <repo-url>
cd lynx

# Create virtual environment and install dependencies
uv sync --all-extras --dev

# Install a Jupyter kernel for the project
uv run ipython kernel install --user --env VIRTUAL_ENV $(pwd)/.venv --name=lynx
```

The project uses a UV virtual environment stored in `.venv/`. Activate it with:

```bash
source .venv/bin/activate  # Unix/macOS
# or
.venv\Scripts\activate  # Windows
```

## Running Tests

### Python Backend Tests

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=lynx --cov-report=term-missing

# Skip coverage for faster iteration
uv run pytest --no-cov

# Enforce coverage threshold (currently 80%)
uv run pytest --cov-fail-under=80
```

Coverage reports are written to `htmlcov/index.html` - open in browser to see detailed line-by-line coverage.

### Frontend Tests

```bash
cd js
npm test              # Run tests once
npm test -- --run     # Run without watch mode
npm test -- --coverage # With coverage
```

## Linting and Formatting

The project uses Ruff for both linting and formatting (replaces Black, isort, and Flake8).

```bash
# Check for linting issues
uv run ruff check .

# Fix auto-fixable issues
uv run ruff check --fix .

# Format code
uv run ruff format .

# Check formatting without modifying files
uv run ruff format --check .
```

Configuration is in `pyproject.toml` under `[tool.ruff]`.

### Frontend formatting

```bash
cd js && npx prettier --write .
```

## Type Checking

The project uses mypy with strict mode enabled.

```bash
# Type check all source files
uv run mypy src/lynx

# Type check specific file
uv run mypy src/lynx/diagram.py
```

Configuration is in `pyproject.toml` under `[tool.mypy]`. All public APIs must be fully typed.

## License checking

Lynx uses REUSE to verify licensing compliance.
Check that all files are correctly annotated with:

```bash
uvx reuse lint
```

Annotate files with, e.g.

```bash
uvx reuse annotate --fallback-dot-license --copyright="Jared Callaham  <jared.callaham@gmail.com>" --license="GPL-3.0-or-later" [files...]
```

## Frontend Development

### Building the Widget

```bash
# Build JavaScript bundle
./build.sh

# Or manually:
cd js
npm run build
```

### Development Workflow

For rapid iteration during frontend development:

1. Start Jupyter Lab:
   ```bash
   uv run jupyter lab
   ```

2. In a separate terminal, run the frontend build in watch mode:
   ```bash
   cd js
   npm run dev  # Rebuilds on file changes
   ```

3. Refresh the Jupyter notebook to see changes

## Pre-commit Checklist

Before committing, ensure:

- [ ] **Tests pass**: `uv run pytest`
- [ ] **Linting clean**: `uv run ruff check .`
- [ ] **Formatting applied**: `uv run ruff format .`
- [ ] **Type checking passes**: `uv run mypy src/lynx`
- [ ] **Coverage maintained**: `uv run pytest --cov-fail-under=80`
- [ ] **Frontend tests pass**: `cd js && npm test -- --run && cd ..`
- [ ] **Frontend linting pass**: `cd js && npm run lint && cd ..`
- [ ] **Licensing check**: `uvx reuse lint`

## Continuous Integration

GitHub Actions runs on every push:
- Linting (Ruff)
- Type checking (mypy)
- Python tests (pytest with coverage)
- Frontend tests (Vitest)

See `.github/workflows/` for CI configuration.
