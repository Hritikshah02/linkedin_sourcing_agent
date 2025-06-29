import re
from config import Config

class CandidateScorer:
    def __init__(self):
        self.weights = Config.SCORING_WEIGHTS
        self.elite_schools = Config.ELITE_SCHOOLS
        self.top_tech_companies = Config.TOP_TECH_COMPANIES
    
    def score_candidates(self, candidates, job_description):
        """
        Score candidates based on job requirements and multi-source data
        """
        job_keywords = self._extract_job_keywords(job_description)
        
        scored_candidates = []
        for candidate in candidates:
            score_breakdown = {}
            
            # Education scoring (enhanced with multi-source data)
            education_score = self._score_education(candidate, job_keywords)
            score_breakdown['education'] = education_score
            
            # Career trajectory scoring
            trajectory_score = self._score_career_trajectory(candidate, job_keywords)
            score_breakdown['trajectory'] = trajectory_score
            
            # Company relevance scoring
            company_score = self._score_company_relevance(candidate, job_keywords)
            score_breakdown['company'] = company_score
            
            # Skills scoring (enhanced with GitHub and website data)
            skills_score = self._score_skills_enhanced(candidate, job_keywords)
            score_breakdown['skills'] = skills_score
            
            # Location scoring
            location_score = self._score_location(candidate, job_description)
            score_breakdown['location'] = location_score
            
            # Tenure scoring
            tenure_score = self._score_tenure(candidate)
            score_breakdown['tenure'] = tenure_score
            
            # Multi-source confidence bonus
            confidence_bonus = self._calculate_confidence_bonus(candidate)
            score_breakdown['confidence_bonus'] = confidence_bonus
            
            # Calculate weighted total score
            weights = {
                'education': 0.15,
                'trajectory': 0.20,
                'company': 0.20,
                'skills': 0.25,
                'location': 0.10,
                'tenure': 0.10
            }
            
            total_score = sum(score_breakdown[key] * weights[key] for key in weights.keys())
            
            # Add confidence bonus
            total_score += confidence_bonus
            
            # Cap at 10.0
            total_score = min(10.0, total_score)
            
            candidate['fit_score'] = round(total_score, 1)
            candidate['score_breakdown'] = score_breakdown
            
            scored_candidates.append(candidate)
        
        # Sort by fit score (highest first)
        scored_candidates.sort(key=lambda x: x['fit_score'], reverse=True)
        
        return scored_candidates
    
    def _calculate_score_breakdown(self, candidate, job_description):
        """
        Calculate individual component scores
        """
        return {
            'education': self._score_education(candidate),
            'trajectory': self._score_career_trajectory(candidate),
            'company': self._score_company_relevance(candidate),
            'skills': self._score_experience_match(candidate, job_description),
            'location': self._score_location_match(candidate, job_description),
            'tenure': self._score_tenure(candidate)
        }
    
    def _score_education(self, candidate, job_keywords=None):
        """
        Score education based on school prestige and degree relevance
        """
        education = candidate.get('education', [])
        headline = candidate.get('headline', '').lower()
        
        # If we have detailed education data, use it
        if education and len(education) > 0:
            max_score = 5.0
            for edu in education:
                school_name = edu.get('school', '').lower()
                degree = edu.get('degree', '').lower()
                
                # Check for elite schools
                if any(elite in school_name for elite in [s.lower() for s in self.elite_schools]):
                    if 'phd' in degree or 'doctorate' in degree:
                        return 10.0
                    elif 'masters' in degree or 'mba' in degree:
                        return 9.0
                    else:
                        return 8.0
                
                # Check for strong schools (state universities, etc.)
                elif any(strong in school_name for strong in ['university', 'college', 'institute']):
                    if 'phd' in degree or 'doctorate' in degree:
                        return 8.5
                    elif 'masters' in degree or 'mba' in degree:
                        return 7.5
                    else:
                        return 6.5
            
            return max_score
        
        # Fallback to headline analysis
        if any(degree in headline for degree in ['phd', 'ph.d', 'doctorate']):
            return 9.0
        elif any(degree in headline for degree in ['masters', 'ms', 'ma', 'mba']):
            return 7.5
        elif any(degree in headline for degree in ['bachelors', 'bs', 'ba']):
            return 6.0
        else:
            return 5.0
    
    def _score_career_trajectory(self, candidate, job_keywords=None):
        """
        Score career trajectory based on progression
        """
        experience = candidate.get('experience', [])
        headline = candidate.get('headline', '').lower()
        
        # If we have detailed experience data, use it
        if experience and len(experience) > 0:
            # Analyze progression
            titles = [exp.get('title', '').lower() for exp in experience]
            
            # Check for clear progression
            senior_titles = ['senior', 'lead', 'principal', 'director', 'vp', 'head', 'manager']
            mid_titles = ['engineer', 'developer', 'analyst', 'specialist', 'consultant']
            junior_titles = ['junior', 'associate', 'intern', 'assistant']
            
            senior_count = sum(1 for title in titles if any(s in title for s in senior_titles))
            mid_count = sum(1 for title in titles if any(s in title for s in mid_titles))
            junior_count = sum(1 for title in titles if any(s in title for s in junior_titles))
            
            if senior_count > 0:
                return 8.0
            elif mid_count > 0:
                return 6.5
            elif junior_count > 0:
                return 5.0
            else:
                return 4.0
        
        # Fallback to headline analysis
        if any(title in headline for title in ['senior', 'lead', 'principal', 'director', 'vp']):
            return 8.0
        elif any(title in headline for title in ['engineer', 'developer', 'analyst']):
            return 6.0
        else:
            return 5.0
    
    def _score_company_relevance(self, candidate, job_keywords=None):
        """
        Score company relevance based on company prestige and industry
        """
        experience = candidate.get('experience', [])
        current_company = candidate.get('current_company', '').lower()
        
        # Check current company first
        if any(company in current_company for company in [c.lower() for c in self.top_tech_companies]):
            return 9.0
        
        # Check all experience if available
        if experience and len(experience) > 0:
            for exp in experience:
                company = exp.get('company', '').lower()
                if any(top_company in company for top_company in [c.lower() for c in self.top_tech_companies]):
                    return 8.5
        
        # Check for relevant industry keywords
        relevant_keywords = ['tech', 'software', 'ai', 'machine learning', 'data', 'fintech', 'startup']
        if any(keyword in current_company for keyword in relevant_keywords):
            return 7.0
        
        return 5.0
    
    def _score_experience_match(self, candidate, job_description):
        """
        Score experience match based on skills and job requirements
        """
        skills = candidate.get('skills', [])
        headline = candidate.get('headline', '').lower()
        experience = candidate.get('experience', [])
        
        # Extract skills from job description
        job_skills = self._extract_skills_from_job_description(job_description)
        
        # If we have detailed skills data, use it
        if skills and len(skills) > 0:
            # Calculate skill match
            matched_skills = 0
            for skill in skills:
                if any(job_skill in skill.lower() for job_skill in job_skills):
                    matched_skills += 1
            
            if len(skills) == 0:
                return 5.0
            
            match_ratio = matched_skills / len(skills)
            
            if match_ratio >= 0.8:
                return 9.5
            elif match_ratio >= 0.6:
                return 8.0
            elif match_ratio >= 0.4:
                return 6.5
            elif match_ratio >= 0.2:
                return 5.0
            else:
                return 3.0
        
        # Fallback to headline and experience analysis
        all_text = headline + ' ' + ' '.join([exp.get('title', '') + ' ' + exp.get('description', '') for exp in experience])
        extracted_skills = self._extract_skills_from_text(all_text)
        
        if extracted_skills:
            matched_skills = 0
            for skill in extracted_skills:
                if any(job_skill in skill.lower() for job_skill in job_skills):
                    matched_skills += 1
            
            if len(extracted_skills) == 0:
                return 5.0
            
            match_ratio = matched_skills / len(extracted_skills)
            
            if match_ratio >= 0.8:
                return 9.5
            elif match_ratio >= 0.6:
                return 8.0
            elif match_ratio >= 0.4:
                return 6.5
            elif match_ratio >= 0.2:
                return 5.0
            else:
                return 3.0
        
        return 5.0
    
    def _score_location_match(self, candidate, job_description):
        """
        Score location match
        """
        candidate_location = candidate.get('location', '').lower()
        job_location = self._extract_location_from_job_description(job_description)
        
        if not candidate_location or not job_location:
            return 6.0  # Neutral score for remote-friendly positions
        
        # Exact city match
        if job_location in candidate_location:
            return 10.0
        
        # Same metro area
        metro_areas = {
            'san francisco': ['sf', 'bay area', 'silicon valley', 'palo alto', 'mountain view'],
            'new york': ['nyc', 'manhattan', 'brooklyn', 'queens'],
            'seattle': ['bellevue', 'redmond', 'kirkland'],
            'austin': ['round rock', 'cedar park'],
            'boston': ['cambridge', 'somerville', 'waltham']
        }
        
        for metro, cities in metro_areas.items():
            if job_location in metro or any(city in job_location for city in cities):
                if any(city in candidate_location for city in [metro] + cities):
                    return 8.0
        
        # Check for remote-friendly indicators
        if any(remote in job_description.lower() for remote in ['remote', 'work from home', 'wfh']):
            return 6.0
        
        return 4.0
    
    def _score_tenure(self, candidate):
        """
        Score tenure based on job stability
        """
        experience = candidate.get('experience', [])
        
        if not experience:
            return 5.0
        
        # Calculate average tenure
        total_years = 0
        job_count = len(experience)
        
        for exp in experience:
            duration = exp.get('duration', '')
            if duration:
                # Extract years from duration string
                years = self._extract_years_from_duration(duration)
                total_years += years
        
        if job_count == 0:
            return 5.0
        
        avg_tenure = total_years / job_count
        
        if avg_tenure >= 2.5:
            return 9.0
        elif avg_tenure >= 2.0:
            return 8.0
        elif avg_tenure >= 1.5:
            return 7.0
        elif avg_tenure >= 1.0:
            return 6.0
        else:
            return 4.0
    
    def _calculate_weighted_score(self, breakdown):
        """
        Calculate weighted final score
        """
        total_score = 0
        for component, score in breakdown.items():
            weight = self.weights.get(component, 0)
            total_score += score * weight
        
        return round(total_score, 1)
    
    def _extract_skills_from_job_description(self, job_description):
        """
        Extract relevant skills from job description
        """
        skills = []
        job_desc_lower = job_description.lower()
        
        # Common tech skills
        tech_skills = [
            'python', 'javascript', 'java', 'react', 'node.js', 'aws', 'docker', 'kubernetes',
            'machine learning', 'ai', 'ml', 'data science', 'backend', 'frontend', 'full stack',
            'sql', 'nosql', 'mongodb', 'postgresql', 'redis', 'elasticsearch', 'kafka',
            'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'git', 'jenkins',
            'terraform', 'ansible', 'microservices', 'api', 'rest', 'graphql'
        ]
        
        for skill in tech_skills:
            if skill in job_desc_lower:
                skills.append(skill)
        
        return skills
    
    def _extract_skills_from_text(self, text):
        """
        Extract skills from text
        """
        skills = []
        text_lower = text.lower()
        
        # Common tech skills
        tech_skills = [
            'python', 'javascript', 'java', 'react', 'node.js', 'aws', 'docker', 'kubernetes',
            'machine learning', 'ai', 'ml', 'data science', 'backend', 'frontend', 'full stack'
        ]
        
        for skill in tech_skills:
            if skill in text_lower:
                skills.append(skill)
        
        return skills
    
    def _extract_location_from_job_description(self, job_description):
        """
        Extract location from job description
        """
        location_patterns = [
            r'(?:in|at|based in)\s+([A-Za-z\s,]+)',
            r'location[:\s]+([A-Za-z\s,]+)',
            r'([A-Za-z\s]+),\s*[A-Z]{2}'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, job_description, re.IGNORECASE)
            if match:
                return match.group(1).strip().lower()
        
        return ""
    
    def _extract_years_from_duration(self, duration):
        """
        Extract years from duration string
        """
        duration_lower = duration.lower()
        
        # Look for year patterns
        year_patterns = [
            r'(\d+)\s*year',
            r'(\d+)\s*yr',
            r'(\d+)\s*y'
        ]
        
        for pattern in year_patterns:
            match = re.search(pattern, duration_lower)
            if match:
                return int(match.group(1))
        
        # Default to 1 year if no pattern found
        return 1
    
    def _extract_job_keywords(self, job_description):
        """
        Extract relevant keywords from job description
        """
        keywords = set()
        description_lower = job_description.lower()
        
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
            if keyword in description_lower:
                keywords.add(keyword)
        
        # Role keywords
        role_keywords = [
            'engineer', 'developer', 'programmer', 'architect', 'lead',
            'senior', 'junior', 'full stack', 'frontend', 'backend',
            'devops', 'data', 'analyst', 'scientist', 'manager'
        ]
        
        for keyword in role_keywords:
            if keyword in description_lower:
                keywords.add(keyword)
        
        return list(keywords)
    
    def _score_skills_enhanced(self, candidate, job_keywords):
        """
        Enhanced skills scoring using multi-source data
        """
        all_skills = set()
        
        # LinkedIn skills
        linkedin_skills = candidate.get('skills', [])
        if linkedin_skills:
            all_skills.update([skill.lower() for skill in linkedin_skills])
        
        # GitHub skills
        github_skills = candidate.get('github_skills', [])
        if github_skills:
            all_skills.update([skill.lower() for skill in github_skills])
        
        # Website skills
        website_skills = candidate.get('personal_website', {}).get('skills_found', [])
        if website_skills:
            all_skills.update([skill.lower() for skill in website_skills])
        
        if not all_skills:
            return 5.0
        
        # Calculate skill match
        job_keywords_lower = [kw.lower() for kw in job_keywords]
        matches = sum(1 for skill in all_skills if any(kw in skill or skill in kw for kw in job_keywords_lower))
        
        # Score based on match percentage
        match_percentage = matches / len(job_keywords_lower) if job_keywords_lower else 0
        
        # Bonus for having multiple sources
        source_bonus = 0
        if linkedin_skills:
            source_bonus += 0.5
        if github_skills:
            source_bonus += 1.0
        if website_skills:
            source_bonus += 0.5
        
        score = min(10.0, (match_percentage * 8.0) + source_bonus)
        return round(score, 1)
    
    def _score_location(self, candidate, job_description):
        """
        Score location relevance
        """
        candidate_location = candidate.get('location', '').lower()
        job_description_lower = job_description.lower()
        
        if not candidate_location:
            return 5.0
        
        # Common location keywords
        location_keywords = [
            'san francisco', 'sf', 'bay area', 'silicon valley',
            'new york', 'nyc', 'manhattan', 'brooklyn',
            'los angeles', 'la', 'seattle', 'austin', 'boston',
            'chicago', 'denver', 'atlanta', 'miami', 'remote',
            'hybrid', 'onsite', 'work from home'
        ]
        
        # Check if candidate location matches job requirements
        for location in location_keywords:
            if location in job_description_lower and location in candidate_location:
                return 10.0
            elif location in candidate_location:
                return 8.0
        
        return 5.0
    
    def _calculate_confidence_bonus(self, candidate):
        """
        Calculate bonus score based on data confidence
        """
        confidence = candidate.get('data_confidence', {})
        overall_confidence = confidence.get('overall', 0.0)
        
        # Bonus up to 1.0 point for high confidence
        bonus = overall_confidence * 1.0
        return round(bonus, 1) 