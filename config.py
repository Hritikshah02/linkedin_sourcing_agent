import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # OpenRouter Configuration
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
    OPENROUTER_MODEL = "meta-llama/llama-3-70b-instruct"
    
    # LinkedIn Search Configuration
    LINKEDIN_SEARCH_DELAY = 2  # seconds between requests
    MAX_SEARCH_RESULTS = 50
    
    # Scoring Weights
    SCORING_WEIGHTS = {
        'education': 0.20,
        'trajectory': 0.20,
        'company': 0.15,
        'skills': 0.25,
        'location': 0.10,
        'tenure': 0.10
    }
    
    # Elite Schools (for education scoring)
    ELITE_SCHOOLS = [
        'MIT', 'Stanford', 'Harvard', 'Berkeley', 'CMU', 'Caltech',
        'Princeton', 'Yale', 'Columbia', 'Cornell', 'UCLA', 'UCSD'
    ]
    
    # Top Tech Companies (for company scoring)
    TOP_TECH_COMPANIES = [
        'Google', 'Meta', 'Facebook', 'Apple', 'Microsoft', 'Amazon',
        'Netflix', 'Uber', 'Airbnb', 'Stripe', 'Palantir', 'OpenAI',
        'Anthropic', 'Databricks', 'Snowflake', 'MongoDB', 'Atlassian'
    ]
    
    # Database Configuration
    DATABASE_PATH = "linkedin_sourcing.db"
    
    # User Agent for web scraping
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36" 