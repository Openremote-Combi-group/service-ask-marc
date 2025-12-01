# Testing Guide for Ask-Marc Services

This document explains how to run and manage tests for the Ask-Marc service project.

## Table of Contents
- [Installation](#installation)
- [Running Tests](#running-tests)
- [Test Structure](#test-structure)
- [Writing Tests](#writing-tests)
- [Coverage Reports](#coverage-reports)
- [Troubleshooting](#troubleshooting)

## Installation

### 1. Install Test Dependencies

First, sync all dependencies including test dependencies:

```powershell
uv sync --all-extras
```

This will install:
- `pytest` - Testing framework
- `pytest-asyncio` - Async test support
- `pytest-cov` - Coverage reporting
- `pytest-mock` - Mocking utilities
- `httpx` - HTTP client for testing

### 2. Verify Installation

Check that pytest is installed:

```powershell
uv run pytest --version
```

## Running Tests

### Run All Tests

```powershell
uv run pytest
```

### Run Tests with Verbose Output

```powershell
uv run pytest -v
```

### Run Tests with Coverage

```powershell
uv run pytest --cov=src --cov-report=html --cov-report=term-missing
```

This generates:
- HTML coverage report in `htmlcov/index.html`
- Terminal output showing coverage percentages

### Run Specific Test Files

```powershell
# Test only shared module
uv run pytest tests/shared/

# Test only MCP server
uv run pytest tests/mcp-server/

# Test only MCP client API
uv run pytest tests/mcp-client-api/

# Test a specific file
uv run pytest tests/shared/test_openremote_service.py

# Test a specific class
uv run pytest tests/shared/test_openremote_service.py::TestOpenRemoteService

# Test a specific test function
uv run pytest tests/shared/test_openremote_service.py::TestOpenRemoteService::test_register_success
```

### Run Tests by Marker

```powershell
# Run only unit tests
uv run pytest -m unit

# Run only integration tests
uv run pytest -m integration

# Run all tests except slow ones
uv run pytest -m "not slow"

# Run unit tests with coverage
uv run pytest -m unit --cov=src
```

### Run Tests in Parallel (faster)

```powershell
# Install pytest-xdist first
uv pip install pytest-xdist

# Run tests in parallel
uv run pytest -n auto
```

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures and configuration
├── test_integration.py      # End-to-end integration tests
├── shared/                  # Tests for shared module
│   ├── __init__.py
│   ├── test_openremote_service.py
│   └── test_mcp_client.py
├── mcp-server/             # Tests for MCP server
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_health.py
│   ├── test_services_asset.py
│   ├── test_services_realm.py
│   ├── test_services_asset_model.py
│   └── test_services_rule.py
└── mcp-client-api/         # Tests for MCP client API
    ├── __init__.py
    ├── test_config.py
    ├── test_health.py
    ├── test_cors.py
    └── test_chat.py
```

### Test Markers

- `@pytest.mark.unit` - Fast, isolated unit tests
- `@pytest.mark.integration` - Tests that test multiple components together
- `@pytest.mark.slow` - Tests that take longer to run
- `@pytest.mark.asyncio` - Async tests (automatically applied)

## Writing Tests

### Example Unit Test

```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

class TestMyFeature:
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_my_function(self, mock_openremote_client):
        """Test description."""
        # Arrange
        mock_openremote_client.some_method = AsyncMock(return_value="result")
        
        # Act
        result = await my_function()
        
        # Assert
        assert result == "expected"
        mock_openremote_client.some_method.assert_called_once()
```

### Using Fixtures

Common fixtures are defined in `tests/conftest.py`:

- `mock_openremote_client` - Mocked OpenRemote client
- `mock_mcp_client` - Mocked MCP client
- `mock_env_vars` - Set up environment variables
- `sample_asset` - Sample asset data
- `sample_ruleset` - Sample ruleset data

### Testing Async Functions

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result is not None
```

### Mocking Dependencies

```python
@pytest.mark.unit
@pytest.mark.asyncio
async def test_with_mock(mock_openremote_client):
    with patch('module.get_openremote_service') as mock_get_service:
        mock_service = MagicMock()
        mock_service.client = mock_openremote_client
        mock_get_service.return_value = mock_service
        
        # Your test code here
```

## Coverage Reports

### Generate HTML Coverage Report

```powershell
uv run pytest --cov=src --cov-report=html
```

Open `htmlcov/index.html` in your browser to see detailed coverage.

### View Coverage in Terminal

```powershell
uv run pytest --cov=src --cov-report=term-missing
```

This shows which lines are not covered by tests.

### Coverage Configuration

Coverage is configured in `pytest.ini`:

```ini
[pytest]
addopts = 
    --cov=src
    --cov-report=html
    --cov-report=term-missing
```

### Coverage Goals

Aim for:
- **Unit tests**: 80%+ coverage
- **Integration tests**: Cover critical paths
- **Overall**: 70%+ coverage

## Continuous Integration

### GitHub Actions Example

Create `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      
      - name: Install dependencies
        run: uv sync --all-extras
      
      - name: Run tests
        run: uv run pytest --cov=src --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

## Troubleshooting

### Import Errors

If you see `Import "pytest" could not be resolved`:

1. Install test dependencies:
   ```powershell
   uv sync --all-extras
   ```

2. Configure Python interpreter in VS Code:
   - Press `Ctrl+Shift+P`
   - Type "Python: Select Interpreter"
   - Choose the uv-managed Python environment

3. Restart VS Code

### Module Not Found Errors

If you see `Import "src.services..." could not be resolved`:

This is expected - VS Code Pylance shows these warnings, but pytest will resolve them correctly at runtime because:
- `pytest.ini` configures the test paths
- Tests use dynamic imports to avoid circular dependencies
- The actual code runs fine when executed

To reduce warnings, you can:
1. Add a `.vscode/settings.json`:
   ```json
   {
     "python.analysis.extraPaths": ["./src"]
   }
   ```

2. Or suppress these specific warnings in test files (not recommended)

### Tests Fail to Run

1. Make sure you're in the project root directory
2. Verify environment variables are set (or use fixtures)
3. Check that all dependencies are installed: `uv sync --all-extras`

### Slow Tests

1. Use test markers to skip slow tests during development:
   ```powershell
   uv run pytest -m "not slow"
   ```

2. Run tests in parallel:
   ```powershell
   uv pip install pytest-xdist
   uv run pytest -n auto
   ```

### Mock Issues

If mocks aren't working:
- Ensure you're patching at the right location (where it's used, not defined)
- Use `AsyncMock` for async functions
- Check that return values match expected types

## Best Practices

1. **Write tests first** (TDD) when adding new features
2. **Keep tests fast** - use mocks for external dependencies
3. **Test edge cases** - not just happy paths
4. **Use descriptive test names** - they serve as documentation
5. **One assertion per test** (when possible)
6. **Arrange-Act-Assert** pattern for clarity
7. **Don't test implementation details** - test behavior
8. **Keep tests isolated** - no dependencies between tests

## Quick Reference

```powershell
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src

# Run specific markers
uv run pytest -m unit
uv run pytest -m integration

# Run specific file
uv run pytest tests/shared/test_openremote_service.py

# Run with verbose output
uv run pytest -v

# Run and stop on first failure
uv run pytest -x

# Run and show local variables on failure
uv run pytest -l

# Run last failed tests only
uv run pytest --lf

# Show print statements
uv run pytest -s
```

## Support

For questions or issues:
1. Check this documentation
2. Review test examples in `tests/` directory
3. Check pytest documentation: https://docs.pytest.org/
4. Review project README.md
