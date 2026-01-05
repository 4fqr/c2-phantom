# Contributing to C2 Phantom

Thank you for your interest in contributing to C2 Phantom! This document provides guidelines for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:
- Be respectful and inclusive
- Use welcoming and inclusive language
- Be collaborative
- Focus on what is best for the community
- Show empathy towards others

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/redteam/c2-phantom/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version, etc.)
   - Relevant logs or screenshots

### Suggesting Features

1. Check existing feature requests in [Issues](https://github.com/redteam/c2-phantom/issues)
2. Create a new issue labeled "enhancement" with:
   - Clear description of the feature
   - Use cases and benefits
   - Possible implementation approach

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Write or update tests
5. Ensure all tests pass
6. Update documentation
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to your branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

#### PR Guidelines

- Follow PEP8 style guide
- Include type hints
- Write docstrings for all functions/classes
- Add unit tests for new features
- Update README if needed
- Keep commits atomic and well-described

### Development Setup

```bash
# Clone repository
git clone https://github.com/redteam/c2-phantom.git
cd c2-phantom

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
flake8 c2_phantom
black c2_phantom
mypy c2_phantom
```

### Code Style

- Follow PEP8 standards
- Use `black` for formatting (line length: 100)
- Use `isort` for import sorting
- Use type hints for all functions
- Write comprehensive docstrings

### Testing

- Write unit tests for all new features
- Maintain or improve code coverage
- Test on multiple Python versions (3.9+)
- Test on multiple platforms (Windows/macOS/Linux)

### Documentation

- Update README for user-facing changes
- Add docstrings to all new functions/classes
- Update API documentation
- Include examples where appropriate

## Project Structure

```
c2-phantom/
├── c2_phantom/           # Main package
│   ├── cli.py           # CLI entrypoint
│   ├── core/            # Core functionality
│   ├── crypto/          # Encryption modules
│   ├── network/         # Network protocols
│   ├── plugins/         # Plugin system
│   ├── persistence/     # Persistence mechanisms
│   └── utils/           # Utilities
├── tests/               # Test suite
├── docs/                # Documentation
└── examples/            # Example scripts
```

## Security

If you discover a security vulnerability:
1. **DO NOT** open a public issue
2. Email security@redteam.local
3. Include detailed description and steps to reproduce
4. Wait for response before disclosing publicly

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

Feel free to:
- Open an issue for questions
- Join our Discord community
- Email: phantom@redteam.local

Thank you for contributing! 🎉
