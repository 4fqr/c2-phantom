# 🔮 C2 Phantom - Project Summary

## Overview

**C2 Phantom** is a professional, enterprise-grade Command & Control (C2) framework designed for authorized red team training and ethical security testing. Built with Python 3.9+, it features advanced encryption, traffic obfuscation, and a beautiful command-line interface.

## ✨ Key Features

### 🔐 Security & Encryption
- **AES-256-GCM** encryption with HMAC verification
- **RSA-4096** encryption with OAEP padding
- **Elliptic Curve Cryptography (ECC)** with SECP384R1
- Perfect Forward Secrecy (PFS) implementation
- Secure key storage using system keyring
- TLS 1.3 support with certificate pinning
- Memory scrubbing after operations

### 🌐 Network Protocols
- **HTTP/HTTPS** covert channels with randomization
- **DNS Tunneling** with TXT record injection
- **WebSocket** persistent connections with auto-reconnect
- **Proxy Chaining** (SOCKS4/SOCKS5/HTTP)
- Domain fronting capability
- Timing obfuscation with configurable jitter
- Payload fragmentation

### 🎨 User Interface
- Beautiful colorized terminal output using Rich library
- Progress bars and spinners
- Interactive tables and panels
- Context-aware help system
- Professional ASCII art banner

### 🔌 Plugin System
- Auto-discovery architecture
- Extensible base classes
- Hot-reloading support
- Example plugin included

### 💾 Persistence
- Windows scheduled tasks (schtasks)
- Windows registry modification
- Linux/macOS cron jobs
- systemd services (Linux)
- launchd services (macOS)

## 📁 Project Structure

```
C2-Phantom/
├── c2_phantom/                 # Main package
│   ├── __init__.py            # Package initialization
│   ├── cli.py                 # CLI entrypoint (Click-based)
│   ├── py.typed               # Type hints marker
│   ├── core/                  # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py          # YAML configuration with Pydantic
│   │   ├── session.py         # Session management
│   │   ├── events.py          # Event-driven architecture
│   │   └── exceptions.py      # Custom exceptions
│   ├── crypto/                # Encryption modules
│   │   ├── __init__.py
│   │   ├── encryption.py      # AES, RSA, ECC implementations
│   │   └── keys.py            # Key management with keyring
│   ├── network/               # Network protocols
│   │   ├── __init__.py
│   │   ├── http.py            # HTTP/HTTPS covert channels
│   │   ├── dns.py             # DNS tunneling
│   │   ├── websocket.py       # WebSocket connections
│   │   └── proxy.py           # Proxy chaining
│   ├── plugins/               # Plugin system
│   │   ├── __init__.py
│   │   ├── base.py            # Base plugin classes
│   │   ├── loader.py          # Auto-discovery loader
│   │   └── example_plugin.py  # Example plugin
│   ├── persistence/           # Persistence mechanisms
│   │   ├── __init__.py
│   │   └── scheduler.py       # Cross-platform scheduler
│   └── utils/                 # Utilities
│       ├── __init__.py
│       └── ui.py              # Rich UI components
│
├── tests/                     # Test suite
│   ├── __init__.py
│   ├── conftest.py           # Pytest fixtures
│   ├── test_encryption.py    # Encryption tests
│   ├── test_network.py       # Network tests
│   └── test_plugins.py       # Plugin tests
│
├── examples/                  # Example scripts
│   └── usage_example.py      # Usage demonstration
│
├── .github/                   # GitHub workflows
│   └── workflows/
│       └── ci.yml            # CI/CD pipeline
│
├── pyproject.toml            # Modern Python packaging
├── setup.py                  # Legacy setup script
├── requirements.txt          # Core dependencies
├── requirements-dev.txt      # Development dependencies
├── Dockerfile                # Multi-stage Docker build
├── docker-compose.yml        # Docker Compose config
├── README.md                 # Comprehensive documentation
├── QUICKSTART.md            # Quick start guide
├── CHANGELOG.md             # Version history
├── CONTRIBUTING.md          # Contribution guidelines
├── BUILD.md                 # Build instructions
├── LICENSE                  # MIT License
├── .gitignore              # Git ignore rules
├── install.py              # Installation script
└── run.ps1                 # Windows quick-start script
```

## 🚀 Installation Methods

### 1. From PyPI (Recommended)
```bash
pip install c2-phantom
```

### 2. From Source
```bash
git clone https://github.com/redteam/c2-phantom.git
cd c2-phantom
pip install -e .
```

### 3. Docker
```bash
docker build -t c2-phantom .
docker run -it c2-phantom phantom --help
```

### 4. Quick Install Script
```bash
python install.py
```

## 📦 Dependencies

### Core Dependencies
- **click** (8.1.7+) - CLI framework
- **rich** (13.7.0+) - Terminal formatting
- **cryptography** (41.0.7+) - Encryption
- **pyyaml** (6.0.1+) - Configuration
- **pydantic** (2.5.3+) - Data validation
- **aiohttp** (3.9.1+) - Async HTTP
- **websockets** (12.0+) - WebSocket support
- **dnspython** (2.4.2+) - DNS operations
- **keyring** (24.3.0+) - Secure key storage
- **psutil** (5.9.6+) - Process utilities

### Development Dependencies
- **pytest** (7.4.3+) - Testing framework
- **pytest-asyncio** (0.21.1+) - Async testing
- **pytest-cov** (4.1.0+) - Coverage reporting
- **black** (23.12.1+) - Code formatting
- **mypy** (1.7.1+) - Type checking
- **flake8** (6.1.0+) - Linting

## 🎯 CLI Commands

```bash
# Initialize
phantom init [--config PATH] [--force]

# Connect to target
phantom connect <target> 
  --protocol [https|dns|websocket]
  --encrypt [aes256|rsa|ecc]
  --proxy <proxy_url>
  --domain-front <domain>
  --jitter <ms>

# List sessions
phantom list 
  --status [active|inactive|all]
  --format [table|json|yaml]
  --verbose

# Upload files
phantom upload <local> <remote>
  --session <id>
  --chunk-size <kb>
  --encrypt
  --progress

# Execute commands
phantom execute <command>
  --session <id>
  --output
  --timeout <seconds>
  --async

# Manage plugins
phantom plugin [list|install|remove|info] [name]
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=c2_phantom --cov-report=html

# Run specific test file
pytest tests/test_encryption.py

# Run with verbose output
pytest -v
```

## 🏗️ Architecture

### Design Patterns
- **Event-Driven Architecture** - Asynchronous operations
- **Plugin Architecture** - Extensibility via plugins
- **Factory Pattern** - Encryption algorithm selection
- **Strategy Pattern** - Network protocol selection
- **Singleton Pattern** - Configuration management

### Core Components

1. **CLI Layer** - Click-based command interface
2. **Core Layer** - Session, config, event management
3. **Crypto Layer** - Encryption implementations
4. **Network Layer** - Protocol implementations
5. **Plugin Layer** - Extensibility system
6. **Persistence Layer** - Cross-platform persistence

## 🔒 Security Features

- ✅ All network traffic encrypted
- ✅ Keys stored in system keyring
- ✅ No plaintext credentials
- ✅ Memory scrubbing after operations
- ✅ Integrity verification (HMAC/SHA-256)
- ✅ Anti-debugging detection (planned)
- ✅ Perfect Forward Secrecy

## 📊 Code Quality

- ✅ PEP8 compliant
- ✅ Type hints throughout
- ✅ Comprehensive docstrings
- ✅ Unit test coverage
- ✅ CI/CD pipeline
- ✅ Code formatting (black)
- ✅ Import sorting (isort)
- ✅ Static analysis (mypy, flake8)

## 🌍 Platform Support

- ✅ Windows 10/11
- ✅ macOS 10.15+
- ✅ Linux (Ubuntu, Debian, CentOS, Fedora)
- ✅ Python 3.9, 3.10, 3.11, 3.12

## 📈 Performance

- Async I/O for network operations
- Connection pooling for HTTP
- Efficient encryption (AES hardware acceleration)
- Minimal memory footprint
- Fast startup time

## 🎓 Use Cases

1. **Red Team Training** - Practice C2 operations
2. **Security Research** - Study C2 techniques
3. **Penetration Testing** - Authorized testing only
4. **Education** - Learn cybersecurity concepts
5. **Blue Team Training** - Understand attacker tools

## ⚠️ Legal & Ethical Use

**CRITICAL**: This tool is for AUTHORIZED security testing ONLY!

- ✅ Obtain written permission before testing
- ✅ Use only in controlled environments
- ✅ Comply with all laws and regulations
- ✅ Document all activities
- ❌ NEVER use for malicious purposes
- ❌ NEVER use without authorization

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! See CONTRIBUTING.md for guidelines.

## 📞 Support

- **Documentation**: README.md, QUICKSTART.md
- **Issues**: GitHub Issues
- **Email**: phantom@redteam.local

## 🙏 Acknowledgments

- Python cryptography library
- Rich terminal library
- Click CLI framework
- Security research community
- Open source contributors

## 📅 Release Information

- **Version**: 1.0.0
- **Release Date**: January 5, 2026
- **Status**: Production Ready
- **Python**: 3.9+
- **License**: MIT

---

**Built with ❤️ by the Red Team Community**

*Remember: With great power comes great responsibility. Use ethically!* 🔮
