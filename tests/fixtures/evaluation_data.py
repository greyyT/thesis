"""Test fixtures for FRR evaluation system."""
import json
from typing import Dict, List, Any


# Test data with known qualification outcomes for validation
SAMPLE_JOB_DESCRIPTIONS = {
    "python_developer": {
        "title": "Python Developer",
        "required_skills": ["Python", "MySQL", "MongoDB", "Java", "HTML"],
        "experience_years": 3,
        "education_level": "Bachelor's",
        "description": """
        We are looking for an experienced Python Developer with expertise in Python, MySQL, MongoDB.
        
        Required Skills:
        - Python
        - MySQL  
        - MongoDB
        - Java
        - HTML
        
        Experience: 3+ years required
        Education: Bachelor's degree preferred
        """
    },
    "data_science": {
        "title": "Data Science", 
        "required_skills": ["Python", "Machine Learning", "SQL", "Statistics", "Pandas"],
        "experience_years": 2,
        "education_level": "Bachelor's",
        "description": """
        Data Scientist position requiring analytical skills and programming expertise.
        
        Required Skills:
        - Python
        - Machine Learning
        - SQL
        - Statistics
        - Pandas
        
        Experience: 2+ years required
        Education: Bachelor's degree in quantitative field
        """
    },
    "java_developer": {
        "title": "Java Developer",
        "required_skills": ["Java", "Spring", "MySQL", "REST API", "Maven"],
        "experience_years": 4,
        "education_level": "Bachelor's", 
        "description": """
        Senior Java Developer for enterprise applications.
        
        Required Skills:
        - Java
        - Spring Framework
        - MySQL
        - REST API
        - Maven
        
        Experience: 4+ years required
        Education: Bachelor's degree in Computer Science
        """
    }
}

SAMPLE_CANDIDATES = {
    # Perfect match for Python Developer - should be QUALIFIED
    "python_expert": {
        "id": "test_001",
        "actual_category": "Python Developer",
        "predicted_position": "Python Developer", 
        "skills": "Python, MySQL, MongoDB, Java, HTML, Django, FastAPI, Docker",
        "education": "Bachelor of Science in Computer Science, State University, 2018",
        "experience": "Senior Python Developer at TechCorp (2019-2023), 4 years experience",
        "companies": "TechCorp, StartupXYZ",
        "expected_qualification": True,
        "expected_frr_contribution": False  # Should NOT be falsely rejected
    },
    
    # Good match but missing one skill - should be QUALIFIED (transferable skills)
    "python_good_match": {
        "id": "test_002", 
        "actual_category": "Python Developer",
        "predicted_position": "Software Developer",
        "skills": "Python, MySQL, JavaScript, React, Git, AWS",
        "education": "Bachelor of Engineering in Information Technology, 2020",
        "experience": "Software Developer at WebCorp (2020-2023), 3 years Python experience",
        "companies": "WebCorp, DigitalAgency",
        "expected_qualification": True,
        "expected_frr_contribution": False  # Should NOT be falsely rejected
    },
    
    # Career changer with relevant skills - should be QUALIFIED but might be falsely rejected
    "career_changer": {
        "id": "test_003",
        "actual_category": "Data Science", 
        "predicted_position": "Business Analyst",
        "skills": "Python, SQL, Excel, Statistics, Machine Learning, Pandas, Numpy",
        "education": "MBA in Finance, Business School, 2019. Bachelor in Economics, 2017",
        "experience": "Business Analyst at FinanceCorp (2019-2023), Self-taught Python and ML",
        "companies": "FinanceCorp, ConsultingFirm",
        "expected_qualification": True,
        "expected_frr_contribution": True  # LIKELY to be falsely rejected due to non-CS background
    },
    
    # Under-qualified candidate - should be UNQUALIFIED
    "under_qualified": {
        "id": "test_004",
        "actual_category": "Java Developer",
        "predicted_position": "Junior Developer", 
        "skills": "Java basics, HTML, CSS, some SQL",
        "education": "Associate Degree in Information Systems, 2022",
        "experience": "Intern at LocalCompany (2022, 6 months), Fresh graduate",
        "companies": "LocalCompany",
        "expected_qualification": False,
        "expected_frr_contribution": False  # Should be correctly rejected
    },
    
    # Mismatched role - should be UNQUALIFIED 
    "role_mismatch": {
        "id": "test_005",
        "actual_category": "Java Developer",
        "predicted_position": "Data Science",
        "skills": "Python, Machine Learning, Tensorflow, Statistics, R",
        "education": "PhD in Statistics, Research University, 2021", 
        "experience": "Data Scientist at MLCorp (2021-2023), 2 years ML experience",
        "companies": "MLCorp, ResearchLab",
        "expected_qualification": False,
        "expected_frr_contribution": False  # Should be correctly rejected (wrong role)
    }
}

# Expected FRR calculation for validation
EXPECTED_FRR_RESULTS = {
    "total_candidates": 5,
    "qualified_candidates": 3,  # python_expert, python_good_match, career_changer
    "falsely_rejected": 1,      # career_changer (due to non-CS background bias)
    "expected_frr": 1/3,        # 33.3% for this small test sample
    "baseline_frr_target": 0.12 # 12% target for full dataset
}

# Skill normalization test cases
SKILL_NORMALIZATION_CASES = [
    {"input": "JavaScript", "expected": "javascript"},
    {"input": "PYTHON", "expected": "python"},
    {"input": "Machine Learning", "expected": "machine learning"},
    {"input": "ML", "expected": "machine learning"},  # Should map to full term
    {"input": "SQL Server", "expected": "sql"},
    {"input": "MySql", "expected": "mysql"},
]

# Job description keyword extraction test cases
KEYWORD_EXTRACTION_CASES = [
    {
        "job_description": SAMPLE_JOB_DESCRIPTIONS["python_developer"]["description"],
        "expected_skills": ["Python", "MySQL", "MongoDB", "Java", "HTML"],
        "expected_experience_years": 3
    },
    {
        "job_description": SAMPLE_JOB_DESCRIPTIONS["data_science"]["description"], 
        "expected_skills": ["Python", "Machine Learning", "SQL", "Statistics", "Pandas"],
        "expected_experience_years": 2
    }
]

def get_test_candidate_by_id(candidate_id: str) -> Dict[str, Any]:
    """Get a test candidate by ID."""
    for candidate_name, candidate_data in SAMPLE_CANDIDATES.items():
        if candidate_data["id"] == candidate_id:
            return candidate_data
    raise ValueError(f"Test candidate with ID {candidate_id} not found")

def get_qualified_test_candidates() -> List[Dict[str, Any]]:
    """Get all candidates that should be qualified."""
    return [
        candidate for candidate in SAMPLE_CANDIDATES.values() 
        if candidate["expected_qualification"]
    ]

def get_expected_false_rejections() -> List[Dict[str, Any]]:
    """Get candidates that should be qualified but likely falsely rejected."""
    return [
        candidate for candidate in SAMPLE_CANDIDATES.values()
        if candidate["expected_qualification"] and candidate["expected_frr_contribution"]
    ]

def create_test_dataset(size: int = 100) -> List[Dict[str, Any]]:
    """Create a larger test dataset by replicating sample candidates."""
    candidates = []
    sample_list = list(SAMPLE_CANDIDATES.values())
    
    for i in range(size):
        base_candidate = sample_list[i % len(sample_list)].copy()
        base_candidate["id"] = f"test_{i+1:03d}"
        candidates.append(base_candidate)
    
    return candidates