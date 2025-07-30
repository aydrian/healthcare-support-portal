#!/bin/bash
# run_all.sh - Start all Healthcare Support Portal services

echo "🏥 Healthcare Support Portal - Starting All Services"
echo "=================================================="

# Function to check if a port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "❌ Port $port is already in use"
        return 1
    else
        echo "✅ Port $port is available"
        return 0
    fi
}

# Check if required ports are available
echo "🔍 Checking port availability..."
check_port 8001 || exit 1
check_port 8002 || exit 1
check_port 8003 || exit 1
check_port 3000 || exit 1

echo ""
echo "🚀 Starting services..."

# Start database if not running
echo "🗄️  Checking database..."
if ! docker ps | grep -q postgres; then
    echo "Starting PostgreSQL database..."
    docker-compose up -d db
    echo "Waiting for database to be ready..."
    sleep 5
fi

# Start services in background
echo "🔐 Starting Auth Service..."
cd services/auth_service && ./run.sh > ../../logs/auth.log 2>&1 &
AUTH_PID=$!
cd ../..

echo "🏥 Starting Patient Service..."
cd services/patient_service && ./run.sh > ../../logs/patient.log 2>&1 &
PATIENT_PID=$!
cd ../..

echo "🤖 Starting RAG Service..."
cd services/rag_service && ./run.sh > ../../logs/rag.log 2>&1 &
RAG_PID=$!
cd ../..

echo "🌐 Starting Frontend Service..."
cd services/frontend_service && ./run.sh > ../../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ../..

# Create logs directory if it doesn't exist
mkdir -p logs

echo ""
echo "✅ All services started!"
echo "=================================================="
echo "🌐 Frontend:        http://localhost:3000"
echo "🔐 Auth Service:    http://localhost:8001/docs"
echo "🏥 Patient Service: http://localhost:8002/docs"
echo "🤖 RAG Service:     http://localhost:8003/docs"
echo ""
echo "📋 Service PIDs:"
echo "   Frontend Service: $FRONTEND_PID"
echo "   Auth Service: $AUTH_PID"
echo "   Patient Service: $PATIENT_PID"
echo "   RAG Service: $RAG_PID"
echo ""
echo "📄 Logs are available in the logs/ directory"
echo "🛑 To stop all services, run: ./stop_all.sh"
echo ""

# Save PIDs for stopping later
echo "$FRONTEND_PID" > logs/frontend.pid
echo "$AUTH_PID" > logs/auth.pid
echo "$PATIENT_PID" > logs/patient.pid
echo "$RAG_PID" > logs/rag.pid

# Wait for user input
echo "Press Ctrl+C to stop all services..."
trap 'echo ""; echo "🛑 Stopping all services..."; kill $FRONTEND_PID $AUTH_PID $PATIENT_PID $RAG_PID 2>/dev/null; exit 0' INT

# Keep script running
wait
