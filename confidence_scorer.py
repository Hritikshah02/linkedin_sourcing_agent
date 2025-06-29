#!/usr/bin/env python3
"""
Confidence Scoring System
Evaluates data quality and completeness for candidate profiles
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ConfidenceMetrics:
    """Confidence metrics for different data sources"""
    linkedin: float = 0.0
    github: float = 0.0
    twitter: float = 0.0
    website: float = 0.0
    overall: float = 0.0
    data_completeness: float = 0.0
    data_freshness: float = 0.0
    data_consistency: float = 0.0
    reliability_score: float = 0.0

class ConfidenceScorer:
    """
    Comprehensive confidence scoring system
    """
    
    def __init__(self):
        # Data quality indicators
        self.quality_indicators = {
            'linkedin': {
                'profile_complete': 0.9,
                'has_headline': 0.7,
                'has_location': 0.6,
                'has_company': 0.8,
                'has_skills': 0.8,
                'has_education': 0.9,
                'has_experience': 0.9,
                'recent_activity': 0.7
            },
            'github': {
                'profile_exists': 0.8,
                'has_repos': 0.9,
                'has_activity': 0.8,
                'has_bio': 0.6,
                'has_location': 0.5,
                'has_company': 0.6,
                'recent_commits': 0.8,
                'stars_received': 0.7
            },
            'twitter': {
                'profile_exists': 0.6,
                'has_bio': 0.5,
                'has_location': 0.4,
                'has_website': 0.6,
                'recent_tweets': 0.7,
                'verified_account': 0.9
            },
            'website': {
                'site_accessible': 0.8,
                'has_contact_info': 0.9,
                'has_skills_section': 0.8,
                'has_portfolio': 0.9,
                'has_about_section': 0.7,
                'professional_design': 0.6,
                'mobile_friendly': 0.5
            }
        }
        
        # Data freshness thresholds (in days)
        self.freshness_thresholds = {
            'linkedin': 30,  # LinkedIn profiles updated within 30 days
            'github': 7,     # GitHub activity within 7 days
            'twitter': 14,   # Twitter activity within 14 days
            'website': 90    # Website updated within 90 days
        }
    
    def calculate_comprehensive_confidence(self, candidate: Dict) -> ConfidenceMetrics:
        """
        Calculate comprehensive confidence metrics for a candidate
        """
        metrics = ConfidenceMetrics()
        
        # Calculate source-specific confidence
        metrics.linkedin = self._calculate_linkedin_confidence(candidate)
        metrics.github = self._calculate_github_confidence(candidate)
        metrics.twitter = self._calculate_twitter_confidence(candidate)
        metrics.website = self._calculate_website_confidence(candidate)
        
        # Calculate overall metrics
        metrics.overall = self._calculate_overall_confidence(metrics)
        metrics.data_completeness = self._calculate_data_completeness(candidate)
        metrics.data_freshness = self._calculate_data_freshness(candidate)
        metrics.data_consistency = self._calculate_data_consistency(candidate)
        metrics.reliability_score = self._calculate_reliability_score(metrics)
        
        return metrics
    
    def _calculate_linkedin_confidence(self, candidate: Dict) -> float:
        """
        Calculate LinkedIn profile confidence
        """
        confidence = 0.0
        indicators = self.quality_indicators['linkedin']
        
        # Basic profile completeness
        if candidate.get('name'):
            confidence += indicators['profile_complete']
        
        if candidate.get('headline'):
            confidence += indicators['has_headline']
        
        if candidate.get('location'):
            confidence += indicators['has_location']
        
        if candidate.get('current_company'):
            confidence += indicators['has_company']
        
        # Skills and experience
        skills = candidate.get('skills', [])
        if skills and len(skills) > 0:
            confidence += indicators['has_skills']
        
        education = candidate.get('education', [])
        if education and len(education) > 0:
            confidence += indicators['has_education']
        
        experience = candidate.get('experience', [])
        if experience and len(experience) > 0:
            confidence += indicators['has_experience']
        
        # Normalize to 0-1 range
        return min(1.0, confidence / len(indicators))
    
    def _calculate_github_confidence(self, candidate: Dict) -> float:
        """
        Calculate GitHub profile confidence
        """
        confidence = 0.0
        indicators = self.quality_indicators['github']
        
        github_profile = candidate.get('github_profile', {})
        github_repos = candidate.get('github_repos', [])
        
        if github_profile:
            confidence += indicators['profile_exists']
            
            if github_profile.get('bio'):
                confidence += indicators['has_bio']
            
            if github_profile.get('location'):
                confidence += indicators['has_location']
            
            if github_profile.get('company'):
                confidence += indicators['has_company']
            
            if github_profile.get('public_repos', 0) > 0:
                confidence += indicators['has_repos']
            
            if github_profile.get('followers', 0) > 0:
                confidence += indicators['has_activity']
        
        # Repository analysis
        if github_repos:
            # Check for recent activity
            recent_repos = [repo for repo in github_repos 
                          if self._is_recent_date(repo.get('updated_at', ''), 30)]
            if recent_repos:
                confidence += indicators['recent_commits']
            
            # Check for stars
            total_stars = sum(repo.get('stars', 0) for repo in github_repos)
            if total_stars > 0:
                confidence += indicators['stars_received']
        
        return min(1.0, confidence / len(indicators))
    
    def _calculate_twitter_confidence(self, candidate: Dict) -> float:
        """
        Calculate Twitter profile confidence
        """
        confidence = 0.0
        indicators = self.quality_indicators['twitter']
        
        twitter_profile = candidate.get('twitter_profile', {})
        
        if twitter_profile:
            confidence += indicators['profile_exists']
            
            # Note: Twitter API access is limited, so confidence is lower
            # In a real implementation, you'd check for bio, location, etc.
            confidence += indicators['has_bio'] * 0.5  # Reduced confidence
        
        return min(1.0, confidence / len(indicators))
    
    def _calculate_website_confidence(self, candidate: Dict) -> float:
        """
        Calculate personal website confidence
        """
        confidence = 0.0
        indicators = self.quality_indicators['website']
        
        personal_website = candidate.get('personal_website', {})
        
        if personal_website:
            confidence += indicators['site_accessible']
            
            contact_info = personal_website.get('contact_info', {})
            if contact_info.get('email') or contact_info.get('phone'):
                confidence += indicators['has_contact_info']
            
            skills_found = personal_website.get('skills_found', [])
            if skills_found:
                confidence += indicators['has_skills_section']
            
            # Check for professional indicators
            title = personal_website.get('title', '').lower()
            description = personal_website.get('description', '').lower()
            
            professional_keywords = ['portfolio', 'resume', 'cv', 'developer', 'engineer']
            if any(keyword in title or keyword in description for keyword in professional_keywords):
                confidence += indicators['has_portfolio']
            
            if 'about' in title or 'about' in description:
                confidence += indicators['has_about_section']
        
        return min(1.0, confidence / len(indicators))
    
    def _calculate_overall_confidence(self, metrics: ConfidenceMetrics) -> float:
        """
        Calculate overall confidence score
        """
        # Weighted average based on data source reliability
        weights = {
            'linkedin': 0.5,   # Most reliable
            'github': 0.3,     # Very reliable for tech roles
            'twitter': 0.1,    # Less reliable
            'website': 0.1     # Variable reliability
        }
        
        overall = (
            metrics.linkedin * weights['linkedin'] +
            metrics.github * weights['github'] +
            metrics.twitter * weights['twitter'] +
            metrics.website * weights['website']
        )
        
        return min(1.0, overall)
    
    def _calculate_data_completeness(self, candidate: Dict) -> float:
        """
        Calculate data completeness score
        """
        required_fields = [
            'name', 'linkedin_url', 'headline', 'location', 
            'current_company', 'skills', 'education', 'experience'
        ]
        
        optional_fields = [
            'github_username', 'github_profile', 'github_repos',
            'twitter_username', 'twitter_profile',
            'personal_website'
        ]
        
        # Calculate completeness
        required_present = sum(1 for field in required_fields if candidate.get(field))
        optional_present = sum(1 for field in optional_fields if candidate.get(field))
        
        # Weight required fields more heavily
        completeness = (required_present * 0.7 + optional_present * 0.3) / (len(required_fields) * 0.7 + len(optional_fields) * 0.3)
        
        return min(1.0, completeness)
    
    def _calculate_data_freshness(self, candidate: Dict) -> float:
        """
        Calculate data freshness score
        """
        freshness_scores = []
        
        # Check LinkedIn profile freshness (if we had timestamps)
        # For now, assume moderate freshness
        freshness_scores.append(0.7)
        
        # Check GitHub activity
        github_repos = candidate.get('github_repos', [])
        if github_repos:
            recent_repos = [repo for repo in github_repos 
                          if self._is_recent_date(repo.get('updated_at', ''), 30)]
            github_freshness = len(recent_repos) / len(github_repos) if github_repos else 0.0
            freshness_scores.append(github_freshness)
        
        # Check website freshness (if we had timestamps)
        if candidate.get('personal_website'):
            freshness_scores.append(0.6)  # Assume moderate freshness
        
        return sum(freshness_scores) / len(freshness_scores) if freshness_scores else 0.5
    
    def _calculate_data_consistency(self, candidate: Dict) -> float:
        """
        Calculate data consistency score
        """
        consistency_checks = []
        
        # Check name consistency across sources
        name = candidate.get('name', '').lower()
        github_name = candidate.get('github_profile', {}).get('name', '').lower()
        
        if name and github_name:
            name_similarity = self._calculate_name_similarity(name, github_name)
            consistency_checks.append(name_similarity)
        
        # Check location consistency
        linkedin_location = candidate.get('location', '').lower()
        github_location = candidate.get('github_profile', {}).get('location', '').lower()
        
        if linkedin_location and github_location:
            location_similarity = self._calculate_location_similarity(linkedin_location, github_location)
            consistency_checks.append(location_similarity)
        
        # Check skills consistency
        linkedin_skills = set(skill.lower() for skill in candidate.get('skills', []))
        github_skills = set(skill.lower() for skill in candidate.get('github_skills', []))
        website_skills = set(skill.lower() for skill in candidate.get('personal_website', {}).get('skills_found', []))
        
        all_skills = linkedin_skills | github_skills | website_skills
        if all_skills:
            # Calculate overlap
            skill_overlaps = []
            if linkedin_skills and github_skills:
                overlap = len(linkedin_skills & github_skills) / len(linkedin_skills | github_skills)
                skill_overlaps.append(overlap)
            if linkedin_skills and website_skills:
                overlap = len(linkedin_skills & website_skills) / len(linkedin_skills | website_skills)
                skill_overlaps.append(overlap)
            if github_skills and website_skills:
                overlap = len(github_skills & website_skills) / len(github_skills | website_skills)
                skill_overlaps.append(overlap)
            
            if skill_overlaps:
                consistency_checks.append(sum(skill_overlaps) / len(skill_overlaps))
        
        return sum(consistency_checks) / len(consistency_checks) if consistency_checks else 0.7
    
    def _calculate_reliability_score(self, metrics: ConfidenceMetrics) -> float:
        """
        Calculate overall reliability score
        """
        # Combine all metrics with weights
        weights = {
            'overall': 0.4,
            'data_completeness': 0.3,
            'data_freshness': 0.2,
            'data_consistency': 0.1
        }
        
        reliability = (
            metrics.overall * weights['overall'] +
            metrics.data_completeness * weights['data_completeness'] +
            metrics.data_freshness * weights['data_freshness'] +
            metrics.data_consistency * weights['data_consistency']
        )
        
        return min(1.0, reliability)
    
    def _is_recent_date(self, date_string: str, days_threshold: int) -> bool:
        """
        Check if a date string is within the threshold
        """
        try:
            from datetime import datetime, timedelta
            if not date_string:
                return False
            
            date_obj = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            threshold_date = datetime.now() - timedelta(days=days_threshold)
            return date_obj > threshold_date
        except:
            return False
    
    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """
        Calculate similarity between two names
        """
        # Simple word-based similarity
        words1 = set(name1.split())
        words2 = set(name2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_location_similarity(self, location1: str, location2: str) -> float:
        """
        Calculate similarity between two locations
        """
        # Simple word-based similarity
        words1 = set(location1.split())
        words2 = set(location2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def get_confidence_summary(self, metrics: ConfidenceMetrics) -> Dict:
        """
        Get a human-readable confidence summary
        """
        summary = {
            'overall_confidence': f"{metrics.overall:.1%}",
            'reliability': f"{metrics.reliability_score:.1%}",
            'data_quality': {
                'completeness': f"{metrics.data_completeness:.1%}",
                'freshness': f"{metrics.data_freshness:.1%}",
                'consistency': f"{metrics.data_consistency:.1%}"
            },
            'source_confidence': {
                'linkedin': f"{metrics.linkedin:.1%}",
                'github': f"{metrics.github:.1%}",
                'twitter': f"{metrics.twitter:.1%}",
                'website': f"{metrics.website:.1%}"
            },
            'recommendations': self._generate_recommendations(metrics)
        }
        
        return summary
    
    def _generate_recommendations(self, metrics: ConfidenceMetrics) -> List[str]:
        """
        Generate recommendations for improving confidence
        """
        recommendations = []
        
        if metrics.overall < 0.7:
            recommendations.append("Overall confidence is low - consider manual verification")
        
        if metrics.linkedin < 0.8:
            recommendations.append("LinkedIn profile data is incomplete")
        
        if metrics.github < 0.6:
            recommendations.append("GitHub profile could provide additional insights")
        
        if metrics.data_completeness < 0.6:
            recommendations.append("Profile data is incomplete - missing key information")
        
        if metrics.data_freshness < 0.5:
            recommendations.append("Data may be outdated - consider recent updates")
        
        if metrics.data_consistency < 0.7:
            recommendations.append("Data consistency issues detected across sources")
        
        if not recommendations:
            recommendations.append("Profile data quality is good")
        
        return recommendations 