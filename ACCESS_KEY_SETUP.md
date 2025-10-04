# 🔑 Access Key Authentication Setup Guide for TutorAI

This guide explains how to set up access key authentication for your TutorAI application.

## 📋 Overview

Access key authentication allows you to control access to your TutorAI app using username/password combinations stored in environment variables.

## 🔧 Setup Instructions

### 1. Configure Environment Variables

Add these to your `.env` file:

```bash
# Required: OpenAI API key
OPENAI_API_KEY=your_openai_key_here

# Required: List of allowed usernames (JSON array)
USERS=["admin", "teacher1", "student1", "parent1"]

# Required: List of access keys (JSON array) - SHA256 hashed
ACCESS_KEYS=["5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8", "another_hashed_key", "third_hashed_key", "fourth_hashed_key"]
```

### 2. Generate Access Keys

Access keys should be stored as SHA256 hashes. Here's how to generate them:

**Using Python:**
```python
import hashlib

# Generate hash for password "mypassword123"
password = "mypassword123"
hashed = hashlib.sha256(password.encode()).hexdigest()
print(hashed)  # Use this in ACCESS_KEYS
```

**Using command line:**
```bash
echo -n "mypassword123" | sha256sum
```

### 3. Example Configuration

```bash
# .env file example
OPENAI_API_KEY=sk-your-openai-key-here
USERS=["admin", "teacher", "student"]
ACCESS_KEYS=[
  "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8",
  "ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f", 
  "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3"
]
```

**Corresponding credentials:**
- Username: `admin`, Password: `hello`
- Username: `teacher`, Password: `password123`
- Username: `student`, Password: `abc`

## 🚀 Running with Access Key Authentication

### Basic Usage
```bash
./run.sh --auth
```

### With Public Sharing
```bash
./run.sh --auth --share
```

### Custom Port
```bash
./run.sh --auth --port 8080
```

## 🔐 How Authentication Works

### Gradio Native Authentication
- ✅ **Uses `gradio.launch(auth=function)`** - Native Gradio authentication
- ✅ **Client-side password hashing** - SHA256 hashing before transmission
- ✅ **Full Gradio compatibility** - Works with sharing, all features
- ✅ **Secure transmission** - Passwords hashed before network transmission

### Authentication Flow
1. **User enters credentials** - Username and access key
2. **JavaScript hashes password** - SHA256 hash on client side
3. **Hashed password transmitted** - Secure network transmission
4. **Server validates hash** - Compares with stored SHA256 hashes
5. **Access granted/denied** - Based on credential validation

## 🔒 Security Features

- **SHA256 Hashing**: Access keys are stored as hashed values
- **Session Management**: Users stay logged in during their session
- **Secure Storage**: Keys are stored in environment variables, not in code
- **Index Matching**: Username and access key are matched by array index

## 📝 User Management

### Adding New Users

1. **Add username to USERS array:**
   ```bash
   USERS=["admin", "teacher", "student", "newuser"]
   ```

2. **Add corresponding hashed access key to ACCESS_KEYS array:**
   ```bash
   ACCESS_KEYS=[
     "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8",
     "ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f",
     "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3",
     "new_hashed_key_here"
   ]
   ```

### Removing Users

1. **Remove username from USERS array**
2. **Remove corresponding access key from ACCESS_KEYS array**
3. **Maintain the same order in both arrays**

## 🛠️ Troubleshooting

### Common Issues

**"Invalid username or access key"**
- Check that the username exists in the USERS array
- Verify the access key hash matches the stored hash
- Ensure the arrays have the same length and order

**"Authentication failed"**
- Verify your .env file is properly formatted
- Check that JSON arrays are valid
- Ensure no extra spaces or quotes in the arrays

**"User not found"**
- Make sure the username is in the USERS array
- Check for typos in the username
- Verify the user index matches the access key index

### Debug Mode

To see detailed error messages, you can modify the Flask app to run in debug mode:

```python
access_app.run(host=args.host, port=args.port, debug=True)
```

## 🔄 Switching Authentication Methods

You can use different authentication methods:

**No Authentication:**
```bash
./run.sh
```

**Access Key Authentication:**
```bash
./run.sh --auth
```

**Google OAuth Authentication:**
```bash
./run.sh --oauth
```

**Note:** You cannot use both `--auth` and `--oauth` at the same time.

## 📚 Additional Resources

- [SHA256 Hash Generator](https://www.sha256hash.com/)
- [JSON Array Format](https://www.json.org/json-en.html)
- [Environment Variables Guide](https://docs.python.org/3/library/os.html#os.environ)

---

**Secure Learning with TutorAI! 🐍🔑**
