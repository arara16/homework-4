#!/bin/bash
echo "Starting CryptoVault Analytics Enhanced..."
echo "Python version: $(python --version)"
echo "Installing dependencies..."
pip install -r requirements.txt
echo "Starting application..."
gunicorn --bind 0.0.0.0:5000 app:app
