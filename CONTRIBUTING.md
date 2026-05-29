# 🤝 Contributing to DataForge-CLI

Thank you for your interest in contributing to DataForge-CLI! This document provides guidelines for contributing.

## 📋 How to Contribute

### 🐛 Report Bugs
1. Check if the issue already exists in [Issues](https://github.com/gitstq/DataForge-CLI/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Minimal reproduction steps
   - Expected vs actual behavior
   - Python version and OS info
   - Error logs if applicable

### 💡 Suggest Features
1. Open an issue with the `enhancement` label
2. Describe the feature and its use case
3. Provide examples of expected behavior

### 🔧 Submit Pull Requests
1. Fork the repository
2. Create a feature branch (`git checkout -b feat/your-feature`)
3. Write code with proper comments and type hints
4. Add tests for new functionality
5. Ensure all tests pass (`python -m unittest discover -s dataforge_cli/tests -v`)
6. Commit with conventional commits format
7. Push and create a Pull Request

## 📝 Commit Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new feature
fix: fix a bug
docs: documentation update
refactor: code refactoring
test: add or update tests
chore: build process or auxiliary tool changes
```

## 🧪 Development Setup

```bash
git clone https://github.com/gitstq/DataForge-CLI.git
cd DataForge-CLI
pip install -e .
python -m dataforge_cli --help
```

## 📄 Code Style

- Python 3.8+ compatible
- Type hints for all functions
- Chinese comments for all modules
- Docstrings for all public APIs
- Maximum line length: 120 characters

Thank you for your contributions! 🎉
