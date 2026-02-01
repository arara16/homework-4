#!/bin/bash
echo "Starting CryptoVault Analytics..."
echo "Python version: $(python --version)"
echo "Installing dependencies..."
pip install -r requirements-azure.txt
echo "Starting application..."
gunicorn --bind 0.0.0.0:5000 azure-app:application
