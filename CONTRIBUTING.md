# Contributing to DNSChanger

First off, thank you for considering contributing to DNSChanger! It's people like you that make DNSChanger such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by respect, professionalism, and collaboration. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

**Bug Report Template:**

```markdown
**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots/Logs**
If applicable, add screenshots and relevant log excerpts from dnschanger.log

**Environment:**
 - OS: [e.g., Windows 11 22H2]
 - DNSChanger Version: [e.g., 2.0.0]
 - Python Version (if running from source): [e.g., 3.12]

**Additional context**
Any other context about the problem.
```

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear title** describing the enhancement
- **Detailed description** of the proposed feature
- **Use cases** explaining why this would be useful
- **Alternative solutions** you've considered
- **Mockups/examples** if applicable

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following the code style guidelines
3. **Add tests** if applicable
4. **Update documentation** if needed
5. **Ensure tests pass** locally
6. **Submit a pull request**

**Pull Request Template:**

```markdown
**Description**
Brief description of changes

**Type of change**
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

**Testing**
- [ ] I have tested these changes locally
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] All tests pass locally

**Checklist:**
- [ ] My code follows the style guidelines
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
```

## Development Setup

### Prerequisites

- Python 3.12 or higher
- Windows 10/11 for testing
- Git

### Setting Up Development Environment

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/DNSChanger.git
cd DNSChanger

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
pip install pytest pytest-cov black flake8 mypy

# Install in editable mode
pip install -e .
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_models.py

# Run with verbose output
pytest -v
```

### Code Style

We follow PEP 8 with some modifications:

```bash
# Format code with black
black .

# Check code style
flake8 .

# Type checking
mypy .
```

**Code Style Guidelines:**

1. **Type Hints**: Use type hints for all function signatures
   ```python
   def my_function(param: str) -> bool:
       """Docstring here."""
       return True
   ```

2. **Docstrings**: Use Google-style docstrings
   ```python
   def complex_function(param1: str, param2: int) -> dict:
       """
       Brief description.
       
       Longer description if needed.
       
       Args:
           param1: Description of param1
           param2: Description of param2
           
       Returns:
           Description of return value
           
       Raises:
           ValueError: When param2 is negative
       """
       pass
   ```

3. **Imports**: Group and order imports
   ```python
   # Standard library
   import os
   import sys
   
   # Third-party
   import yaml
   from pydantic import BaseModel
   
   # Local
   from core import DNSLoader
   from models import DNSProvider
   ```

4. **Line Length**: Maximum 100 characters (120 for comments/docstrings)

5. **Naming Conventions**:
   - Classes: `PascalCase`
   - Functions/Methods: `snake_case`
   - Constants: `UPPER_SNAKE_CASE`
   - Private: `_leading_underscore`

### Project Structure

```
dnschanger/
├── core/          # Business logic (pure Python, no UI)
├── ps/            # PowerShell integration (Windows-specific)
├── models/        # Data models (Pydantic schemas)
├── ui/            # User interface (CustomTkinter)
├── scripts/       # Helper scripts
└── tests/         # Test suite
```

**Guidelines by Module:**

- **core/**: No UI dependencies, fully testable
- **ps/**: Mock PowerShell in tests
- **models/**: Pure data models, heavily tested
- **ui/**: Minimal logic, mostly composition

### Testing Guidelines

1. **Write tests for**:
   - New features
   - Bug fixes
   - Edge cases
   - Error handling

2. **Test structure**:
   ```python
   def test_function_name():
       """Test description."""
       # Arrange
       setup_data = create_test_data()
       
       # Act
       result = function_under_test(setup_data)
       
       # Assert
       assert result == expected_value
   ```

3. **Use fixtures** for common setup:
   ```python
   @pytest.fixture
   def sample_provider():
       return DNSProvider(name="Test", ipv4=["1.1.1.1"])
   ```

4. **Mock external dependencies**:
   ```python
   from unittest.mock import Mock, patch
   
   @patch('ps.ps_adapter.subprocess.run')
   def test_with_mock(mock_run):
       mock_run.return_value = Mock(returncode=0, stdout="success")
       # Test code
   ```

### Commit Messages

Follow conventional commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding/updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(doh): add support for DNS-over-TLS

Implemented DoT alongside existing DoH support.
Added new configuration options in provider schema.

Closes #123
```

```
fix(ui): resolve interface list refresh issue

Fixed bug where interface list wasn't updating after
network changes. Now properly refreshes on adapter state change.

Fixes #456
```

### Documentation

Update documentation when:
- Adding new features
- Changing behavior
- Fixing bugs that affect usage
- Updating dependencies

**Files to update:**
- `README.md`: User-facing documentation
- `CHANGELOG.md`: Version history
- Code docstrings: API documentation
- Comments: Complex logic explanation

### Building and Testing Locally

```bash
# Clean previous builds
python build.py clean

# Build with PyInstaller
python build.py pyinstaller

# Build with Nuitka (slower but optimized)
python build.py nuitka

# Test the executable
cd release
./DNSChanger.exe
```

## Release Process (Maintainers)

1. Update version in `__init__.py`
2. Update `CHANGELOG.md`
3. Run full test suite
4. Build executables
5. Test on clean Windows installation
6. Create git tag
7. Create GitHub release
8. Upload artifacts

## Questions?

Feel free to:
- Open an issue for discussion
- Ask in pull request comments
- Reach out to maintainers

## Recognition

Contributors will be recognized in:
- `README.md` contributors section
- Release notes
- GitHub contributors page

Thank you for contributing to DNSChanger! 🎉
