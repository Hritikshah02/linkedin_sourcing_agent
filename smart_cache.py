#!/usr/bin/env python3
"""
Smart Caching System
Caches LinkedIn profiles, GitHub data, and multi-source information
"""

import json
import hashlib
import time
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import sqlite3
import logging

logger = logging.getLogger(__name__)

class SmartCache:
    """
    Intelligent caching system for LinkedIn sourcing data
    """
    
    def __init__(self, cache_db_path="cache.db"):
        self.cache_db_path = cache_db_path
        self.init_cache_db()
        
        # Cache expiration times (in hours)
        self.expiration_times = {
            'linkedin_profile': 24,  # LinkedIn profiles change less frequently
            'github_profile': 12,    # GitHub activity is more dynamic
            'github_repos': 6,       # Repositories change frequently
            'twitter_profile': 24,   # Twitter profiles are relatively static
            'website_data': 48,      # Personal websites change slowly
            'search_results': 2,     # Search results change quickly
            'job_analysis': 168      # Job analysis can be cached longer (1 week)
        }
    
    def init_cache_db(self):
        """
        Initialize the cache database
        """
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            # Create cache table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    data TEXT,
                    cache_type TEXT,
                    created_at TIMESTAMP,
                    expires_at TIMESTAMP,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TIMESTAMP
                )
            ''')
            
            # Create index for faster lookups
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_cache_type_expires 
                ON cache(cache_type, expires_at)
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Cache database initialized")
            
        except Exception as e:
            logger.error(f"Error initializing cache database: {e}")
    
    def _generate_cache_key(self, data_type: str, identifier: str) -> str:
        """
        Generate a unique cache key
        """
        key_string = f"{data_type}:{identifier}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _is_expired(self, expires_at: str) -> bool:
        """
        Check if cache entry is expired
        """
        try:
            expires_time = datetime.fromisoformat(expires_at)
            return datetime.now() > expires_time
        except:
            return True
    
    def get(self, data_type: str, identifier: str) -> Optional[Any]:
        """
        Get data from cache
        """
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            cache_key = self._generate_cache_key(data_type, identifier)
            
            cursor.execute('''
                SELECT data, expires_at FROM cache 
                WHERE key = ? AND expires_at > ?
            ''', (cache_key, datetime.now().isoformat()))
            
            result = cursor.fetchone()
            
            if result:
                data, expires_at = result
                
                # Update access statistics
                cursor.execute('''
                    UPDATE cache 
                    SET access_count = access_count + 1, 
                        last_accessed = ? 
                    WHERE key = ?
                ''', (datetime.now().isoformat(), cache_key))
                
                conn.commit()
                conn.close()
                
                logger.info(f"Cache HIT for {data_type}:{identifier}")
                return json.loads(data)
            else:
                conn.close()
                logger.info(f"Cache MISS for {data_type}:{identifier}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting from cache: {e}")
            return None
    
    def set(self, data_type: str, identifier: str, data: Any, custom_expiration: Optional[int] = None):
        """
        Store data in cache
        """
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            cache_key = self._generate_cache_key(data_type, identifier)
            
            # Calculate expiration time
            expiration_hours = custom_expiration or self.expiration_times.get(data_type, 24)
            expires_at = datetime.now() + timedelta(hours=expiration_hours)
            
            # Store in cache
            cursor.execute('''
                INSERT OR REPLACE INTO cache 
                (key, data, cache_type, created_at, expires_at, access_count, last_accessed)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                cache_key,
                json.dumps(data),
                data_type,
                datetime.now().isoformat(),
                expires_at.isoformat(),
                0,
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Cached {data_type}:{identifier} (expires in {expiration_hours}h)")
            
        except Exception as e:
            logger.error(f"Error setting cache: {e}")
    
    def delete(self, data_type: str, identifier: str):
        """
        Delete specific cache entry
        """
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            cache_key = self._generate_cache_key(data_type, identifier)
            
            cursor.execute('DELETE FROM cache WHERE key = ?', (cache_key,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Deleted cache entry: {data_type}:{identifier}")
            
        except Exception as e:
            logger.error(f"Error deleting from cache: {e}")
    
    def clear_expired(self):
        """
        Clear all expired cache entries
        """
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM cache WHERE expires_at <= ?', (datetime.now().isoformat(),))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            logger.info(f"Cleared {deleted_count} expired cache entries")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error clearing expired cache: {e}")
            return 0
    
    def get_cache_stats(self) -> Dict:
        """
        Get cache statistics
        """
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            # Total entries
            cursor.execute('SELECT COUNT(*) FROM cache')
            total_entries = cursor.fetchone()[0]
            
            # Expired entries
            cursor.execute('SELECT COUNT(*) FROM cache WHERE expires_at <= ?', (datetime.now().isoformat(),))
            expired_entries = cursor.fetchone()[0]
            
            # Cache by type
            cursor.execute('''
                SELECT cache_type, COUNT(*) as count, 
                       AVG(access_count) as avg_access,
                       MAX(last_accessed) as last_access
                FROM cache 
                GROUP BY cache_type
            ''')
            
            type_stats = {}
            for row in cursor.fetchall():
                cache_type, count, avg_access, last_access = row
                type_stats[cache_type] = {
                    'count': count,
                    'avg_access': round(avg_access or 0, 2),
                    'last_access': last_access
                }
            
            conn.close()
            
            return {
                'total_entries': total_entries,
                'expired_entries': expired_entries,
                'active_entries': total_entries - expired_entries,
                'by_type': type_stats
            }
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}
    
    def get_cached_linkedin_profile(self, linkedin_url: str) -> Optional[Dict]:
        """
        Get cached LinkedIn profile data
        """
        return self.get('linkedin_profile', linkedin_url)
    
    def cache_linkedin_profile(self, linkedin_url: str, profile_data: Dict):
        """
        Cache LinkedIn profile data
        """
        self.set('linkedin_profile', linkedin_url, profile_data)
    
    def get_cached_github_data(self, github_username: str) -> Optional[Dict]:
        """
        Get cached GitHub data
        """
        return self.get('github_profile', github_username)
    
    def cache_github_data(self, github_username: str, github_data: Dict):
        """
        Cache GitHub data
        """
        self.set('github_profile', github_username, github_data)
        if github_data.get('github_repos'):
            self.set('github_repos', github_username, github_data['github_repos'])
    
    def get_cached_website_data(self, website_url: str) -> Optional[Dict]:
        """
        Get cached website data
        """
        return self.get('website_data', website_url)
    
    def cache_website_data(self, website_url: str, website_data: Dict):
        """
        Cache website data
        """
        self.set('website_data', website_url, website_data)
    
    def get_cached_search_results(self, search_query: str) -> Optional[List[Dict]]:
        """
        Get cached search results
        """
        result = self.get('search_results', search_query)
        return result if isinstance(result, list) else None
    
    def cache_search_results(self, search_query: str, results: List[Dict]):
        """
        Cache search results
        """
        self.set('search_results', search_query, results)
    
    def get_cached_job_analysis(self, job_description: str) -> Optional[Dict]:
        """
        Get cached job analysis
        """
        return self.get('job_analysis', job_description)
    
    def cache_job_analysis(self, job_description: str, analysis: Dict):
        """
        Cache job analysis
        """
        self.set('job_analysis', job_description, analysis)
    
    def invalidate_linkedin_profile(self, linkedin_url: str):
        """
        Invalidate LinkedIn profile cache
        """
        self.delete('linkedin_profile', linkedin_url)
    
    def invalidate_github_data(self, github_username: str):
        """
        Invalidate GitHub data cache
        """
        self.delete('github_profile', github_username)
        self.delete('github_repos', github_username)
    
    def invalidate_website_data(self, website_url: str):
        """
        Invalidate website data cache
        """
        self.delete('website_data', website_url)
    
    def cleanup_old_cache(self, days_old: int = 7):
        """
        Clean up cache entries older than specified days
        """
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            cursor.execute('DELETE FROM cache WHERE created_at <= ?', (cutoff_date.isoformat(),))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            logger.info(f"Cleaned up {deleted_count} cache entries older than {days_old} days")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old cache: {e}")
            return 0 