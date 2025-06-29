# 🚀 LinkedIn Sourcing Agent

An AI-powered LinkedIn candidate sourcing system that automatically finds, scores, and generates personalized outreach messages for job candidates.

## ✨ Features

- 🔍 **Intelligent LinkedIn Search**: Automated profile discovery
- 📊 **Multi-Factor Scoring**: Education, experience, skills, location, company relevance
- 🤖 **AI Message Generation**: Personalized outreach using OpenRouter API
- 🔗 **Multi-Source Data**: Enhanced with GitHub, Twitter, personal websites
- ⚡ **Smart Caching**: Performance optimization
- 📈 **Confidence Scoring**: Data quality metrics
- 🔄 **Batch Processing**: Handle multiple jobs simultaneously
- 📄 **PDF Support**: Process job descriptions from PDF files

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Chrome/Chromium browser
- OpenRouter API key (optional)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/linkedin-sourcing-agent.git
cd linkedin-sourcing-agent

# Install dependencies
pip install -r requirements.txt

# Set up API key (optional)
echo "your_openrouter_api_key_here" > open_router_key.txt
```

### Basic Usage

1. **Create a job description file** (`job_desc.txt`):
```
Senior Python Developer

We're looking for a Senior Python Developer with:
- 5+ years of Python development experience
- Experience with Django/Flask frameworks
- Knowledge of machine learning libraries
- AWS cloud infrastructure experience
```

2. **Run the sourcing agent**:
```bash
python main.py job_desc.txt
```

3. **View results**:
- Results saved to `sourcing_results_[position].json`
- Database stored in `linkedin_sourcing.db`

## 📖 Usage Examples

```bash
# Basic usage
python main.py job_desc.txt

# Process PDF job description
python main.py job_description.pdf

# Batch processing
python main.py job_desc.txt --batch

# Demo mode
python main.py --demo
```

## 📊 Output Format

```json
{
  "job_id": "senior-python-developer",
  "candidates_found": 25,
  "top_candidates": [
    {
      "name": "Jane Smith",
      "linkedin_url": "https://linkedin.com/in/janesmith",
      "fit_score": 8.5,
      "score_breakdown": {
        "education": 9.0,
        "trajectory": 8.0,
        "company": 8.5,
        "skills": 9.0,
        "location": 10.0,
        "tenure": 7.0
      },
      "outreach_message": "Hi Jane, I noticed your 6 years of Python development experience..."
    }
  ]
}
```

## 🐳 Docker Deployment

```bash
# Build and run with Docker
docker build -t linkedin-sourcing-agent .
docker run -v $(pwd)/data:/app/data linkedin-sourcing-agent python main.py job_desc.txt

# Or use docker-compose
docker-compose up
```

## 🔧 Configuration

Create a `.env` file for configuration:

```env
OPENROUTER_API_KEY=your_api_key_here
DATABASE_PATH=linkedin_sourcing.db
CACHE_EXPIRATION_HOURS=24
MAX_SEARCH_RESULTS=50
SEARCH_DELAY_SECONDS=2
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific tests
python test_extraction.py
python test_batch_processing.py
python test_smart_cache.py
```

## 🐛 Troubleshooting

### Common Issues

**Chrome not found**: Install Chrome/Chromium browser
```bash
# Ubuntu/Debian
sudo apt-get install chromium-browser

# macOS
brew install --cask google-chrome
```

**No candidates found**: 
- Check internet connectivity
- Verify job description is clear
- Try different search terms

**API key warning**: 
- Optional for AI message generation
- System uses template messages as fallback

## 📁 Project Structure

```
linkedin-sourcing-agent/
├── main.py                 # Main entry point
├── linkedin_agent.py       # Core orchestrator
├── linkedin_searcher.py    # LinkedIn search & extraction
├── scorer.py              # Candidate scoring
├── message_generator.py   # AI message generation
├── multi_source_collector.py # Multi-source data collection
├── smart_cache.py         # Caching system
├── confidence_scorer.py   # Data quality scoring
├── batch_processor.py     # Batch processing
├── database.py            # Database operations
├── pdf_processor.py       # PDF processing
├── config.py              # Configuration
├── requirements.txt       # Dependencies
└── tests/                 # Test files
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/linkedin-sourcing-agent/issues)
- **Email**: your-email@example.com

---

**Made with ❤️ for recruiters and HR professionals** 