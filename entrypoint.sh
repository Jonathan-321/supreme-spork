#!/bin/bash

# This script serves as the entry point for the AgriFinance application
# It helps manage the startup process with proper logging

echo "Starting AgriFinance application..."

# Run with debug app for now
exec gunicorn --bind 0.0.0.0:5000 --timeout 120 --log-level debug wsgi:application