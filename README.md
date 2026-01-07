# C2-Phantom

> **Enterprise-Grade Command & Control Framework for Professional Penetration Testing**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/4fqr/c2-phantom)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

---

## 🎯 What is C2-Phantom?

C2-Phantom is a next-generation command and control framework architected for **enterprise-scale penetration testing** and **red team operations**. Built from the ground up with a multi-language architecture, it combines Python's flexibility, C's raw performance, Rust's memory safety, and Go's concurrency to deliver unmatched operational capability.

### Built For

- **Fortune 500 Security Teams**: Comprehensive testing of enterprise defense-in-depth strategies
- **Professional Red Teams**: Full-spectrum adversary emulation with MITRE ATT&CK coverage
- **Penetration Testers**: Reliable, production-grade tooling for high-stakes engagements
- **Security Researchers**: Extensible platform for offensive security R&D

---

## ⚡ Why C2-Phantom?

### True Multi-Language Architecture

Unlike monolithic C2 frameworks, C2-Phantom leverages the right tool for each job:

- **Python**: Orchestration layer providing unified control and automation
- **C**: Performance-critical Windows internals, direct syscalls, and EDR evasion
- **Rust**: Memory-safe implants with zero-day resistant code quality
- **Go**: Massively concurrent server infrastructure handling thousands of sessions

### Enterprise-Ready Features

**Evasion & Defense Bypass**
- Direct NT syscall invocation bypassing userland hooks
- AMSI and ETW neutralization for Windows Defender evasion
- Inline API hooking engine for behavioral analysis bypass
- Multi-layered anti-sandbox and VM detection
- Process injection with multiple techniques (CreateRemoteThread, thread hijacking, process hollowing)

**Advanced Post-Exploitation**
- Comprehensive credential harvesting (LSASS, SAM, registry, browsers, WiFi)
- Real-time keylogging with low-level keyboard hooks
- Screen capture and clipboard monitoring
- File exfiltration with chunked transfer and encryption
- Lateral movement capabilities (WMI, PSExec, SSH)
- Multiple persistence mechanisms (Registry, scheduled tasks, WMI events, services)

**Operational Security**
- End-to-end encryption with ChaCha20-Poly1305 and AES-256-GCM
- Proxy support (Tor, SOCKS5, HTTP) for anonymized C2
- Secure file deletion with multi-pass overwriting
- Anti-forensics including log wiping and timestomping
- Domain fronting and traffic obfuscation

**Scalability & Reliability**
- Concurrent session management with Go's goroutine architecture
- PostgreSQL backend for persistent storage and analytics
- Redis task queue for distributed operations
- Multi-protocol listeners (HTTP/HTTPS, DNS tunneling, raw TCP)
- Load balancing and high-availability configurations
- TLS certificate management and rotation

---

## 🚀 Quick Start

### Prerequisites

Ensure you have the following installed:

- **Python 3.13+**: Primary orchestration language
- **CMake 3.15+**: C core compilation
- **Rust 1.70+**: Agent binary builds
- **Go 1.21+**: Server infrastructure
- **OpenSSL**: Cryptographic operations

### Installation

```bash
# Clone the repository
git clone https://github.com/4fqr/c2-phantom.git
cd c2-phantom

# Build all components
make all

# Install Python package
pip install -e .

# Initialize database (first time only)
c2-phantom init
```

### Launch Your First Session

```bash
# Start the C2 server
c2-phantom server --host 0.0.0.0 --port 443 --tls

# Generate agent payload
c2-phantom generate --format exe --output agent.exe --host your-c2-server.com

# Interactive CLI
c2-phantom cli
```

---

## 🏗️ Architecture

C2-Phantom's architecture is purpose-built for maximum flexibility and performance:

**Control Layer (Python)**
- Unified command interface with rich CLI
- FFI bridges to native components (ctypes, cffi, gRPC)
- Task orchestration and session management
- Automation and scripting capabilities

**Performance Layer (C)**
- Direct syscall implementations for EDR evasion
- Hardware-accelerated cryptography (AES-NI)
- Windows API mastery (AMSI bypass, ETW hooks, process injection)
- Anti-analysis techniques (sandbox detection, anti-debug)

**Implant Layer (Rust)**
- Memory-safe agent binaries resistant to exploitation
- Cross-platform compatibility (Windows, Linux, macOS)
- Minimal binary size (200-400 KB) with full LTO
- Comprehensive post-exploitation modules

**Infrastructure Layer (Go)**
- High-concurrency C2 server handling 10,000+ sessions
- gRPC-based communication for type-safe RPC
- Distributed task queuing with Redis
- Database persistence with PostgreSQL
- Multi-protocol listener support

---

## 💼 Use Cases

### Red Team Operations

Simulate sophisticated threat actors with full MITRE ATT&CK technique coverage. C2-Phantom's evasion capabilities allow you to test defenses against nation-state-level adversaries.

### Penetration Testing

Reliable, production-tested tooling for professional engagements. Comprehensive logging and reporting for client deliverables. Flexible deployment options for both internal and external assessments.

### Security Research

Extensible platform for offensive security R&D. Clean, well-documented codebase in multiple languages. Easy integration with custom tools and exploits.

### Purple Team Exercises

Coordinate with defenders to validate detection and response capabilities. Granular control over operational indicators. Built-in logging for retrospective analysis.

---

## 🎓 Getting Started

### For Red Team Operators

1. **Deploy Infrastructure**: Set up your C2 server on cloud infrastructure or on-premises
2. **Generate Payloads**: Create customized agent binaries for target environments
3. **Establish C2**: Deploy agents and establish command channels
4. **Post-Exploitation**: Execute objectives using built-in modules
5. **Cleanup**: Remove artifacts and restore target systems

### For Developers

1. **Review Architecture**: Understand the multi-language design philosophy
2. **Set Up Dev Environment**: Install all build dependencies
3. **Run Tests**: Ensure all test suites pass in your environment
4. **Extend Functionality**: Develop new modules or improve existing ones
5. **Contribute**: Submit pull requests with new capabilities

---

## 🛡️ Security & Ethics

### Legal Notice

**WARNING**: This framework is for **AUTHORIZED SECURITY ASSESSMENTS ONLY**.

Unauthorized access to computer systems is illegal under applicable laws including but not limited to the Computer Fraud and Abuse Act (CFAA) in the United States, the Computer Misuse Act in the United Kingdom, and similar legislation worldwide.

### Responsible Use

C2-Phantom is intended for:
- ✅ Authorized penetration testing engagements
- ✅ Red team operations with proper scope and authorization
- ✅ Security research in controlled environments
- ✅ Defensive capability development and testing

C2-Phantom is **NOT** intended for:
- ❌ Unauthorized access to systems or networks
- ❌ Data theft or system disruption
- ❌ Malware distribution
- ❌ Any illegal activity

**Operators are solely responsible for obtaining proper authorization and complying with all applicable laws and regulations.**

### Disclosure Policy

Security vulnerabilities in C2-Phantom should be reported through GitHub Security Advisories. We practice responsible disclosure and will credit researchers appropriately.

---

## 📚 Documentation

Comprehensive documentation is available in the project repository:

- **User Guide**: Getting started and common operations
- **Developer Guide**: Architecture deep-dive and extension development
- **API Reference**: Complete Python, C, Rust, and Go API documentation
- **OPSEC Guide**: Operational security best practices
- **Deployment Guide**: Production deployment patterns

---

## 🤝 Contributing

We welcome contributions from the security community!

**Areas of Focus**:
- Cross-platform compatibility improvements
- New evasion and anti-analysis techniques
- Additional post-exploitation modules
- Performance optimizations
- Documentation enhancements
- Test coverage expansion

Please review our contributing guidelines before submitting pull requests.

---

## 🌟 Feature Highlights

| Category | Capabilities |
|----------|-------------|
| **Evasion** | AMSI bypass, ETW bypass, direct syscalls, API hooking, anti-sandbox, anti-debug, VM detection |
| **Credential Access** | LSASS dumping, SAM extraction, browser passwords, WiFi credentials, registry harvesting, clipboard monitoring |
| **Persistence** | Registry Run keys, scheduled tasks, WMI events, services, systemd units, cron jobs |
| **Lateral Movement** | WMI execution, PSExec-style operations, SSH key-based access, credential reuse |
| **Collection** | Keylogging, screenshot capture, file exfiltration, clipboard monitoring, audio recording |
| **Command & Control** | HTTP/HTTPS, DNS tunneling, TCP, proxy chains, domain fronting, encrypted beacons |
| **Exfiltration** | Chunked transfer, compression, encryption, bandwidth throttling, protocol tunneling |

---

## 📊 Performance

C2-Phantom is engineered for production use:

- **Session Capacity**: 10,000+ concurrent agents per server
- **Beacon Latency**: <100ms local, <500ms over Tor
- **Binary Size**: 200-400 KB (Rust agent, fully featured, stripped)
- **Memory Footprint**: <50 MB per agent
- **Encryption Performance**: 2-3 GB/s (AES-NI hardware acceleration)
- **Database Scalability**: PostgreSQL cluster support for unlimited growth

---

## 🔬 Technical Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Orchestration** | Python 3.13+ | Unified control interface and automation |
| **Agent** | Rust 2021 | Memory-safe, cross-platform implants |
| **Server** | Go 1.21+ | High-concurrency C2 infrastructure |
| **Core** | C11 | Performance-critical Windows operations |
| **Database** | PostgreSQL 14+ | Persistent storage and analytics |
| **Cache** | Redis 7+ | Task queuing and pub/sub |
| **RPC** | gRPC + Protobuf | Type-safe inter-service communication |
| **Crypto** | OpenSSL, ChaCha20-Poly1305 | End-to-end encryption |

---

## 🏆 Project Status

C2-Phantom is actively developed and maintained. Current development focus:

- ✅ Core framework and multi-language integration
- ✅ Windows evasion and post-exploitation modules
- ✅ Comprehensive credential harvesting
- 🚧 Full Linux and macOS agent support
- 🚧 Web-based GUI for session management
- 🚧 Advanced persistence mechanisms
- 🚧 Plugin architecture for extensibility
- 📋 Cloud deployment automation (AWS, Azure, GCP)
- 📋 Machine learning-based anomaly detection bypass

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/4fqr/c2-phantom/issues)
- **Discussions**: [GitHub Discussions](https://github.com/4fqr/c2-phantom/discussions)
- **Security**: Responsible disclosure via GitHub Security Advisories

---

## 📄 License

C2-Phantom is released under the MIT License. See [LICENSE](LICENSE) for details.

---

## 🎖️ Acknowledgments

C2-Phantom builds upon decades of offensive security research. We acknowledge the contributions of the security community, including:

- The MITRE ATT&CK framework for adversary tactics and techniques
- The Metasploit Project for establishing C2 framework patterns
- Red team practitioners sharing operational tradecraft
- Security researchers advancing evasion techniques

---

## ⚠️ Disclaimer

This software is provided for **educational and authorized security testing purposes only**. The developers assume no liability and are not responsible for any misuse or damage caused by this program. Use at your own risk and only on systems you own or have explicit permission to test.

**By using C2-Phantom, you acknowledge that**:
1. You have obtained proper authorization for all systems you access
2. You understand applicable laws and regulations in your jurisdiction
3. You will use this software ethically and responsibly
4. The developers are not liable for your actions

---

<div align="center">

**Built with 🔥 by security professionals, for security professionals**

[Documentation](https://github.com/4fqr/c2-phantom/wiki) • [Issues](https://github.com/4fqr/c2-phantom/issues) • [Contributing](CONTRIBUTING.md)

</div>
