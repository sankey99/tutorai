# 🐳 TutorAI Docker Setup

This guide explains how to run TutorAI in a Docker container with proper file access and logging.

## 📁 File Structure

```
tutorai/
├── app.py                 # Main application
├── questions.txt          # Tutoring questions (read-only in container)
├── logs/                  # Log files (mounted as volume)
├── .env                   # Environment variables
├── Dockerfile             # Docker image definition
├── docker-compose.yml     # Docker Compose configuration
├── docker-run.sh          # Easy run script
└── .dockerignore          # Files to exclude from Docker build
```

## 🚀 Quick Start

### 1. **Using the Easy Script (Recommended)**

```bash
# Basic run
./docker-run.sh

# With public sharing
./docker-run.sh --share

# With authentication
./docker-run.sh --auth --share


# Custom port
./docker-run.sh --port 8080
```

### 2. **Using Docker Compose**

```bash
# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

### 3. **Using Docker Directly**

```bash
# Build the image
docker build -t tutorai:latest .

# Run the container
docker run -p 7777:7777 \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/questions.txt:/app/questions.txt:ro \
  -v $(pwd)/.env:/app/.env:ro \
  tutorai:latest
```

## 📋 Prerequisites

1. **Docker** installed on your system
2. **Docker Compose** (optional, for easier management)
3. **OpenAI API Key** in `.env` file

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional - Access Key Authentication
USERS=user1,user2,user3
ACCESS_KEYS=key1,key2,key3
```

### Questions File (questions.txt)

The application reads questions from `questions.txt`. Each question should be separated by double newlines:

```
1. Hello, Python! Write a Python program that prints:
Hello, World!

2. Introduce Yourself. Create a variable 'name' with your name and print:
My name is <your name>
```

## 📊 Container Features

### ✅ **File Access**
- **Read-only**: `questions.txt` (mounted as volume)
- **Read-write**: `logs/` directory for application logs
- **Environment**: `.env` file for configuration

### ✅ **Security**
- **Non-root user**: Runs as `tutorai` user (UID 1000)
- **Minimal image**: Based on Python 3.11 slim
- **Health checks**: Built-in container health monitoring

### ✅ **Logging**
- **Access logs**: `logs/access.log`
- **Application logs**: `logs/app.log`
- **Persistent**: Logs survive container restarts

## 🛠️ Management Commands

### **View Logs**
```bash
# Docker Compose logs
docker-compose logs -f

# Application logs
./view_logs.py

# Access logs only
./view_logs.py --access

# Application logs only
./view_logs.py --app
```

### **Container Management**
```bash
# Stop application
docker-compose down

# Restart application
docker-compose restart

# Rebuild and restart
docker-compose up --build -d

# View running containers
docker ps
```

### **Update Questions**
```bash
# Edit questions.txt
nano questions.txt

# Restart to load new questions
docker-compose restart
```

## 🌐 Access URLs

- **Local**: http://localhost:7777
- **Public** (with --share): Check container logs for Gradio share URL

## 🔍 Troubleshooting

### **Container Won't Start**
```bash
# Check logs
docker-compose logs

# Check if port is in use
lsof -i :7777

# Rebuild image
docker-compose build --no-cache
```

### **Questions Not Loading**
```bash
# Check if questions.txt exists
ls -la questions.txt

# Check file permissions
ls -la questions.txt

# Verify file format (double newlines between questions)
cat -A questions.txt
```

### **Logs Not Writing**
```bash
# Check logs directory permissions
ls -la logs/

# Create logs directory if missing
mkdir -p logs && chmod 755 logs
```

## 📈 Production Deployment

### **Using Docker Compose**

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  tutorai:
    build: .
    ports:
      - "7777:7777"
    volumes:
      - ./logs:/app/logs
      - ./questions.txt:/app/questions.txt:ro
      - ./.env:/app/.env:ro
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:7777/"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### **Using Docker Swarm**

```bash
# Deploy stack
docker stack deploy -c docker-compose.yml tutorai

# Scale service
docker service scale tutorai_tutorai=3
```

## 🔒 Security Notes

1. **Environment Variables**: Never commit `.env` files to version control
2. **File Permissions**: The container runs as non-root user
3. **Network**: Only port 7777 is exposed
4. **Volumes**: Only necessary directories are mounted

## 📝 Development

### **Local Development**
```bash
# Run without Docker
python app.py

# Run with Docker for testing
./docker-run.sh --port 8080
```

### **Building Custom Images**
```bash
# Build with custom tag
docker build -t tutorai:v1.0 .

# Run custom image
docker run -p 7777:7777 tutorai:v1.0
```

## 🆘 Support

If you encounter issues:

1. **Check logs**: `docker-compose logs -f`
2. **Verify files**: Ensure `questions.txt` and `.env` exist
3. **Check permissions**: Ensure `logs/` directory is writable
4. **Rebuild**: Try `docker-compose up --build -d`

For more help, check the main [README.md](README.md) file.


