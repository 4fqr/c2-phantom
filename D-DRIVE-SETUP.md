# 🔮 C2 Phantom - D: Drive Setup Guide

## ✅ Installation Complete!

Your C2 Phantom installation on **D:\c2-phantom** is ready to use!

---

## 🚀 How to Use

### Option 1: Activate Virtual Environment (Recommended)

```powershell
# Navigate to the project
cd D:\c2-phantom

# Activate the virtual environment
.\.venv\Scripts\Activate.ps1

# Now you can use 'phantom' directly
phantom --help
phantom --version
phantom init
```

### Option 2: Run Without Activation

```powershell
# Use the full Python path
D:\c2-phantom\.venv\Scripts\python.exe -m c2_phantom.cli --help
D:\c2-phantom\.venv\Scripts\python.exe -m c2_phantom.cli --version
D:\c2-phantom\.venv\Scripts\python.exe -m c2_phantom.cli init
```

### Option 3: Use the run.ps1 Script (Already exists in repo)

```powershell
cd D:\c2-phantom
.\run.ps1 --help
.\run.ps1 init
.\run.ps1 connect https://target.example.com
```

---

## 📋 Available Commands

```
phantom init         # Initialize configuration and generate keys
phantom connect      # Establish connection to target
phantom list         # List active sessions
phantom upload       # Upload files to target
phantom execute      # Execute commands on target
phantom plugin       # Manage plugins
```

---

## 🧪 Running Tests

```powershell
# Activate venv first
.\.venv\Scripts\Activate.ps1

# Run tests
pytest

# Run with coverage
pytest --cov=c2_phantom --cov-report=html
```

---

## 🔧 Development

```powershell
# Activate venv
.\.venv\Scripts\Activate.ps1

# Install in editable mode (already done)
pip install -e .

# Run code formatting
black c2_phantom/
isort c2_phantom/

# Run linting
flake8 c2_phantom/
mypy c2_phantom/
```

---

## 📝 Example Usage

```powershell
# Activate environment
.\.venv\Scripts\Activate.ps1

# Initialize C2 framework
phantom init

# Connect to a target with AES-256 encryption
phantom connect https://target.example.com --encrypt aes256

# List active sessions
phantom list --status active

# Upload a file
phantom upload C:\local\file.txt /remote/path/file.txt --session sess_001

# Execute a command
phantom execute "whoami" --session sess_001 --output
```

---

## 💡 Quick Tips

1. **Always activate the venv first** for the cleanest experience
2. **Use tab completion** for commands (when venv is activated)
3. **Check logs** at `~/.phantom/logs/phantom.log`
4. **Configuration** is stored at `~/.phantom/config.yaml`
5. **Plugins** go in `~/.phantom/plugins/`

---

## 🔗 Links

- **GitHub**: https://github.com/4fqr/c2-phantom
- **Documentation**: See README.md
- **Issues**: https://github.com/4fqr/c2-phantom/issues

---

## 🎉 You're All Set!

Your C2 Phantom framework is installed and ready to use on D: drive.

**Next Steps:**
1. Activate the virtual environment
2. Run `phantom init` to set up your configuration
3. Explore the commands with `phantom --help`
4. Read the full README.md for advanced features

Happy hacking! 🚀
