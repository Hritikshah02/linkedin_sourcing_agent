#!/usr/bin/env python3
"""
Batch Processor for LinkedIn Sourcing
Handles multiple jobs in parallel with resource management
"""

import asyncio
import concurrent.futures
import threading
import time
import json
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
import logging
from dataclasses import dataclass
from queue import Queue, Empty
import traceback

from linkedin_agent import LinkedInSourcingAgent

logger = logging.getLogger(__name__)

@dataclass
class JobRequest:
    """Job request data structure"""
    job_id: str
    job_description: str
    company_name: Optional[str] = None
    position_title: Optional[str] = None
    location: Optional[str] = None
    max_candidates: int = 20
    priority: int = 1  # Higher number = higher priority
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class JobResult:
    """Job result data structure"""
    job_id: str
    success: bool
    result: Optional[Dict] = None
    error: Optional[str] = None
    processing_time: float = 0.0
    candidates_found: int = 0
    completed_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.completed_at is None:
            self.completed_at = datetime.now()

class BatchProcessor:
    """
    Batch processor for handling multiple LinkedIn sourcing jobs
    """
    
    def __init__(self, max_workers: int = 3, max_queue_size: int = 100):
        self.max_workers = max_workers
        self.max_queue_size = max_queue_size
        self.job_queue = Queue(maxsize=max_queue_size)
        self.results_queue = Queue()
        self.workers = []
        self.is_running = False
        self.stats = {
            'jobs_submitted': 0,
            'jobs_completed': 0,
            'jobs_failed': 0,
            'total_processing_time': 0.0,
            'average_processing_time': 0.0
        }
        self.lock = threading.Lock()
        
        # Initialize agents pool
        self.agents_pool = Queue(maxsize=max_workers)
        for _ in range(max_workers):
            agent = LinkedInSourcingAgent()
            self.agents_pool.put(agent)
    
    def start_workers(self):
        """
        Start worker threads
        """
        if self.is_running:
            logger.warning("Batch processor is already running")
            return
        
        self.is_running = True
        logger.info(f"Starting batch processor with {self.max_workers} workers")
        
        # Start worker threads
        for i in range(self.max_workers):
            worker = threading.Thread(
                target=self._worker_loop,
                name=f"Worker-{i}",
                daemon=True
            )
            worker.start()
            self.workers.append(worker)
        
        logger.info("All workers started")
    
    def stop_workers(self):
        """
        Stop worker threads gracefully
        """
        if not self.is_running:
            return
        
        logger.info("Stopping batch processor...")
        self.is_running = False
        
        # Wait for workers to finish
        for worker in self.workers:
            worker.join(timeout=30)
        
        logger.info("Batch processor stopped")
    
    def _worker_loop(self):
        """
        Main worker loop
        """
        worker_name = threading.current_thread().name
        
        while self.is_running:
            try:
                # Get job from queue with timeout
                job_request = self.job_queue.get(timeout=1)
                logger.info(f"{worker_name} processing job {job_request.job_id}")
                
                # Get agent from pool
                agent = self.agents_pool.get(timeout=5)
                
                try:
                    # Process the job
                    start_time = time.time()
                    result = self._process_job(agent, job_request)
                    processing_time = time.time() - start_time
                    
                    # Create job result
                    job_result = JobResult(
                        job_id=job_request.job_id,
                        success=True,
                        result=result,
                        processing_time=processing_time,
                        candidates_found=result.get('candidates_found', 0) if result else 0
                    )
                    
                    logger.info(f"{worker_name} completed job {job_request.job_id} in {processing_time:.2f}s")
                    
                except Exception as e:
                    processing_time = time.time() - start_time
                    error_msg = f"Error processing job {job_request.job_id}: {str(e)}"
                    logger.error(error_msg)
                    
                    job_result = JobResult(
                        job_id=job_request.job_id,
                        success=False,
                        error=error_msg,
                        processing_time=processing_time
                    )
                
                finally:
                    # Return agent to pool
                    self.agents_pool.put(agent)
                
                # Put result in results queue
                self.results_queue.put(job_result)
                
                # Update statistics
                with self.lock:
                    self.stats['jobs_completed'] += 1
                    self.stats['total_processing_time'] += processing_time
                    if job_result.success:
                        self.stats['jobs_completed'] += 1
                    else:
                        self.stats['jobs_failed'] += 1
                    
                    # Update average processing time
                    completed = self.stats['jobs_completed'] + self.stats['jobs_failed']
                    if completed > 0:
                        self.stats['average_processing_time'] = (
                            self.stats['total_processing_time'] / completed
                        )
                
                # Mark job as done
                self.job_queue.task_done()
                
            except Empty:
                # No jobs in queue, continue
                continue
            except Exception as e:
                logger.error(f"{worker_name} encountered error: {e}")
                continue
    
    def _process_job(self, agent: LinkedInSourcingAgent, job_request: JobRequest) -> Dict:
        """
        Process a single job
        """
        return agent.process_job(
            job_description=job_request.job_description,
            company_name=job_request.company_name,
            position_title=job_request.position_title,
            location=job_request.location,
            max_candidates=job_request.max_candidates
        )
    
    def submit_job(self, job_request: JobRequest) -> bool:
        """
        Submit a job to the processing queue
        """
        try:
            self.job_queue.put(job_request, timeout=5)
            with self.lock:
                self.stats['jobs_submitted'] += 1
            logger.info(f"Submitted job {job_request.job_id} to queue")
            return True
        except Exception as e:
            logger.error(f"Failed to submit job {job_request.job_id}: {e}")
            return False
    
    def get_result(self, timeout: float = 1.0) -> Optional[JobResult]:
        """
        Get a completed job result
        """
        try:
            return self.results_queue.get(timeout=timeout)
        except Empty:
            return None
    
    def get_all_results(self) -> List[JobResult]:
        """
        Get all completed job results
        """
        results = []
        while True:
            result = self.get_result(timeout=0.1)
            if result is None:
                break
            results.append(result)
        return results
    
    def get_stats(self) -> Dict:
        """
        Get batch processor statistics
        """
        with self.lock:
            stats = self.stats.copy()
            stats['queue_size'] = self.job_queue.qsize()
            stats['results_queue_size'] = self.results_queue.qsize()
            stats['active_workers'] = len([w for w in self.workers if w.is_alive()])
            return stats
    
    def wait_for_completion(self, timeout: Optional[float] = None) -> bool:
        """
        Wait for all jobs in queue to complete
        """
        try:
            self.job_queue.join()
            return True
        except Exception as e:
            logger.error(f"Error waiting for completion: {e}")
            return False

class AsyncBatchProcessor:
    """
    Asynchronous batch processor using asyncio
    """
    
    def __init__(self, max_concurrent: int = 3):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.jobs = []
        self.results = []
        self.agents = []
        
        # Initialize agents
        for _ in range(max_concurrent):
            self.agents.append(LinkedInSourcingAgent())
    
    async def process_jobs(self, job_requests: List[JobRequest]) -> List[JobResult]:
        """
        Process multiple jobs concurrently
        """
        self.jobs = job_requests
        self.results = []
        
        logger.info(f"Starting async batch processing of {len(job_requests)} jobs")
        
        # Create tasks for all jobs
        tasks = []
        for job_request in job_requests:
            task = asyncio.create_task(self._process_job_async(job_request))
            tasks.append(task)
        
        # Wait for all tasks to complete
        await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.info(f"Completed async batch processing. {len(self.results)} results")
        return self.results
    
    async def _process_job_async(self, job_request: JobRequest):
        """
        Process a single job asynchronously
        """
        async with self.semaphore:
            start_time = time.time()
            
            try:
                # Get agent (simple round-robin for now)
                agent = self.agents[len(self.results) % len(self.agents)]
                
                # Process job in thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    self._process_job_sync,
                    agent,
                    job_request
                )
                
                processing_time = time.time() - start_time
                
                job_result = JobResult(
                    job_id=job_request.job_id,
                    success=True,
                    result=result,
                    processing_time=processing_time,
                    candidates_found=result.get('candidates_found', 0) if result else 0
                )
                
                logger.info(f"Completed job {job_request.job_id} in {processing_time:.2f}s")
                
            except Exception as e:
                processing_time = time.time() - start_time
                error_msg = f"Error processing job {job_request.job_id}: {str(e)}"
                logger.error(error_msg)
                
                job_result = JobResult(
                    job_id=job_request.job_id,
                    success=False,
                    error=error_msg,
                    processing_time=processing_time
                )
            
            self.results.append(job_result)
    
    def _process_job_sync(self, agent: LinkedInSourcingAgent, job_request: JobRequest) -> Dict:
        """
        Process job synchronously (called from thread pool)
        """
        return agent.process_job(
            job_description=job_request.job_description,
            company_name=job_request.company_name,
            position_title=job_request.position_title,
            location=job_request.location,
            max_candidates=job_request.max_candidates
        )

def create_sample_jobs() -> List[JobRequest]:
    """
    Create sample job requests for testing
    """
    jobs = [
        JobRequest(
            job_id="backend-engineer-1",
            job_description="""
            Senior Backend Engineer - FinTech Startup
            
            We're looking for a Senior Backend Engineer with:
            - 5+ years of Python/Django experience
            - PostgreSQL and Redis knowledge
            - AWS cloud infrastructure experience
            - Docker and Kubernetes familiarity
            """,
            company_name="FinTech Startup",
            position_title="Senior Backend Engineer",
            location="San Francisco, CA",
            max_candidates=10
        ),
        JobRequest(
            job_id="frontend-developer-1",
            job_description="""
            Frontend Developer - E-commerce Platform
            
            Requirements:
            - 3+ years of React/TypeScript experience
            - CSS/SCSS and responsive design skills
            - Experience with state management (Redux/Zustand)
            - Knowledge of modern build tools (Webpack/Vite)
            """,
            company_name="E-commerce Platform",
            position_title="Frontend Developer",
            location="Remote",
            max_candidates=15
        ),
        JobRequest(
            job_id="data-scientist-1",
            job_description="""
            Data Scientist - AI Company
            
            Looking for:
            - PhD in Computer Science or related field
            - Strong Python skills with ML libraries
            - Experience with TensorFlow/PyTorch
            - Knowledge of statistical analysis and A/B testing
            """,
            company_name="AI Company",
            position_title="Data Scientist",
            location="New York, NY",
            max_candidates=12
        )
    ]
    return jobs 