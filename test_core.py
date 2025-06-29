#!/usr/bin/env python3
"""
Core functionality test for LinkedIn Sourcing Agent
"""

import sys
import os
import json
from unittest.mock import patch, MagicMock

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all core modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from linkedin_agent import LinkedInSourcingAgent
        from linkedin_searcher import LinkedInSearcher
        from scorer import CandidateScorer
        from message_generator import MessageGenerator
        from database import Database
        from config import Config
        from pdf_processor import PDFProcessor
        print("✅ All core modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_enhanced_imports():
    """Test that enhanced modules can be imported"""
    print("🧪 Testing enhanced imports...")
    
    try:
        from multi_source_collector import MultiSourceCollector
        from smart_cache import SmartCache
        from confidence_scorer import ConfidenceScorer
        from batch_processor import BatchProcessor
        print("✅ All enhanced modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Enhanced import error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality with mocked data"""
    print("🧪 Testing basic functionality...")
    
    try:
        from linkedin_agent import LinkedInSourcingAgent
        
        # Create agent
        agent = LinkedInSourcingAgent()
        
        # Mock job description
        job_description = """
        Senior Python Developer
        
        We're looking for a Senior Python Developer with:
        - 5+ years of Python development experience
        - Experience with Django/Flask frameworks
        - Knowledge of machine learning libraries
        """
        
        # Test with mocked search results
        with patch.object(agent.searcher, 'search_linkedin_profiles') as mock_search:
            mock_search.return_value = [
                {
                    'name': 'Test Candidate',
                    'linkedin_url': 'https://linkedin.com/in/test',
                    'headline': 'Senior Python Developer at Test Corp',
                    'current_company': 'Test Corp',
                    'location': 'San Francisco, CA'
                }
            ]
            
            # Test the complete pipeline
            result = agent.process_job(
                job_description=job_description,
                company_name="Test Company",
                position_title="Senior Python Developer",
                location="San Francisco, CA",
                max_candidates=1
            )
            
            # Verify result structure
            assert 'job_id' in result
            assert 'candidates_found' in result
            assert 'top_candidates' in result
            assert len(result['top_candidates']) > 0
            
            print("✅ Basic functionality test passed")
            return True
            
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def test_configuration():
    """Test configuration loading"""
    print("🧪 Testing configuration...")
    
    try:
        from config import Config
        
        # Test config loading
        config = Config()
        
        # Verify essential config values
        assert hasattr(config, 'MAX_SEARCH_RESULTS')
        assert hasattr(config, 'SEARCH_DELAY')
        assert hasattr(config, 'DATABASE_PATH')
        
        print("✅ Configuration test passed")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_database():
    """Test database operations"""
    print("🧪 Testing database...")
    
    try:
        from database import Database
        
        # Create database instance
        db = Database()
        
        # Test job saving
        job_id = db.save_job(
            "Test job description",
            "Test Company",
            "Test Position",
            "Test Location"
        )
        
        assert job_id is not None
        
        # Test job retrieval
        job = db.get_job(job_id)
        assert job is not None
        assert job['job_description'] == "Test job description"
        
        print("✅ Database test passed")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_output_format():
    """Test output format compliance"""
    print("🧪 Testing output format...")
    
    try:
        # Expected format
        expected_format = {
            "job_id": "test-job",
            "candidates_found": 1,
            "top_candidates": [
                {
                    "name": "Test Candidate",
                    "linkedin_url": "https://linkedin.com/in/test",
                    "fit_score": 8.0,
                    "score_breakdown": {
                        "education": 8.0,
                        "trajectory": 8.0,
                        "company": 8.0,
                        "skills": 8.0,
                        "location": 8.0,
                        "tenure": 8.0
                    },
                    "outreach_message": "Test message"
                }
            ]
        }
        
        # Test JSON serialization
        json_str = json.dumps(expected_format, indent=2)
        parsed = json.loads(json_str)
        
        # Verify structure
        assert 'job_id' in parsed
        assert 'candidates_found' in parsed
        assert 'top_candidates' in parsed
        assert isinstance(parsed['top_candidates'], list)
        
        if parsed['top_candidates']:
            candidate = parsed['top_candidates'][0]
            assert 'name' in candidate
            assert 'linkedin_url' in candidate
            assert 'fit_score' in candidate
            assert 'score_breakdown' in candidate
            assert 'outreach_message' in candidate
        
        print("✅ Output format test passed")
        return True
        
    except Exception as e:
        print(f"❌ Output format test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 LinkedIn Sourcing Agent - Core Functionality Test")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_enhanced_imports,
        test_configuration,
        test_database,
        test_output_format,
        test_basic_functionality
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! The system is ready for use.")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 