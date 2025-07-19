"""Unit tests for keyword extraction from job descriptions."""
import pytest
from typing import List, Dict, Any
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tests.fixtures.evaluation_data import (
    SAMPLE_JOB_DESCRIPTIONS,
    KEYWORD_EXTRACTION_CASES
)


class TestKeywordExtractor:
    """Test keyword extraction from job descriptions."""
    
    def test_keyword_extractor_interface(self):
        """Test that KeywordExtractor implements required methods."""
        # RED: This will fail until we implement KeywordExtractor
        from evaluation.keyword_extractor import KeywordExtractor
        
        extractor = KeywordExtractor()
        
        # Test required method interfaces
        assert hasattr(extractor, 'extract_required_skills')
        assert hasattr(extractor, 'extract_experience_years')
        assert hasattr(extractor, 'extract_education_requirements')
        assert hasattr(extractor, 'parse_job_description')
    
    def test_extract_required_skills_from_python_jd(self):
        """Test extraction of required skills from Python developer job description."""
        from evaluation.keyword_extractor import KeywordExtractor
        
        extractor = KeywordExtractor()
        jd = SAMPLE_JOB_DESCRIPTIONS["python_developer"]["description"]
        
        skills = extractor.extract_required_skills(jd)
        expected_skills = ["Python", "MySQL", "MongoDB", "Java", "HTML"]
        
        # All expected skills should be found
        for skill in expected_skills:
            assert skill.lower() in [s.lower() for s in skills], f"Missing skill: {skill}"
        
        # Should not include empty strings or None
        assert all(skill and skill.strip() for skill in skills)
    
    def test_extract_required_skills_from_data_science_jd(self):
        """Test extraction of required skills from Data Science job description."""
        from evaluation.keyword_extractor import KeywordExtractor
        
        extractor = KeywordExtractor()
        jd = SAMPLE_JOB_DESCRIPTIONS["data_science"]["description"]
        
        skills = extractor.extract_required_skills(jd)
        expected_skills = ["Python", "Machine Learning", "SQL", "Statistics", "Pandas"]
        
        for skill in expected_skills:
            assert skill.lower() in [s.lower() for s in skills], f"Missing skill: {skill}"
    
    def test_extract_experience_years(self):
        """Test extraction of experience requirements from job descriptions."""
        from evaluation.keyword_extractor import KeywordExtractor
        
        extractor = KeywordExtractor()
        
        test_cases = [
            ("3+ years required", 3),
            ("5+ years of experience", 5),
            ("2-3 years preferred", 2),
            ("Minimum 4 years", 4),
            ("At least 6 years", 6),
            ("Fresh graduate welcome", 0),
            ("No experience specified", 0)
        ]
        
        for text, expected_years in test_cases:
            years = extractor.extract_experience_years(text)
            assert years == expected_years, f"Failed for '{text}': expected {expected_years}, got {years}"
    
    def test_extract_education_requirements(self):
        """Test extraction of education requirements."""
        from evaluation.keyword_extractor import KeywordExtractor
        
        extractor = KeywordExtractor()
        
        test_cases = [
            ("Bachelor's degree required", "Bachelor's"),
            ("Master's degree preferred", "Master's"),
            ("PhD in Computer Science", "PhD"),
            ("High school diploma", "High School"),
            ("Associate degree", "Associate"),
            ("No specific education required", None)
        ]
        
        for text, expected_education in test_cases:
            education = extractor.extract_education_requirements(text)
            assert education == expected_education, f"Failed for '{text}'"
    
    def test_parse_job_description_complete(self):
        """Test complete job description parsing."""
        from evaluation.keyword_extractor import KeywordExtractor
        
        extractor = KeywordExtractor()
        jd = SAMPLE_JOB_DESCRIPTIONS["python_developer"]["description"]
        
        parsed = extractor.parse_job_description(jd)
        
        # Test structure
        assert "required_skills" in parsed
        assert "experience_years" in parsed
        assert "education_level" in parsed
        assert "nice_to_have" in parsed
        
        # Test content
        assert isinstance(parsed["required_skills"], list)
        assert isinstance(parsed["experience_years"], (int, float))
        assert parsed["experience_years"] >= 0
        
        # Verify expected content
        skills = [s.lower() for s in parsed["required_skills"]]
        assert "python" in skills
        assert "mysql" in skills
    
    def test_skill_normalization(self):
        """Test skill name normalization and standardization."""
        from evaluation.keyword_extractor import KeywordExtractor
        
        extractor = KeywordExtractor()
        
        test_cases = [
            ("JavaScript", "javascript"),
            ("PYTHON", "python"),
            ("Machine Learning", "machine learning"),
            ("ML", "machine learning"),  # Should expand abbreviation
            ("SQL Server", "sql"),
            ("MySql", "mysql"),
            ("Node.js", "nodejs"),
            ("React.js", "react")
        ]
        
        for input_skill, expected_normalized in test_cases:
            normalized = extractor.normalize_skill(input_skill)
            assert normalized == expected_normalized, f"Failed normalizing '{input_skill}'"
    
    def test_extract_skills_with_variations(self):
        """Test extraction handles skill name variations."""
        from evaluation.keyword_extractor import KeywordExtractor
        
        extractor = KeywordExtractor()
        
        jd_with_variations = """
        Required Skills:
        - JavaScript (ES6+)
        - Node.js backend development
        - SQL databases (MySQL, PostgreSQL)
        - Machine Learning / AI
        - Python 3.x
        """
        
        skills = extractor.extract_required_skills(jd_with_variations)
        normalized_skills = [extractor.normalize_skill(s) for s in skills]
        
        expected_normalized = ["javascript", "nodejs", "sql", "machine learning", "python"]
        
        for expected in expected_normalized:
            assert expected in normalized_skills, f"Missing normalized skill: {expected}"
    
    def test_extract_from_unstructured_text(self):
        """Test extraction from less structured job description text."""
        from evaluation.keyword_extractor import KeywordExtractor
        
        extractor = KeywordExtractor()
        
        unstructured_jd = """
        We need someone with Python programming skills and database knowledge.
        Experience with MySQL is essential. JavaScript would be nice to have.
        The candidate should have at least 2 years of software development experience.
        A bachelor's degree in computer science is preferred.
        """
        
        parsed = extractor.parse_job_description(unstructured_jd)
        
        # Should extract key information even from unstructured text
        skills = [s.lower() for s in parsed["required_skills"]]
        assert "python" in skills
        assert "mysql" in skills
        
        assert parsed["experience_years"] == 2
        assert "bachelor" in parsed["education_level"].lower()
    
    def test_handle_empty_or_invalid_input(self):
        """Test handling of empty or invalid job descriptions."""
        from evaluation.keyword_extractor import KeywordExtractor
        
        extractor = KeywordExtractor()
        
        # Empty string
        parsed_empty = extractor.parse_job_description("")
        assert parsed_empty["required_skills"] == []
        assert parsed_empty["experience_years"] == 0
        assert parsed_empty["education_level"] is None
        
        # None input should be handled gracefully
        parsed_none = extractor.parse_job_description(None)
        assert parsed_none["required_skills"] == []
        
        # Whitespace only
        parsed_whitespace = extractor.parse_job_description("   \n\t   ")
        assert parsed_whitespace["required_skills"] == []
    
    def test_keyword_extraction_test_cases(self):
        """Test using predefined keyword extraction test cases."""
        from evaluation.keyword_extractor import KeywordExtractor
        
        extractor = KeywordExtractor()
        
        for test_case in KEYWORD_EXTRACTION_CASES:
            jd = test_case["job_description"]
            expected_skills = test_case["expected_skills"]
            expected_years = test_case["expected_experience_years"]
            
            parsed = extractor.parse_job_description(jd)
            
            # Check skills extraction
            extracted_skills = [s.lower() for s in parsed["required_skills"]]
            for expected_skill in expected_skills:
                assert expected_skill.lower() in extracted_skills, \
                    f"Missing skill '{expected_skill}' in extraction from: {jd[:100]}..."
            
            # Check experience years
            assert parsed["experience_years"] == expected_years, \
                f"Wrong experience years for JD: {jd[:50]}..."


class TestSkillMatching:
    """Test skill matching logic for baseline evaluation."""
    
    def test_exact_skill_matching(self):
        """Test exact skill matching between candidate and job."""
        from evaluation.keyword_extractor import KeywordExtractor
        
        extractor = KeywordExtractor()
        
        job_skills = ["Python", "MySQL", "Docker"]
        candidate_skills = "Python, MySQL, JavaScript, Git"
        
        matches = extractor.find_skill_matches(job_skills, candidate_skills)
        
        assert "Python" in matches
        assert "MySQL" in matches
        assert "Docker" not in matches  # Candidate doesn't have Docker
        assert "JavaScript" not in matches  # Not required by job
    
    def test_fuzzy_skill_matching(self):
        """Test fuzzy/approximate skill matching."""
        from evaluation.keyword_extractor import KeywordExtractor
        
        extractor = KeywordExtractor()
        
        job_skills = ["JavaScript", "Machine Learning", "SQL"]
        candidate_skills = "JS, ML, MySQL, Python"
        
        # Should match with fuzzy logic
        matches = extractor.find_skill_matches(job_skills, candidate_skills, fuzzy=True)
        
        # These should match with fuzzy logic
        assert any("javascript" in match.lower() for match in matches)  # JS -> JavaScript
        assert any("machine learning" in match.lower() for match in matches)  # ML -> Machine Learning
        assert any("sql" in match.lower() for match in matches)  # MySQL contains SQL
    
    def test_skill_gap_analysis(self):
        """Test identification of missing skills."""
        from evaluation.keyword_extractor import KeywordExtractor
        
        extractor = KeywordExtractor()
        
        job_skills = ["Python", "MySQL", "Docker", "AWS", "Git"]
        candidate_skills = "Python, MySQL, JavaScript"
        
        gaps = extractor.find_skill_gaps(job_skills, candidate_skills)
        
        expected_gaps = ["Docker", "AWS", "Git"]
        for gap in expected_gaps:
            assert gap in gaps, f"Missing skill gap: {gap}"
        
        assert "Python" not in gaps  # Candidate has this
        assert "MySQL" not in gaps   # Candidate has this