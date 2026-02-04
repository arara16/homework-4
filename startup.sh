#!/bin/bash
# Azure App Service startup script
set -e  # Exit on any error

echo "Starting CryptoVault Analytics on Azure..."

# Validate and change to application directory
APP_DIR="/home/site/wwwroot"
if [ ! -d "$APP_DIR" ]; then
    echo "Error: Application directory $APP_DIR does not exist"
    exit 1
fi

cd "$APP_DIR"
echo "Changed to directory: $(pwd)"

# Set port environment variable
export WEBSITES_PORT=${WEBSITES_PORT:-5000}
echo "Using port: $WEBSITES_PORT"

# Install dependencies with error handling
echo "Installing dependencies..."
if ! python -m pip install -r requirements.txt; then
    echo "Error: Failed to install dependencies"
    exit 1
fi

echo "Dependencies installed successfully"
echo "Starting application..."

# Start the application
exec gunicorn --bind=0.0.0.0:$WEBSITES_PORT app:app
