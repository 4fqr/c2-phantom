<div align="center">

# 🔮 C2 Phantom

<img src="https://img.shields.io/badge/C2-Phantom-8A2BE2?style=for-the-badge&logo=ghost&logoColor=white" alt="C2 Phantom">

### Advanced Command & Control Framework for Ethical Red Team Operations

*Professional-grade C2 infrastructure with military-grade encryption, traffic obfuscation, and cross-platform compatibility*

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-success?style=for-the-badge)](LICENSE)
[![Security](https://img.shields.io/badge/Encryption-AES--256--GCM-critical?style=for-the-badge&logo=lock)](https://en.wikipedia.org/wiki/Galois/Counter_Mode)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-blue?style=for-the-badge)]()

[![Code Style](https://img.shields.io/badge/code%20style-black-000000?style=flat-square)](https://github.com/psf/black)
[![Type Hints](https://img.shields.io/badge/type%20hints-mypy-blue?style=flat-square)](http://mypy-lang.org/)
[![Tests](https://img.shields.io/badge/tests-pytest-orange?style=flat-square)](https://pytest.org/)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?style=flat-square&logo=github-actions&logoColor=white)](https://github.com/features/actions)

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-installation">Installation</a> •
  <a href="#-usage">Usage</a> •
  <a href="#-documentation">Documentation</a> •
  <a href="#-contributing">Contributing</a>
</p>

<img src="https://user-images.githubusercontent.com/placeholder/banner.gif" alt="C2 Phantom Demo" width="800">

---

### ⚠️ **LEGAL DISCLAIMER**

**This tool is designed EXCLUSIVELY for AUTHORIZED security testing, red team training, and educational purposes.**

```diff
! Use of this software for attacking targets without prior mutual consent is ILLEGAL.
! The developer assumes NO RESPONSIBILITY for misuse or damage caused by this program.
+ Always obtain proper written authorization before conducting security assessments.
+ Comply with all applicable laws, regulations, and ethical guidelines.
```

</div>

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🔐 **Military-Grade Cryptography**

- **AES-256-GCM**: Authenticated encryption for data confidentiality and integrity
- **RSA-4096**: Asymmetric encryption for secure key exchange
- **Elliptic Curve Cryptography (ECC)**: P-256/P-384/P-521 curves with ECDH & ECDSA
- **Perfect Forward Secrecy (PFS)**: Ephemeral keys for session-level security
- **TLS 1.3**: Modern transport layer security with certificate pinning
- **Secure Key Storage**: Platform-specific keychains (Keyring integration)

</td>
<td width="50%">

### 🌐 **Advanced Network Protocols**

- **HTTP/HTTPS Channels**: Covert communication with randomized headers
- **DNS Tunneling**: Exfiltration via TXT/CNAME records
- **WebSocket Fallback**: Persistent bidirectional connections
- **Domain Fronting**: CDN-based traffic masking
- **Proxy Chaining**: Multi-hop SOCKS5/HTTP proxy support
- **Custom TCP/UDP**: Protocol flexibility for specialized environments

</td>
</tr>
<tr>
<td width="50%">

### 🎭 **Evasion & Obfuscation**

- **Timing Jitter**: Randomized delays to evade pattern detection
- **Payload Fragmentation**: Split data to bypass IDS/IPS
- **Protocol Fingerprinting Evasion**: Mimic legitimate traffic patterns
- **Header Randomization**: Dynamic User-Agent and cookie generation
- **Memory Scrubbing**: Zero sensitive data after operations
- **Anti-Debugging**: Detect runtime analysis attempts

</td>
<td width="50%">

### 🔌 **Plugin Ecosystem**

- **Auto-Discovery**: Automatically load plugins from directory
- **Hot-Reload**: Update plugins without restarting framework
- **Command Registration**: Extend CLI with custom commands
- **Event Hooks**: Integrate with core event system
- **Version Control**: Dependency management and compatibility checks
- **Example Templates**: Quickstart plugin development

</td>
</tr>
<tr>
<td width="50%">

### 💾 **Cross-Platform Persistence**

- **Windows**: Scheduled Tasks, Registry Run Keys, Service Installation
- **Linux**: Cron Jobs, Systemd Services, Init Scripts
- **macOS**: Launch Agents/Daemons, Cron, Login Items
- **Automatic Detection**: Platform-aware persistence selection
- **Privilege Escalation**: Integrated with UAC/sudo workflows

</td>
<td width="50%">

### 🎨 **Beautiful User Experience**

- **Rich Terminal UI**: Colorized output, tables, progress bars
- **Interactive Prompts**: Context-aware input with validation
- **Session Management**: Track multiple simultaneous targets
- **Command History**: Replay and audit operations
- **Tab Completion**: Shell-like autocompletion support
- **ASCII Art Banners**: Professional branded interface

</td>
</tr>
</table>

---

## 🚀 Quick Start

### Prerequisites

<table>
<tr>
<td>

**System Requirements**
- Python 3.9 or higher
- pip (Python package manager)
- Git (for cloning)
- Virtual environment support

</td>
<td>

**Supported Platforms**
- ✅ Windows 10/11 (x64)
- ✅ Linux (Ubuntu 20.04+, Debian, Arch)
- ✅ macOS 11.0+ (Big Sur and later)
- ✅ Docker (any platform)

</td>
</tr>
</table>

### 📦 Installation Methods

<details open>
<summary><b>Method 1: Install from PyPI (Recommended)</b></summary>

```bash
# Install via pip
pip install c2-phantom

# Verify installation
phantom --version
```

</details>

<details>
<summary><b>Method 2: Install from Source</b></summary>

```bash
# Clone the repository
git clone https://github.com/4fqr/c2-phantom.git
cd c2-phantom

# Create and activate virtual environment
python -m venv .venv

# On Windows
.venv\Scripts\activate

# On Linux/macOS
source .venv/bin/activate

# Install in editable mode (for development)
pip install -e .

# Or install normally
pip install .
```

</details>

<details>
<summary><b>Method 3: Docker Installation</b></summary>

```bash
# Build Docker image
docker build -t c2-phantom:latest .

# Run container
docker run -it --rm \
  -v ~/.phantom:/root/.phantom \
  -p 443:443 \
  c2-phantom:latest

# Or use Docker Compose
docker-compose up -d
```

</details>

<details>
<summary><b>Method 4: Development Setup</b></summary>

```bash
# Clone repository
git clone https://github.com/4fqr/c2-phantom.git
cd c2-phantom

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Check code quality
black .
mypy c2_phantom/
```

</details>

---

### 🎯 Basic Usage Examples

#### **1. Initialize C2 Framework**

```bash
# Generate configuration and encryption keys
phantom init

# Custom configuration path
phantom init --config /custom/path/config.yaml
```

**Output:**
```
╔══════════════════════════════════════════════════════════╗
║           C2 Phantom - Initialization                     ║
╚══════════════════════════════════════════════════════════╝

✅ Configuration file created: ~/.phantom/config.yaml
✅ AES-256-GCM key generated
✅ RSA-4096 keypair generated
✅ ECC P-384 keypair generated
✅ Plugin directory initialized

🎉 C2 Phantom is ready to use!
```

#### **2. Connect to Target System**

```bash
# HTTPS connection with AES-256 encryption
phantom connect https://target.example.com --encrypt aes256

# DNS tunneling with proxy chain
phantom connect dns://target.com --protocol dns --proxy socks5://proxy:1080

# WebSocket with domain fronting
phantom connect wss://target.com --domain-front cdn.cloudflare.com --jitter 2000
```

#### **3. Session Management**

```bash
# List all active sessions
phantom list --status active

# Show detailed session info
phantom list --verbose --format table

# Export session data
phantom list --format json > sessions.json
```

**Example Output:**
```
┌─────────────┬──────────────────────┬──────────┬─────────────┬───────────┐
│ Session ID  │ Target               │ Protocol │ Encryption  │ Status    │
├─────────────┼──────────────────────┼──────────┼─────────────┼───────────┤
│ sess_001    │ 192.168.1.100:443    │ HTTPS    │ AES-256-GCM │ Active    │
│ sess_002    │ target.example.com   │ DNS      │ RSA-4096    │ Active    │
│ sess_003    │ 10.0.0.50:8443       │ WebSocket│ ECC-P384    │ Idle      │
└─────────────┴──────────────────────┴──────────┴─────────────┴───────────┘
```

#### **4. File Operations**

```bash
# Upload file with progress bar
phantom upload /local/file.pdf /remote/docs/file.pdf \
  --session sess_001 \
  --encrypt \
  --progress

# Download file
phantom download /remote/data.db /local/data.db --session sess_001

# Bulk upload directory
phantom upload /local/folder/ /remote/folder/ --recursive --session sess_001
```

#### **5. Command Execution**

```bash
# Execute single command
phantom execute "whoami" --session sess_001 --output

# Execute with timeout
phantom execute "long-running-script.sh" --session sess_001 --timeout 300

# Asynchronous execution
phantom execute "background-task.py" --session sess_001 --async

# Interactive shell
phantom shell --session sess_001
```

#### **6. Plugin Management**

```bash
# List available plugins
phantom plugin list

# Install plugin from repository
phantom plugin install persistence-toolkit

# View plugin information
phantom plugin info example

# Reload plugin
phantom plugin reload example

# Remove plugin
phantom plugin remove old-plugin
```

---

## 📖 Documentation

### Commands

#### `phantom init`
Initialize C2 Phantom configuration and generate encryption keys.

```bash
phantom init [--config PATH] [--force]
```

#### `phantom connect`
Establish a connection to a target system.

```bash
phantom connect <target> [OPTIONS]

Options:
  --protocol [https|dns|websocket]  Connection protocol (default: https)
  --encrypt [aes256|rsa|ecc]        Encryption method (default: aes256)
  --proxy TEXT                       Proxy chain (e.g., http://proxy:8080)
  --domain-front TEXT               Domain fronting target
  --jitter INTEGER                   Timing jitter in ms (default: 1000)
  --timeout INTEGER                  Connection timeout in seconds
```

#### `phantom list`
List active sessions and connections.

```bash
phantom list [OPTIONS]

Options:
  --status [active|inactive|all]  Filter by session status
  --format [table|json|yaml]      Output format
  --verbose                        Show detailed information
```

#### `phantom upload`
Upload files to target systems.

```bash
phantom upload <local_path> <remote_path> [OPTIONS]

Options:
  --session TEXT      Session ID (required)
  --chunk-size INT    Upload chunk size in KB (default: 1024)
  --encrypt          Encrypt file during transfer
  --progress         Show progress bar
```

#### `phantom execute`
Execute commands on target systems.

```bash
phantom execute <command> [OPTIONS]

Options:
  --session TEXT      Session ID (required)
  --output           Show command output
  --timeout INT      Execution timeout in seconds
  --async            Execute asynchronously
```

#### `phantom plugin`
Manage plugins.

```bash
phantom plugin [list|install|remove|info] [PLUGIN_NAME]
```

---

## ⚙️ Configuration

C2 Phantom uses YAML configuration files located in `~/.phantom/config.yaml`:

```yaml
# Server Configuration
server:
  host: 0.0.0.0
  port: 443
  tls_enabled: true
  certificate: /path/to/cert.pem
  key: /path/to/key.pem

# Encryption Settings
encryption:
  default_algorithm: aes256-gcm
  key_size: 256
  forward_secrecy: true
  
# Network Configuration
network:
  protocols:
    - https
    - dns
    - websocket
  user_agents:
    - "Mozilla/5.0 (Windows NT 10.0; Win64; x64)..."
    - "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)..."
  headers:
    randomize: true
  timing:
    jitter_min: 500
    jitter_max: 2000

# Evasion Techniques
evasion:
  domain_fronting: true
  payload_fragmentation: true
  protocol_fingerprinting_evasion: true
  
# Logging
logging:
  level: INFO
  file: ~/.phantom/logs/phantom.log
  max_size: 10MB
  backup_count: 5

# Plugins
plugins:
  directory: ~/.phantom/plugins
  auto_load: true
```

---

## 🔌 Plugin Development

Create custom plugins by placing Python files in `~/.phantom/plugins/`:

```python
"""
Example C2 Phantom Plugin
"""
from c2_phantom.plugins import BasePlugin
from c2_phantom.core.decorators import command

class ExamplePlugin(BasePlugin):
    """Example plugin demonstrating the plugin API."""
    
    name = "example"
    version = "1.0.0"
    description = "Example plugin for C2 Phantom"
    author = "Your Name"
    
    def initialize(self) -> None:
        """Initialize plugin resources."""
        self.logger.info("Example plugin initialized")
    
    @command(name="hello", help="Say hello")
    def hello_command(self, name: str = "World") -> str:
        """Greet someone."""
        return f"Hello, {name}!"
    
    def cleanup(self) -> None:
        """Cleanup plugin resources."""
        self.logger.info("Example plugin cleaned up")
```

---

## 🧪 Testing & Quality Assurance

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=c2_phantom --cov-report=html --cov-report=term

# Run specific test suite
pytest tests/test_encryption.py -v

# Run with markers
pytest -m "not slow"  # Skip slow tests

# Parallel execution
pytest -n auto
```

### Code Quality Checks

```bash
# Type checking with mypy
mypy c2_phantom/

# Linting with flake8
flake8 c2_phantom/ --max-line-length=100

# Code formatting
black c2_phantom/ tests/
isort c2_phantom/ tests/

# Security audit
bandit -r c2_phantom/
safety check
```

---

## 🏗️ Architecture & Design

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      CLI Interface (Click + Rich)             │
│                   Beautiful Terminal UI Layer                 │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                   Core Framework Layer                        │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │   Config    │  │   Session    │  │   Event Bus     │   │
│  │  Management │  │   Manager    │  │   System        │   │
│  └─────────────┘  └──────────────┘  └─────────────────┘   │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│              Security & Cryptography Layer                    │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │ AES-256-GCM │  │  RSA-4096    │  │   ECC P-384     │   │
│  │  Encryption │  │  Encryption  │  │   Key Exchange  │   │
│  └─────────────┘  └──────────────┘  └─────────────────┘   │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│              Network & Communication Layer                    │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │ HTTP/HTTPS  │  │     DNS      │  │   WebSocket     │   │
│  │   Channels  │  │   Tunneling  │  │   Connections   │   │
│  └─────────────┘  └──────────────┘  └─────────────────┘   │
│  ┌─────────────┐  ┌──────────────┐                         │
│  │   Proxy     │  │    Domain    │                         │
│  │   Chaining  │  │   Fronting   │                         │
│  └─────────────┘  └──────────────┘                         │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│          Evasion & Obfuscation Layer                         │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │   Timing    │  │   Payload    │  │   Protocol      │   │
│  │   Jitter    │  │Fragmentation │  │  Fingerprint    │   │
│  └─────────────┘  └──────────────┘  └─────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

### Project Structure

```
c2-phantom/
├── 📁 c2_phantom/              # Main package directory
│   ├── 📄 __init__.py          # Package initialization
│   ├── 📄 cli.py               # CLI entrypoint with Click
│   │
│   ├── 📁 core/                # Core framework components
│   │   ├── 📄 config.py        # Configuration management
│   │   ├── 📄 session.py       # Session tracking & management
│   │   ├── 📄 events.py        # Event-driven architecture
│   │   └── 📄 exceptions.py    # Custom exception hierarchy
│   │
│   ├── 📁 crypto/              # Cryptographic implementations
│   │   ├── 📄 encryption.py    # AES-256-GCM, RSA-4096, ECC
│   │   ├── 📄 tls.py           # TLS 1.3 with cert pinning
│   │   └── 📄 keys.py          # Key generation & storage
│   │
│   ├── 📁 network/             # Network protocol handlers
│   │   ├── 📄 http.py          # HTTP/HTTPS covert channels
│   │   ├── 📄 dns.py           # DNS tunneling (TXT/CNAME)
│   │   ├── 📄 websocket.py     # WebSocket bidirectional comms
│   │   └── 📄 proxy.py         # SOCKS5/HTTP proxy chaining
│   │
│   ├── 📁 evasion/             # Evasion & obfuscation techniques
│   │   ├── 📄 timing.py        # Jitter & randomized delays
│   │   ├── 📄 fragmentation.py # Payload splitting
│   │   └── 📄 fingerprint.py   # Protocol mimicry
│   │
│   ├── 📁 persistence/         # Cross-platform persistence
│   │   ├── 📄 scheduler.py     # Task scheduling (all platforms)
│   │   ├── 📄 registry.py      # Windows registry persistence
│   │   └── 📄 cron.py          # Unix cron jobs & services
│   │
│   ├── 📁 plugins/             # Plugin architecture
│   │   ├── 📄 base.py          # BasePlugin abstract class
│   │   ├── 📄 loader.py        # Auto-discovery & hot-reload
│   │   └── 📄 example_plugin.py # Example plugin template
│   │
│   └── 📁 utils/               # Utility functions
│       ├── 📄 ui.py            # Rich console UI helpers
│       ├── 📄 logging.py       # Structured logging
│       └── 📄 validators.py    # Input validation utilities
│
├── 📁 tests/                   # Test suite
│   ├── 📄 conftest.py          # Pytest fixtures & configuration
│   ├── 📄 test_encryption.py   # Crypto unit tests
│   ├── 📄 test_network.py      # Network protocol tests
│   └── 📄 test_plugins.py      # Plugin system tests
│
├── 📁 docs/                    # Documentation
│   ├── 📄 QUICKSTART.md        # Quick start guide
│   ├── 📄 API.md               # API documentation
│   ├── 📄 CONTRIBUTING.md      # Contribution guidelines
│   └── 📄 TROUBLESHOOTING.md   # Common issues & solutions
│
├── 📁 .github/                 # GitHub configuration
│   └── 📁 workflows/           # CI/CD workflows
│       └── 📄 ci.yml           # GitHub Actions CI pipeline
│
├── 📄 Dockerfile               # Container image definition
├── 📄 docker-compose.yml       # Multi-container orchestration
├── 📄 pyproject.toml           # Modern Python packaging config
├── 📄 setup.py                 # Setup script for installation
├── 📄 requirements.txt         # Production dependencies
├── 📄 requirements-dev.txt     # Development dependencies
├── 📄 .gitignore               # Git ignore patterns
├── 📄 .pre-commit-config.yaml  # Pre-commit hooks
├── 📄 LICENSE                  # MIT License
└── 📄 README.md                # This file
```

---

## 🐳 Docker Deployment

### Using Docker

```bash
# Build the image
docker build -t c2-phantom:latest .

# Run interactive container
docker run -it --rm \
  -v ~/.phantom:/root/.phantom \
  -p 443:443 \
  -p 53:53/udp \
  --name phantom-c2 \
  c2-phantom:latest

# Run in background with persistent volume
docker run -d \
  -v phantom-data:/root/.phantom \
  -p 443:443 \
  --restart unless-stopped \
  --name phantom-c2 \
  c2-phantom:latest
```

### Using Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f phantom

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

**docker-compose.yml Example:**

```yaml
version: '3.8'

services:
  phantom:
    build: .
    container_name: c2-phantom
    restart: unless-stopped
    ports:
      - "443:443"
      - "53:53/udp"
    volumes:
      - phantom-config:/root/.phantom
      - ./plugins:/root/.phantom/plugins
    environment:
      - PHANTOM_LOG_LEVEL=INFO
      - PHANTOM_ENCRYPT_DEFAULT=aes256
    networks:
      - phantom-net

  redis:
    image: redis:alpine
    container_name: phantom-redis
    restart: unless-stopped
    networks:
      - phantom-net

volumes:
  phantom-config:

networks:
  phantom-net:
    driver: bridge
```

---

## 🔒 Security Best Practices

### ⚠️ **CRITICAL WARNINGS**

```diff
! This tool is designed EXCLUSIVELY for AUTHORIZED security testing
! Use without proper authorization is ILLEGAL and UNETHICAL
! The authors assume NO LIABILITY for misuse of this software
```

### Security Guidelines

<table>
<tr>
<td width="50%">

**🔐 Operational Security**

- ✅ Always obtain written authorization
- ✅ Use VPN/proxy chains for anonymity
- ✅ Encrypt all C2 communications
- ✅ Regularly rotate encryption keys
- ✅ Use isolated testing environments
- ✅ Implement proper logging & auditing
- ❌ Never use default configurations
- ❌ Never store credentials in plaintext

</td>
<td width="50%">

**🛡️ Infrastructure Hardening**

- ✅ Enable TLS 1.3 with certificate pinning
- ✅ Use domain fronting for traffic masking
- ✅ Implement timing jitter (1-3 seconds)
- ✅ Fragment payloads < 1KB chunks
- ✅ Use secure key storage (OS keychain)
- ✅ Enable memory scrubbing after use
- ❌ Never expose debug/admin endpoints
- ❌ Never reuse compromised infrastructure

</td>
</tr>
</table>

### Recommended Practices

1. **Authorization**: Obtain explicit written permission before any testing
2. **Scope Definition**: Clearly define IP ranges, domains, and systems in scope
3. **Data Protection**: Encrypt all exfiltrated data and store securely
4. **Incident Response**: Have a rollback plan if operations are detected
5. **Legal Compliance**: Follow SOC 2, ISO 27001, and local laws
6. **Documentation**: Maintain detailed logs for post-assessment reporting

---

## 🤝 Contributing

We welcome contributions from the security community! Here's how to get involved:

### Development Workflow

```bash
# 1. Fork the repository on GitHub

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/c2-phantom.git
cd c2-phantom

# 3. Create a feature branch
git checkout -b feature/your-amazing-feature

# 4. Set up development environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

# 5. Install pre-commit hooks
pre-commit install

# 6. Make your changes and commit
git add .
git commit -m "feat: add amazing feature"

# 7. Push to your fork
git push origin feature/your-amazing-feature

# 8. Open a Pull Request
```

### Code Standards

<table>
<tr>
<td>

**Style Guidelines**
- Follow PEP 8 conventions
- Use Black for code formatting
- Use isort for import sorting
- Maximum line length: 100 chars
- Use type hints (PEP 484)

</td>
<td>

**Documentation**
- Write docstrings (Google style)
- Add inline comments for complex logic
- Update README for new features
- Include usage examples
- Document breaking changes

</td>
</tr>
<tr>
<td>

**Testing Requirements**
- Write unit tests (pytest)
- Maintain > 80% code coverage
- Test edge cases & errors
- Mock external dependencies
- Add integration tests

</td>
<td>

**Commit Messages**
- Use conventional commits
- Format: `type(scope): message`
- Types: feat, fix, docs, test, refactor
- Keep messages concise
- Reference issues (#123)

</td>
</tr>
</table>

### Pull Request Checklist

- [ ] Code follows project style guidelines
- [ ] All tests pass (`pytest`)
- [ ] Code coverage maintained/improved
- [ ] Documentation updated
- [ ] Commit messages follow conventions
- [ ] No merge conflicts with main branch
- [ ] PR description explains changes clearly
- [ ] Linked related issues

---

## 📚 Additional Resources

### Documentation

- 📖 [Quick Start Guide](docs/QUICKSTART.md) - Get up and running in 5 minutes
- 📖 [API Documentation](docs/API.md) - Complete API reference
- 📖 [Configuration Guide](docs/CONFIGURATION.md) - Advanced configuration options
- 📖 [Plugin Development](docs/PLUGINS.md) - Create custom plugins
- 📖 [Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues & solutions

### External Resources

- 🔗 [MITRE ATT&CK Framework](https://attack.mitre.org/) - Adversary tactics & techniques
- 🔗 [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/) - Security testing methodology
- 🔗 [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework) - Security standards
- 🔗 [Red Team Field Manual](https://www.amazon.com/Rtfm-Red-Team-Field-Manual/dp/1494295504) - Operator reference

---

## 📝 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 C2 Phantom Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙏 Acknowledgments

This project stands on the shoulders of giants. Special thanks to:

- 🎖️ **Security Researchers** - For advancing offensive security techniques
- 👨‍💻 **Open Source Contributors** - For maintaining critical cryptography libraries
- 🏢 **Cryptography.io Team** - For the excellent `cryptography` library
- 🎨 **Will McGugan** - For the beautiful `rich` library
- 🔧 **Pallets Team** - For the powerful `click` framework
- 📚 **Python Community** - For comprehensive documentation and support

### Built With

<div align="center">

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Click](https://img.shields.io/badge/Click-000000?style=for-the-badge)
![Rich](https://img.shields.io/badge/Rich-009485?style=for-the-badge)
![Cryptography](https://img.shields.io/badge/Cryptography-8A2BE2?style=for-the-badge&logo=lock&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)

</div>

---

## 📞 Support & Contact

<table align="center">
<tr>
<td align="center">

### 💬 GitHub Discussions
Ask questions and share knowledge
<br>
[Join Discussion](https://github.com/4fqr/c2-phantom/discussions)

</td>
<td align="center">

### 🐛 Issue Tracker
Report bugs and request features
<br>
[Open Issue](https://github.com/4fqr/c2-phantom/issues)

</td>
</tr>
<tr>
<td align="center">

### 📖 Documentation
Comprehensive guides and API docs
<br>
[Read the Docs](https://c2-phantom.readthedocs.io)

</td>
<td align="center">

### 💼 Professional Support
Enterprise training and consulting
<br>
[Contact Us](mailto:phantom@redteam.security)

</td>
</tr>
</table>

---

## 📊 Project Stats

<div align="center">

![GitHub Stars](https://img.shields.io/github/stars/4fqr/c2-phantom?style=social)
![GitHub Forks](https://img.shields.io/github/forks/4fqr/c2-phantom?style=social)
![GitHub Issues](https://img.shields.io/github/issues/4fqr/c2-phantom)
![GitHub Pull Requests](https://img.shields.io/github/issues-pr/4fqr/c2-phantom)
![Contributors](https://img.shields.io/github/contributors/4fqr/c2-phantom)
![Last Commit](https://img.shields.io/github/last-commit/4fqr/c2-phantom)

</div>

---

## 🔄 Changelog

### Version 1.0.0 (2024-01-XX)

**🎉 Initial Release**

- ✨ Advanced encryption (AES-256-GCM, RSA-4096, ECC)
- ✨ Multiple network protocols (HTTP/HTTPS, DNS, WebSocket)
- ✨ Evasion techniques (timing jitter, fragmentation, domain fronting)
- ✨ Plugin architecture with auto-discovery
- ✨ Cross-platform persistence mechanisms
- ✨ Beautiful Rich-based CLI interface
- ✨ Comprehensive test suite
- ✨ Docker support
- ✨ Full documentation

See [CHANGELOG.md](CHANGELOG.md) for complete version history.

---

<div align="center">

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=4fqr/c2-phantom&type=Date)](https://star-history.com/#4fqr/c2-phantom&Date)

---

### 🎯 Made with ❤️ by Security Professionals, for Security Professionals

**C2 Phantom** - *Where stealth meets sophistication*

<img src="https://img.shields.io/badge/Built_with-Passion-red?style=for-the-badge" alt="Built with Passion">
<img src="https://img.shields.io/badge/Ethical-Use_Only-green?style=for-the-badge" alt="Ethical Use Only">

---

*Remember: With great power comes great responsibility. Always obtain authorization before conducting security assessments.*

**[⬆ Back to Top](#-c2-phantom)**

</div>

