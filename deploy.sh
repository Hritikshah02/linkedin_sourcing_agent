#!/bin/bash

# LinkedIn Sourcing Agent Deployment Script
# This script helps deploy the application to production

set -e

echo "🚀 LinkedIn Sourcing Agent - Deployment Script"
echo "=============================================="

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please don't run this script as root"
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command_exists python3; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+"
    exit 1
fi

if ! command_exists pip; then
    echo "❌ pip is not installed. Please install pip"
    exit 1
fi

if ! command_exists git; then
    echo "❌ git is not installed. Please install git"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Create virtual environment
echo "🔧 Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data
mkdir -p logs

# Set up environment
echo "⚙️ Setting up environment..."
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# LinkedIn Sourcing Agent Configuration
OPENROUTER_API_KEY=your_api_key_here
DATABASE_PATH=linkedin_sourcing.db
CACHE_EXPIRATION_HOURS=24
MAX_SEARCH_RESULTS=50
SEARCH_DELAY_SECONDS=2
REQUESTS_PER_MINUTE=30
LOG_LEVEL=INFO
EOF
    echo "⚠️ Please edit .env file with your actual API keys"
fi

# Create sample job description if it doesn't exist
if [ ! -f "job_desc.txt" ]; then
    echo "📝 Creating sample job description..."
    cat > job_desc.txt << EOF
Senior Python Developer

We're looking for a Senior Python Developer with:
- 5+ years of Python development experience
- Experience with Django/Flask frameworks
- Knowledge of machine learning libraries
- AWS cloud infrastructure experience
- Docker and Kubernetes familiarity

Location: San Francisco, CA
Salary: $120,000 - $180,000
EOF
fi

# Set up API key file if it doesn't exist
if [ ! -f "open_router_key.txt" ]; then
    echo "🔑 Creating API key file..."
    echo "your_openrouter_api_key_here" > open_router_key.txt
    echo "⚠️ Please edit open_router_key.txt with your actual OpenRouter API key"
fi

# Test the installation
echo "🧪 Testing installation..."
python main.py --demo

echo ""
echo "✅ Deployment completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Edit open_router_key.txt with your API key"
echo "3. Edit job_desc.txt with your job description"
echo "4. Run: python main.py job_desc.txt"
echo ""
echo "📚 For more information, see README.md"
echo "🐳 For Docker deployment, run: docker-compose up" 