# Python Version Configuration

This project uses **Python 3.11** to match the Docker environment.

## Current Configuration

- **Docker**: Python 3.11 (already configured in Dockerfile)
- **Local venv**: Python 3.13 (needs to be downgraded)

## Recreating Virtual Environment with Python 3.11

### Option 1: If Python 3.11 is installed

```bash
# Remove old virtual environment
rm -rf venv

# Create new venv with Python 3.11
python3.11 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Option 2: Install Python 3.11 first

#### macOS (using Homebrew):
```bash
brew install python@3.11
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### macOS (using pyenv):
```bash
# Install pyenv if not already installed
brew install pyenv

# Install Python 3.11
pyenv install 3.11.9

# Set local Python version
pyenv local 3.11.9

# Create venv
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt-get update
sudo apt-get install python3.11 python3.11-venv python3.11-pip
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Option 3: Use Docker for local development

Since Docker already uses Python 3.11, you can develop entirely in Docker:

```bash
# Build and run
./docker-run.sh --auth

# Or use docker-compose directly
docker-compose up
```

## Verify Python Version

After recreating the venv:

```bash
source venv/bin/activate
python --version
# Should show: Python 3.11.x
```

## Notes

- The `setup.py` now requires Python `>=3.8,<3.12` to ensure compatibility
- Docker environment already uses Python 3.11
- All code is compatible with Python 3.11

