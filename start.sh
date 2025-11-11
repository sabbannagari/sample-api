#!/bin/bash

# Startup script for User Management API
# This script runs the FastAPI application in the background with logging

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Define log file and PID file paths
LOG_FILE="$SCRIPT_DIR/api.log"
PID_FILE="$SCRIPT_DIR/api.pid"

# Check if the API is already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "API is already running with PID $PID"
        exit 1
    else
        echo "Removing stale PID file"
        rm "$PID_FILE"
    fi
fi

# Start the API using the virtual environment's Python
echo "Starting User Management API..."
echo "Logs will be written to: $LOG_FILE"

# Start uvicorn in the background using the full path to the virtual environment
nohup "$SCRIPT_DIR/autoagent/bin/python" -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 > "$LOG_FILE" 2>&1 &

# Save the process ID
echo $! > "$PID_FILE"

echo "API started successfully with PID $(cat $PID_FILE)"
echo "Access the API at: http://localhost:8000"
echo "API documentation at: http://localhost:8000/docs"
echo ""
echo "To view logs in real-time, run: tail -f $LOG_FILE"
echo "To stop the API, run: ./stop.sh"
