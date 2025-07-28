#!/bin/bash
# setup.sh - Initial setup for Healthcare Support Portal

echo "🏥 Healthcare Support Portal - Initial Setup"
echo "============================================="

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p data/postgres

# Copy example .env files
echo "📋 Setting up environment files..."
for service in auth_service patient_service rag_service; do
    if [ ! -f "services/$service/.env" ]; then
        if [ -f "services/$service/.env.example" ]; then
            cp "services/$service/.env.example" "services/$service/.env"
            echo "✅ Created services/$service/.env from example"
        fi
    else
        echo "⚠️  services/$service/.env already exists, skipping"
    fi
done

# Generate a secure SECRET_KEY
echo "🔑 Generating secure SECRET_KEY..."
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# Update .env files with the generated SECRET_KEY
echo "🔄 Updating .env files with generated SECRET_KEY..."
for service in auth_service patient_service rag_service; do
    if [ -f "services/$service/.env" ]; then
        sed -i.bak "s/SECRET_KEY=change-me-in-production/SECRET_KEY=$SECRET_KEY/" "services/$service/.env"
        rm "services/$service/.env.bak" 2>/dev/null || true
        echo "✅ Updated SECRET_KEY in services/$service/.env"
    fi
done

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x run_all.sh
chmod +x stop_all.sh
chmod +x services/auth_service/run.sh
chmod +x services/patient_service/run.sh
chmod +x services/rag_service/run.sh

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Edit services/rag_service/.env and add your OpenAI API key"
echo "2. Start the database: docker-compose up -d db"
echo "3. Install dependencies in each service: cd services/[service] && uv sync"
echo "4. Start all services: ./run_all.sh"
echo ""
echo "📚 API Documentation will be available at:"
echo "   🔐 Auth Service:    http://localhost:8001/docs"
echo "   🏥 Patient Service: http://localhost:8002/docs"
echo "   🤖 RAG Service:     http://localhost:8003/docs"
