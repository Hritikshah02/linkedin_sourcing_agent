import json
import requests
from config import Config

class MessageGenerator:
    def __init__(self):
        self.api_key = Config.OPENROUTER_API_KEY
        self.model = Config.OPENROUTER_MODEL
    
    def generate_outreach_messages(self, candidates, job_description, max_messages=5):
        """
        Generate personalized outreach messages for top candidates
        """
        if not self.api_key:
            print("⚠️  No OpenRouter API key found. Using template messages.")
            return self._generate_template_messages(candidates, job_description)
        
        print(f"🤖 Generating AI-powered messages for top {max_messages} candidates...")
        
        messages = []
        for i, candidate in enumerate(candidates[:max_messages]):
            try:
                message = self._generate_ai_message(candidate, job_description)
                candidate['outreach_message'] = message
                messages.append(candidate)
                print(f"   ✅ Generated message for {candidate['name']}")
            except Exception as e:
                print(f"   ❌ Error generating message for {candidate['name']}: {e}")
                # Fallback to template
                message = self._generate_template_message_single(candidate, job_description)
                candidate['outreach_message'] = message
                messages.append(candidate)
        
        return messages
    
    def _generate_ai_message(self, candidate, job_description):
        """
        Generate AI-powered personalized message
        """
        prompt = self._create_message_prompt(candidate, job_description)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 300
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
        else:
            raise Exception(f"API request failed: {response.status_code}")
    
    def _create_message_prompt(self, candidate, job_description):
        """
        Create a prompt for message generation
        """
        name = self._extract_clean_name(candidate.get('name', 'there'))
        headline = candidate.get('headline', '')
        current_company = candidate.get('current_company', '')
        location = candidate.get('location', '')
        fit_score = candidate.get('fit_score', 0)
        score_breakdown = candidate.get('score_breakdown', {})
        
        # Extract job details
        job_title = self._extract_job_title(job_description)
        company_name = self._extract_company_name(job_description)
        
        prompt = f"""
        Generate a professional LinkedIn outreach message for a candidate with the following details:
        
        Candidate Name: {name}
        Current Role: {headline}
        Current Company: {current_company}
        Location: {location}
        Fit Score: {fit_score}/10
        
        Score Breakdown:
        - Education: {score_breakdown.get('education', 0)}/10
        - Career Trajectory: {score_breakdown.get('trajectory', 0)}/10
        - Company Relevance: {score_breakdown.get('company', 0)}/10
        - Skills Match: {score_breakdown.get('skills', 0)}/10
        - Location: {score_breakdown.get('location', 0)}/10
        - Tenure: {score_breakdown.get('tenure', 0)}/10
        
        Job Details:
        - Position: {job_title}
        - Company: {company_name}
        - Description: {job_description[:300]}...
        
        Requirements for the message:
        1. Start with a professional greeting using their first name only
        2. Reference something specific from their background (role, company, or expertise)
        3. Mention the specific job opportunity and company
        4. Include a clear, professional call-to-action
        5. Keep it concise (under 150 words)
        6. Use professional, warm tone
        7. Don't be overly salesy or pushy
        8. End with a professional sign-off
        9. Make it feel personalized and relevant to their background
        
        Generate only the message content, no additional formatting or explanations.
        """
        
        return prompt
    
    def _generate_template_messages(self, candidates, job_description):
        """
        Generate template messages when OpenRouter is not available
        """
        messages = []
        
        for candidate in candidates:
            message = self._generate_template_message_single(candidate, job_description)
            candidate['outreach_message'] = message
            messages.append(candidate)
        
        return messages
    
    def _generate_template_message_single(self, candidate, job_description):
        """
        Generate a single template message with improved professional language
        """
        name = self._extract_clean_name(candidate.get('name', 'there'))
        headline = candidate.get('headline', '')
        current_company = candidate.get('current_company', '')
        fit_score = candidate.get('fit_score', 0)
        
        # Extract job details
        job_title = self._extract_job_title(job_description)
        company_name = self._extract_company_name(job_description)
        
        # Clean up company name
        if company_name:
            company_name = company_name.strip()
        else:
            company_name = "our company"
        
        # Extract role from headline
        role = self._extract_role_from_headline(headline)
        
        if fit_score >= 8:
            template = f"""Hi {name},

I came across your profile and was impressed by your work as {role} at {current_company}. Your background in {self._extract_key_skills(headline)} aligns perfectly with a {job_title} opportunity I'm recruiting for at {company_name}.

Would you be open to a brief conversation about this role? I'd love to share more details and see if it might be a good fit for your career goals.

Best regards"""
        elif fit_score >= 6:
            template = f"""Hi {name},

I noticed your experience as {role} and thought you might be interested in a {job_title} opportunity I'm working on at {company_name}.

Your background in {self._extract_key_skills(headline)} seems relevant to what we're looking for. Would you be open to learning more about this role?

Best regards"""
        else:
            template = f"""Hi {name},

I'm reaching out about a {job_title} opportunity at {company_name} that might be of interest given your background in tech.

Would you be open to a quick chat about this role?

Best regards"""
        
        return template
    
    def _extract_clean_name(self, name):
        """
        Extract clean first name from candidate name
        """
        if not name:
            return "there"
        
        # Remove LinkedIn suffixes and extra info
        suffixes = [' | LinkedIn', ' - LinkedIn', ' (@', ' •', '\nLinkedIn', 'LinkedIn ·']
        clean_name = name
        for suffix in suffixes:
            if suffix in clean_name:
                clean_name = clean_name.split(suffix)[0]
        
        # Extract first name
        first_name = clean_name.split()[0] if clean_name.split() else "there"
        return first_name.strip()
    
    def _extract_job_title(self, job_description):
        """
        Extract job title from job description
        """
        titles = [
            'Software Engineer, ML Research', 'Machine Learning Engineer', 'ML Engineer', 
            'AI Engineer', 'Research Engineer', 'Software Engineer', 'Backend Engineer', 
            'Frontend Engineer', 'Full Stack Engineer', 'Data Scientist', 'DevOps Engineer', 
            'Product Manager', 'Senior Engineer', 'Lead Engineer', 'Principal Engineer', 
            'Research Scientist', 'Applied Scientist'
        ]
        
        job_desc_lower = job_description.lower()
        for title in titles:
            if title.lower() in job_desc_lower:
                return title
        
        return "Software Engineer"
    
    def _extract_company_name(self, job_description):
        """
        Extract company name from job description
        """
        # Look for company name patterns
        patterns = [
            r'at\s+([A-Z][A-Za-z\s&]+?)(?:\s+is|\s+in|\s+seeks|\s+looking|\s+we)',
            r'([A-Z][A-Za-z\s&]+?)\s+is\s+looking',
            r'([A-Z][A-Za-z\s&]+?)\s+seeks',
            r'join\s+([A-Z][A-Za-z\s&]+?)',
            r'work\s+at\s+([A-Z][A-Za-z\s&]+?)'
        ]
        
        import re
        for pattern in patterns:
            match = re.search(pattern, job_description, re.IGNORECASE)
            if match:
                company = match.group(1).strip()
                if len(company) > 2 and len(company) < 50:
                    return company
        
        return ""
    
    def _extract_role_from_headline(self, headline):
        """
        Extract role from headline
        """
        if not headline:
            return "a software engineer"
        
        # Look for role patterns
        role_patterns = [
            r'([^•\n]+) at',
            r'([^•\n]+) -',
            r'([^•\n]+) \|'
        ]
        
        import re
        for pattern in role_patterns:
            match = re.search(pattern, headline)
            if match:
                role = match.group(1).strip()
                if len(role) > 3 and len(role) < 50:
                    return role
        
        return "a software engineer"
    
    def _extract_key_skills(self, headline):
        """
        Extract key skills from headline
        """
        if not headline:
            return "software development"
        
        # Look for skill keywords
        skills = ['AI', 'ML', 'Machine Learning', 'Software Engineering', 'Data Science', 
                 'Backend', 'Frontend', 'Full Stack', 'DevOps', 'Cloud', 'AWS', 'Python', 
                 'JavaScript', 'React', 'Node.js', 'Database', 'API', 'Microservices']
        
        found_skills = []
        for skill in skills:
            if skill.lower() in headline.lower():
                found_skills.append(skill)
        
        if found_skills:
            return ", ".join(found_skills[:2])  # Return max 2 skills
        
        return "software development" 