#!/bin/bash
echo "Starting CryptoVault Analytics..."
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Files in directory:"
ls -la
echo "Installing dependencies..."
pip install -r requirements.txt
echo "Starting application..."
exec gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 app:app
