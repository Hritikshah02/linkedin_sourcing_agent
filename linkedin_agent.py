from linkedin_searcher import LinkedInSearcher
from scorer import CandidateScorer
from message_generator import MessageGenerator
from database import Database
from multi_source_collector import MultiSourceCollector
from smart_cache import SmartCache
import json
from datetime import datetime
import time

class LinkedInSourcingAgent:
    def __init__(self):
        self.searcher = LinkedInSearcher()
        self.scorer = CandidateScorer()
        self.message_generator = MessageGenerator()
        self.database = Database()
        self.multi_source_collector = MultiSourceCollector()
        self.smart_cache = SmartCache()
    
    def process_job(self, job_description, company_name=None, position_title=None, location=None, max_candidates=20):
        """
        Complete pipeline: search → extract details → score → generate messages
        """
        print(f"🚀 Starting LinkedIn sourcing for job...")
        
        # Save job to database
        job_id = self.database.save_job(job_description, company_name, position_title, location)
        print(f"📝 Job saved with ID: {job_id}")
        
        # Step 1: Search for candidates
        print("🔍 Searching for LinkedIn profiles...")
        
        # Check cache for search results
        search_query = f"{job_description[:100]} {company_name or ''} {location or ''}"
        cached_results = self.smart_cache.get_cached_search_results(search_query)
        
        if cached_results:
            print(f"✅ Found {len(cached_results)} candidates in cache")
            candidates = cached_results
        else:
            candidates = self.searcher.search_linkedin_profiles(job_description, max_candidates)
            print(f"✅ Found {len(candidates)} candidates")
            
            # Cache the search results
            self.smart_cache.cache_search_results(search_query, candidates)
            print("💾 Cached search results")
        
        # Step 2: Extract detailed profile information
        print("📋 Extracting detailed profile information...")
        enhanced_candidates = []
        for i, candidate in enumerate(candidates):
            try:
                print(f"   Extracting details for {candidate['name']} ({i+1}/{len(candidates)})")
                
                # Check cache for profile details
                cached_profile = self.smart_cache.get_cached_linkedin_profile(candidate['linkedin_url'])
                
                if cached_profile:
                    print(f"   ✅ Found profile in cache for {candidate['name']}")
                    profile_details = cached_profile
                else:
                    profile_details = self.searcher.get_profile_details(candidate['linkedin_url'])
                    # Cache the profile details
                    self.smart_cache.cache_linkedin_profile(candidate['linkedin_url'], profile_details)
                    print(f"   💾 Cached profile for {candidate['name']}")
                
                # Merge profile details with candidate data
                enhanced_candidate = candidate.copy()
                enhanced_candidate.update(profile_details)
                
                # Step 2.5: Multi-source enhancement
                print(f"   🔍 Enhancing with multi-source data for {candidate['name']}")
                enhanced_candidate = self.multi_source_collector.enhance_candidate_data(enhanced_candidate)
                
                enhanced_candidates.append(enhanced_candidate)
                
                # Add delay to avoid rate limiting
                time.sleep(2)
                
            except Exception as e:
                print(f"   ❌ Error extracting details for {candidate['name']}: {e}")
                enhanced_candidates.append(candidate)
        
        print(f"✅ Enhanced {len(enhanced_candidates)} candidates with detailed information")
        
        # Step 3: Score candidates
        print("📊 Scoring candidates...")
        scored_candidates = self.scorer.score_candidates(enhanced_candidates, job_description)
        print(f"✅ Scored {len(scored_candidates)} candidates")
        
        # Step 4: Generate outreach messages
        print("💬 Generating outreach messages...")
        final_candidates = self.message_generator.generate_outreach_messages(
            scored_candidates, job_description, max_messages=5
        )
        print(f"✅ Generated messages for top {len(final_candidates)} candidates")
        
        # Step 5: Save candidates to database
        for candidate in final_candidates:
            self.database.save_candidate(job_id, candidate)
        
        # Step 6: Return results in preferred format
        top_candidates_formatted = []
        for candidate in final_candidates[:5]:  # Top 5 candidates
            formatted_candidate = {
                "name": candidate.get('name', ''),
                "linkedin_url": candidate.get('linkedin_url', ''),
                "fit_score": candidate.get('fit_score', 0.0),
                "score_breakdown": candidate.get('score_breakdown', {}),
                "outreach_message": candidate.get('outreach_message', '')
            }
            top_candidates_formatted.append(formatted_candidate)
        
        result = {
            "job_id": str(job_id),
            "candidates_found": len(candidates),
            "top_candidates": top_candidates_formatted
        }
        
        return result
    
    def search_linkedin(self, job_description, max_results=20):
        """
        Step 1: Find LinkedIn profiles
        """
        return self.searcher.search_linkedin_profiles(job_description, max_results)
    
    def score_candidates(self, candidates, job_description):
        """
        Step 2: Score candidates based on fit
        """
        return self.scorer.score_candidates(candidates, job_description)
    
    def generate_outreach(self, scored_candidates, job_description, max_messages=5):
        """
        Step 3: Generate personalized outreach messages
        """
        return self.message_generator.generate_outreach_messages(
            scored_candidates, job_description, max_messages
        )
    
    def get_job_results(self, job_id):
        """
        Retrieve results for a specific job in preferred format
        """
        job = self.database.get_job(job_id)
        candidates = self.database.get_candidates_for_job(job_id)
        
        # Format candidates in preferred structure
        top_candidates_formatted = []
        for candidate in candidates[:5]:  # Top 5 candidates
            formatted_candidate = {
                "name": candidate.get('name', ''),
                "linkedin_url": candidate.get('linkedin_url', ''),
                "fit_score": candidate.get('fit_score', 0.0),
                "score_breakdown": candidate.get('score_breakdown', {}),
                "outreach_message": candidate.get('outreach_message', '')
            }
            top_candidates_formatted.append(formatted_candidate)
        
        return {
            "job_id": str(job_id),
            "candidates_found": len(candidates),
            "top_candidates": top_candidates_formatted
        }
    
    def export_results(self, job_id, format='json'):
        """
        Export results in specified format using preferred structure
        """
        results = self.get_job_results(job_id)
        
        if format == 'json':
            return json.dumps(results, indent=2, default=str)
        elif format == 'csv':
            # Simple CSV export with essential fields
            csv_lines = ["Name,LinkedIn URL,Fit Score,Education,Trajectory,Company,Skills,Location,Tenure,Outreach Message"]
            for candidate in results['top_candidates']:
                score_breakdown = candidate.get('score_breakdown', {})
                csv_lines.append(f'"{candidate["name"]}","{candidate["linkedin_url"]}",{candidate["fit_score"]},{score_breakdown.get("education", 0)},{score_breakdown.get("trajectory", 0)},{score_breakdown.get("company", 0)},{score_breakdown.get("skills", 0)},{score_breakdown.get("location", 0)},{score_breakdown.get("tenure", 0)},"{candidate["outreach_message"]}"')
            return '\n'.join(csv_lines)
        else:
            return results
    
    def print_summary(self, result):
        """
        Print a nice summary of the results
        """
        print("\n" + "="*60)
        print("🎯 LINKEDIN SOURCING RESULTS")
        print("="*60)
        print(f"Job ID: {result['job_id']}")
        print(f"Candidates Found: {result['candidates_found']}")
        print(f"Top Candidates: {len(result['top_candidates'])}")
        print("\n" + "-"*60)
        
        for i, candidate in enumerate(result['top_candidates'], 1):
            print(f"\n🏆 #{i} - {candidate['name']}")
            print(f"   Score: {candidate['fit_score']}/10")
            print(f"   Role: {candidate['headline']}")
            print(f"   Company: {candidate['current_company']}")
            print(f"   Location: {candidate['location']}")
            print(f"   LinkedIn: {candidate['linkedin_url']}")
            
            if candidate.get('score_breakdown'):
                print("   Score Breakdown:")
                for component, score in candidate['score_breakdown'].items():
                    print(f"     - {component.title()}: {score}/10")
            
            print(f"\n   💬 Message:")
            print(f"   {candidate['outreach_message']}")
            print("-"*60) 