#!/bin/bash
# services/patient_service/run.sh

# Load .env file if it exists
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# Set PYTHONPATH to include common package
export PYTHONPATH="../../common/src:$PYTHONPATH"

# Set default environment variables if not already set
export SECRET_KEY="${SECRET_KEY:-your-secret-key-here}"
export DATABASE_URL="${DATABASE_URL:-postgresql+psycopg2://postgres:postgres@localhost:5432/healthcare}"
export DEBUG="${DEBUG:-true}"
export HOST="${HOST:-0.0.0.0}"
export PORT="${PORT:-8002}"

echo "🏥 Starting Patient Service on port $PORT..."
echo "📊 Debug mode: $DEBUG"
echo "🔑 Using SECRET_KEY: ${SECRET_KEY:0:10}..."
echo "🗄️  Database: ${DATABASE_URL%%@*}@***"

# Run the patient service
uv run uvicorn src.patient_service.main:app --reload --host $HOST --port $PORT
