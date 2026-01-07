# C2-Phantom: Advanced Multi-Language Command & Control Framework

[![CI](https://github.com/4fqr/c2-phantom/actions/workflows/ci.yml/badge.svg)](https://github.com/4fqr/c2-phantom/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)

## Executive Summary

C2-Phantom is a production-grade command and control framework implementing defense evasion, privilege escalation, credential harvesting, and lateral movement capabilities. The architecture leverages Python for orchestration, C for performance-critical operations, Rust for memory-safe agent implementation, and Go for scalable server infrastructure.

**Target Audience**: Security researchers, red team operators, penetration testers, and security engineers with advanced technical expertise.

## Architecture Overview

### Multi-Language Design Philosophy

```
┌─────────────────────────────────────────────────────────────┐
│                    Python Orchestrator                       │
│  • Command-line interface (Click + Rich)                    │
│  • FFI bridges (ctypes, cffi, gRPC)                        │
│  • Session management and task queueing                     │
│  • High-level automation and scripting                     │
└─────────────────┬───────────────────────────────────────────┘
                  │
    ┌─────────────┼─────────────┬──────────────────┐
    │             │             │                  │
    ▼             ▼             ▼                  ▼
┌─────────┐ ┌──────────┐ ┌──────────┐      ┌───────────┐
│ C Core  │ │  Rust    │ │   Go     │      │  Protobuf │
│ Library │ │  Agent   │ │  Server  │      │   RPC     │
└─────────┘ └──────────┘ └──────────┘      └───────────┘
```

### Component Breakdown

#### 1. Python Orchestrator (`c2_phantom/`)
- **Purpose**: Unified control interface and automation layer
- **Key Modules**:
  - `orchestrator.py`: Main coordination class integrating C/Rust/Go
  - `core/native.py`: ctypes bindings to C shared library
  - `bridge/rust_ffi.py`: FFI bridge to Rust agent library
  - `bridge/go_rpc.py`: gRPC client for Go server communication
- **Lines of Code**: ~2000 (Python)

#### 2. C Core Library (`core/`)
- **Purpose**: Performance-critical Windows API operations, EDR evasion
- **Components**:
  - **Crypto** (`crypto/aes.{c,h}`): AES-256-GCM with OpenSSL EVP API, AES-NI hardware acceleration
  - **Network** (`network/beacon.{c,h}`): HTTP beacon with libcurl, jitter, and encryption
  - **Evasion** (`evasion/`):
    - `amsi.{c,h}`: AMSI bypass via memory patching (VirtualProtect)
    - `etw.{c,h}`: ETW bypass (EtwEventWrite hooking)
  - **Syscalls** (`syscall/direct.{c,h}`): Direct NT syscalls for EDR bypass (NtAllocateVirtualMemory, NtWriteVirtualMemory, NtCreateThreadEx)
  - **Hooks** (`hooks/inline.{c,h}`): Inline hooking engine (JMP-based, trampoline support)
  - **Anti-Analysis** (`anti/sandbox.{c,h}`): Sandbox/VM detection (timing, artifacts, user interaction, hardware checks)
  - **Process** (`process/inject.{c,h}`): Process injection (CreateRemoteThread, DLL injection)
- **Build System**: CMake 3.15+ with cross-platform support
- **Lines of Code**: ~2500 (C)

#### 3. Rust Agent (`agent/`)
- **Purpose**: Memory-safe implant with full C2 capabilities
- **Modules**:
  - `commands.rs`: Command execution (PowerShell, CMD, Bash) with timeout support
  - `files.rs`: File operations (read, write, upload, download, secure delete, search)
  - `credentials.rs`: Credential harvesting (LSASS dump, SAM hashes, registry, browser passwords, WiFi passwords, clipboard)
  - `keylog.rs`: Keylogger (SetWindowsHookEx low-level keyboard hook)
  - `screen.rs`: Screenshot capture (GDI BitBlt → PNG conversion)
  - `persist.rs`: Persistence mechanisms (Registry Run keys, scheduled tasks, WMI events, systemd, cron)
- **Crypto**: ChaCha20-Poly1305 (pure Rust, no OpenSSL dependency)
- **Optimizations**: LTO, strip symbols, size-optimized (`opt-level = "z"`)
- **Binary Size**: ~200-400 KB (release build)
- **Lines of Code**: ~3500 (Rust)

#### 4. Go Server (`server/`)
- **Purpose**: Scalable C2 backend with concurrent session management
- **Features**:
  - Fiber web framework (Express-like API)
  - Concurrent beacon handling (goroutines)
  - Task queueing and result storage
  - Multi-protocol listeners (HTTP, HTTPS, DNS, TCP)
  - gRPC API for Python client
- **Planned**:
  - PostgreSQL for persistent storage
  - Redis for task queuing and pub/sub
  - Load balancing across listeners
  - TLS certificate management
- **Lines of Code**: ~2500 (Go, in progress)

#### 5. Protocol Buffers (`proto/`)
- **Purpose**: Type-safe, efficient RPC between Go server and Python client
- **Schemas**:
  - Agent registration and lifecycle
  - Task management (send, receive results)
  - File operations (chunked upload/download)
  - Process enumeration
  - Credential harvesting responses

## Technical Capabilities

### Evasion Techniques

| Technique | Implementation | Bypass Target |
|-----------|---------------|---------------|
| **AMSI Bypass** | Memory patching of `amsidrv.dll!AmsiScanBuffer` | Windows Defender, AV with AMSI integration |
| **ETW Bypass** | Hooking `ntdll.dll!EtwEventWrite` | EDR telemetry, Sysmon |
| **Direct Syscalls** | Manual syscall invocation (mov r10, rcx; mov eax, <NR>; syscall) | Userland hooks (EDR), API monitoring |
| **Inline Hooking** | Detours-style JMP hooks with trampolines | API interception, sandboxes |
| **Anti-Sandbox** | Timing checks (RDTSC), artifact detection (VMware/VBox drivers), user interaction validation | Automated analysis systems |
| **Process Injection** | CreateRemoteThread, NtCreateThreadEx syscall | Behavioral analysis, process monitoring |

### Credential Harvesting

- **LSASS Dump**: MiniDumpWriteDump (requires SeDebugPrivilege)
- **SAM Hashes**: Registry hive extraction (`reg save HKLM\SAM`)
- **Browser Passwords**: SQLite database parsing + DPAPI decryption (Chrome, Edge, Firefox)
- **WiFi Passwords**: `netsh wlan show profile key=clear`
- **Registry Credentials**: Winlogon DefaultPassword, cached credentials
- **Environment Variables**: All user/system env vars
- **Clipboard**: Real-time clipboard monitoring

### Operational Security (OPSEC)

1. **Anonymity**:
   - Tor/SOCKS5 proxy support (aiohttp-socks)
   - IP leak detection (WebRTC, DNS)
   - MAC address randomization
   - User-Agent rotation

2. **Anti-Forensics**:
   - Secure file deletion (multi-pass overwrite: random → zeros → delete)
   - Log wiping (Windows Event Logs, system logs)
   - Timestomping (SetFileTime with fake MACE timestamps)
   - Memory scrubbing (secure_zero() after crypto operations)

3. **Stealth**:
   - No console window (CREATE_NO_WINDOW flag)
   - Process hollowing (suspended process + memory replacement)
   - Reflective DLL injection (LoadLibrary in-memory)
   - API obfuscation (dynamic resolution, string encryption)

## Installation & Build

### Prerequisites

```bash
# Python 3.13+
python --version

# CMake 3.15+ (for C core)
cmake --version

# Rust 1.70+ (for agent)
rustc --version

# Go 1.21+ (for server)
go version

# OpenSSL development libraries
# Ubuntu/Debian:
sudo apt-get install libssl-dev libcurl4-openssl-dev

# Windows (vcpkg):
vcpkg install openssl:x64-windows curl:x64-windows
```

### Quick Build

```bash
# Clone repository
git clone https://github.com/4fqr/c2-phantom
cd c2-phantom

# Build all components
make all

# Or build individually:
make c-core        # Build C shared library
make rust-agent    # Build Rust agent
make go-server     # Build Go server

# Install Python package (editable)
pip install -e .
```

### Build Configuration

#### C Core (CMake)
```bash
cd build
cmake .. \
  -DCMAKE_BUILD_TYPE=Release \
  -DENABLE_HARDWARE_ACCEL=ON \
  -DENABLE_OBFUSCATION=OFF
make -j$(nproc)
```

#### Rust Agent
```bash
cd agent
cargo build --release --features full

# Minimal build (no image/clipboard):
cargo build --release --features minimal
```

#### Go Server
```bash
cd server
go build -ldflags="-s -w" -o c2server main.go
```

## Usage

### Initialize Framework

```python
import asyncio
from c2_phantom.orchestrator import C2Orchestrator

async def main():
    orchestrator = C2Orchestrator()
    await orchestrator.initialize()
    
    # Check system capabilities
    if orchestrator.c_core.check_aes_hardware():
        print("✓ AES-NI available")
    
    # Enable evasion
    orchestrator.enable_evasion()
    
    # Deploy agent
    agent_id = await orchestrator.deploy_agent("192.168.1.100", 443)
    
    # Execute command
    result = await orchestrator.execute_command(agent_id, "whoami /all")
    print(result)

asyncio.run(main())
```

### CLI Interface

```bash
# Start C2 server
c2-phantom server --host 0.0.0.0 --port 443 --tls

# Interactive shell
c2-phantom cli

# Generate agent
c2-phantom generate --format exe --output agent.exe

# List sessions
c2-phantom sessions list

# Interact with session
c2-phantom sessions interact <agent_id>
```

### C Core Direct Usage

```c
#include "c2core.h"

int main() {
    // Initialize syscalls
    syscall_init();
    
    // Bypass AMSI
    if (amsi_bypass_memory_patch() == 0) {
        printf("✓ AMSI bypassed\n");
    }
    
    // Bypass ETW
    if (etw_bypass_event_write() == 0) {
        printf("✓ ETW bypassed\n");
    }
    
    // Check for sandbox
    if (sandbox_check_all()) {
        printf("⚠ Sandbox detected, exiting\n");
        return 1;
    }
    
    // Inject into process
    inject_dll_remote_thread(1234, "payload.dll");
    
    return 0;
}
```

## Threat Model

### Adversary Capabilities

- **Tier 1**: AV/EDR with signature-based detection
  - Mitigation: Polymorphic code, encryption, direct syscalls
  
- **Tier 2**: Behavioral analysis and sandboxes
  - Mitigation: Anti-sandbox checks, timing delays, user interaction validation
  
- **Tier 3**: Advanced EDR with memory scanning
  - Mitigation: Process hollowing, reflective loading, in-memory execution

- **Tier 4**: SOC with human analysts
  - Mitigation: OPSEC discipline, proxy chains, low-and-slow beacons

### Detection Vectors

1. **Network**:
   - Risk: C2 traffic patterns, non-standard TLS, DNS tunneling
   - Mitigation: Domain fronting, encrypted beacons with jitter, legitimate UA strings

2. **Host**:
   - Risk: Unsigned binaries, suspicious process trees, registry persistence
   - Mitigation: Code signing, process migration, fileless execution

3. **Memory**:
   - Risk: In-memory PE analysis, YARA scanning
   - Mitigation: Memory obfuscation, encryption at rest, RWX cleanup

## Testing

### C Core Tests
```bash
cd build
make test_crypto
./test_crypto
```

### Rust Agent Tests
```bash
cd agent
cargo test --all-features
```

### Python Tests
```bash
pytest tests/ -v --cov=c2_phantom
```

## Legal & Ethics

**WARNING**: This framework is for authorized security assessments only. Unauthorized use against systems you do not own or have explicit permission to test is illegal and unethical.

- **Authorized Use Cases**: Red team engagements, penetration testing, security research, defensive capability development
- **Prohibited Use**: Unauthorized access, data theft, system disruption, malware distribution

**Operators are solely responsible for compliance with applicable laws** (CFAA, GDPR, local legislation).

## Development Roadmap

- [x] Python orchestration layer with FFI bindings
- [x] C core with syscalls, ETW bypass, inline hooks, anti-sandbox
- [x] Rust agent with commands, files, credentials, keylog, screenshots, persistence
- [ ] Go server with PostgreSQL, Redis, multi-listeners
- [ ] Complete protobuf RPC integration
- [ ] Interactive CLI with Rich UI
- [ ] Module system for extensibility
- [ ] Docker deployment
- [ ] Comprehensive test suite (>80% coverage)

## Contributing

PRs welcome. Focus areas:
- Cross-platform support (Linux, macOS)
- Additional persistence mechanisms
- New evasion techniques
- Performance optimizations
- Documentation improvements

## License

MIT License - See [LICENSE](LICENSE) for details.

## References

- [MITRE ATT&CK Framework](https://attack.mitre.org/)
- [Windows Internals (7th Edition)](https://docs.microsoft.com/en-us/sysinternals/resources/windows-internals)
- [Red Team Development and Operations](https://redteam.guide/)
- [Malware Analysis and Detection Engineering](https://www.wiley.com/en-us/Malware+Analysis+and+Detection+Engineering-p-9781394230822)

## Contact

- GitHub Issues: [https://github.com/4fqr/c2-phantom/issues](https://github.com/4fqr/c2-phantom/issues)
- Security Disclosures: Responsible disclosure via GitHub Security Advisories

---

**Disclaimer**: Educational purposes only. Misuse may result in civil/criminal liability.
