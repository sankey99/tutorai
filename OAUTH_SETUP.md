# 🔐 Google OAuth Setup Guide for TutorAI

This guide will walk you through setting up Google OAuth authentication for your TutorAI application.

## 📋 Prerequisites

- A Google account
- Access to Google Cloud Console
- Your TutorAI application running

## 🚀 Step 1: Create Google OAuth Credentials

### 1.1 Go to Google Cloud Console
1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account
3. Create a new project or select an existing one

### 1.2 Enable Google+ API
1. Go to **APIs & Services** > **Library**
2. Search for "Google+ API" or "Google Identity"
3. Click on it and press **Enable**

### 1.3 Create OAuth 2.0 Credentials
1. Go to **APIs & Services** > **Credentials**
2. Click **+ CREATE CREDENTIALS** > **OAuth client ID**
3. If prompted, configure the OAuth consent screen first:
   - Choose **External** user type
   - Fill in the required fields:
     - App name: `TutorAI`
     - User support email: Your email
     - Developer contact: Your email
   - Add your email to test users
   - Save and continue through the steps

### 1.4 Configure OAuth Client
1. Application type: **Web application**
2. Name: `TutorAI OAuth Client`
3. Authorized redirect URIs:
   - For local development: `http://localhost:7860/auth/callback`
   - For production: `https://yourdomain.com/auth/callback`
   - For Gradio share URLs: `https://your-gradio-share-url.com/auth/callback`

### 1.5 Get Your Credentials
1. After creating, you'll see a popup with:
   - **Client ID** (copy this)
   - **Client Secret** (copy this)
2. Save these credentials securely

## 🔧 Step 2: Configure Your Application

### 2.1 Update Environment Variables
Add these to your `.env` file:

```bash
# Existing OpenAI key
OPENAI_API_KEY=your_openai_key_here

# New Google OAuth credentials
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:7860/auth/callback
```

### 2.2 For Production/Public URLs
If you're using Gradio's `--share` feature or deploying to a public URL:

```bash
# For Gradio share URLs
GOOGLE_REDIRECT_URI=https://your-gradio-share-url.com/auth/callback

# For custom domain
GOOGLE_REDIRECT_URI=https://yourdomain.com/auth/callback
```

## 🚀 Step 3: Run with OAuth

### 3.1 Install Dependencies
```bash
pip install -r requirements.txt
```

### 3.2 Launch with OAuth
```bash
# For local development
python app.py --oauth

# For public sharing with OAuth
python app.py --oauth --share

# For custom host/port
python app.py --oauth --host 0.0.0.0 --port 8080
```

## 🔍 Step 4: Test the Setup

1. **Start the application** with `--oauth` flag
2. **Open your browser** to the application URL
3. **You should see a login page** instead of the direct Gradio interface
4. **Click "Sign in with Google"**
5. **Complete the OAuth flow**
6. **You should be redirected** to the TutorAI interface

## 🛠️ Troubleshooting

### Common Issues

**"Invalid redirect URI"**
- Make sure the redirect URI in your Google OAuth settings matches exactly
- Check for trailing slashes or HTTP vs HTTPS mismatches

**"OAuth consent screen not configured"**
- Complete the OAuth consent screen setup in Google Cloud Console
- Add your email as a test user

**"Client ID not found"**
- Double-check your `.env` file has the correct `GOOGLE_CLIENT_ID`
- Make sure there are no extra spaces or quotes

**"Authentication failed"**
- Verify your `GOOGLE_CLIENT_SECRET` is correct
- Check that the Google+ API is enabled in your project

### Debug Mode
To see detailed error messages, you can modify the Flask app to run in debug mode:

```python
oauth_app.run(host=args.host, port=args.port, debug=True)
```

## 🔒 Security Considerations

1. **Never commit your `.env` file** to version control
2. **Use HTTPS in production** for secure token transmission
3. **Regularly rotate your OAuth credentials**
4. **Monitor OAuth usage** in Google Cloud Console
5. **Set up proper session management** for production use

## 📚 Additional Resources

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Google Cloud Console](https://console.cloud.google.com/)
- [Gradio Documentation](https://gradio.app/docs/)

## 🆘 Getting Help

If you encounter issues:
1. Check the console output for error messages
2. Verify your OAuth credentials are correct
3. Ensure all redirect URIs are properly configured
4. Test with a simple OAuth flow first

---

**Happy Learning with Secure TutorAI! 🐍🔐**
