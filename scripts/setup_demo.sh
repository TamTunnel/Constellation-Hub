#!/bin/bash
set -e

echo "======================================================================"
echo "🚀 Constellation Hub - Demo Setup"
echo "======================================================================"
echo ""
echo "This script will:"
echo "  1. Run database migrations"
echo "  2. Load demo data (satellites, ground stations, users)"
echo "  3. Display access instructions"
echo ""
echo "⚠️  FOR DEMONSTRATION USE ONLY"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running"
    echo "   Please start Docker and try again"
    exit 1
fi

# Check if services are running
if ! docker-compose ps | grep -q "Up"; then
    echo "⚠️  Services don't appear to be running"
    echo "   Starting services with docker-compose up -d..."
    docker-compose up -d
    echo "   Waiting for services to be ready..."
    sleep 10
fi

# Run migrations
echo "📝 Running database migrations..."
cd backend
python scripts/run_migrations.py upgrade head
cd ..

# Load demo data
echo ""
echo "📦 Loading demo data..."
cd backend
python scripts/load_demo_data.py
cd ..

echo ""
echo "======================================================================"
echo "✅ Demo setup complete!"
echo "======================================================================"
echo ""
echo "Access the application:"
echo "  🌐 Web UI: http://localhost:3000"
echo "  📡 API Docs: http://localhost:8001/docs"
echo ""
echo "Demo credentials are displayed above."
echo ""
