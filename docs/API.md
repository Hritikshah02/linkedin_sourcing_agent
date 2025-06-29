# 🔌 API Documentation

This document describes the API and usage patterns for the LinkedIn Sourcing Agent.

## 📋 Overview

The LinkedIn Sourcing Agent provides a comprehensive API for automated candidate sourcing, scoring, and outreach message generation.

## 🏗️ Architecture

```
LinkedIn Sourcing Agent
├── LinkedInSourcingAgent (Main Orchestrator)
├── LinkedInSearcher (Profile Discovery & Extraction)
├── CandidateScorer (Multi-factor Scoring)
├── MessageGenerator (AI-powered Outreach)
├── MultiSourceCollector (GitHub, Twitter, Websites)
├── SmartCache (Performance Optimization)
├── ConfidenceScorer (Data Quality Assessment)
└── BatchProcessor (Parallel Processing)
```

## 🔧 Core Classes

### LinkedInSourcingAgent

Main orchestrator class that coordinates the entire sourcing pipeline.

#### Constructor
```python
agent = LinkedInSourcingAgent()
```

#### Methods

##### `process_job(job_description, company_name=None, position_title=None, location=None, max_candidates=20)`

Process a complete job sourcing pipeline.

**Parameters:**
- `job_description` (str): Job description text
- `company_name` (str, optional): Company name
- `position_title` (str, optional): Job title
- `location` (str, optional): Job location
- `max_candidates` (int, optional): Maximum candidates to process (default: 20)

**Returns:**
```python
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
            "outreach_message": "Hi Jane, I noticed your 6 years...",
            "confidence_analysis": {
                "overall_confidence": 0.85,
                "data_completeness": 0.90,
                "data_freshness": 0.80
            }
        }
    ]
}
```

**Example:**
```python
from linkedin_agent import LinkedInSourcingAgent

agent = LinkedInSourcingAgent()
result = agent.process_job(
    job_description="Senior Python Developer with ML experience...",
    company_name="Tech Corp",
    position_title="Senior Python Developer",
    location="San Francisco, CA",
    max_candidates=15
)
```

##### `search_linkedin(job_description, max_results=20)`

Search for LinkedIn profiles only.

**Parameters:**
- `job_description` (str): Job description
- `max_results` (int, optional): Maximum results (default: 20)

**Returns:**
```python
[
    {
        "name": "Jane Smith",
        "linkedin_url": "https://linkedin.com/in/janesmith",
        "headline": "Senior Python Developer at Tech Corp",
        "current_company": "Tech Corp",
        "location": "San Francisco, CA"
    }
]
```

##### `score_candidates(candidates, job_description)`

Score candidates based on job requirements.

**Parameters:**
- `candidates` (list): List of candidate dictionaries
- `job_description` (str): Job description

**Returns:**
```python
[
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
        }
    }
]
```

##### `generate_outreach(scored_candidates, job_description, max_messages=5)`

Generate personalized outreach messages.

**Parameters:**
- `scored_candidates` (list): List of scored candidates
- `job_description` (str): Job description
- `max_messages` (int, optional): Maximum messages to generate (default: 5)

**Returns:**
```python
[
    {
        "name": "Jane Smith",
        "linkedin_url": "https://linkedin.com/in/janesmith",
        "fit_score": 8.5,
        "outreach_message": "Hi Jane, I noticed your 6 years..."
    }
]
```

### MultiSourceCollector

Enhances candidate data with information from multiple sources.

#### Constructor
```python
collector = MultiSourceCollector()
```

#### Methods

##### `enhance_candidate_data(candidate)`

Enhance a candidate with multi-source data.

**Parameters:**
- `candidate` (dict): Candidate data

**Returns:**
```python
{
    "name": "Jane Smith",
    "linkedin_url": "https://linkedin.com/in/janesmith",
    "github_username": "janesmith",
    "github_profile": {
        "name": "Jane Smith",
        "bio": "Senior Python Developer",
        "public_repos": 25,
        "followers": 150
    },
    "github_repos": [
        {
            "name": "ml-project",
            "description": "Machine learning project",
            "language": "Python",
            "stars": 50
        }
    ],
    "twitter_username": "janesmith_dev",
    "personal_website": {
        "url": "https://janesmith.dev",
        "title": "Jane Smith - Developer",
        "skills_found": ["Python", "Django", "ML"]
    },
    "data_confidence": {
        "linkedin": 0.9,
        "github": 0.8,
        "twitter": 0.6,
        "website": 0.7,
        "overall": 0.8
    }
}
```

### SmartCache

Intelligent caching system for performance optimization.

#### Constructor
```python
cache = SmartCache(cache_db_path="cache.db")
```

#### Methods

##### `get(data_type, identifier)`

Retrieve cached data.

**Parameters:**
- `data_type` (str): Type of cached data
- `identifier` (str): Unique identifier

**Returns:**
```python
{
    "data": {...},
    "created_at": "2024-01-01T00:00:00",
    "expires_at": "2024-01-02T00:00:00"
}
```

##### `set(data_type, identifier, data, custom_expiration=None)`

Cache data.

**Parameters:**
- `data_type` (str): Type of data to cache
- `identifier` (str): Unique identifier
- `data` (dict): Data to cache
- `custom_expiration` (int, optional): Custom expiration in hours

##### `get_cache_stats()`

Get cache statistics.

**Returns:**
```python
{
    "total_entries": 150,
    "expired_entries": 10,
    "active_entries": 140,
    "by_type": {
        "linkedin_profile": {
            "count": 50,
            "avg_access": 3.2,
            "last_access": "2024-01-01T12:00:00"
        }
    }
}
```

### ConfidenceScorer

Assesses data quality and reliability.

#### Constructor
```python
scorer = ConfidenceScorer()
```

#### Methods

##### `calculate_comprehensive_confidence(candidate)`

Calculate comprehensive confidence metrics.

**Parameters:**
- `candidate` (dict): Candidate data

**Returns:**
```python
ConfidenceMetrics(
    linkedin=0.9,
    github=0.8,
    twitter=0.6,
    website=0.7,
    overall=0.8,
    data_completeness=0.85,
    data_freshness=0.75,
    data_consistency=0.9,
    reliability_score=0.82
)
```

##### `get_confidence_summary(metrics)`

Get human-readable confidence summary.

**Parameters:**
- `metrics` (ConfidenceMetrics): Confidence metrics

**Returns:**
```python
{
    "overall_confidence": 0.8,
    "data_completeness": 0.85,
    "data_freshness": 0.75,
    "data_consistency": 0.9,
    "reliability_score": 0.82,
    "recommendations": [
        "Consider refreshing GitHub data",
        "LinkedIn profile is highly reliable"
    ]
}
```

### BatchProcessor

Handles multiple jobs in parallel.

#### Constructor
```python
processor = BatchProcessor(max_workers=3, max_queue_size=100)
```

#### Methods

##### `start_workers()`

Start worker threads.

##### `submit_job(job_request)`

Submit a job for processing.

**Parameters:**
- `job_request` (JobRequest): Job request object

**Returns:**
- `bool`: Success status

##### `get_result(timeout=1.0)`

Get a completed job result.

**Parameters:**
- `timeout` (float): Timeout in seconds

**Returns:**
```python
JobResult(
    job_id="backend-engineer-1",
    success=True,
    result={...},
    processing_time=45.2,
    candidates_found=15
)
```

##### `get_all_results()`

Get all completed results.

**Returns:**
```python
[JobResult(...), JobResult(...)]
```

## 📊 Data Models

### JobRequest

```python
@dataclass
class JobRequest:
    job_id: str
    job_description: str
    company_name: Optional[str] = None
    position_title: Optional[str] = None
    location: Optional[str] = None
    max_candidates: int = 20
    priority: int = 1
    created_at: Optional[datetime] = None
```

### JobResult

```python
@dataclass
class JobResult:
    job_id: str
    success: bool
    result: Optional[Dict] = None
    error: Optional[str] = None
    processing_time: float = 0.0
    candidates_found: int = 0
    completed_at: Optional[datetime] = None
```

### ConfidenceMetrics

```python
@dataclass
class ConfidenceMetrics:
    linkedin: float = 0.0
    github: float = 0.0
    twitter: float = 0.0
    website: float = 0.0
    overall: float = 0.0
    data_completeness: float = 0.0
    data_freshness: float = 0.0
    data_consistency: float = 0.0
    reliability_score: float = 0.0
```

## 🔄 Usage Patterns

### Basic Usage

```python
from linkedin_agent import LinkedInSourcingAgent

# Initialize agent
agent = LinkedInSourcingAgent()

# Process a job
result = agent.process_job(
    job_description="Senior Python Developer...",
    company_name="Tech Corp",
    position_title="Senior Python Developer",
    location="San Francisco, CA",
    max_candidates=20
)

# Access results
print(f"Found {result['candidates_found']} candidates")
for candidate in result['top_candidates']:
    print(f"{candidate['name']}: {candidate['fit_score']}/10")
```

### Advanced Usage with Multi-Source Data

```python
from linkedin_agent import LinkedInSourcingAgent
from multi_source_collector import MultiSourceCollector

# Initialize components
agent = LinkedInSourcingAgent()
collector = MultiSourceCollector()

# Process job
result = agent.process_job(
    job_description="Senior Python Developer...",
    max_candidates=10
)

# Enhance with multi-source data
enhanced_candidates = []
for candidate in result['top_candidates']:
    enhanced = collector.enhance_candidate_data(candidate)
    enhanced_candidates.append(enhanced)

# Filter by confidence
high_confidence = [
    c for c in enhanced_candidates 
    if c.get('data_confidence', {}).get('overall', 0) > 0.7
]
```

### Batch Processing

```python
from batch_processor import BatchProcessor, JobRequest

# Initialize batch processor
processor = BatchProcessor(max_workers=3)
processor.start_workers()

# Create job requests
jobs = [
    JobRequest(
        job_id="backend-1",
        job_description="Backend Developer...",
        company_name="Tech Corp",
        max_candidates=15
    ),
    JobRequest(
        job_id="frontend-1", 
        job_description="Frontend Developer...",
        company_name="Tech Corp",
        max_candidates=15
    )
]

# Submit jobs
for job in jobs:
    processor.submit_job(job)

# Wait for completion
processor.wait_for_completion()

# Get results
results = processor.get_all_results()
for result in results:
    print(f"Job {result.job_id}: {result.candidates_found} candidates")
```

### Caching Integration

```python
from linkedin_agent import LinkedInSourcingAgent
from smart_cache import SmartCache

# Initialize with cache
agent = LinkedInSourcingAgent()
cache = SmartCache()

# Check cache first
cached_result = cache.get('job_analysis', job_description_hash)
if cached_result:
    print("Using cached result")
    result = cached_result
else:
    # Process and cache
    result = agent.process_job(job_description)
    cache.set('job_analysis', job_description_hash, result)

# Monitor cache performance
stats = cache.get_cache_stats()
print(f"Cache hit rate: {stats['active_entries']}/{stats['total_entries']}")
```

## 🔧 Configuration

### Environment Variables

```bash
# API Configuration
OPENROUTER_API_KEY=your_api_key_here

# Database Configuration
DATABASE_PATH=linkedin_sourcing.db

# Cache Configuration
CACHE_EXPIRATION_HOURS=24

# Search Configuration
MAX_SEARCH_RESULTS=50
SEARCH_DELAY_SECONDS=2

# Rate Limiting
REQUESTS_PER_MINUTE=30

# Logging
LOG_LEVEL=INFO
```

### Configuration File

```python
# config.py
class Config:
    # Search parameters
    MAX_SEARCH_RESULTS = 50
    SEARCH_DELAY = 2
    
    # Scoring weights
    EDUCATION_WEIGHT = 0.25
    EXPERIENCE_WEIGHT = 0.30
    SKILLS_WEIGHT = 0.20
    LOCATION_WEIGHT = 0.15
    COMPANY_WEIGHT = 0.10
    
    # Cache settings
    CACHE_EXPIRATION = 24
```

## 🐛 Error Handling

### Common Exceptions

```python
from linkedin_agent import LinkedInSourcingAgent

try:
    agent = LinkedInSourcingAgent()
    result = agent.process_job(job_description)
except ImportError as e:
    print(f"Missing dependency: {e}")
except ConnectionError as e:
    print(f"Network error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Retry Logic

```python
import time
from functools import wraps

def retry_on_failure(max_retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    time.sleep(delay * (2 ** attempt))  # Exponential backoff
            return None
        return wrapper
    return decorator

# Usage
@retry_on_failure(max_retries=3, delay=2)
def search_linkedin_profiles(job_description):
    # Implementation
    pass
```

## 📈 Performance Tips

### Optimization Strategies

1. **Use Caching**
   ```python
   # Cache expensive operations
   cache.set('linkedin_profile', url, profile_data)
   cached = cache.get('linkedin_profile', url)
   ```

2. **Batch Processing**
   ```python
   # Process multiple jobs in parallel
   processor = BatchProcessor(max_workers=3)
   ```

3. **Rate Limiting**
   ```python
   # Respect API limits
   time.sleep(2)  # Between requests
   ```

4. **Async Processing**
   ```python
   # Use async for I/O operations
   async def process_jobs_async(jobs):
       tasks = [process_job(job) for job in jobs]
       return await asyncio.gather(*tasks)
   ```

## 🔒 Security Considerations

### API Key Management

```python
import os
from dotenv import load_dotenv

# Load from environment
load_dotenv()
api_key = os.getenv('OPENROUTER_API_KEY')

# Validate API key
if not api_key:
    raise ValueError("OpenRouter API key not found")
```

### Data Validation

```python
def validate_candidate_data(candidate):
    required_fields = ['name', 'linkedin_url']
    for field in required_fields:
        if field not in candidate:
            raise ValueError(f"Missing required field: {field}")
    
    # Validate URL format
    if not candidate['linkedin_url'].startswith('https://linkedin.com/'):
        raise ValueError("Invalid LinkedIn URL")
```

## 📞 Support

For API-related issues:

1. Check the error handling section
2. Review the configuration
3. Test with minimal data
4. Create an issue with:
   - Error message
   - Code snippet
   - Expected vs actual behavior
   - System information 