import PyPDF2
import os
import re
from typing import Dict, Optional

class PDFProcessor:
    def __init__(self):
        pass
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text content from a PDF file
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                return text.strip()
        except Exception as e:
            raise Exception(f"Error reading PDF: {e}")
    
    def parse_job_description(self, pdf_text: str) -> Dict[str, str]:
        """
        Parse job description text to extract structured information
        """
        # Initialize with default values
        job_info = {
            'job_description': pdf_text,
            'company_name': '',
            'position_title': '',
            'location': '',
            'salary': '',
            'requirements': []
        }
        
        # Extract company name (look for patterns like "at Company" or "Company is hiring")
        company_patterns = [
            r'at\s+([A-Z][A-Za-z\s&]+?)(?:\s+is|\s+in|\s+seeks|\s+looking)',
            r'([A-Z][A-Za-z\s&]+?)\s+is\s+hiring',
            r'([A-Z][A-Za-z\s&]+?)\s+seeks',
            r'([A-Z][A-Za-z\s&]+?)\s+looking\s+for'
        ]
        
        for pattern in company_patterns:
            match = re.search(pattern, pdf_text, re.IGNORECASE)
            if match:
                job_info['company_name'] = match.group(1).strip()
                break
        
        # Extract position title (look for patterns like "Position Title" or "Role:")
        title_patterns = [
            r'(?:Position|Role|Title)[:\s]+([A-Za-z\s]+?)(?:\n|\.|at|in)',
            r'([A-Za-z\s]+?(?:Engineer|Developer|Manager|Scientist|Analyst))(?:\s+at|\s+in)',
            r'We\s+are\s+hiring\s+a\s+([A-Za-z\s]+?)(?:\s+to|\s+for|\s+at)'
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, pdf_text, re.IGNORECASE)
            if match:
                job_info['position_title'] = match.group(1).strip()
                break
        
        # Extract location
        location_patterns = [
            r'(?:Location|Based in|Office in)[:\s]+([A-Za-z\s,]+?)(?:\n|\.|Salary|Requirements)',
            r'(?:in|at)\s+([A-Za-z\s]+?,\s*[A-Z]{2})(?:\s|\.|Salary|Requirements)',
            r'([A-Za-z\s]+?,\s*[A-Z]{2})(?:\s|\.|Salary|Requirements)'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, pdf_text, re.IGNORECASE)
            if match:
                job_info['location'] = match.group(1).strip()
                break
        
        # Extract salary information
        salary_patterns = [
            r'(?:Salary|Compensation)[:\s]+([$0-9,\-\s]+k?)(?:\n|\.|Requirements)',
            r'(\$[0-9,\-\s]+k?)(?:\s|\.|Requirements|Benefits)',
            r'([0-9,\-\s]+k?)(?:\s*\+\s*equity|\s*per\s*year)'
        ]
        
        for pattern in salary_patterns:
            match = re.search(pattern, pdf_text, re.IGNORECASE)
            if match:
                job_info['salary'] = match.group(1).strip()
                break
        
        # Extract requirements (look for bullet points or numbered lists)
        requirements = []
        lines = pdf_text.split('\n')
        in_requirements = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if we're entering requirements section
            if any(keyword in line.lower() for keyword in ['requirements:', 'qualifications:', 'what you need:', 'skills:', 'experience:']):
                in_requirements = True
                continue
            
            # Check if we're leaving requirements section
            if in_requirements and any(keyword in line.lower() for keyword in ['benefits:', 'perks:', 'about us:', 'apply:', 'contact:']):
                in_requirements = False
                continue
            
            # Extract requirement items
            if in_requirements and (line.startswith('-') or line.startswith('•') or line.startswith('*') or re.match(r'^\d+\.', line)):
                requirement = re.sub(r'^[-•*\d\.\s]+', '', line).strip()
                if requirement:
                    requirements.append(requirement)
        
        job_info['requirements'] = requirements
        
        return job_info
    
    def process_job_pdf(self, pdf_path: str) -> Dict[str, str]:
        """
        Process a job description PDF and return structured information
        """
        # Extract text from PDF
        pdf_text = self.extract_text_from_pdf(pdf_path)
        
        # Parse the job description
        job_info = self.parse_job_description(pdf_text)
        
        return job_info
    
    def print_job_summary(self, job_info: Dict[str, str]):
        """
        Print a summary of the extracted job information
        """
        print("\n" + "="*60)
        print("📄 EXTRACTED JOB INFORMATION")
        print("="*60)
        
        if job_info['company_name']:
            print(f"🏢 Company: {job_info['company_name']}")
        
        if job_info['position_title']:
            print(f"💼 Position: {job_info['position_title']}")
        
        if job_info['location']:
            print(f"📍 Location: {job_info['location']}")
        
        if job_info['salary']:
            print(f"💰 Salary: {job_info['salary']}")
        
        if job_info['requirements']:
            print(f"\n📋 Requirements ({len(job_info['requirements'])} items):")
            for i, req in enumerate(job_info['requirements'][:5], 1):  # Show first 5
                print(f"   {i}. {req}")
            if len(job_info['requirements']) > 5:
                print(f"   ... and {len(job_info['requirements']) - 5} more")
        
        print("="*60) 