# C2 Phantom - Multi-Language Architecture

## 🚀 **Vision: Military-Grade Hybrid C2**

### **Core Principles**
1. **Performance**: C/C++ for core engine and crypto
2. **Stealth**: Assembly for shellcode, process injection, anti-debugging
3. **Flexibility**: Python for orchestration and rapid development
4. **Compatibility**: Rust for cross-platform agent with zero dependencies
5. **Obfuscation**: Go for packed loaders and C2 server

---

## 📦 **Component Architecture**

```
c2-phantom/
├── core/                      # Core C/C++ Engine
│   ├── crypto/                # AES-256-GCM, ChaCha20, RSA (OpenSSL)
│   ├── network/               # Raw sockets, HTTP/2, DNS, ICMP
│   ├── process/               # Process injection, hollowing, DLL injection
│   └── evasion/               # AMSI/ETW bypass, anti-debug (ASM)
│
├── agent/                     # Rust Implant (Zero Dependencies)
│   ├── beacon/                # Beacon with jitter, TLS 1.3
│   ├── commands/              # Command execution engine
│   ├── persistence/           # Registry, WMI, scheduled tasks
│   └── stager/                # In-memory reflective loader
│
├── server/                    # Go C2 Server (High Performance)
│   ├── listener/              # HTTP/HTTPS/DNS/TCP listeners
│   ├── database/              # PostgreSQL for sessions/tasks
│   ├── api/                   # REST API for operators
│   └── teamserver/            # Multi-operator support
│
├── loader/                    # C Shellcode Loaders
│   ├── pe_loader/             # PE in-memory loader
│   ├── donut/                 # Donut-style shellcode generator
│   └── syscalls/              # Direct syscalls (ntdll bypass)
│
├── stager/                    # Assembly Stagers
│   ├── http_stager.asm        # HTTP download + exec
│   ├── dns_stager.asm         # DNS TXT record stager
│   └── smb_stager.asm         # SMB named pipe stager
│
├── obfuscation/               # C++ Obfuscators
│   ├── strings/               # String encryption (XOR, AES)
│   ├── control_flow/          # Control flow flattening
│   └── polymorphic/           # Polymorphic code engine
│
└── python/                    # Python Orchestration (Current)
    ├── cli/                   # Operator interface
    ├── modules/               # Post-exploitation modules
    └── plugins/               # Plugin system
```

---

## 🔥 **Technology Stack**

### **1. Core Engine (C/C++)**
**Why**: Raw performance, direct memory access, syscall access
- **Crypto**: OpenSSL 3.0+ for AES-256-GCM, RSA-4096, Ed25519
- **Network**: libuv for async I/O, raw sockets for custom protocols
- **Process**: Native Win32 API, direct syscalls via assembly
- **Anti-Debug**: Inline assembly for TEB/PEB checks

**Files**:
```c
// core/crypto/aes.c - Hardware AES-NI acceleration
// core/network/beacon.c - Low-level beacon with TLS 1.3
// core/process/inject.c - Process injection (CreateRemoteThread, QueueUserAPC)
// core/evasion/amsi.c - AMSI bypass via memory patching
```

### **2. Agent (Rust)**
**Why**: Memory safety, zero-cost abstractions, single-binary deployment
- **No Dependencies**: Statically linked, no runtime required
- **Cross-Platform**: Windows, Linux, macOS from single codebase
- **Size**: <500KB stripped binary
- **Evasion**: Compile-time obfuscation, no strings in binary

**Features**:
```rust
// agent/src/beacon.rs - Async beacon with Tokio
// agent/src/commands.rs - Command execution engine
// agent/src/crypto.rs - ChaCha20-Poly1305 (pure Rust, no OpenSSL)
// agent/src/loader.rs - Reflective DLL loader
```

### **3. C2 Server (Go)**
**Why**: Concurrency (goroutines), fast compilation, built-in HTTP/2
- **Performance**: Handle 10,000+ agents simultaneously
- **Database**: PostgreSQL for persistence, Redis for caching
- **API**: gRPC for internal comms, REST for operators
- **Packaging**: Single binary, cross-compile for all platforms

**Components**:
```go
// server/listener/http.go - HTTP/2 with H2C support
// server/listener/dns.go - DNS over HTTPS (DoH)
// server/database/postgres.go - Session/task persistence
// server/teamserver/multi_operator.go - Real-time collaboration
```

### **4. Loaders (C + Assembly)**
**Why**: Shellcode execution, in-memory PE loading, syscall obfuscation
- **PE Loader**: Load EXE/DLL from memory without touching disk
- **Donut Integration**: Convert .NET assemblies to shellcode
- **Syscalls**: Direct ntdll syscalls (no IAT hooking detection)

**Files**:
```c
// loader/pe_loader.c - Reflective PE loader
// loader/syscalls.c - Direct syscall stubs (NtAllocateVirtualMemory, etc.)
```

```asm
; stager/http_stager.asm - Position-independent shellcode
; stager/syscalls.asm - Direct syscall trampoline
```

### **5. Obfuscation Engine (C++)**
**Why**: LLVM-based obfuscation, control flow flattening
- **String Encryption**: All strings encrypted at compile-time
- **Control Flow**: Flatten control flow (no if/else/switch patterns)
- **Polymorphic**: Different binary signature on each compile

**Tools**:
```cpp
// obfuscation/llvm_pass.cpp - Custom LLVM obfuscation pass
// obfuscation/string_encrypt.cpp - Compile-time string encryption
// obfuscation/cfg_flatten.cpp - Control flow graph flattening
```

---

## 🛠️ **Build System**

### **Makefile Structure**
```makefile
all: core agent server loader stager

core:
    cd core && cmake -DCMAKE_BUILD_TYPE=Release . && make

agent:
    cd agent && cargo build --release --target x86_64-pc-windows-gnu

server:
    cd server && go build -ldflags="-s -w" -o c2server

loader:
    cd loader && gcc -O3 -s -masm=intel -o pe_loader.exe pe_loader.c

stager:
    cd stager && nasm -f win64 http_stager.asm -o http_stager.bin
```

### **Cross-Compilation Targets**
- **Windows**: x86_64-pc-windows-gnu, i686-pc-windows-gnu
- **Linux**: x86_64-unknown-linux-musl (static binary)
- **macOS**: x86_64-apple-darwin, aarch64-apple-darwin

---

## 🔐 **Encryption & Obfuscation**

### **1. Network Encryption**
- **TLS 1.3**: Enforced for all HTTP traffic
- **Custom Protocol**: AES-256-GCM with ephemeral keys (ECDH)
- **DNS**: Encrypted payloads in TXT records (ChaCha20)

### **2. Binary Obfuscation**
- **String Encryption**: XOR + AES at compile-time
- **API Hashing**: No plaintext API names (CRC32 hashing)
- **Control Flow**: LLVM-based obfuscation
- **Packing**: UPX + custom stub for loader

### **3. Anti-Analysis**
- **Anti-Debug**: IsDebuggerPresent, CheckRemoteDebuggerPresent, TEB flags
- **Anti-VM**: CPUID checks, hypervisor detection, timing attacks
- **Anti-Sandbox**: Mouse movement, user interaction checks
- **Self-Destruct**: Secure wipe on detection

---

## 🚀 **Performance Targets**

| Metric | Target | Implementation |
|--------|--------|----------------|
| **Agent Size** | <500KB | Rust + static linking + UPX |
| **Beacon Latency** | <50ms | C beacon + libuv async I/O |
| **Server Capacity** | 10,000 agents | Go goroutines + Redis caching |
| **Startup Time** | <100ms | Lazy loading, on-demand modules |
| **Memory Usage** | <10MB | Rust zero-copy, arena allocators |
| **Detection Rate** | <5% | Polymorphic engine, syscalls |

---

## 📋 **Development Roadmap**

### **Phase 1: Core Infrastructure** (Week 1-2)
- [x] Python foundation (current)
- [ ] C crypto library (OpenSSL wrapper)
- [ ] Rust agent skeleton
- [ ] Go C2 server scaffold
- [ ] CMake + Cargo + Go build system

### **Phase 2: Stealth Components** (Week 3-4)
- [ ] Assembly stagers (HTTP, DNS, SMB)
- [ ] C PE loader (reflective DLL injection)
- [ ] Direct syscalls (ntdll bypass)
- [ ] AMSI/ETW patching (C + ASM)

### **Phase 3: Network Stack** (Week 5-6)
- [ ] HTTP/2 with TLS 1.3 (Go server)
- [ ] DNS over HTTPS (DoH)
- [ ] Raw TCP with custom protocol
- [ ] ICMP covert channel

### **Phase 4: Obfuscation** (Week 7-8)
- [ ] LLVM obfuscation pass
- [ ] String encryption (compile-time)
- [ ] Control flow flattening
- [ ] Polymorphic engine

### **Phase 5: Testing & Hardening** (Week 9-10)
- [ ] AV/EDR evasion testing
- [ ] Sandbox detection bypass
- [ ] Performance profiling
- [ ] Penetration testing

---

## 🎯 **Success Metrics**

1. **Stealth**: <5% detection rate on VirusTotal
2. **Performance**: 10,000 concurrent agents per server
3. **Reliability**: 99.9% uptime, zero crashes
4. **Portability**: Single binary, no dependencies
5. **Security**: Military-grade encryption, no vulnerabilities

---

## 🔧 **Development Environment**

### **Required Tools**
```bash
# C/C++
sudo apt install build-essential cmake clang llvm

# Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
rustup target add x86_64-pc-windows-gnu

# Go
wget https://go.dev/dl/go1.21.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.21.linux-amd64.tar.gz

# Assembly
sudo apt install nasm yasm

# Cross-compilation
sudo apt install mingw-w64 gcc-multilib
```

### **Build All Components**
```bash
make clean
make all -j$(nproc)
./scripts/package.sh  # Create release bundle
```

---

## 📊 **Component Communication**

```
┌─────────────┐     TLS 1.3      ┌─────────────┐
│ Rust Agent  │◄────────────────►│  Go Server  │
│ (Implant)   │  AES-256-GCM     │  (Listener) │
└─────────────┘                  └─────────────┘
       │                                 │
       │ Commands                        │ API
       ▼                                 ▼
┌─────────────┐                  ┌─────────────┐
│  C Loader   │                  │  PostgreSQL │
│ (In-Memory) │                  │  (Storage)  │
└─────────────┘                  └─────────────┘
       │                                 │
       │ Shellcode                       │ Sessions
       ▼                                 ▼
┌─────────────┐                  ┌─────────────┐
│ ASM Stager  │                  │ Python CLI  │
│ (Bootstrap) │                  │ (Operator)  │
└─────────────┘                  └─────────────┘
```

---

**This is the blueprint. Let's build it piece by piece, starting with the C crypto core. Ready?** 🚀
