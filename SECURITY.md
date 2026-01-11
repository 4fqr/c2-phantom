# 🛡️ C2-Phantom Security Hardening Guide

## 🎯 Production Security Requirements

### ⚠️ CRITICAL - Must Complete Before Production

1. **Change ALL Default Credentials**
   ```powershell
   # Generate secure API key
   python -c "import secrets; print('API_KEY=' + secrets.token_urlsafe(48))"
   
   # Generate session secrets
   python -c "import secrets; print('SESSION_SECRET=' + secrets.token_hex(32))"
   python -c "import secrets; print('JWT_SECRET=' + secrets.token_hex(32))"
   ```

2. **Enable TLS/HTTPS**
   ```powershell
   # Generate self-signed certificate (development)
   openssl req -x509 -newkey rsa:4096 -keyout server.key -out server.crt -days 365 -nodes -subj "/CN=c2phantom.local"
   
   # Or use Let's Encrypt (production)
   certbot certonly --standalone -d your-domain.com
   ```

3. **Secure Database**
   ```sql
   -- Change PostgreSQL password
   ALTER USER c2phantom WITH PASSWORD 'strong_random_password_here';
   
   -- Restrict network access (pg_hba.conf)
   host c2phantom c2phantom 127.0.0.1/32 scram-sha-256
   
   -- Enable SSL connections
   ssl = on
   ```

4. **Enable Redis Authentication**
   ```bash
   # redis.conf
   requirepass your_strong_redis_password_here
   bind 127.0.0.1
   ```

5. **Configure Firewall**
   ```powershell
   # Windows Firewall - Allow only specific IPs
   New-NetFirewallRule -DisplayName "C2-Phantom HTTPS" `
       -Direction Inbound -LocalPort 443 -Protocol TCP `
       -Action Allow -RemoteAddress 10.0.0.0/8
   
   # Block HTTP if using HTTPS
   New-NetFirewallRule -DisplayName "Block C2-Phantom HTTP" `
       -Direction Inbound -LocalPort 8080 -Protocol TCP -Action Block
   ```

---

## 🔒 Security Hardening Checklist

### Network Security

- [ ] **TLS 1.3 Enabled** - Enforce modern TLS only
  ```env
  TLS_ENABLED=true
  TLS_MIN_VERSION=1.3
  ```

- [ ] **Certificate Pinning** - Prevent MITM attacks
  ```powershell
  # Get certificate fingerprint
  openssl x509 -in server.crt -noout -fingerprint -sha256
  ```
  ```env
  CERT_PINS=sha256/ABCD1234...
  ```

- [ ] **IP Whitelisting** - Restrict server access
  ```env
  IP_WHITELIST=10.0.0.0/8,192.168.1.0/24
  ```

- [ ] **Rate Limiting** - Prevent DOS attacks
  ```env
  RATE_LIMIT_ENABLED=true
  RATE_LIMIT_REQUESTS=100
  RATE_LIMIT_WINDOW=60
  ```

### Authentication & Authorization

- [ ] **Strong API Keys** - 32+ character random strings
  ```env
  API_KEY=Use-Output-From-secrets.token_urlsafe(48)
  ```

- [ ] **Session Security** - Separate secrets for sessions and JWTs
  ```env
  SESSION_SECRET=64_char_hex_string
  JWT_SECRET=different_64_char_hex_string
  ```

- [ ] **Key Rotation** - Automatic rotation every 24 hours
  ```env
  KEY_ROTATION_HOURS=24
  ```

- [ ] **Multi-Factor Authentication** - For operator access (planned feature)

### Data Protection

- [ ] **Database Encryption** - Encrypt data at rest
  ```sql
  -- PostgreSQL with pgcrypto
  CREATE EXTENSION pgcrypto;
  ```
  ```env
  DB_ENCRYPTION=true
  DB_SSL_MODE=verify-full
  ```

- [ ] **Memory Encryption** - Protect sensitive data in memory
  ```env
  MEMORY_ENCRYPTION=true
  ```

- [ ] **Secure Logging** - Redact sensitive information
  ```env
  AUDIT_LOGGING=true
  LOG_LEVEL=info  # Avoid 'debug' in production
  ```

- [ ] **Data Retention** - Auto-delete old data
  ```env
  DATA_RETENTION_DAYS=90
  LOG_RETENTION_DAYS=30
  ```

### Agent Security

- [ ] **Kill Date** - Agents self-destruct after date
  ```env
  AGENT_KILL_DATE=2026-12-31T23:59:59Z
  ```

- [ ] **Working Hours** - Agents only active during business hours
  ```env
  AGENT_WORKING_HOURS=09:00-17:00
  ```

- [ ] **Beacon Jitter** - Randomize traffic patterns
  ```env
  AGENT_BEACON_INTERVAL=30
  AGENT_BEACON_JITTER=20
  ```

- [ ] **Anti-Analysis** - Prevent VM/debugger execution
  ```env
  ANTI_VM=true
  ANTI_DEBUG=true
  PREVENT_PROCESS_HOLLOWING=true
  ```

### Monitoring & Alerting

- [ ] **Security Alerts** - Notify on suspicious activity
  ```env
  ALERT_WEBHOOK=https://your-alerting-system/webhook
  ALERT_EMAIL=security@yourcompany.com
  ```

- [ ] **Metrics Collection** - Monitor server health
  ```env
  METRICS_ENABLED=true
  METRICS_PORT=9090  # Prometheus
  ```

- [ ] **Audit Logging** - Full operation trail
  ```env
  AUDIT_LOGGING=true
  ```

### Compliance

- [ ] **Operator Identification** - Required for audit
  ```env
  OPERATOR_NAME=John Doe
  OPERATOR_EMAIL=jdoe@company.com
  OPERATOR_ORG=Red Team Inc
  ```

- [ ] **Engagement Tracking** - Link to authorized test
  ```env
  ENGAGEMENT_ID=PENTEST-2026-001
  COMPLIANCE_MODE=redteam
  ```

- [ ] **Legal Documentation** - Maintain authorization paperwork

---

## 🚨 Incident Response

### Compromise Detection

**Signs of compromise:**
- Unauthorized API keys in logs
- Agents from unexpected IPs/locations
- Unusual task execution patterns
- Database access anomalies

**Immediate Actions:**
1. Rotate all API keys and secrets
2. Audit database for unauthorized changes
3. Review firewall logs for suspicious IPs
4. Check agent list for rogue implants
5. Examine task history for unauthorized commands

### Emergency Shutdown

```powershell
# Stop server immediately
docker-compose down

# Or kill process
Get-Process c2-server | Stop-Process -Force

# Disable database access
psql -c "ALTER USER c2phantom WITH NOLOGIN;"

# Block network access
New-NetFirewallRule -DisplayName "Emergency Block C2" `
    -Direction Inbound -LocalPort 443,8080 -Protocol TCP -Action Block
```

### Forensic Preservation

```powershell
# Enable legal hold (prevent data deletion)
# In .env:
LEGAL_HOLD=true

# Backup database immediately
pg_dump c2phantom > incident_$(Get-Date -Format "yyyyMMdd_HHmmss").sql

# Backup logs
Copy-Item -Recurse ~/.phantom/logs incident_logs_$(Get-Date -Format "yyyyMMdd_HHmmss")

# Copy Redis data
redis-cli --rdb incident_redis.rdb
```

---

## 🔐 Encryption Details

### Supported Algorithms

**Symmetric Encryption:**
- AES-256-GCM (default, NIST approved)
- ChaCha20-Poly1305 (faster on mobile/ARM)
- AES-128-GCM (lower overhead)

**Key Exchange:**
- ECDH with Curve25519 (modern, fast)
- RSA-4096 (legacy compatibility)

**Hashing:**
- SHA-256 (integrity checks)
- BLAKE2b (high performance)

### Key Management

```powershell
# Generate encryption keys (first time)
python phantom.py init

# Rotate keys manually
python phantom.py rotate-keys

# Export keys for backup (SECURE STORAGE ONLY)
python phantom.py export-keys --output backup_keys_encrypted.bin
```

---

## 🌐 Network Evasion

### Domain Fronting

```env
# Use CDN to mask C2 traffic
DOMAIN_FRONT_TARGET=cloudfront.amazonaws.com
```

**Example agent configuration:**
```rust
// Agent connects to CDN, routes to C2
let client = HttpsClient::new()
    .domain_front("cloudfront.amazonaws.com")
    .host_header("your-c2-server.com");
```

### DNS Tunneling

```env
# Fallback to DNS if HTTPS blocked
DNS_TUNNELING=true
DNS_SERVER=8.8.8.8
```

### Proxy Chains

```env
# Route through multiple proxies
PROXY_URL=socks5://proxy1:1080,socks5://proxy2:1080
```

---

## 📊 Security Metrics

### Monitor These KPIs

1. **Authentication Failures** - Alert on >5 failed attempts
2. **Unusual Agent Registration** - New agents from unknown IPs
3. **High Task Failure Rate** - Possible detection/blocking
4. **Database Query Anomalies** - Injection attempts
5. **Certificate Validation Failures** - MITM attempts

### Grafana Dashboard (example metrics)

```prometheus
# Failed authentication attempts
rate(c2_auth_failures_total[5m])

# Active agent count
c2_agents_active

# Task execution rate
rate(c2_tasks_completed_total[1m])

# Database connection errors
rate(c2_db_errors_total[5m])
```

---

## 🛠️ Security Tools

### Recommended Security Scanning

```powershell
# TLS configuration test
Invoke-WebRequest -Uri "https://www.ssllabs.com/ssltest/analyze.html?d=your-c2-server.com"

# Port scanning (verify firewall)
nmap -p 1-65535 -sV -sS -T4 your-c2-server.com

# SQL injection testing
sqlmap -u "http://your-c2-server.com/api/v1/agents" --headers="X-API-Key: test"

# Web application scanning
nikto -h http://your-c2-server.com
```

### Log Analysis

```powershell
# Search for failed authentications
Select-String -Path ~/.phantom/logs/*.log -Pattern "authentication failed"

# Find suspicious IPs
Get-Content ~/.phantom/logs/access.log | Select-String -Pattern "POST /register" | Group-Object

# Detect rapid beacon activity (possible automated scanning)
Get-Content ~/.phantom/logs/beacon.log | Where-Object {$_ -match "429"} | Measure-Object
```

---

## 📖 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [CIS Controls](https://www.cisecurity.org/controls)
- [MITRE ATT&CK](https://attack.mitre.org/)

---

## ⚖️ Legal & Ethical Use

### ✅ Authorized Use Cases

- Penetration testing with written authorization
- Red team exercises within scope
- Security research on owned systems
- Educational training environments

### ❌ Prohibited Activities

- Unauthorized access to systems
- Data exfiltration without consent
- Malicious damage or disruption
- Violating applicable laws

**Always obtain explicit written authorization before deployment.**

---

**🔒 Security is a continuous process, not a one-time setup.**
