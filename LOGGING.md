# 📊 TutorAI Logging System

## 🔍 Overview

TutorAI now includes comprehensive logging that captures:
- **Access logs** - Authentication attempts, IP addresses, locations
- **Application logs** - Code executions, help requests, errors
- **Security events** - Failed logins, suspicious activity

## 📁 Log Files

### `logs/access.log`
**Captures all access-related events:**
- ✅ **Authentication attempts** (success/failure)
- ✅ **IP addresses** and **geographic locations**
- ✅ **Application startup/shutdown**
- ✅ **User sessions**

**Example entries:**
```
2024-01-15 10:30:15,123 - IP: 192.168.1.100 | Location: Local Network | Event: AUTH_SUCCESS | Details: User authenticated: admin
2024-01-15 10:31:22,456 - IP: 203.0.113.45 | Location: New York, NY, United States | Event: AUTH_FAILED | Details: Invalid access key for user: student1
```

### `logs/app.log`
**Captures all application events:**
- ✅ **Code executions** (success/failure)
- ✅ **Help requests** and AI responses
- ✅ **Application startup/shutdown**
- ✅ **Errors and warnings**

**Example entries:**
```
2024-01-15 10:30:15,123 - INFO - Code execution started | Details: Question: Hello, Python! Write a Python program... | Code: print("Hello, World!")
2024-01-15 10:30:15,456 - INFO - Code execution successful | Details: Question: Hello, Python! Write a Python program... | Output: Hello, World!
2024-01-15 10:31:22,789 - ERROR - Code execution failed | Details: Question: Your Age. Store your age... | Error: NameError: name 'age' is not defined | Code: print(age)
```

## 🚀 Using the Log Viewer

### View Access Logs
```bash
# View last 50 access log entries
python view_logs.py access

# View last 100 access log entries
python view_logs.py access 100
```

### View Application Logs
```bash
# View last 50 application log entries
python view_logs.py app

# View last 100 application log entries
python view_logs.py app 100
```

### View Code Executions Only
```bash
# View all code execution logs
python view_logs.py code
```

### View Authentication Attempts
```bash
# View all authentication attempts
python view_logs.py auth
```

### View Log Statistics
```bash
# View log file statistics
python view_logs.py stats
```

### View All Logs
```bash
# View both access and app logs (last 20 lines each)
python view_logs.py all

# View both access and app logs (last 50 lines each)
python view_logs.py all 50
```

## 📊 What Gets Logged

### 🔐 Authentication Events
- **AUTH_SUCCESS** - Successful login
- **AUTH_FAILED** - Failed login attempt
- **AUTH_ERROR** - Authentication system error
- **APP_START** - Application startup

### 🐍 Code Execution Events
- **Code execution started** - When user clicks "Run Code"
- **Code execution successful** - Code runs without errors
- **Code execution failed** - Code throws an exception
- **Help request received** - When user clicks "Get Help"
- **Help response generated** - AI response created

### 🌐 Access Events
- **IP addresses** - Client IP addresses
- **Geographic locations** - City, region, country
- **User sessions** - Login/logout events
- **Application events** - Startup, shutdown, configuration

## 🔒 Security Features

### IP Address Tracking
- ✅ **External IP detection** - Uses ipify.org API
- ✅ **Local network detection** - Identifies local connections
- ✅ **Fallback to hostname** - If external IP unavailable

### Geographic Location
- ✅ **City, region, country** - Using ip-api.com
- ✅ **Local network detection** - For internal connections
- ✅ **Error handling** - Graceful fallback for API failures

### Privacy Considerations
- ✅ **No sensitive data logged** - Passwords are hashed
- ✅ **IP addresses only** - No personal information
- ✅ **Code truncation** - Long code snippets are truncated
- ✅ **Error sanitization** - Sensitive error details filtered

## 📈 Log Analysis

### Common Patterns
```bash
# Find all successful authentications
grep "AUTH_SUCCESS" logs/access.log

# Find all code execution errors
grep "Code execution failed" logs/app.log

# Find help requests
grep "Help request received" logs/app.log

# Find specific user activity
grep "admin" logs/access.log
```

### Monitoring Commands
```bash
# Monitor logs in real-time
tail -f logs/access.log
tail -f logs/app.log

# Count authentication attempts
grep -c "AUTH_" logs/access.log

# Count code executions
grep -c "Code execution" logs/app.log
```

## 🛠️ Log Management

### Log Rotation
Logs will grow over time. Consider implementing log rotation:

```bash
# Archive old logs
mv logs/access.log logs/access.log.$(date +%Y%m%d)
mv logs/app.log logs/app.log.$(date +%Y%m%d)

# Create new log files
touch logs/access.log logs/app.log
```

### Log Cleanup
```bash
# Remove logs older than 30 days
find logs/ -name "*.log.*" -mtime +30 -delete
```

## 📋 Log Format

### Access Log Format
```
TIMESTAMP - IP: <ip_address> | Location: <location> | Event: <event_type> | Details: <details>
```

### Application Log Format
```
TIMESTAMP - LEVEL - MESSAGE | Details: <details>
```

## 🚨 Security Alerts

### Suspicious Activity Patterns
- **Multiple failed logins** from same IP
- **Code execution errors** with malicious patterns
- **Unusual geographic locations**
- **High frequency requests**

### Monitoring Commands
```bash
# Find multiple failed logins from same IP
grep "AUTH_FAILED" logs/access.log | cut -d'|' -f1 | sort | uniq -c | sort -nr

# Find code execution errors
grep "Code execution failed" logs/app.log | tail -20

# Find unusual locations
grep -v "Local Network" logs/access.log | grep -v "Unknown Location"
```

---

**Happy Logging! 📊🔍**


