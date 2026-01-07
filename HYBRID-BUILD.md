# Multi-Language C2 Build Guide
## C/Rust/Go/Assembly Hybrid Framework

Complete build instructions for the hybrid C2 architecture.

---

## Prerequisites

### Windows Environment
```powershell
# C/C++ compiler
winget install Microsoft.VisualStudio.2022.Community

# Build tools
winget install Kitware.CMake
winget install NASM.NASM
winget install OpenSSL.OpenSSL

# Language toolchains
winget install Rustlang.Rustup
winget install GoLang.Go

# Rust targets
rustup target add x86_64-pc-windows-gnu
rustup target add i686-pc-windows-gnu
```

### Linux Environment
```bash
# Debian/Ubuntu
sudo apt install -y build-essential cmake nasm libssl-dev pkg-config

# Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
rustup target add x86_64-unknown-linux-musl

# Go
wget https://go.dev/dl/go1.21.5.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.21.5.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin
```

---

## Quick Build

```bash
# Build all components
make all

# Or individually
make core      # C libraries
make agent     # Rust agent
make server    # Go server
make stagers   # ASM stagers
```

---

## C Core Libraries

```bash
mkdir -p build
cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
cmake --build . --config Release
```

**Output:**
- `build/libc2_crypto.a` - AES-256-GCM
- `build/libc2_network.a` - TLS 1.3 beacon
- `build/libc2_process.a` - Process injection
- `build/libc2_evasion.a` - AMSI/ETW bypass

---

## Rust Agent

```bash
cd agent

# Windows
cargo build --release --target x86_64-pc-windows-gnu

# Linux
cargo build --release --target x86_64-unknown-linux-musl
```

**Output:** `~200KB` agent binary

**Optimize:**
```bash
strip target/x86_64-pc-windows-gnu/release/c2-agent.exe
upx --best --lzma target/x86_64-pc-windows-gnu/release/c2-agent.exe
```

---

## Go Server

```bash
cd server
go mod download
go build -ldflags="-s -w" -o ../build/c2-server
```

**Features:**
- 10,000+ concurrent agents
- TLS 1.3 listener
- PostgreSQL backend
- REST API

---

## Assembly Stagers

```bash
nasm -f win64 stager/http_stager.asm -o build/stagers/http_stager.bin
nasm -f win64 stager/dns_stager.asm -o build/stagers/dns_stager.bin
```

**Output:** Position-independent shellcode (~1KB)

---

## Running the Server

### Setup Database
```bash
sudo -u postgres psql
CREATE DATABASE c2phantom;
CREATE USER c2phantom WITH PASSWORD 'c2phantom';
GRANT ALL PRIVILEGES ON DATABASE c2phantom TO c2phantom;
```

### Generate TLS Certs
```bash
mkdir -p server/certs
openssl req -x509 -newkey rsa:4096 -keyout server/certs/server.key \
  -out server/certs/server.crt -days 365 -nodes
```

### Start Server
```bash
export DATABASE_URL="host=localhost user=c2phantom password=c2phantom dbname=c2phantom"
./build/c2-server
```

---

## Performance

- **C Crypto:** 2.5 GB/s (AES-NI)
- **Agent Size:** 200KB (compressed)
- **Server Capacity:** 10K+ agents
- **Beacon Latency:** <10ms

---

## Security Notes

⚠️ **Use only with authorization**
⚠️ **Never upload binaries to VirusTotal**
⚠️ **Test in isolated environments**

See [ARCHITECTURE.md](ARCHITECTURE.md) for design details.
