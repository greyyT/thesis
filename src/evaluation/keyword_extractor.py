"""Keyword extraction from job descriptions for baseline FRR evaluation."""
import re
from typing import List, Dict, Any, Optional, Set, Union
from dataclasses import dataclass
import pandas as pd


@dataclass
class JobRequirements:
    """Parsed job requirements structure."""
    required_skills: List[str]
    experience_years: int
    education_level: Optional[str]
    nice_to_have: List[str]


class KeywordExtractor:
    """Extract keywords and requirements from job descriptions using rule-based patterns."""
    
    def __init__(self):
        """Initialize with common skill mappings and patterns."""
        # Common skill abbreviations and aliases
        self.skill_aliases = {
            "js": "javascript",
            "ml": "machine learning",
            "ai": "artificial intelligence",
            "db": "database",
            "mysql": "mysql",
            "sql server": "sql",
            "postgresql": "postgresql",
            "postgres": "postgresql",
            "node.js": "nodejs",
            "nodejs": "nodejs",
            "react.js": "react",
            "vue.js": "vue",
            "angular.js": "angular",
            "tf": "tensorflow",
            "k8s": "kubernetes",
            "aws": "amazon web services",
            "gcp": "google cloud platform",
            "ci/cd": "continuous integration",
        }
        
        # Common technical skills to recognize
        self.known_skills = {
            "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
            "html", "css", "react", "angular", "vue", "nodejs", "node.js", "express",
            "mysql", "postgresql", "mongodb", "redis", "sql", "nosql",
            "docker", "kubernetes", "aws", "azure", "gcp", "terraform",
            "git", "jenkins", "gitlab", "github", "ci/cd",
            "machine learning", "deep learning", "tensorflow", "pytorch",
            "pandas", "numpy", "scikit-learn", "statistics", "data science",
            "fastapi", "django", "flask", "spring", "rest api", "graphql",
            "microservices", "cloud", "devops", "agile", "scrum"
        }
    
    def extract_required_skills(self, job_description: str) -> List[str]:
        """Extract required skills from job description text.
        
        Args:
            job_description: Raw job description text
            
        Returns:
            List of extracted skill names
        """
        if not job_description:
            return []
        
        skills = set()
        text = job_description.lower()
        
        # Pattern 1: Skills listed after "required skills:", "requirements:", etc.
        skill_section_patterns = [
            r"required skills?:?\s*\n?(.+?)(?:\n\s*\n|\nexperience|\neducation|$)",
            r"requirements?:?\s*\n?(.+?)(?:\n\s*\n|\nexperience|\neducation|$)",
            r"technical skills?:?\s*\n?(.+?)(?:\n\s*\n|\nexperience|\neducation|$)",
            r"must have:?\s*\n?(.+?)(?:\n\s*\n|\nexperience|\neducation|$)",
        ]
        
        for pattern in skill_section_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                skills.update(self._parse_skill_list(match))
        
        # Pattern 2: Look for skills in bullet points
        bullet_skills = re.findall(r"[•\-\*]\s*([^•\-\*\n]+)", text)
        for skill_text in bullet_skills:
            skills.update(self._parse_skill_list(skill_text))
        
        # Pattern 3: Direct skill mentions in text
        for skill in self.known_skills:
            if skill in text:
                skills.add(skill)
        
        # Normalize and filter skills
        normalized_skills = []
        for skill in skills:
            if skill and skill.strip():
                normalized = self.normalize_skill(skill.strip())
                if normalized and len(normalized) > 1:  # Filter out single characters
                    normalized_skills.append(normalized)
        
        return list(set(normalized_skills))  # Remove duplicates
    
    def extract_experience_years(self, text: Any) -> int:
        """Extract experience requirements in years.
        
        Args:
            text: Text to search for experience requirements
            
        Returns:
            Number of years required (0 if not specified)
        """
        if not text or pd.isna(text):
            return 0
        
        text = str(text).lower()
        
        # Handle "fresh graduate" or "no experience" cases
        if any(phrase in text for phrase in ["fresh graduate", "no experience", "entry level"]):
            return 0
        
        # Patterns for extracting years - order matters for ranges
        year_patterns = [
            r"(\d+)-\d+\s*years?",  # Take minimum from range - check this first
            r"(\d+)\+?\s*years?",
            r"minimum\s+(\d+)\s*years?",
            r"at least\s+(\d+)\s*years?",
            r"(\d+)\s*years?\s+(?:of\s+)?experience",
            r"(\d+)\s*years?\s+(?:of\s+)?(?:relevant\s+)?experience",
        ]
        
        for pattern in year_patterns:
            matches = re.findall(pattern, text)
            if matches:
                try:
                    return int(matches[0])
                except (ValueError, IndexError):
                    continue
        
        return 0
    
    def extract_education_requirements(self, text: Any) -> Optional[str]:
        """Extract education level requirements.
        
        Args:
            text: Text to search for education requirements
            
        Returns:
            Education level or None if not specified
        """
        if not text or pd.isna(text):
            return None
        
        text = str(text).lower()
        
        education_patterns = [
            (r"phd|doctorate", "PhD"),
            (r"master'?s?|msc|ms\b", "Master's"),
            (r"bachelor'?s?|bsc|bs\b|undergraduate", "Bachelor's"),
            (r"associate'?s?", "Associate"),
            (r"high school|diploma", "High School"),
        ]
        
        for pattern, level in education_patterns:
            if re.search(pattern, text):
                return level
        
        return None
    
    def parse_job_description(self, job_description: str) -> Dict[str, Any]:
        """Parse complete job description into structured requirements.
        
        Args:
            job_description: Raw job description text
            
        Returns:
            Dictionary with parsed requirements
        """
        if not job_description:
            return {
                "required_skills": [],
                "experience_years": 0,
                "education_level": None,
                "nice_to_have": []
            }
        
        return {
            "required_skills": self.extract_required_skills(job_description),
            "experience_years": self.extract_experience_years(job_description),
            "education_level": self.extract_education_requirements(job_description),
            "nice_to_have": self._extract_nice_to_have(job_description)
        }
    
    def normalize_skill(self, skill: str) -> str:
        """Normalize skill name to standard format.
        
        Args:
            skill: Raw skill name
            
        Returns:
            Normalized skill name
        """
        if not skill:
            return ""
        
        # Clean and lowercase
        normalized = skill.lower().strip()
        
        # Remove special characters and extra spaces
        normalized = re.sub(r'[^\w\s\-\+\.]', '', normalized)
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        # Check for skill within the text (for compound phrases) - longest match first
        for known_skill in sorted(self.known_skills, key=len, reverse=True):
            if known_skill in normalized and len(known_skill) > 2:  # Avoid short matches
                normalized = known_skill
                break
        
        # Apply aliases
        if normalized in self.skill_aliases:
            normalized = self.skill_aliases[normalized]
        
        # Handle common variations - but preserve specific SQL databases
        if normalized in ["mysql", "postgresql", "mongodb"]:
            # Keep specific database names
            pass
        elif "sql" in normalized and normalized != "sql" and normalized not in ["mysql", "postgresql"]:
            normalized = "sql"  # Other SQL variants -> SQL
        
        return normalized
    
    def find_skill_matches(self, job_skills: List[str], candidate_skills: str, fuzzy: bool = False) -> List[str]:
        """Find matching skills between job requirements and candidate.
        
        Args:
            job_skills: List of required skills from job
            candidate_skills: Candidate's skills as string
            fuzzy: Whether to use fuzzy/approximate matching
            
        Returns:
            List of matching skills
        """
        if not candidate_skills:
            return []
        
        # Normalize job skills
        job_skills_normalized = [self.normalize_skill(skill) for skill in job_skills]
        
        # Extract and normalize candidate skills
        candidate_skills_list = self._parse_skill_list(candidate_skills)
        candidate_skills_normalized = [self.normalize_skill(skill) for skill in candidate_skills_list]
        
        matches = []
        
        for i, job_skill in enumerate(job_skills_normalized):
            if not job_skill:
                continue
                
            # Exact match
            if job_skill in candidate_skills_normalized:
                matches.append(job_skills[i])  # Return original case
                continue
            
            # Fuzzy matching if enabled
            if fuzzy:
                for candidate_skill in candidate_skills_normalized:
                    if self._is_fuzzy_match(job_skill, candidate_skill):
                        matches.append(job_skills[i])  # Return original case
                        break
        
        return matches
    
    def find_skill_gaps(self, job_skills: List[str], candidate_skills: str) -> List[str]:
        """Find skills required by job but missing from candidate.
        
        Args:
            job_skills: List of required skills from job
            candidate_skills: Candidate's skills as string
            
        Returns:
            List of missing skills
        """
        matches = self.find_skill_matches(job_skills, candidate_skills, fuzzy=True)
        matches_normalized = [self.normalize_skill(match) for match in matches]
        
        gaps = []
        for skill in job_skills:
            skill_normalized = self.normalize_skill(skill)
            if skill_normalized not in matches_normalized:
                gaps.append(skill)
        
        return gaps
    
    def _parse_skill_list(self, text: str) -> List[str]:
        """Parse a text block into individual skills."""
        if not text:
            return []
        
        # Split by common delimiters
        skills = re.split(r'[,;•\-\*\n]', text)
        
        # Clean each skill
        cleaned_skills = []
        for skill in skills:
            # Remove bullet points, numbers, extra whitespace
            cleaned = re.sub(r'^[\d\.\)\s\-•\*]+', '', skill).strip()
            cleaned = re.sub(r'[^\w\s\-\+\.\#]', '', cleaned).strip()
            
            # Filter out non-skill text (experience, education, etc.)
            if cleaned and len(cleaned) > 1:
                # Skip if it contains experience/education keywords
                if not any(word in cleaned.lower() for word in ['experience', 'education', 'degree', 'years', 'bachelor', 'master', 'phd']):
                    # Only keep if it's in known skills or looks like a skill
                    if (cleaned.lower() in self.known_skills or 
                        any(known_skill in cleaned.lower() for known_skill in self.known_skills) or
                        len(cleaned.split()) <= 3):  # Short phrases likely to be skills
                        cleaned_skills.append(cleaned)
        
        return cleaned_skills
    
    def _extract_nice_to_have(self, job_description: str) -> List[str]:
        """Extract nice-to-have/preferred skills."""
        if not job_description:
            return []
        
        text = job_description.lower()
        nice_to_have = set()
        
        # Look for nice-to-have sections
        nice_patterns = [
            r"nice to have:?\s*\n?(.+?)(?:\n\n|\n[A-Z]|$)",
            r"preferred:?\s*\n?(.+?)(?:\n\n|\n[A-Z]|$)",
            r"bonus:?\s*\n?(.+?)(?:\n\n|\n[A-Z]|$)",
        ]
        
        for pattern in nice_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                nice_to_have.update(self._parse_skill_list(match))
        
        return list(nice_to_have)
    
    def _is_fuzzy_match(self, skill1: str, skill2: str) -> bool:
        """Check if two skills are a fuzzy match."""
        if not skill1 or not skill2:
            return False
        
        # Exact match
        if skill1 == skill2:
            return True
        
        # One contains the other
        if skill1 in skill2 or skill2 in skill1:
            return True
        
        # Check for common abbreviations
        abbreviations = {
            ("javascript", "js"),
            ("machine learning", "ml"),
            ("artificial intelligence", "ai"),
            ("database", "db"),
        }
        
        for abbrev_pair in abbreviations:
            if (skill1 in abbrev_pair and skill2 in abbrev_pair):
                return True
        
        return False