# 🐍 TutorAI - Python Learning Assistant for Kids

A self-contained Python learning application designed to teach programming to children through interactive exercises and AI-powered tutoring.

## ✨ Features

- **Interactive Learning**: 10 progressive Python exercises for beginners
- **AI-Powered Help**: Get personalized guidance from GPT-4o-mini
- **Safe Code Execution**: Run Python code in a secure environment
- **Kid-Friendly Interface**: Simple, colorful web interface
- **Access Key Authentication**: Simple username/password authentication
- **Self-Contained**: No complex setup required

## 🚀 Quick Start

### Option 1: Docker (Recommended)

1. **Clone or download this repository**
2. **Set up your API key:**
   ```bash
   echo "OPENAI_API_KEY=your_key_here" > .env
   ```
3. **Run with Docker:**
   ```bash
   # Basic run
   ./docker-run.sh
   
   # With public sharing
   ./docker-run.sh --share
   
   # With authentication
   ./docker-run.sh --auth --share
   ```
4. **Open your browser to http://localhost:7777**

### Option 2: Using the Launch Script

1. **Clone or download this repository**
2. **Make the script executable and run:**
   ```bash
   chmod +x run.sh
   ./run.sh
   ```
3. **Follow the prompts to set up your OpenAI API key**
4. **Open your browser to the displayed URL**

### Option 3: Manual Setup

1. **Install Python 3.8+** (if not already installed)
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Set up your API keys:**
   ```bash
   # Option A: Create a .env file
   echo "OPENAI_API_KEY=your_key_here" > .env
   echo "GOOGLE_CLIENT_ID=your_google_client_id" >> .env
   echo "GOOGLE_CLIENT_SECRET=your_google_client_secret" >> .env
   echo "GOOGLE_REDIRECT_URI=http://localhost:7860/auth/callback" >> .env
   
   # Option B: Set environment variables
   export OPENAI_API_KEY=your_key_here
   export GOOGLE_CLIENT_ID=your_google_client_id
   export GOOGLE_CLIENT_SECRET=your_google_client_secret
   export GOOGLE_REDIRECT_URI=http://localhost:7860/auth/callback
   ```
4. **Run the app:**
   ```bash
   python app.py
   ```

## 🔑 Getting API Keys

### OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign up or log in to your account
3. Create a new API key
4. Copy the key and use it in one of the setup methods above

### Access Key Authentication (for simple username/password)
1. Follow the detailed guide in [ACCESS_KEY_SETUP.md](ACCESS_KEY_SETUP.md)
2. Configure USERS and ACCESS_KEYS environment variables
3. Use SHA256 hashed passwords for security

## 📖 Usage

### Command Line Options

```bash
python app.py [OPTIONS]

Options:
  --port PORT        Port to run the app on (default: 7860)
  --api-key KEY      OpenAI API key (overrides environment variable)
  --share            Enable public sharing (creates public URL)
  --host HOST        Host to bind to (default: 127.0.0.1)
  --auth             Enable access key authentication
  -h, --help         Show help message
```

### Examples

```bash
# Basic usage
python app.py

# Run on different port
python app.py --port 8080

# Enable public sharing
python app.py --share

# Enable access key authentication
python app.py --auth

# Secure public sharing with access keys
python app.py --auth --share

# Use API key directly
python app.py --api-key sk-your-key-here

# Run on all interfaces
python app.py --host 0.0.0.0
```

## 🎯 Learning Exercises

The app includes 10 progressive Python exercises:

1. **Hello, Python!** - Basic print statement
2. **Introduce Yourself** - Variables and strings
3. **Your Age** - Number variables
4. **Adding Numbers** - Basic arithmetic
5. **Counting Fruits** - Variable assignment
6. **Check Data Types** - Type checking
7. **Swap Values** - Variable manipulation
8. **Repeat Printing** - Loops
9. **First Letter** - String indexing
10. **Combine Strings** - String concatenation

## 🐳 Docker Deployment

For production deployments or easy setup, use Docker:

### **Quick Docker Start**
```bash
# Set up API key
echo "OPENAI_API_KEY=your_key_here" > .env

# Run with Docker
./docker-run.sh --share
```

### **Docker Features**
- ✅ **File Access**: Reads `questions.txt`, writes to `logs/` directory
- ✅ **Security**: Non-root user, minimal attack surface
- ✅ **Persistence**: Logs survive container restarts
- ✅ **Easy Updates**: Edit `questions.txt` and restart

### **Docker Commands**
```bash
# Basic run
./docker-run.sh

# With authentication and sharing
./docker-run.sh --auth --share

# Custom port
./docker-run.sh --port 8080

# View logs
docker-compose logs -f
```

For detailed Docker setup, see [DOCKER.md](DOCKER.md).

## 🛠️ Development

### Project Structure

```
tutorai/
├── app.py              # Main application
├── questions.txt       # Tutoring questions (Docker: read-only)
├── view_logs.py        # Log viewer utility
├── requirements.txt    # Python dependencies
├── run.sh             # Launch script
├── docker-run.sh      # Docker run script
├── Dockerfile        # Docker image definition
├── docker-compose.yml # Docker Compose configuration
├── .dockerignore      # Docker ignore file
├── setup.py           # Package setup
├── README.md          # This file
├── DOCKER.md          # Docker setup guide
├── ACCESS_KEY_SETUP.md # Access key setup guide
├── LOGGING.md         # Logging system guide
├── logs/              # Log files (Docker: mounted volume)
└── .env               # Environment variables (create this)
```

### Installing for Development

```bash
# Install in development mode
pip install -e .

# Or install dependencies manually
pip install -r requirements.txt
```

## 🔧 Troubleshooting

### Common Issues

**"OPENAI_API_KEY not found"**
- Make sure you've set up your API key in `.env` file or environment variable
- Check that the key is valid and has sufficient credits

**"Port already in use"**
- Use `--port` option to specify a different port
- Check what's running on the port: `lsof -i :7860`

**"Module not found" errors**
- Make sure you've installed dependencies: `pip install -r requirements.txt`
- Check that you're using the correct Python version (3.8+)

**App won't start**
- Check your internet connection (needed for OpenAI API)
- Verify your API key is correct
- Try running with `--host 127.0.0.1` explicitly

### Getting Help

1. Check the console output for error messages
2. Try running with `--help` to see all options
3. Make sure all dependencies are installed
4. Verify your OpenAI API key is valid

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## 🎓 Educational Use

TutorAI is designed for educational purposes, particularly for teaching Python to children. The AI tutor provides age-appropriate explanations and guidance without giving away the complete solutions.

---

**Happy Learning! 🐍✨**

