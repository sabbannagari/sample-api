#!/bin/bash

# Stop script for User Management API
# This script stops the running FastAPI application

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Define PID file path
PID_FILE="$SCRIPT_DIR/api.pid"

# Check if PID file exists
if [ ! -f "$PID_FILE" ]; then
    echo "API is not running (PID file not found)"
    exit 1
fi

# Read the PID
PID=$(cat "$PID_FILE")

# Check if the process is running
if ! ps -p "$PID" > /dev/null 2>&1; then
    echo "API is not running (process $PID not found)"
    rm "$PID_FILE"
    exit 1
fi

# Stop the process
echo "Stopping User Management API (PID: $PID)..."
kill "$PID"

# Wait for the process to stop
sleep 2

# Check if it's still running
if ps -p "$PID" > /dev/null 2>&1; then
    echo "Process didn't stop gracefully, forcing shutdown..."
    kill -9 "$PID"
    sleep 1
fi

# Remove PID file
rm "$PID_FILE"

echo "API stopped successfully"
