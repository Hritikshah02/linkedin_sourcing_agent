import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from config import Config

class LinkedInSearcher:
    def __init__(self):
        self.driver = None
        self.setup_driver()

    def setup_driver(self):
        """Setup Chrome WebDriver with webdriver-manager for automatic ChromeDriver management"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in background
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument(f"--user-agent={Config.USER_AGENT}")
        
        # Add additional options to avoid detection
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            # Use webdriver-manager to automatically download and manage ChromeDriver
            print("🔧 Setting up Chrome WebDriver...")
            
            # Get the ChromeDriver path and fix it if needed
            driver_path = ChromeDriverManager().install()
            
            # Fix the path if it points to a documentation file
            if "THIRD_PARTY_NOTICES" in driver_path:
                import os
                # Navigate to the parent directory and find chromedriver.exe
                parent_dir = os.path.dirname(driver_path)
                chromedriver_exe = os.path.join(parent_dir, "chromedriver.exe")
                if os.path.exists(chromedriver_exe):
                    driver_path = chromedriver_exe
                    print(f"   Fixed ChromeDriver path: {driver_path}")
                else:
                    # Try to find chromedriver.exe in the directory
                    for file in os.listdir(parent_dir):
                        if file == "chromedriver.exe":
                            driver_path = os.path.join(parent_dir, file)
                            print(f"   Found ChromeDriver: {driver_path}")
                            break
            
            self.driver = webdriver.Chrome(
                service=Service(driver_path),
                options=chrome_options
            )
            
            # Execute script to remove webdriver property
            if self.driver:
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                print("✅ Chrome WebDriver setup complete!")
        except Exception as e:
            print(f"❌ Error setting up Chrome driver: {e}")
            print("Please ensure Chrome browser is installed")
            self.driver = None

    def search_linkedin_profiles(self, job_description, max_results=20):
        """
        Search for LinkedIn profiles using Selenium-based Google X-Ray search.
        """
        if not self.driver:
            print("❌ Chrome driver not available. Cannot perform search.")
            return []

        # Extract X-Ray search query
        xray_query = self._build_xray_query(job_description)
        print(f"🔍 Google X-Ray query: {xray_query}")
        
        candidates = self._selenium_google_xray_search(xray_query, max_results)
        print(f"   Total unique candidates found: {len(candidates)}")
        return candidates

    def _build_xray_query(self, job_description):
        """
        Build a Google X-Ray search query from the job description.
        Format: site:linkedin.com/in/ AND ("job title" OR "skills") AND ("location" OR "company")
        """
        job_title = self._extract_job_title(job_description)
        skills = self._extract_skills(job_description)
        location = self._extract_location(job_description)
        company = self._extract_company(job_description)

        # Build the query
        query = 'site:linkedin.com/in/'
        or_terms = []
        if job_title:
            or_terms.append(f'"{job_title}"')
        if skills:
            or_terms.append(f'"{skills[0]}"')
        if or_terms:
            query += f' AND ({" OR ".join(or_terms)})'
        and_terms = []
        if location:
            and_terms.append(f'"{location}"')
        if company:
            and_terms.append(f'"{company}"')
        if and_terms:
            query += f' AND ({" OR ".join(and_terms)})'
        return query

    def _selenium_google_xray_search(self, query, max_results=10):
        """
        Perform Google X-Ray search using Selenium
        """
        if not self.driver:
            return []
            
        try:
            # Navigate to Google
            search_url = f"https://www.google.com/search?q={query}&num={max_results}"
            print(f"   Navigating to: {search_url}")
            
            self.driver.get(search_url)
            time.sleep(3)  # Wait for page to load
            
            # Wait for search results to appear
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.g, div[data-sokoban-container], div.tF2Cxc, div.yuRUbf")))
            
            candidates = []
            
            # Find all search result containers
            search_selectors = [
                "div.g",
                "div[data-sokoban-container]", 
                "div.tF2Cxc",
                "div.yuRUbf",
                "div.rc"
            ]
            
            search_results = []
            for selector in search_selectors:
                try:
                    results = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if results:
                        search_results = results
                        print(f"   Found {len(results)} results using selector: {selector}")
                        break
                except Exception as e:
                    continue
            
            if not search_results:
                print("   No search results found with any selector")
                return []
            
            # Process each search result
            for result in search_results[:max_results]:
                try:
                    # Find the link element
                    link_element = None
                    link_selectors = ["a", "h3 a", "h2 a"]
                    
                    for selector in link_selectors:
                        try:
                            links = result.find_elements(By.CSS_SELECTOR, selector)
                            for link in links:
                                href = link.get_attribute('href')
                                if href and 'linkedin.com/in/' in href:
                                    link_element = link
                                    break
                            if link_element:
                                break
                        except:
                            continue
                    
                    if not link_element:
                        continue
                    
                    # Extract LinkedIn URL
                    linkedin_url = link_element.get_attribute('href')
                    if not linkedin_url or 'linkedin.com/in/' not in linkedin_url:
                        continue
                    
                    # Extract title
                    title = link_element.text.strip()
                    if not title:
                        # Try to get title from parent elements
                        try:
                            title_element = result.find_element(By.CSS_SELECTOR, "h3, h2")
                            title = title_element.text.strip()
                        except:
                            title = "LinkedIn Profile"
                    
                    # Extract snippet
                    snippet = ""
                    snippet_selectors = [
                        "div.VwiC3b",
                        "div.s3v9rd", 
                        "span.st",
                        "div.s",
                        "div.rc div.s div.st"
                    ]
                    
                    for selector in snippet_selectors:
                        try:
                            snippet_element = result.find_element(By.CSS_SELECTOR, selector)
                            snippet = snippet_element.text.strip()
                            if snippet:
                                break
                        except:
                            continue
                    
                    # Extract profile ID
                    profile_id = self._extract_linkedin_profile_id(linkedin_url)
                    if profile_id:
                        candidate = {
                            'name': self._extract_name_from_title(title),
                            'linkedin_url': f"https://www.linkedin.com/in/{profile_id}",
                            'headline': self._extract_headline_from_snippet(snippet),
                            'current_company': self._extract_company_from_snippet(snippet),
                            'location': self._extract_location_from_snippet(snippet),
                            'education': [],
                            'experience': [],
                            'skills': []
                        }
                        candidates.append(candidate)
                        print(f"   Found candidate: {candidate['name']} - {candidate['headline']}")
                
                except Exception as e:
                    print(f"   Error parsing search result: {e}")
                    continue
            
            return self._deduplicate_candidates(candidates)
            
        except TimeoutException:
            print("   Timeout waiting for search results")
            return []
        except Exception as e:
            print(f"   Error performing Selenium Google X-Ray search: {e}")
            return []

    def _extract_job_title(self, job_description):
        titles = [
            'machine learning engineer', 'ml engineer', 'ai engineer', 'research engineer',
            'software engineer', 'backend engineer', 'frontend engineer', 'full stack engineer',
            'data scientist', 'devops engineer', 'product manager', 'senior engineer',
            'lead engineer', 'principal engineer', 'research scientist', 'applied scientist'
        ]
        job_desc_lower = job_description.lower()
        for title in titles:
            if title in job_desc_lower:
                return title
        return ''

    def _extract_skills(self, job_description):
        skills = [
            'python', 'javascript', 'java', 'react', 'node.js', 'aws', 'docker', 'kubernetes',
            'machine learning', 'ai', 'ml', 'data science', 'backend', 'frontend', 'full stack',
            'pytorch', 'tensorflow', 'llm', 'neural networks', 'deep learning', 'nlp',
            'computer vision', 'reinforcement learning', 'statistics', 'sql', 'nosql'
        ]
        job_desc_lower = job_description.lower()
        found = [skill for skill in skills if skill in job_desc_lower]
        return found

    def _extract_location(self, job_description):
        location_patterns = [
            r'(?:in|at|based in|located in)\s+([A-Za-z\s,]+?)(?:\s+and|\s+we|\s+is|\s+looking)',
            r'([A-Za-z\s,]+?),\s*[A-Z]{2}(?:\s+and|\s+we|\s+is|\s+looking)',
            r'remote\s+(?:from\s+)?([A-Za-z\s,]+)',
            r'([A-Za-z\s,]+?)\s+area'
        ]
        for pattern in location_patterns:
            match = re.search(pattern, job_description, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                location = re.sub(r'\s+', ' ', location).strip()
                if len(location) > 2 and len(location) < 30:
                    return location
        return ''

    def _extract_company(self, job_description):
        company_patterns = [
            r'at\s+([A-Z][A-Za-z\s&]+?)(?:\s+is|\s+in|\s+seeks|\s+looking|\s+we)',
            r'([A-Z][A-Za-z\s&]+?)\s+is\s+looking',
            r'([A-Z][A-Za-z\s&]+?)\s+seeks',
            r'join\s+([A-Z][A-Za-z\s&]+?)',
            r'work\s+at\s+([A-Z][A-Za-z\s&]+?)'
        ]
        for pattern in company_patterns:
            match = re.search(pattern, job_description, re.IGNORECASE)
            if match:
                company = match.group(1).strip()
                company = re.sub(r'\s+', ' ', company).strip()
                if len(company) > 2 and len(company) < 50:
                    return company
        return ''

    def _extract_linkedin_profile_id(self, url):
        try:
            if '/in/' in url:
                profile_part = url.split('/in/')[1]
                profile_id = profile_part.split('?')[0].split('/')[0]
                return profile_id
        except:
            pass
        return None

    def _extract_name_from_title(self, title):
        suffixes = [' | LinkedIn', ' - LinkedIn', ' (@', ' •']
        name = title
        for suffix in suffixes:
            if suffix in name:
                name = name.split(suffix)[0]
        return name.strip()

    def _extract_headline_from_snippet(self, snippet):
        patterns = [
            r'([^•]+) at ([^•]+)',
            r'([^•]+) - ([^•]+)',
            r'([^•]+) \| ([^•]+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, snippet)
            if match:
                return f"{match.group(1).strip()} at {match.group(2).strip()}"
        return snippet[:100] if snippet else ""

    def _extract_company_from_snippet(self, snippet):
        patterns = [
            r'at ([^•\n]+)',
            r'- ([^•\n]+)',
            r'\| ([^•\n]+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, snippet)
            if match:
                company = match.group(1).strip()
                company = re.sub(r'\d+', '', company).strip()
                return company
        return ""

    def _extract_location_from_snippet(self, snippet):
        location_patterns = [
            r'([A-Za-z\s]+), ([A-Z]{2})',
            r'([A-Za-z\s]+), ([A-Za-z\s]+)',
        ]
        for pattern in location_patterns:
            match = re.search(pattern, snippet)
            if match:
                return f"{match.group(1).strip()}, {match.group(2).strip()}"
        return ""

    def _deduplicate_candidates(self, candidates):
        seen_urls = set()
        unique_candidates = []
        for candidate in candidates:
            if candidate['linkedin_url'] not in seen_urls:
                seen_urls.add(candidate['linkedin_url'])
                unique_candidates.append(candidate)
        return unique_candidates

    def get_profile_details(self, linkedin_url):
        """
        Extract detailed profile information from LinkedIn profile
        Note: This is a simplified version that extracts from search snippets
        For full profile scraping, you would need to implement actual LinkedIn profile parsing
        """
        if not self.driver:
            return {
                'education': [],
                'experience': [],
                'skills': []
            }
        
        try:
            # Navigate to the profile
            self.driver.get(linkedin_url)
            time.sleep(3)
            
            # Extract education
            education = self._extract_education_from_profile()
            
            # Extract experience
            experience = self._extract_experience_from_profile()
            
            # Extract skills
            skills = self._extract_skills_from_profile()
            
            # If we couldn't extract detailed data, try fallback extraction
            if not education or not experience:
                print("   Using fallback extraction for missing data...")
                fallback_data = self._extract_fallback_data()
                if not education and fallback_data.get('education'):
                    education = fallback_data['education']
                if not experience and fallback_data.get('experience'):
                    experience = fallback_data['experience']
            
            # Final validation - if we still don't have valid data, return empty arrays
            if not self._has_valid_education_data(education):
                print("   No valid education data found, returning empty array")
                education = []
            
            if not self._has_valid_experience_data(experience):
                print("   No valid experience data found, returning empty array")
                experience = []
            
            return {
                'education': education,
                'experience': experience,
                'skills': skills
            }
            
        except Exception as e:
            print(f"   Error extracting profile details: {e}")
            # Return empty arrays instead of trying fallback when profile access fails
            return {
                'education': [],
                'experience': [],
                'skills': []
            }
    
    def _has_valid_education_data(self, education_list):
        """
        Check if education list contains valid data
        """
        if not education_list:
            return False
        
        for edu in education_list:
            if self._is_valid_education_data(edu.get('school', ''), edu.get('degree', '')):
                return True
        
        return False
    
    def _has_valid_experience_data(self, experience_list):
        """
        Check if experience list contains valid data
        """
        if not experience_list:
            return False
        
        for exp in experience_list:
            if self._is_valid_experience_data(exp.get('title', ''), exp.get('company', '')):
                return True
        
        return False

    def _extract_education_from_profile(self):
        """
        Extract education information from profile
        """
        education = []
        try:
            if not self.driver:
                return education
                
            # More comprehensive education selectors
            education_selectors = [
                "section[data-section='education']",
                ".education-section",
                "[data-test-id='education']",
                ".pv-education-entity",
                ".education-item",
                "[data-control-name='education_section']",
                ".background-education",
                ".education"
            ]
            
            for selector in education_selectors:
                try:
                    education_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if education_elements:
                        print(f"   Found education section with selector: {selector}")
                        for element in education_elements[:3]:  # Limit to 3 most recent
                            try:
                                # Try multiple selectors for school name
                                school_selectors = [
                                    "h3", ".school-name", ".institution-name", 
                                    ".pv-entity__school-name", ".education__school-name",
                                    ".pv-entity__degree-name", ".degree-name"
                                ]
                                school = ""
                                for school_selector in school_selectors:
                                    try:
                                        school_element = element.find_element(By.CSS_SELECTOR, school_selector)
                                        school = school_element.text.strip()
                                        if school:
                                            break
                                    except:
                                        continue
                                
                                # Try multiple selectors for degree
                                degree_selectors = [
                                    ".degree-name", ".field-of-study", ".pv-entity__degree-name",
                                    ".pv-entity__field-of-study", ".education__degree-name"
                                ]
                                degree = ""
                                for degree_selector in degree_selectors:
                                    try:
                                        degree_element = element.find_element(By.CSS_SELECTOR, degree_selector)
                                        degree = degree_element.text.strip()
                                        if degree:
                                            break
                                    except:
                                        continue
                                
                                if school or degree:
                                    education.append({
                                        'school': school,
                                        'degree': degree,
                                        'duration': ''
                                    })
                                    print(f"   Extracted education: {degree} from {school}")
                            except Exception as e:
                                print(f"   Error extracting individual education item: {e}")
                                continue
                        if education:
                            break
                except Exception as e:
                    print(f"   Error with education selector {selector}: {e}")
                    continue
            
            # If no structured education found, try to extract from page text
            if not education and self.driver:
                print("   Attempting text-based education extraction...")
                page_text = self.driver.page_source.lower()
                education_keywords = ['university', 'college', 'institute', 'school', 'bachelor', 'master', 'phd', 'mba']
                
                # Look for education patterns in the text
                import re
                education_patterns = [
                    r'([A-Z][A-Za-z\s&]+(?:University|College|Institute|School))',
                    r'(Bachelor|Master|PhD|MBA|BSc|MSc|MS|MA|BS|BA)\s+(?:of|in|from)\s+([A-Z][A-Za-z\s&]+)',
                    r'([A-Z][A-Za-z\s&]+)\s+(?:University|College|Institute|School)'
                ]
                
                for pattern in education_patterns:
                    matches = re.findall(pattern, self.driver.page_source, re.IGNORECASE)
                    for match in matches[:2]:  # Limit to 2 matches
                        if isinstance(match, tuple):
                            degree, school = match
                        else:
                            school = match
                            degree = "Degree"
                        
                        education.append({
                            'school': school.strip(),
                            'degree': degree.strip(),
                            'duration': ''
                        })
                        print(f"   Extracted education from text: {degree} from {school}")
                        break
                
        except Exception as e:
            print(f"   Error extracting education: {e}")
        
        return education
    
    def _extract_experience_from_profile(self):
        """
        Extract experience information from profile
        """
        experience = []
        try:
            if not self.driver:
                return experience
                
            # More comprehensive experience selectors
            experience_selectors = [
                "section[data-section='experience']",
                ".experience-section",
                "[data-test-id='experience']",
                ".pv-position-entity",
                ".experience-item",
                "[data-control-name='experience_section']",
                ".background-experience",
                ".experience"
            ]
            
            for selector in experience_selectors:
                try:
                    experience_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if experience_elements:
                        print(f"   Found experience section with selector: {selector}")
                        for element in experience_elements[:5]:  # Limit to 5 most recent
                            try:
                                # Try multiple selectors for job title
                                title_selectors = [
                                    "h3", ".job-title", ".position-title", 
                                    ".pv-entity__summary-info-v3__title",
                                    ".experience__title", ".role-title"
                                ]
                                title = ""
                                for title_selector in title_selectors:
                                    try:
                                        title_element = element.find_element(By.CSS_SELECTOR, title_selector)
                                        title = title_element.text.strip()
                                        if title:
                                            break
                                    except:
                                        continue
                                
                                # Try multiple selectors for company name
                                company_selectors = [
                                    ".company-name", ".organization-name", 
                                    ".pv-entity__secondary-title",
                                    ".experience__company", ".company"
                                ]
                                company = ""
                                for company_selector in company_selectors:
                                    try:
                                        company_element = element.find_element(By.CSS_SELECTOR, company_selector)
                                        company = company_element.text.strip()
                                        if company:
                                            break
                                    except:
                                        continue
                                
                                # Try multiple selectors for duration
                                duration_selectors = [
                                    ".date-range", ".duration", ".pv-entity__date-range",
                                    ".experience__duration", ".time-period"
                                ]
                                duration = ""
                                for duration_selector in duration_selectors:
                                    try:
                                        duration_element = element.find_element(By.CSS_SELECTOR, duration_selector)
                                        duration = duration_element.text.strip()
                                        if duration:
                                            break
                                    except:
                                        continue
                                
                                if title or company:
                                    experience.append({
                                        'title': title,
                                        'company': company,
                                        'duration': duration,
                                        'description': ''
                                    })
                                    print(f"   Extracted experience: {title} at {company}")
                            except Exception as e:
                                print(f"   Error extracting individual experience item: {e}")
                                continue
                        if experience:
                            break
                except Exception as e:
                    print(f"   Error with experience selector {selector}: {e}")
                    continue
            
        except Exception as e:
            print(f"   Error extracting experience: {e}")
        
        return experience
    
    def _extract_skills_from_profile(self):
        """
        Extract skills from profile
        """
        skills = []
        try:
            if not self.driver:
                return skills
                
            # More comprehensive skills selectors
            skills_selectors = [
                "section[data-section='skills']",
                ".skills-section",
                "[data-test-id='skills']",
                ".skill-categories",
                ".pv-skill-category-entity",
                ".skill-item",
                ".endorsed-skill",
                ".skill"
            ]
            
            for selector in skills_selectors:
                try:
                    skill_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if skill_elements:
                        print(f"   Found skills section with selector: {selector}")
                        for element in skill_elements[:10]:  # Limit to 10 skills
                            try:
                                # Try multiple selectors for skill names
                                skill_selectors = [
                                    ".skill-name", ".skill-title", ".pv-skill-category-entity__name",
                                    ".endorsed-skill__name", ".skill__name", "span", "div"
                                ]
                                skill = ""
                                for skill_selector in skill_selectors:
                                    try:
                                        skill_element = element.find_element(By.CSS_SELECTOR, skill_selector)
                                        skill = skill_element.text.strip()
                                        if skill and len(skill) > 2 and len(skill) < 50:
                                            # Filter out common non-skill text
                                            if skill.lower() not in ['endorsed', 'skill', 'skills', 'add skill', 'show more']:
                                                break
                                    except:
                                        continue
                                
                                if skill and skill not in skills:
                                    skills.append(skill)
                                    print(f"   Extracted skill: {skill}")
                            except Exception as e:
                                print(f"   Error extracting individual skill: {e}")
                                continue
                        if skills:
                            break
                except Exception as e:
                    print(f"   Error with skills selector {selector}: {e}")
                    continue
            
            # If no structured skills found, try to extract from text
            if not skills and self.driver:
                print("   Attempting text-based skills extraction...")
                page_text = self.driver.page_source.lower()
                tech_skills = [
                    'python', 'javascript', 'java', 'react', 'node.js', 'aws', 'docker', 'kubernetes',
                    'machine learning', 'ai', 'ml', 'data science', 'backend', 'frontend', 'full stack',
                    'sql', 'nosql', 'mongodb', 'postgresql', 'redis', 'elasticsearch', 'kafka',
                    'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'git', 'jenkins',
                    'terraform', 'ansible', 'microservices', 'api', 'rest', 'graphql', 'html', 'css',
                    'typescript', 'angular', 'vue.js', 'express.js', 'django', 'flask', 'spring',
                    'hibernate', 'junit', 'maven', 'gradle', 'npm', 'yarn', 'webpack', 'babel',
                    'jest', 'cypress', 'selenium', 'jira', 'confluence', 'slack', 'zoom', 'figma',
                    'sketch', 'adobe', 'photoshop', 'illustrator', 'invision', 'zeplin'
                ]
                
                for skill in tech_skills:
                    if skill in page_text:
                        skills.append(skill.title())
                
        except Exception as e:
            print(f"   Error extracting skills: {e}")
        
        return skills[:10]  # Return max 10 skills

    def _extract_fallback_data(self):
        """
        Extract education and experience from available text when detailed scraping fails
        """
        fallback_data = {
            'education': [],
            'experience': [],
            'skills': []
        }
        
        try:
            # Get the page source for text analysis
            page_text = self.driver.page_source if self.driver else ""
            
            # Extract education from text patterns
            import re
            education_patterns = [
                r'([A-Z][A-Za-z\s&]+(?:University|College|Institute|School))',
                r'(Bachelor|Master|PhD|MBA|BSc|MSc|MS|MA|BS|BA)\s+(?:of|in|from)\s+([A-Z][A-Za-z\s&]+)',
                r'([A-Z][A-Za-z\s&]+)\s+(?:University|College|Institute|School)',
                r'(MIT|Stanford|Harvard|Berkeley|CMU|Caltech|Princeton|Yale|Columbia|Cornell|UCLA|UCSD)',
                r'(Bachelor|Master|PhD|MBA|BSc|MSc|MS|MA|BS|BA)\s+(?:degree|in|of)',
            ]
            
            for pattern in education_patterns:
                matches = re.findall(pattern, page_text, re.IGNORECASE)
                for match in matches[:2]:  # Limit to 2 matches
                    if isinstance(match, tuple):
                        if len(match) == 2:
                            degree, school = match
                        else:
                            continue
                    else:
                        if 'university' in match.lower() or 'college' in match.lower() or 'institute' in match.lower():
                            school = match
                            degree = "Degree"
                        elif match.upper() in ['MIT', 'STANFORD', 'HARVARD', 'BERKELEY', 'CMU', 'CALTECH', 'PRINCETON', 'YALE', 'COLUMBIA', 'CORNELL', 'UCLA', 'UCSD']:
                            school = match
                            degree = "Degree"
                        else:
                            degree = match
                            school = "University"
                    
                    # Validate the extracted data
                    if self._is_valid_education_data(school.strip(), degree.strip()):
                        # Check if we already have this education entry
                        existing = [e for e in fallback_data['education'] if e['school'] == school.strip()]
                        if not existing:
                            fallback_data['education'].append({
                                'school': school.strip(),
                                'degree': degree.strip(),
                                'duration': ''
                            })
                            print(f"   Fallback extracted education: {degree} from {school}")
            
            # Extract experience from text patterns
            experience_patterns = [
                r'([A-Z][A-Za-z\s&]+)\s+(?:at|@)\s+([A-Z][A-Za-z\s&]+)',
                r'(Senior|Lead|Principal|Software|Data|ML|AI|Full Stack|Backend|Frontend)\s+(Engineer|Developer|Scientist|Architect|Manager)',
                r'([A-Z][A-Za-z\s&]+)\s+(?:Engineer|Developer|Scientist|Architect|Manager)',
            ]
            
            for pattern in experience_patterns:
                matches = re.findall(pattern, page_text, re.IGNORECASE)
                for match in matches[:3]:  # Limit to 3 matches
                    if isinstance(match, tuple):
                        if len(match) == 2:
                            title, company = match
                        else:
                            continue
                    else:
                        title = match
                        company = "Company"
                    
                    # Validate the extracted data
                    if self._is_valid_experience_data(title.strip(), company.strip()):
                        # Check if we already have this experience entry
                        existing = [e for e in fallback_data['experience'] if e['title'] == title.strip()]
                        if not existing:
                            fallback_data['experience'].append({
                                'title': title.strip(),
                                'company': company.strip(),
                                'duration': '',
                                'description': ''
                            })
                            print(f"   Fallback extracted experience: {title} at {company}")
            
            # Extract skills from text
            tech_skills = [
                'python', 'javascript', 'java', 'react', 'node.js', 'aws', 'docker', 'kubernetes',
                'machine learning', 'ai', 'ml', 'data science', 'backend', 'frontend', 'full stack',
                'sql', 'nosql', 'mongodb', 'postgresql', 'redis', 'elasticsearch', 'kafka',
                'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'git', 'jenkins',
                'terraform', 'ansible', 'microservices', 'api', 'rest', 'graphql', 'html', 'css',
                'typescript', 'angular', 'vue.js', 'express.js', 'django', 'flask', 'spring',
                'hibernate', 'junit', 'maven', 'gradle', 'npm', 'yarn', 'webpack', 'babel',
                'jest', 'cypress', 'selenium', 'jira', 'confluence', 'slack', 'zoom', 'figma',
                'sketch', 'adobe', 'photoshop', 'illustrator', 'invision', 'zeplin'
            ]
            
            for skill in tech_skills:
                if skill in page_text.lower():
                    fallback_data['skills'].append(skill.title())
            
            fallback_data['skills'] = fallback_data['skills'][:10]  # Limit to 10 skills
            
        except Exception as e:
            print(f"   Error in fallback data extraction: {e}")
        
        return fallback_data
    
    def _is_valid_education_data(self, school, degree):
        """
        Validate if extracted education data is legitimate
        """
        # Filter out common invalid patterns
        invalid_patterns = [
            'password', 'must have', 'least', 'character', 'number', 'letter',
            'uppercase', 'lowercase', 'special', 'symbol', 'validation',
            'error', 'invalid', 'required', 'field', 'form', 'submit',
            'login', 'signup', 'register', 'account', 'profile', 'settings'
        ]
        
        school_lower = school.lower()
        degree_lower = degree.lower()
        
        # Check for invalid patterns
        for pattern in invalid_patterns:
            if pattern in school_lower or pattern in degree_lower:
                return False
        
        # Check for minimum length and meaningful content
        if len(school) < 3 or len(degree) < 3:
            return False
        
        # Check if it looks like a real school name
        if not any(char.isalpha() for char in school):
            return False
        
        # Check if it looks like a real degree
        if not any(char.isalpha() for char in degree):
            return False
        
        # Filter out generic/meaningless data
        if degree_lower in ['degree', 'diploma', 'certificate'] and len(school) < 5:
            return False
        
        # Check for more specific degree patterns
        degree_keywords = [
            'bachelor', 'master', 'phd', 'doctorate', 'mba', 'ms', 'ma', 'bs', 'ba',
            'science', 'engineering', 'arts', 'business', 'computer', 'technology'
        ]
        
        has_meaningful_degree = any(keyword in degree_lower for keyword in degree_keywords)
        
        return has_meaningful_degree
    
    def _is_valid_experience_data(self, title, company):
        """
        Validate if extracted experience data is legitimate
        """
        # Filter out common invalid patterns
        invalid_patterns = [
            'password', 'must have', 'least', 'character', 'number', 'letter',
            'uppercase', 'lowercase', 'special', 'symbol', 'validation',
            'error', 'invalid', 'required', 'field', 'form', 'submit',
            'login', 'signup', 'register', 'account', 'profile', 'settings',
            'button', 'click', 'submit', 'save', 'cancel', 'delete', 'edit'
        ]
        
        title_lower = title.lower()
        company_lower = company.lower()
        
        # Check for invalid patterns
        for pattern in invalid_patterns:
            if pattern in title_lower or pattern in company_lower:
                return False
        
        # Check for minimum length and meaningful content
        if len(title) < 3 or len(company) < 3:
            return False
        
        # Check if it looks like a real job title
        if not any(char.isalpha() for char in title):
            return False
        
        # Check if it looks like a real company name
        if not any(char.isalpha() for char in company):
            return False
        
        # Check for common job title keywords
        job_keywords = [
            'engineer', 'developer', 'scientist', 'architect', 'manager',
            'analyst', 'specialist', 'consultant', 'lead', 'senior',
            'principal', 'director', 'vp', 'head', 'chief', 'officer'
        ]
        
        has_job_keyword = any(keyword in title_lower for keyword in job_keywords)
        
        return has_job_keyword

    def __del__(self):
        """Cleanup driver when object is destroyed"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass 