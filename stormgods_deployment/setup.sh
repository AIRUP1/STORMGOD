#!/bin/bash
# StormBuster Environment Setup Script

echo "🌩️ Setting up StormBuster environment..."

# Create .env file from .env.example
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ Created .env file from template"
    echo "⚠️  Please edit .env file with your actual API keys"
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements-vercel.txt

# Install Node.js dependencies (if package.json exists)
if [ -f package.json ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

echo "✅ Environment setup complete!"
echo "🚀 Ready to deploy StormBuster to stormgods.us"
