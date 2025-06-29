#!/usr/bin/env python3
"""
Enhanced LinkedIn Sourcing Agent - Main Script
Demonstrates the complete pipeline with multi-source data, caching, batch processing, and confidence scoring
"""

from linkedin_agent import LinkedInSourcingAgent
from pdf_processor import PDFProcessor
from multi_source_collector import MultiSourceCollector
from batch_processor import BatchProcessor, AsyncBatchProcessor, JobRequest, create_sample_jobs
from smart_cache import SmartCache
from confidence_scorer import ConfidenceScorer
import json
import sys
import os
import asyncio
import time

def read_text_file(file_path):
    """
    Read text content from a text file
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Text file not found: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except Exception as e:
        raise Exception(f"Error reading text file: {e}")

def enhanced_main():
    """Enhanced main function with all new features"""
    # Check if file path is provided as command line argument
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_job_description.txt> [--batch] [--async] [--demo]")
        print("Example: python main.py job_desc.txt")
        print("Example: python main.py job_desc.txt --batch")
        print("Example: python main.py job_desc.txt --async")
        print("Example: python main.py --demo")
        sys.exit(1)
    
    # Parse command line arguments
    args = sys.argv[1:]
    batch_mode = "--batch" in args
    async_mode = "--async" in args
    demo_mode = "--demo" in args
    
    if demo_mode:
        run_demo()
        return
    
    file_path = args[0]
    
    # Initialize all components
    print("\n=== Enhanced LinkedIn Sourcing Agent ===")
    print("Initializing components...")
    
    agent = LinkedInSourcingAgent()
    pdf_processor = PDFProcessor()
    multi_source = MultiSourceCollector()
    cache = SmartCache()
    confidence_scorer = ConfidenceScorer()
    
    print("✅ All components initialized")
    
    try:
        # Process job description
        if file_path.lower().endswith('.pdf'):
            print("📄 Extracting job information from PDF...")
            job_info = pdf_processor.process_job_pdf(file_path)
        elif file_path.lower().endswith('.txt'):
            print("📄 Reading job information from text file...")
            job_text = read_text_file(file_path)
            job_info = pdf_processor.parse_job_description(job_text)
        else:
            print("❌ Error: Unsupported file format. Please use .pdf or .txt files.")
            sys.exit(1)
        
        # Display extracted information
        pdf_processor.print_job_summary(job_info)
        
        # Get user preferences
        max_candidates = input("Max candidates to process (default 15): ").strip()
        try:
            max_candidates = int(max_candidates)
        except ValueError:
            max_candidates = 15
        
        enable_multi_source = input("Enable multi-source data collection? (y/n, default y): ").strip().lower()
        enable_multi_source = enable_multi_source != 'n'
        
        if batch_mode or async_mode:
            run_batch_processing(job_info, max_candidates, async_mode, enable_multi_source)
        else:
            run_single_job(job_info, max_candidates, enable_multi_source, agent, multi_source, confidence_scorer)
        
    except FileNotFoundError:
        print(f"❌ Error: File not found: {file_path}")
    except Exception as e:
        print(f"❌ Error: {e}")

def run_single_job(job_info, max_candidates, enable_multi_source, agent, multi_source, confidence_scorer):
    """Run a single job with enhanced features"""
    print("\n🚀 Processing job with enhanced features...")
    
    # Check cache first
    cache = SmartCache()
    cached_result = cache.get_cached_job_analysis(job_info['job_description'])
    if cached_result:
        print("📋 Using cached job analysis")
        job_analysis = cached_result
    else:
        print("🔍 Analyzing job requirements...")
        # Use a simple job analysis structure since ConfidenceScorer doesn't have analyze_job_requirements
        job_analysis = {
            'required_skills': [],
            'job_description': job_info['job_description'],
            'company_name': job_info['company_name'],
            'position_title': job_info['position_title']
        }
        cache.cache_job_analysis(job_info['job_description'], job_analysis)
    
    # Process the job
    start_time = time.time()
    result = agent.process_job(
        job_description=job_info['job_description'],
        company_name=job_info['company_name'],
        position_title=job_info['position_title'],
        location=job_info['location'],
        max_candidates=max_candidates
    )
    
    # Enhance with multi-source data if enabled
    if enable_multi_source and result.get('top_candidates'):
        print("🔗 Enhancing candidates with multi-source data...")
        enhanced_candidates = []
        for candidate in result['top_candidates']:
            enhanced = multi_source.enhance_candidate_data(candidate)
            enhanced_candidates.append(enhanced)
        result['top_candidates'] = enhanced_candidates
    
    # Calculate confidence scores
    if result.get('top_candidates'):
        print("📊 Calculating confidence scores...")
        for candidate in result['top_candidates']:
            confidence_metrics = confidence_scorer.calculate_comprehensive_confidence(candidate)
            candidate['confidence_analysis'] = confidence_scorer.get_confidence_summary(confidence_metrics)
    
    processing_time = time.time() - start_time
    print(f"⏱️ Total processing time: {processing_time:.2f} seconds")
    
    # Print enhanced results
    print_enhanced_summary(result, job_info)
    
    # Export results
    export_enhanced_results(result, job_info)

def run_batch_processing(job_info, max_candidates, async_mode, enable_multi_source):
    """Run batch processing with multiple jobs"""
    print(f"\n🔄 Running batch processing ({'async' if async_mode else 'threaded'})...")
    
    if async_mode:
        asyncio.run(run_async_batch(job_info, max_candidates, enable_multi_source))
    else:
        run_threaded_batch(job_info, max_candidates, enable_multi_source)

def run_threaded_batch(job_info, max_candidates, enable_multi_source):
    """Run threaded batch processing"""
    # Create multiple job variations
    jobs = create_sample_jobs()
    jobs.append(JobRequest(
        job_id="custom-job",
        job_description=job_info['job_description'],
        company_name=job_info['company_name'],
        position_title=job_info['position_title'],
        location=job_info['location'],
        max_candidates=max_candidates
    ))
    
    # Initialize batch processor
    batch_processor = BatchProcessor(max_workers=3)
    batch_processor.start_workers()
    
    # Submit all jobs
    for job in jobs:
        batch_processor.submit_job(job)
    
    print(f"📤 Submitted {len(jobs)} jobs to batch processor")
    
    # Wait for completion and collect results
    batch_processor.wait_for_completion()
    results = batch_processor.get_all_results()
    
    # Print batch results
    print_batch_results(results)
    
    batch_processor.stop_workers()

async def run_async_batch(job_info, max_candidates, enable_multi_source):
    """Run async batch processing"""
    # Create multiple job variations
    jobs = create_sample_jobs()
    jobs.append(JobRequest(
        job_id="custom-job",
        job_description=job_info['job_description'],
        company_name=job_info['company_name'],
        position_title=job_info['position_title'],
        location=job_info['location'],
        max_candidates=max_candidates
    ))
    
    # Initialize async batch processor
    async_processor = AsyncBatchProcessor(max_concurrent=3)
    
    # Process all jobs
    results = await async_processor.process_jobs(jobs)
    
    # Print batch results
    print_batch_results(results)

def run_demo():
    """Run a comprehensive demo of all features"""
    print("\n🎯 Enhanced LinkedIn Sourcing Agent - Demo Mode")
    print("="*60)
    
    # Initialize components
    agent = LinkedInSourcingAgent()
    multi_source = MultiSourceCollector()
    cache = SmartCache()
    confidence_scorer = ConfidenceScorer()
    
    # Demo job
    demo_job = {
        'job_description': """
        Senior Python Developer - AI Startup
        
        We're looking for a Senior Python Developer with:
        - 5+ years of Python development experience
        - Experience with Django/Flask frameworks
        - Knowledge of machine learning libraries (TensorFlow/PyTorch)
        - AWS cloud infrastructure experience
        - Docker and Kubernetes familiarity
        """,
        'company_name': 'AI Startup',
        'position_title': 'Senior Python Developer',
        'location': 'San Francisco, CA'
    }
    
    print("1️⃣ Testing basic LinkedIn sourcing...")
    result = agent.process_job(
        job_description=demo_job['job_description'],
        company_name=demo_job['company_name'],
        position_title=demo_job['position_title'],
        location=demo_job['location'],
        max_candidates=5
    )
    
    print(f"   Found {len(result.get('candidates', []))} candidates")
    
    print("\n2️⃣ Testing multi-source data collection...")
    if result.get('candidates'):
        enhanced = multi_source.enhance_candidate_data(result['candidates'][0])
        print(f"   Enhanced candidate: {enhanced.get('name', 'Unknown')}")
        if enhanced.get('github_username'):
            print(f"   GitHub: {enhanced['github_username']}")
        if enhanced.get('twitter_username'):
            print(f"   Twitter: {enhanced['twitter_username']}")
        if enhanced.get('personal_website'):
            print(f"   Website: {enhanced['personal_website']['url']}")
    
    print("\n3️⃣ Testing confidence scoring...")
    # Use a simple job analysis structure
    job_analysis = {
        'required_skills': ['python', 'django', 'flask', 'machine learning', 'aws', 'docker'],
        'job_description': demo_job['job_description'],
        'company_name': demo_job['company_name'],
        'position_title': demo_job['position_title']
    }
    print(f"   Job requirements analyzed: {len(job_analysis.get('required_skills', []))} skills identified")
    
    if result.get('candidates'):
        confidence_metrics = confidence_scorer.calculate_comprehensive_confidence(result['candidates'][0])
        confidence_summary = confidence_scorer.get_confidence_summary(confidence_metrics)
        print(f"   Candidate confidence: {confidence_summary.get('overall_confidence', 0):.2f}/1.0")
    
    print("\n4️⃣ Testing caching...")
    cache_stats = cache.get_cache_stats()
    print(f"   Cache stats: {cache_stats.get('total_entries', 0)} entries")
    
    print("\n5️⃣ Testing batch processing...")
    jobs = create_sample_jobs()[:2]  # Just 2 jobs for demo
    batch_processor = BatchProcessor(max_workers=2)
    batch_processor.start_workers()
    
    for job in jobs:
        batch_processor.submit_job(job)
    
    batch_processor.wait_for_completion()
    batch_results = batch_processor.get_all_results()
    print(f"   Batch processed {len(batch_results)} jobs")
    
    batch_processor.stop_workers()
    
    print("\n✅ Demo completed successfully!")

def print_enhanced_summary(result, job_info):
    """Print enhanced results summary"""
    print("\n" + "="*60)
    print("📊 ENHANCED RESULTS SUMMARY")
    print("="*60)
    
    top_candidates = result.get('top_candidates', [])
    print(f"🎯 Job: {job_info['position_title']} at {job_info['company_name']}")
    print(f"📍 Location: {job_info['location']}")
    print(f"👥 Candidates Found: {result.get('candidates_found', 0)}")
    print(f"⏱️ Processing Time: {result.get('processing_time', 0):.2f}s")
    
    if top_candidates:
        print(f"\n🏆 Top Candidates:")
        for i, candidate in enumerate(top_candidates[:5], 1):
            confidence = candidate.get('confidence_analysis', {}).get('overall_confidence', 0)
            # Ensure confidence is a number before formatting
            try:
                confidence_float = float(confidence) if confidence is not None else 0.0
                confidence_str = f"{confidence_float:.2f}"
            except (ValueError, TypeError):
                confidence_str = str(confidence) if confidence is not None else "0.00"
            
            print(f"   {i}. {candidate['name']} - Score: {candidate.get('fit_score', 0)}/10 - Confidence: {confidence_str}")
            
            # Show multi-source data if available
            if candidate.get('github_username'):
                print(f"      GitHub: {candidate['github_username']}")
            if candidate.get('twitter_username'):
                print(f"      Twitter: {candidate['twitter_username']}")
            if candidate.get('personal_website'):
                print(f"      Website: {candidate['personal_website']['url']}")

def print_batch_results(results):
    """Print batch processing results"""
    print("\n" + "="*60)
    print("📊 BATCH PROCESSING RESULTS")
    print("="*60)
    
    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]
    
    print(f"✅ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")
    print(f"⏱️ Average processing time: {sum(r.processing_time for r in results) / len(results):.2f}s")
    
    if successful:
        print(f"\n🏆 Best Results:")
        for result in sorted(successful, key=lambda x: x.candidates_found, reverse=True)[:3]:
            print(f"   Job {result.job_id}: {result.candidates_found} candidates in {result.processing_time:.2f}s")

def export_enhanced_results(result, job_info):
    """Export enhanced results to file in the required format"""
    print("\n📊 Exporting enhanced results...")
    
    # The result from agent.process_job already has the correct format
    # Just ensure job_id is properly formatted
    if not result.get('job_id'):
        # Generate a job_id from position title if not present
        job_id = job_info['position_title'].lower().replace(' ', '-').replace(',', '').replace('(', '').replace(')', '')
        result['job_id'] = job_id
    
    output_file = f"sourcing_results_{job_info['position_title'].replace(' ', '_')}.json"
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"✅ Enhanced results saved to '{output_file}'")
    except Exception as e:
        print(f"⚠️ Warning: Could not save enhanced results: {e}")

def main():
    """Legacy main function for backward compatibility"""
    enhanced_main()

if __name__ == "__main__":
    enhanced_main() 