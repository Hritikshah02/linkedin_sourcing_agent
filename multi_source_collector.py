#!/usr/bin/env python3
"""
Multi-Source Data Collector
Enhances LinkedIn data with GitHub, Twitter, and personal website information
"""

import requests
import re
import time
import json
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup, Tag
import logging
from typing import Dict, List, Optional, Tuple
from smart_cache import SmartCache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultiSourceCollector:
    """
    Collects candidate information from multiple sources:
    - LinkedIn (existing)
    - GitHub
    - Twitter/X
    - Personal websites
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.github_api_base = "https://api.github.com"
        self.twitter_api_base = "https://api.twitter.com/2"
        self.smart_cache = SmartCache()
        
    def extract_github_username(self, linkedin_url: str, name: str) -> Optional[str]:
        """
        Extract GitHub username from LinkedIn profile or search
        """
        try:
            # Try to find GitHub in LinkedIn profile
            response = self.session.get(linkedin_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for GitHub links in profile
                github_patterns = [
                    r'github\.com/([a-zA-Z0-9_-]+)',
                    r'@([a-zA-Z0-9_-]+)',
                    r'github\.com/([a-zA-Z0-9_-]+)'
                ]
                
                page_text = soup.get_text()
                for pattern in github_patterns:
                    matches = re.findall(pattern, page_text)
                    if matches:
                        return matches[0]
                
                # Search for GitHub links
                github_links = soup.find_all('a', href=re.compile(r'github\.com'))
                for link in github_links:
                    href = link.get('href', '')
                    match = re.search(r'github\.com/([a-zA-Z0-9_-]+)', href)
                    if match:
                        return match.group(1)
            
            # Fallback: search GitHub by name
            return self._search_github_by_name(name)
            
        except Exception as e:
            logger.warning(f"Error extracting GitHub username: {e}")
            return None
    
    def _search_github_by_name(self, name: str) -> Optional[str]:
        """
        Search GitHub users by name
        """
        try:
            # Simple name-based search (GitHub doesn't have public search API without auth)
            # This is a basic implementation - in production you'd use GitHub API with auth
            search_url = f"https://github.com/search?q={name}&type=users"
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                # Look for first user result
                user_links = soup.find_all('a', href=re.compile(r'/[a-zA-Z0-9_-]+$'))
                for link in user_links:
                    href = link.get('href', '')
                    if href.startswith('/') and len(href.split('/')) == 2:
                        return href.strip('/')
            
            return None
            
        except Exception as e:
            logger.warning(f"Error searching GitHub by name: {e}")
            return None
    
    def get_github_data(self, username: str) -> Dict:
        """
        Fetch GitHub profile data with caching
        """
        if not username:
            return {}
        
        # Check cache first
        cached_data = self.smart_cache.get_cached_github_data(username)
        if cached_data:
            logger.info(f"Using cached GitHub data for {username}")
            return cached_data
        
        try:
            # GitHub API endpoints (public data)
            profile_url = f"{self.github_api_base}/users/{username}"
            repos_url = f"{self.github_api_base}/users/{username}/repos"
            
            # Get profile data
            profile_response = self.session.get(profile_url, timeout=10)
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                
                # Get repositories
                repos_response = self.session.get(repos_url, timeout=10)
                repos_data = []
                if repos_response.status_code == 200:
                    repos_data = repos_response.json()
                
                github_data = {
                    'github_username': username,
                    'github_profile': {
                        'name': profile_data.get('name', ''),
                        'bio': profile_data.get('bio', ''),
                        'location': profile_data.get('location', ''),
                        'company': profile_data.get('company', ''),
                        'public_repos': profile_data.get('public_repos', 0),
                        'followers': profile_data.get('followers', 0),
                        'created_at': profile_data.get('created_at', ''),
                        'updated_at': profile_data.get('updated_at', '')
                    },
                    'github_repos': [
                        {
                            'name': repo.get('name', ''),
                            'description': repo.get('description', ''),
                            'language': repo.get('language', ''),
                            'stars': repo.get('stargazers_count', 0),
                            'forks': repo.get('forks_count', 0),
                            'created_at': repo.get('created_at', ''),
                            'updated_at': repo.get('updated_at', '')
                        }
                        for repo in repos_data[:10]  # Top 10 repos
                    ],
                    'github_skills': self._extract_github_skills(repos_data)
                }
                
                # Cache the data
                self.smart_cache.cache_github_data(username, github_data)
                logger.info(f"Cached GitHub data for {username}")
                
                return github_data
            
            return {}
            
        except Exception as e:
            logger.warning(f"Error fetching GitHub data for {username}: {e}")
            return {}
    
    def _extract_github_skills(self, repos: List[Dict]) -> List[str]:
        """
        Extract skills from GitHub repositories
        """
        skills = set()
        for repo in repos:
            language = repo.get('language', '')
            if language:
                skills.add(language)
            
            # Extract from description
            description = repo.get('description', '').lower()
            tech_keywords = [
                'python', 'javascript', 'java', 'react', 'node.js', 'django',
                'flask', 'vue', 'angular', 'typescript', 'go', 'rust', 'c++',
                'c#', 'php', 'ruby', 'swift', 'kotlin', 'scala', 'docker',
                'kubernetes', 'aws', 'azure', 'gcp', 'mongodb', 'postgresql',
                'mysql', 'redis', 'elasticsearch', 'kafka', 'spark', 'tensorflow',
                'pytorch', 'machine learning', 'ai', 'blockchain', 'web3'
            ]
            
            for keyword in tech_keywords:
                if keyword in description:
                    skills.add(keyword)
        
        return list(skills)
    
    def extract_twitter_username(self, linkedin_url: str, name: str) -> Optional[str]:
        """
        Extract Twitter username from LinkedIn profile
        """
        try:
            response = self.session.get(linkedin_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for Twitter links
                twitter_patterns = [
                    r'twitter\.com/([a-zA-Z0-9_]+)',
                    r'x\.com/([a-zA-Z0-9_]+)',
                    r'@([a-zA-Z0-9_]+)'
                ]
                
                page_text = soup.get_text()
                for pattern in twitter_patterns:
                    matches = re.findall(pattern, page_text)
                    if matches:
                        return matches[0]
                
                # Search for Twitter links
                twitter_links = soup.find_all('a', href=re.compile(r'(twitter\.com|x\.com)'))
                for link in twitter_links:
                    href = link.get('href', '')
                    match = re.search(r'(twitter\.com|x\.com)/([a-zA-Z0-9_]+)', href)
                    if match:
                        return match.group(2)
            
            return None
            
        except Exception as e:
            logger.warning(f"Error extracting Twitter username: {e}")
            return None
    
    def get_twitter_data(self, username: str) -> Dict:
        """
        Fetch Twitter profile data (basic public info)
        Note: Twitter API requires authentication, so this is limited
        """
        if not username:
            return {}
        
        try:
            # Try to get basic profile info from Twitter web page
            twitter_url = f"https://twitter.com/{username}"
            response = self.session.get(twitter_url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract basic info (this is limited due to Twitter's structure)
                return {
                    'twitter_username': username,
                    'twitter_profile': {
                        'username': username,
                        'url': twitter_url,
                        'exists': True
                    }
                }
            
            return {}
            
        except Exception as e:
            logger.warning(f"Error fetching Twitter data for {username}: {e}")
            return {}
    
    def find_personal_website(self, linkedin_url: str, name: str) -> Optional[str]:
        """
        Find personal website from LinkedIn profile
        """
        try:
            response = self.session.get(linkedin_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for website links
                website_patterns = [
                    r'https?://[^\s<>"]+',
                    r'www\.[^\s<>"]+'
                ]
                
                page_text = soup.get_text()
                for pattern in website_patterns:
                    matches = re.findall(pattern, page_text)
                    for match in matches:
                        if self._is_personal_website(match):
                            return match
                
                # Search for website links
                website_links = soup.find_all('a', href=re.compile(r'https?://'))
                for link in website_links:
                    href = link.get('href', '')
                    if self._is_personal_website(href):
                        return href
            
            return None
            
        except Exception as e:
            logger.warning(f"Error finding personal website: {e}")
            return None
    
    def _is_personal_website(self, url: str) -> bool:
        """
        Determine if URL is likely a personal website
        """
        if not url:
            return False
        
        # Exclude social media and common platforms
        exclude_domains = [
            'linkedin.com', 'github.com', 'twitter.com', 'x.com',
            'facebook.com', 'instagram.com', 'youtube.com', 'medium.com',
            'dev.to', 'hashnode.dev', 'substack.com', 'notion.so'
        ]
        
        try:
            domain = urlparse(url).netloc.lower()
            for exclude in exclude_domains:
                if exclude in domain:
                    return False
            return True
        except:
            return False
    
    def get_website_data(self, url: str) -> Dict:
        """
        Extract information from personal website with caching
        """
        if not url:
            return {}
        
        # Check cache first
        cached_data = self.smart_cache.get_cached_website_data(url)
        if cached_data:
            logger.info(f"Using cached website data for {url}")
            return cached_data
        
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract text content
                text_content = soup.get_text()
                
                # Extract skills and technologies
                skills = self._extract_website_skills(text_content)
                
                # Extract contact information
                contact_info = self._extract_contact_info(text_content)
                
                # Extract meta description safely
                meta_description = ''
                meta_tag = soup.find('meta', {'name': 'description'})
                if meta_tag and isinstance(meta_tag, Tag) and hasattr(meta_tag, 'attrs'):
                    meta_description = meta_tag.get('content', '')
                
                website_data = {
                    'personal_website': {
                        'url': url,
                        'title': soup.title.string if soup.title else '',
                        'description': meta_description,
                        'skills_found': skills,
                        'contact_info': contact_info
                    }
                }
                
                # Cache the data
                self.smart_cache.cache_website_data(url, website_data)
                logger.info(f"Cached website data for {url}")
                
                return website_data
            
            return {}
            
        except Exception as e:
            logger.warning(f"Error fetching website data for {url}: {e}")
            return {}
    
    def _extract_website_skills(self, text: str) -> List[str]:
        """
        Extract skills from website content
        """
        skills = set()
        text_lower = text.lower()
        
        # Technology keywords
        tech_keywords = [
            'python', 'javascript', 'java', 'react', 'node.js', 'django',
            'flask', 'vue', 'angular', 'typescript', 'go', 'rust', 'c++',
            'c#', 'php', 'ruby', 'swift', 'kotlin', 'scala', 'docker',
            'kubernetes', 'aws', 'azure', 'gcp', 'mongodb', 'postgresql',
            'mysql', 'redis', 'elasticsearch', 'kafka', 'spark', 'tensorflow',
            'pytorch', 'machine learning', 'ai', 'blockchain', 'web3',
            'html', 'css', 'sass', 'less', 'bootstrap', 'tailwind',
            'jquery', 'express', 'fastapi', 'spring', 'laravel', 'rails'
        ]
        
        for keyword in tech_keywords:
            if keyword in text_lower:
                skills.add(keyword)
        
        return list(skills)
    
    def _extract_contact_info(self, text: str) -> Dict:
        """
        Extract contact information from website
        """
        contact_info = {}
        
        # Email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact_info['email'] = emails[0]
        
        # Phone
        phone_pattern = r'(\+?1?[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
        phones = re.findall(phone_pattern, text)
        if phones:
            contact_info['phone'] = ''.join(phones[0])
        
        return contact_info
    
    def enhance_candidate_data(self, candidate: Dict) -> Dict:
        """
        Enhance candidate data with multi-source information
        """
        enhanced_candidate = candidate.copy()
        
        try:
            linkedin_url = candidate.get('linkedin_url', '')
            name = candidate.get('name', '')
            
            logger.info(f"Enhancing data for {name}")
            
            # Get GitHub data
            github_username = self.extract_github_username(linkedin_url, name)
            if github_username:
                github_data = self.get_github_data(github_username)
                enhanced_candidate.update(github_data)
                logger.info(f"Found GitHub data for {name}: {github_username}")
            
            # Get Twitter data
            twitter_username = self.extract_twitter_username(linkedin_url, name)
            if twitter_username:
                twitter_data = self.get_twitter_data(twitter_username)
                enhanced_candidate.update(twitter_data)
                logger.info(f"Found Twitter data for {name}: {twitter_username}")
            
            # Get personal website data
            website_url = self.find_personal_website(linkedin_url, name)
            if website_url:
                website_data = self.get_website_data(website_url)
                enhanced_candidate.update(website_data)
                logger.info(f"Found personal website for {name}: {website_url}")
            
            # Add confidence scoring
            enhanced_candidate['data_confidence'] = self._calculate_confidence(enhanced_candidate)
            
            return enhanced_candidate
            
        except Exception as e:
            logger.error(f"Error enhancing candidate data for {name}: {e}")
            return candidate
    
    def _calculate_confidence(self, candidate: Dict) -> Dict:
        """
        Calculate confidence levels for different data sources
        """
        confidence = {
            'linkedin': 0.8,  # Base LinkedIn confidence
            'github': 0.0,
            'twitter': 0.0,
            'website': 0.0,
            'overall': 0.0
        }
        
        # GitHub confidence
        if candidate.get('github_username'):
            confidence['github'] = 0.9
            if candidate.get('github_repos'):
                confidence['github'] = min(1.0, confidence['github'] + 0.1)
        
        # Twitter confidence
        if candidate.get('twitter_username'):
            confidence['twitter'] = 0.7
        
        # Website confidence
        if candidate.get('personal_website'):
            confidence['website'] = 0.8
            if candidate.get('personal_website', {}).get('skills_found'):
                confidence['website'] = min(1.0, confidence['website'] + 0.1)
        
        # Overall confidence (weighted average)
        weights = {'linkedin': 0.5, 'github': 0.3, 'twitter': 0.1, 'website': 0.1}
        overall = sum(confidence[source] * weights[source] for source in weights)
        confidence['overall'] = min(1.0, overall)
        
        return confidence 