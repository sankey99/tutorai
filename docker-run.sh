#!/bin/bash

# Docker TutorAI Runner Script
# This script builds and runs the TutorAI application in Docker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🐳 TutorAI Docker Setup${NC}"
echo "================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if docker-compose is available
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    echo -e "${RED}❌ Neither docker-compose nor 'docker compose' is available.${NC}"
    exit 1
fi

# Create logs directory if it doesn't exist
if [ ! -d "logs" ]; then
    echo -e "${YELLOW}📁 Creating logs directory...${NC}"
    mkdir -p logs
    chmod 755 logs
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating a template...${NC}"
    cat > .env << EOF
# OpenAI API Key (required)
OPENAI_API_KEY=your_openai_api_key_here


# Access Key Authentication (optional - for --auth)
USERS=user1,user2,user3
ACCESS_KEYS=key1,key2,key3
EOF
    echo -e "${YELLOW}📝 Please edit .env file with your actual API keys.${NC}"
fi

# Check if data/questions.txt exists
if [ ! -f "data/questions.txt" ]; then
    echo -e "${RED}❌ data/questions.txt not found. Please create it first.${NC}"
    exit 1
fi

# Parse command line arguments
SHARE=false
AUTH=true
OAUTH=false
PORT=7777
HOST="0.0.0.0"

while [[ $# -gt 0 ]]; do
    case $1 in
        --share)
            SHARE=true
            shift
            ;;
        --auth)
            AUTH=true
            shift
            ;;
        --no-auth)
            AUTH=false
            shift
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --host)
            HOST="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --share     Enable Gradio sharing (public URL)"
            echo "  --auth      Enable access key authentication (default)"
            echo "  --no-auth   Disable authentication"
            echo "  --port      Set port (default: 7777)"
            echo "  --host      Set host (default: 0.0.0.0)"
            echo "  --help      Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                          # Basic run with authentication"
            echo "  $0 --share                  # With public sharing and authentication"
            echo "  $0 --no-auth                # Without authentication"
            echo "  $0 --no-auth --share        # Without authentication but with sharing"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Build the Docker image
echo -e "${BLUE}🔨 Building Docker image...${NC}"
# Set build date for cache busting
export BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
# Use docker compose to build so it uses the same tag as docker-compose.yml
$COMPOSE_CMD build

# Stop any existing containers
echo -e "${YELLOW}🛑 Stopping existing containers...${NC}"
$COMPOSE_CMD down 2>/dev/null || true

# Check if .env file has changed and restart if needed
if [ -f ".env" ]; then
    echo -e "${BLUE}📝 Checking for .env changes...${NC}"
    # Force restart to pick up any .env changes
    $COMPOSE_CMD down 2>/dev/null || true
fi

# Prepare environment variables for docker-compose
export TUTORAI_SHARE=$SHARE
export TUTORAI_AUTH=$AUTH
export TUTORAI_OAUTH=$OAUTH
export TUTORAI_PORT=$PORT
export TUTORAI_HOST=$HOST

# Create docker-compose override for runtime options
# Build command array
CMD_ARRAY=("python" "src/app.py" "--host" "${HOST}" "--port" "${PORT}")
if [ "$SHARE" = true ]; then
    CMD_ARRAY+=("--share")
fi
if [ "$AUTH" = true ]; then
    CMD_ARRAY+=("--auth")
fi

# Convert array to YAML list format
CMD_STR="["
for i in "${!CMD_ARRAY[@]}"; do
    if [ $i -gt 0 ]; then
        CMD_STR="${CMD_STR}, "
    fi
    CMD_STR="${CMD_STR}\"${CMD_ARRAY[$i]}\""
done
CMD_STR="${CMD_STR}]"

cat > docker-compose.override.yml << EOF
version: '3.8'

services:
  tutorai:
    command: ${CMD_STR}
EOF

# Start the application
echo -e "${GREEN}🚀 Starting TutorAI application...${NC}"
$COMPOSE_CMD up -d

# Wait for the application to start
echo -e "${YELLOW}⏳ Waiting for application to start...${NC}"
sleep 5

# Check if the application is running
if docker ps | grep -q tutorai; then
    echo -e "${GREEN}✅ TutorAI is running!${NC}"
    echo ""
    echo -e "${BLUE}📊 Container Status:${NC}"
    docker ps --filter "name=tutorai" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""
    echo -e "${BLUE}🌐 Access URLs:${NC}"
    echo -e "  Local:    ${GREEN}http://localhost:${PORT}${NC}"
    if [ "$SHARE" = true ]; then
        echo -e "  Public:   ${GREEN}Check container logs for Gradio share URL${NC}"
    fi
    echo ""
    echo -e "${BLUE}📝 Useful Commands:${NC}"
    echo "  View logs:     docker-compose logs -f"
    echo "  Stop app:      docker-compose down"
    echo "  Restart app:   docker-compose restart"
    echo "  View logs:     python src/view_logs.py"
    echo ""
    echo -e "${YELLOW}💡 Tip: Edit data/questions.txt to modify the tutoring questions!${NC}"
else
    echo -e "${RED}❌ Failed to start TutorAI. Check logs:${NC}"
    $COMPOSE_CMD logs
    exit 1
fi
