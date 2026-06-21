#!/usr/bin/env bash
set -e

# Setup script for OpenClaw AI Engineering Organization

echo "🚀 Setting up OpenClaw..."

# Check dependencies
for cmd in docker docker-compose poetry npm python3; do
    if ! command -v $cmd &> /dev/null; then
        echo "❌ $cmd could not be found. Please install it first."
        exit 1
    fi
done

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/postgres
mkdir -p data/redis
mkdir -p data/qdrant
mkdir -p data/grafana
mkdir -p data/prometheus
mkdir -p logs

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📄 Creating .env from .env.example..."
    cp .env.example .env
fi

# Install backend dependencies
echo "🐍 Installing Python dependencies..."
poetry install

# Install frontend dependencies
echo "⚛️ Installing Node dependencies..."
if [ -d "src/frontend" ]; then
    cd src/frontend
    npm install
    cd ../..
fi

# Make scripts executable
chmod +x infra/scripts/*.sh

echo "✅ Setup complete! You can now run 'docker-compose up -d' to start the infrastructure."
