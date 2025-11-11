#!/bin/bash

# Startup script for all services
# Usage: ./start.sh [all|login|product|order]
# Default: all

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Get service argument (default to "all")
SERVICE="${1:-all}"

# Function to start a service
start_service() {
    local service_name=$1
    local service_module=$2
    local port=$3
    local log_file="$SCRIPT_DIR/${service_name}.log"
    local pid_file="$SCRIPT_DIR/${service_name}.pid"

    # Check if the service is already running
    if [ -f "$pid_file" ]; then
        PID=$(cat "$pid_file")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "⚠️  $service_name is already running with PID $PID"
            return 1
        else
            echo "Removing stale PID file for $service_name"
            rm "$pid_file"
        fi
    fi

    # Start the service
    echo "🚀 Starting $service_name on port $port..."
    nohup "$SCRIPT_DIR/autoagent/bin/python" -m uvicorn "$service_module:app" --reload --host 0.0.0.0 --port "$port" > "$log_file" 2>&1 &

    # Save the process ID
    echo $! > "$pid_file"

    echo "✅ $service_name started successfully with PID $(cat $pid_file)"
    echo "   Access: http://localhost:$port"
    echo "   Docs: http://localhost:$port/docs"
    echo "   Logs: $log_file"
    echo ""
}

# Display usage
if [ "$SERVICE" == "--help" ] || [ "$SERVICE" == "-h" ]; then
    echo "Usage: ./start.sh [all|login|product|order|ui]"
    echo ""
    echo "Services:"
    echo "  all      - Start all services including UI (default)"
    echo "  login    - Start login service on port 8001"
    echo "  product  - Start product service on port 8002"
    echo "  order    - Start order service on port 8003"
    echo "  ui       - Start React UI on port 3000"
    echo ""
    echo "Examples:"
    echo "  ./start.sh           # Start all services"
    echo "  ./start.sh login     # Start only login service"
    echo "  ./start.sh ui        # Start only UI"
    exit 0
fi

# Check if virtual environment exists
if [ ! -d "$SCRIPT_DIR/autoagent" ]; then
    echo "❌ Virtual environment not found. Please run ./setup.sh first"
    exit 1
fi

echo "================================================"
echo "  Starting Services"
echo "================================================"
echo ""

# Function to start UI service
start_ui_service() {
    local log_file="$SCRIPT_DIR/ui-service/ui.log"
    local pid_file="$SCRIPT_DIR/ui-service/ui.pid"

    # Check if the service is already running
    if [ -f "$pid_file" ]; then
        PID=$(cat "$pid_file")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "⚠️  UI service is already running with PID $PID"
            return 1
        else
            echo "Removing stale PID file for UI service"
            rm "$pid_file"
        fi
    fi

    # Check if node_modules exists
    if [ ! -d "$SCRIPT_DIR/ui-service/node_modules" ]; then
        echo "📦 Installing UI dependencies..."
        cd "$SCRIPT_DIR/ui-service"
        npm install
        cd "$SCRIPT_DIR"
    fi

    # Start the UI service
    echo "🚀 Starting UI service on port 3000..."
    cd "$SCRIPT_DIR/ui-service"
    nohup npm start > "$log_file" 2>&1 &
    echo $! > "$pid_file"
    cd "$SCRIPT_DIR"

    echo "✅ UI service started successfully with PID $(cat $pid_file)"
    echo "   Access: http://localhost:3000"
    echo "   Logs: $log_file"
    echo ""
}

# Start services based on argument
case "$SERVICE" in
    all)
        start_service "login" "login.main" 8001
        start_service "product" "product-service.main" 8002
        start_service "order" "order-service.main" 8003
        start_ui_service
        echo "📝 Note: Order and Product services require authentication from login service"
        echo "📝 UI available at http://localhost:3000"
        ;;
    login)
        start_service "login" "login.main" 8001
        ;;
    product)
        start_service "product" "product-service.main" 8002
        ;;
    order)
        start_service "order" "order-service.main" 8003
        echo "📝 Note: Order service requires authentication from login service (port 8001)"
        ;;
    ui)
        start_ui_service
        ;;
    *)
        echo "❌ Unknown service: $SERVICE"
        echo "Usage: ./start.sh [all|login|product|order|ui]"
        exit 1
        ;;
esac

echo "================================================"
echo "  To stop services, run: ./stop.sh [service]"
echo "================================================"
