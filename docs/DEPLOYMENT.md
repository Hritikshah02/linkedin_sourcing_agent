# 🚀 Deployment Guide

This guide covers different deployment options for the LinkedIn Sourcing Agent.

## 📋 Prerequisites

- Python 3.8+
- Chrome/Chromium browser
- Git
- Docker (optional, for containerized deployment)

## 🏠 Local Deployment

### Quick Start (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/linkedin-sourcing-agent.git
   cd linkedin-sourcing-agent
   ```

2. **Run deployment script**
   ```bash
   # Linux/Mac
   ./deploy.sh
   
   # Windows
   deploy.bat
   ```

3. **Configure API keys**
   ```bash
   # Edit the generated files
   nano .env
   nano open_router_key.txt
   ```

4. **Run the application**
   ```bash
   python main.py job_desc.txt
   ```

### Manual Setup

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate.bat  # Windows
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment**
   ```bash
   cp env_example.txt .env
   # Edit .env with your configuration
   ```

4. **Create API key file**
   ```bash
   echo "your_openrouter_api_key_here" > open_router_key.txt
   ```

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

1. **Build and run**
   ```bash
   docker-compose up --build
   ```

2. **Run in background**
   ```bash
   docker-compose up -d
   ```

3. **View logs**
   ```bash
   docker-compose logs -f
   ```

### Using Docker directly

1. **Build image**
   ```bash
   docker build -t linkedin-sourcing-agent .
   ```

2. **Run container**
   ```bash
   docker run -v $(pwd)/data:/app/data \
     -v $(pwd)/job_desc.txt:/app/job_desc.txt:ro \
     linkedin-sourcing-agent python main.py job_desc.txt
   ```

## ☁️ Cloud Deployment

### AWS Lambda

1. **Package the application**
   ```bash
   pip install -r requirements.txt -t package/
   cd package
   zip -r ../lambda-deployment.zip .
   ```

2. **Deploy to Lambda**
   ```bash
   aws lambda create-function \
     --function-name linkedin-sourcing \
     --runtime python3.9 \
     --handler main.lambda_handler \
     --zip-file fileb://lambda-deployment.zip
   ```

### Google Cloud Functions

1. **Deploy function**
   ```bash
   gcloud functions deploy linkedin-sourcing \
     --runtime python39 \
     --trigger-http \
     --source . \
     --entry-point main
   ```

### Heroku

1. **Create Procfile**
   ```
   web: python main.py job_desc.txt
   ```

2. **Deploy**
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENROUTER_API_KEY` | OpenRouter API key for AI messages | None |
| `DATABASE_PATH` | Database file path | `linkedin_sourcing.db` |
| `CACHE_EXPIRATION_HOURS` | Cache expiration time | `24` |
| `MAX_SEARCH_RESULTS` | Maximum search results | `50` |
| `SEARCH_DELAY_SECONDS` | Delay between requests | `2` |
| `REQUESTS_PER_MINUTE` | Rate limiting | `30` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Configuration File (`config.py`)

Key settings you can modify:

```python
# Search parameters
MAX_SEARCH_RESULTS = 50
SEARCH_DELAY = 2  # seconds between requests

# Scoring weights
EDUCATION_WEIGHT = 0.25
EXPERIENCE_WEIGHT = 0.30
SKILLS_WEIGHT = 0.20
LOCATION_WEIGHT = 0.15
COMPANY_WEIGHT = 0.10

# Cache settings
CACHE_EXPIRATION = 24  # hours
```

## 📊 Monitoring

### Logs

- Application logs: `logs/app.log`
- Error logs: `logs/error.log`
- Access logs: `logs/access.log`

### Metrics

- Cache hit rate: Available via `SmartCache.get_cache_stats()`
- Processing time: Included in job results
- Success rate: Tracked in batch processing

### Health Checks

```bash
# Test core functionality
python test_core.py

# Check cache status
python -c "from smart_cache import SmartCache; print(SmartCache().get_cache_stats())"

# Test database connection
python -c "from database import Database; db = Database(); print('Database OK')"
```

## 🔒 Security

### API Key Management

- Store API keys in environment variables
- Never commit API keys to version control
- Use `.env` files for local development
- Use cloud secret management for production

### Rate Limiting

- Respect LinkedIn's rate limits
- Implement exponential backoff
- Monitor request frequency
- Use caching to reduce requests

### Data Privacy

- Only collect publicly available information
- Respect robots.txt and terms of service
- Implement data retention policies
- Secure database access

## 🐛 Troubleshooting

### Common Issues

#### Chrome not found
```bash
# Ubuntu/Debian
sudo apt-get install chromium-browser

# macOS
brew install --cask google-chrome

# Windows
# Download from https://www.google.com/chrome/
```

#### Permission denied
```bash
# Fix file permissions
chmod +x deploy.sh
chmod +x main.py
```

#### Database locked
```bash
# Remove database and recreate
rm linkedin_sourcing.db
python main.py job_desc.txt
```

#### Memory issues
```bash
# Reduce batch size
python main.py job_desc.txt --max-candidates 10
```

### Debug Mode

```bash
# Enable verbose logging
python main.py job_desc.txt --verbose

# Run with debug flags
DEBUG=1 python main.py job_desc.txt
```

## 📈 Performance Optimization

### Caching Strategy

- LinkedIn profiles: 24 hours
- Search results: 2 hours
- GitHub data: 12 hours
- Website data: 48 hours

### Rate Limiting

- 2-second delay between LinkedIn requests
- 1-second delay between search requests
- Automatic retry with exponential backoff

### Resource Management

- Configurable worker threads (default: 3)
- Async processing for I/O-bound operations
- Queue management for large job volumes

## 🔄 Updates

### Updating the Application

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart services
docker-compose restart  # if using Docker
```

### Database Migrations

```bash
# Backup current database
cp linkedin_sourcing.db linkedin_sourcing.db.backup

# Run migrations (if any)
python -c "from database import Database; db = Database(); db.migrate()"
```

## 📞 Support

For deployment issues:

1. Check the troubleshooting section
2. Review logs in the `logs/` directory
3. Run `python test_core.py` to verify installation
4. Create an issue on GitHub with:
   - Error message
   - System information
   - Steps to reproduce
   - Log files (if applicable) 