#!/bin/bash

# Stop script for all services
# Usage: ./stop.sh [all|login|product|order]
# Default: all

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Get service argument (default to "all")
SERVICE="${1:-all}"

# Function to stop a service
stop_service() {
    local service_name=$1
    local pid_file="$SCRIPT_DIR/${service_name}.pid"

    # Check if PID file exists
    if [ ! -f "$pid_file" ]; then
        echo "⚠️  $service_name is not running (PID file not found)"
        return 1
    fi

    # Read the PID
    PID=$(cat "$pid_file")

    # Check if the process is running
    if ! ps -p "$PID" > /dev/null 2>&1; then
        echo "⚠️  $service_name is not running (process $PID not found)"
        rm "$pid_file"
        return 1
    fi

    # Stop the process
    echo "🛑 Stopping $service_name (PID: $PID)..."
    kill "$PID"

    # Wait for the process to stop
    sleep 2

    # Check if it's still running
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "   Process didn't stop gracefully, forcing shutdown..."
        kill -9 "$PID"
        sleep 1
    fi

    # Remove PID file
    rm "$pid_file"

    echo "✅ $service_name stopped successfully"
    echo ""
}

# Display usage
if [ "$SERVICE" == "--help" ] || [ "$SERVICE" == "-h" ]; then
    echo "Usage: ./stop.sh [all|login|product|order|ui]"
    echo ""
    echo "Services:"
    echo "  all      - Stop all services including UI (default)"
    echo "  login    - Stop login service"
    echo "  product  - Stop product service"
    echo "  order    - Stop order service"
    echo "  ui       - Stop React UI"
    echo ""
    echo "Examples:"
    echo "  ./stop.sh           # Stop all services"
    echo "  ./stop.sh login     # Stop only login service"
    echo "  ./stop.sh ui        # Stop only UI"
    exit 0
fi

echo "================================================"
echo "  Stopping Services"
echo "================================================"
echo ""

# Function to stop UI service
stop_ui_service() {
    local pid_file="$SCRIPT_DIR/ui-service/ui.pid"

    # Check if PID file exists
    if [ ! -f "$pid_file" ]; then
        echo "⚠️  UI service is not running (PID file not found)"
        return 1
    fi

    # Read the PID
    PID=$(cat "$pid_file")

    # Check if the process is running
    if ! ps -p "$PID" > /dev/null 2>&1; then
        echo "⚠️  UI service is not running (process $PID not found)"
        rm "$pid_file"
        return 1
    fi

    # Stop the process
    echo "🛑 Stopping UI service (PID: $PID)..."
    kill "$PID"

    # Wait for the process to stop
    sleep 2

    # Check if it's still running
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "   Process didn't stop gracefully, forcing shutdown..."
        kill -9 "$PID"
        sleep 1
    fi

    # Remove PID file
    rm "$pid_file"

    echo "✅ UI service stopped successfully"
    echo ""
}

# Stop services based on argument
case "$SERVICE" in
    all)
        stop_service "login"
        stop_service "product"
        stop_service "order"
        stop_ui_service
        ;;
    login)
        stop_service "login"
        ;;
    product)
        stop_service "product"
        ;;
    order)
        stop_service "order"
        ;;
    ui)
        stop_ui_service
        ;;
    *)
        echo "❌ Unknown service: $SERVICE"
        echo "Usage: ./stop.sh [all|login|product|order|ui]"
        exit 1
        ;;
esac

echo "================================================"
echo "  All requested services stopped"
echo "================================================"
