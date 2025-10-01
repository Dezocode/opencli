# Contributing to OpenCLI

Thank you for your interest in contributing to OpenCLI! This document provides guidelines for contributing to the project.

## 🎯 Project Philosophy

OpenCLI is designed to be:
- **Fast** - Optimized for low-latency, streaming responses
- **Modular** - Easy to extend with new features
- **Reliable** - Safe upgrades with automatic rollback
- **User-friendly** - Intuitive commands and clear documentation

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Git
- OpenRouter API key (or compatible API)
- Optional: `gh` CLI for GitHub integration

### Development Setup

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/opencli.git
   cd opencli
   ```

2. **Install dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Install in development mode**:
   ```bash
   ./install.sh
   ```

4. **Make your changes** and test thoroughly

## 📝 Development Guidelines

### Code Style

- **Python**: Follow PEP 8 style guidelines
- **Shell scripts**: Use shellcheck for validation
- **Documentation**: Update relevant `.md` files when adding features

### Project Structure

```
opencli/
├── opencli.py              # Main CLI entry point
├── modules/                # Core modules
│   ├── agent_manager.py    # Agent system
│   ├── command_registry.py # Command permissions
│   ├── context_builder.py  # Context optimization
│   ├── prompt_processor.py # Input processing
│   ├── upgrade_manager.py  # Version control
│   └── rollback_manager.py # Rollback system
├── agents/                 # Agent configurations
│   └── configs/
│       └── agents.yaml     # Agent definitions
└── install.sh             # Installation script
```

### Adding New Features

1. **Modules**: Place new functionality in `modules/`
2. **Agents**: Add agent configs to `agents/configs/agents.yaml`
3. **Commands**: Register new commands in `modules/command_registry.py`
4. **Version**: Update `version.json` with changes

### Version Control

OpenCLI uses semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

When adding features, update `version.json`:

```json
{
  "version": "1.3.0",
  "changelog": [{
    "version": "1.3.0",
    "date": "2025-10-XX",
    "changes": [
      "Added new feature X",
      "Improved Y functionality"
    ],
    "bump_type": "minor"
  }]
}
```

## 🧪 Testing

### Manual Testing

1. Test the installation process:
   ```bash
   ./install.sh
   ```

2. Test core functionality:
   ```bash
   opencli
   > /status
   > /agents
   > /commands
   ```

3. Test new features thoroughly before submitting PR

### Test Checklist

- [ ] Installation works cleanly
- [ ] Upgrade/rollback system works
- [ ] No API keys or secrets in code
- [ ] Documentation updated
- [ ] Commands registered in command_registry.py
- [ ] Version.json updated

## 📋 Pull Request Process

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Write clean, documented code
   - Update relevant documentation
   - Add entries to `version.json` changelog

3. **Test thoroughly**:
   - Test installation
   - Test new features
   - Test existing features still work

4. **Commit with clear messages**:
   ```bash
   git commit -m "feat: add new feature X"
   ```

   Use conventional commit prefixes:
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation
   - `refactor:` - Code refactoring
   - `test:` - Testing
   - `chore:` - Maintenance

5. **Push and create PR**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **PR Description should include**:
   - What the change does
   - Why it's needed
   - How to test it
   - Any breaking changes

## 🐛 Bug Reports

When reporting bugs, please include:

- OpenCLI version (`opencli --version` or check `~/.opencli/version.json`)
- Operating system
- Python version
- Steps to reproduce
- Expected vs actual behavior
- Relevant logs or error messages

## 💡 Feature Requests

Feature requests are welcome! Please include:

- Use case / problem to solve
- Proposed solution
- Any alternative approaches considered
- How it fits with OpenCLI's philosophy

## 🔒 Security

If you discover a security vulnerability, please email security@yourdomain.com rather than opening a public issue.

## 📄 License

By contributing to OpenCLI, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

Contributors will be recognized in the project README. Thank you for helping make OpenCLI better!

## 📞 Questions?

- Open a GitHub Discussion for questions
- Check existing issues and documentation
- Review ARCHITECTURE.md for technical details

---

**Happy Contributing! 🚀**
