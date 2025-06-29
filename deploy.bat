@echo off
REM LinkedIn Sourcing Agent Deployment Script for Windows
REM This script helps deploy the application to production

echo 🚀 LinkedIn Sourcing Agent - Deployment Script
echo ==============================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8+
    pause
    exit /b 1
)

REM Check if pip is installed
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip is not installed. Please install pip
    pause
    exit /b 1
)

echo ✅ Prerequisites check passed

REM Create virtual environment
echo 🔧 Setting up virtual environment...
if not exist "venv" (
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo 📦 Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Create necessary directories
echo 📁 Creating directories...
if not exist "data" mkdir data
if not exist "logs" mkdir logs

REM Set up environment
echo ⚙️ Setting up environment...
if not exist ".env" (
    echo 📝 Creating .env file...
    (
        echo # LinkedIn Sourcing Agent Configuration
        echo OPENROUTER_API_KEY=your_api_key_here
        echo DATABASE_PATH=linkedin_sourcing.db
        echo CACHE_EXPIRATION_HOURS=24
        echo MAX_SEARCH_RESULTS=50
        echo SEARCH_DELAY_SECONDS=2
        echo REQUESTS_PER_MINUTE=30
        echo LOG_LEVEL=INFO
    ) > .env
    echo ⚠️ Please edit .env file with your actual API keys
)

REM Create sample job description if it doesn't exist
if not exist "job_desc.txt" (
    echo 📝 Creating sample job description...
    (
        echo Senior Python Developer
        echo.
        echo We're looking for a Senior Python Developer with:
        echo - 5+ years of Python development experience
        echo - Experience with Django/Flask frameworks
        echo - Knowledge of machine learning libraries
        echo - AWS cloud infrastructure experience
        echo - Docker and Kubernetes familiarity
        echo.
        echo Location: San Francisco, CA
        echo Salary: $120,000 - $180,000
    ) > job_desc.txt
)

REM Set up API key file if it doesn't exist
if not exist "open_router_key.txt" (
    echo 🔑 Creating API key file...
    echo your_openrouter_api_key_here > open_router_key.txt
    echo ⚠️ Please edit open_router_key.txt with your actual OpenRouter API key
)

REM Test the installation
echo 🧪 Testing installation...
python main.py --demo

echo.
echo ✅ Deployment completed successfully!
echo.
echo 📋 Next steps:
echo 1. Edit .env file with your configuration
echo 2. Edit open_router_key.txt with your API key
echo 3. Edit job_desc.txt with your job description
echo 4. Run: python main.py job_desc.txt
echo.
echo 📚 For more information, see README.md
echo 🐳 For Docker deployment, run: docker-compose up

pause 