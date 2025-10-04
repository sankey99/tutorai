# 🔗 Sharing with Authentication - Guide

## ❌ Why `--share` Doesn't Work with Authentication

When you use `--auth` or `--oauth` flags, the app uses **Flask** instead of Gradio's native launch method. This means:

- ✅ **Authentication works** - Users must login before accessing the app
- ❌ **Gradio sharing doesn't work** - No public URL is created
- ❌ **Flask doesn't support Gradio's sharing** - They're separate systems

## 🔧 Solutions for Public Access with Authentication

### Option 1: Use Without Authentication (Recommended for Testing)

**For testing Gradio sharing:**
```bash
# This WILL create a public URL
./run.sh --share
```

**For production with authentication:**
```bash
# This will NOT create a public URL, but provides security
./run.sh --auth --share
```

### Option 2: Deploy to a Cloud Platform

**Recommended platforms:**
- **Hugging Face Spaces** - Free hosting with authentication
- **Railway** - Easy deployment with custom domains
- **Heroku** - Professional hosting
- **DigitalOcean** - VPS with full control

### Option 3: Use a Reverse Proxy

**With nginx or Apache:**
```nginx
# Example nginx configuration
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:7777;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Option 4: Use ngrok for Tunneling

**Install ngrok:**
```bash
# Install ngrok
npm install -g ngrok
# or download from https://ngrok.com/
```

**Create tunnel:**
```bash
# Run your app with authentication
./run.sh --auth

# In another terminal, create tunnel
ngrok http 7777
```

**Result:** You'll get a public URL like `https://abc123.ngrok.io` that works with authentication!

## 🚀 Recommended Workflow

### For Development/Testing:
```bash
# Test without authentication
./run.sh --share
# This creates: https://xxxxx.gradio.live
```

### For Production with Security:
```bash
# Use authentication (no public URL)
./run.sh --auth

# Then use ngrok for public access
ngrok http 7777
# This creates: https://abc123.ngrok.io
```

### For Permanent Deployment:
1. **Deploy to Hugging Face Spaces** (free, supports authentication)
2. **Use Railway/Heroku** with custom domain
3. **Set up VPS** with nginx reverse proxy

## 📋 Environment Variables for Different Scenarios

### Local Development (No Auth):
```bash
OPENAI_API_KEY=your_key_here
# No USERS or ACCESS_KEYS needed
```

### Local with Authentication:
```bash
OPENAI_API_KEY=your_key_here
USERS=["admin", "user1"]
ACCESS_KEYS=["hashed_key1", "hashed_key2"]
```

### Production with ngrok:
```bash
OPENAI_API_KEY=your_key_here
USERS=["admin", "user1"]
ACCESS_KEYS=["hashed_key1", "hashed_key2"]
# Run: ./run.sh --auth
# Then: ngrok http 7777
```

## 🔍 Troubleshooting

### "No public URL created"
- ✅ **Expected behavior** when using `--auth` or `--oauth`
- 💡 **Solution:** Use ngrok or deploy to a cloud platform

### "Authentication not working"
- Check your `.env` file has correct `USERS` and `ACCESS_KEYS`
- Verify the arrays have the same length
- Ensure access keys are SHA256 hashed

### "Gradio interface not loading"
- Make sure you're logged in first
- Check that the authentication was successful
- Try refreshing the page

## 🎯 Best Practices

1. **For Testing:** Use `./run.sh --share` (no authentication)
2. **For Security:** Use `./run.sh --auth` + ngrok
3. **For Production:** Deploy to a cloud platform
4. **For Teams:** Use Hugging Face Spaces with authentication

---

**Happy Secure Sharing! 🔐🌐**
