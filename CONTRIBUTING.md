# Contributing to Discord Multi-Agent Support System

Thank you for your interest in contributing to this project! This document provides guidelines and instructions for contributing.

## 🌟 Ways to Contribute

- 🐛 **Report Bugs**: Submit bug reports via [GitHub Issues](https://github.com/yourusername/discord-multi-agent/issues)
- 💡 **Suggest Features**: Propose new features via [GitHub Issues](https://github.com/yourusername/discord-multi-agent/issues)
- 📖 **Improve Documentation**: Fix typos, clarify explanations, add examples
- 🧪 **Write Tests**: Increase test coverage
- 🔧 **Submit Pull Requests**: Fix bugs, implement features

---

## 🚀 Getting Started

### 1. Fork & Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/discord-multi-agent.git
cd discord-multi-agent

# Add the upstream repository
git remote add upstream https://github.com/original-owner/discord-multi-agent.git
```

### 2. Create a Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

### 4. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

---

## 📋 Development Guidelines

### Code Style

- **Follow PEP 8**: Use `flake8` or `pylint` to check your code
- **Use Black**: Format your code with `black .`
- **Type Hints**: Add type hints to function signatures
- **Docstrings**: Write clear docstrings (Google style preferred)

Example:

```python
def process_message(message: str, user_id: str) -> Dict[str, Any]:
    """
    Process a user message and return the response.
    
    Args:
        message: The user's message text
        user_id: Discord user ID
        
    Returns:
        Dictionary containing intent, reply, and metadata
        
    Raises:
        ValueError: If message is empty
    """
    if not message:
        raise ValueError("Message cannot be empty")
    
    # Implementation...
    return {"intent": "...", "reply": "..."}
```

### Testing

- **Write Tests**: All new features must include unit tests
- **Test Coverage**: Aim for >80% test coverage
- **Run Tests**: Ensure all tests pass before submitting

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=src tests/

# Run specific test file
python -m pytest tests/test_agents.py -v
```

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Build process or auxiliary tool changes

Examples:

```bash
feat(agents): add sentiment analysis to IntentAgent

- Add sentiment scoring for better intent detection
- Update tests for IntentAgent.sentiment_analysis

Closes #123
```

```bash
fix(bot): handle edge case in message processing

- Check for None message before processing
- Add test case for empty message

Fixes #456
```

---

## 🧪 Testing Guide

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test class
python -m pytest tests/test_agents.py::TestIntentAgent -v

# Run specific test method
python -m pytest tests/test_agents.py::TestIntentAgent::test_intent_types_defined -v

# Run with print statements visible
python -m pytest tests/ -s

# Run with coverage report
python -m pytest --cov=src --cov-report=html tests/
```

### Writing Tests

Use `unittest` and `unittest.mock`:

```python
import unittest
from unittest.mock import Mock, patch

class TestMyFeature(unittest.TestCase):
    """Test cases for MyFeature."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.instance = MyClass()
    
    @patch('src.module.ExternalClass')
    def test_feature(self, mock_external):
        """Test that feature works correctly."""
        # Arrange
        mock_external.return_value = "mocked"
        input_data = {"key": "value"}
        
        # Act
        result = self.instance.process(input_data)
        
        # Assert
        self.assertEqual(result["status"], "success")
        mock_external.assert_called_once()
    
    def test_edge_case(self):
        """Test edge case handling."""
        with self.assertRaises(ValueError):
            self.instance.process(None)
```

---

## 🔄 Pull Request Process

### 1. Update Your Branch

```bash
# Fetch latest changes from upstream
git fetch upstream

# Merge or rebase onto your branch
git rebase upstream/main
```

### 2. Run Tests

```bash
# Ensure all tests pass
python -m pytest tests/ -v

# Ensure code style compliance
flake8 src/ tests/
black --check src/ tests/
```

### 3. Commit Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat(module): add amazing feature"
```

### 4. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 5. Create Pull Request

- Go to your fork on GitHub
- Click "Compare & pull request"
- Fill in the PR template
- Link related issues
- Request reviews from maintainers

### PR Checklist

- [ ] Tests added/updated for new functionality
- [ ] Documentation updated (if needed)
- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] Commits follow conventional commit format
- [ ] PR description clearly describes the changes

---

## 🐛 Bug Reports

When reporting a bug, please include:

1. **Description**: Clear description of the bug
2. **Reproduction Steps**: Step-by-step instructions to reproduce
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Environment**:
   - OS: [e.g., Windows 11, Ubuntu 22.04]
   - Python version: [e.g., 3.11.2]
   - Package versions: [output of `pip freeze`]
6. **Logs**: Relevant error messages or logs
7. **Screenshots**: If applicable

**Template**:

```markdown
## Bug Description
A clear description of the bug.

## Steps to Reproduce
1. Run command '...'
2. Send message '...'
3. See error

## Expected Behavior
The bot should respond with...

## Actual Behavior
The bot crashes with error: ...

## Environment
- OS: Windows 11
- Python: 3.11.2
- discord.py: 2.3.2

## Additional Context
Any other context about the problem.
```

---

## 💡 Feature Requests

When suggesting a feature, please include:

1. **Problem Description**: What problem does this solve?
2. **Proposed Solution**: Your suggested solution
3. **Alternatives Considered**: Other solutions you've considered
4. **Additional Context**: Screenshots, examples, etc.

---

## 📝 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

## 📞 Questions?

Feel free to reach out:

- **Open a Discussion**: [GitHub Discussions](https://github.com/yourusername/discord-multi-agent/discussions)
- **Join Discord**: [Discord Server](https://discord.gg/yourserver)
- **Contact Maintainer**: your-email@example.com

---

**Thank you for contributing! 🎉**
