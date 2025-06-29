import sqlite3
import json
from datetime import datetime
from config import Config

class Database:
    def __init__(self, db_path=None):
        self.db_path = db_path or Config.DATABASE_PATH
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Jobs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_description TEXT NOT NULL,
                company_name TEXT,
                position_title TEXT,
                location TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Candidates table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER,
                name TEXT NOT NULL,
                linkedin_url TEXT UNIQUE,
                headline TEXT,
                current_company TEXT,
                location TEXT,
                education TEXT,
                experience TEXT,
                skills TEXT,
                fit_score REAL,
                score_breakdown TEXT,
                outreach_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_id) REFERENCES jobs (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_job(self, job_description, company_name=None, position_title=None, location=None):
        """Save a new job to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO jobs (job_description, company_name, position_title, location)
            VALUES (?, ?, ?, ?)
        ''', (job_description, company_name, position_title, location))
        
        job_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return job_id
    
    def save_candidate(self, job_id, candidate_data):
        """Save a candidate to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO candidates 
            (job_id, name, linkedin_url, headline, current_company, location, 
             education, experience, skills, fit_score, score_breakdown, outreach_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            job_id,
            candidate_data.get('name'),
            candidate_data.get('linkedin_url'),
            candidate_data.get('headline'),
            candidate_data.get('current_company'),
            candidate_data.get('location'),
            json.dumps(candidate_data.get('education', [])),
            json.dumps(candidate_data.get('experience', [])),
            json.dumps(candidate_data.get('skills', [])),
            candidate_data.get('fit_score'),
            json.dumps(candidate_data.get('score_breakdown', {})),
            candidate_data.get('outreach_message')
        ))
        
        conn.commit()
        conn.close()
    
    def get_candidates_for_job(self, job_id):
        """Retrieve all candidates for a specific job"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM candidates WHERE job_id = ? ORDER BY fit_score DESC
        ''', (job_id,))
        
        columns = [description[0] for description in cursor.description]
        candidates = []
        
        for row in cursor.fetchall():
            candidate = dict(zip(columns, row))
            # Parse JSON fields
            for field in ['education', 'experience', 'skills', 'score_breakdown']:
                if candidate[field]:
                    candidate[field] = json.loads(candidate[field])
                else:
                    candidate[field] = []
            candidates.append(candidate)
        
        conn.close()
        return candidates
    
    def get_job(self, job_id):
        """Retrieve a specific job"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM jobs WHERE id = ?', (job_id,))
        row = cursor.fetchone()
        
        if row:
            columns = [description[0] for description in cursor.description]
            job = dict(zip(columns, row))
        else:
            job = None
        
        conn.close()
        return job 