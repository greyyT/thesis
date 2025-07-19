"""Unit tests for skill ontology service."""
import pytest
from typing import List, Dict, Set

from services.skill_ontology import SkillOntologyService


class TestSkillOntologyService:
    """Test suite for skill ontology service."""
    
    @pytest.fixture
    def skill_service(self):
        """Create skill ontology service instance."""
        return SkillOntologyService()
    
    def test_normalize_skill(self, skill_service: SkillOntologyService):
        """Test: Should normalize skill names to canonical form."""
        # Test basic normalization
        assert skill_service.normalize_skill("python") == "Python"
        assert skill_service.normalize_skill("PYTHON") == "Python"
        assert skill_service.normalize_skill("Python") == "Python"
        
        # Test common variations
        assert skill_service.normalize_skill("JS") == "JavaScript"
        assert skill_service.normalize_skill("javascript") == "JavaScript"
        assert skill_service.normalize_skill("node.js") == "Node.js"
        assert skill_service.normalize_skill("nodejs") == "Node.js"
        
        # Test compound skills
        assert skill_service.normalize_skill("react.js") == "React"
        assert skill_service.normalize_skill("ReactJS") == "React"
        assert skill_service.normalize_skill("vue.js") == "Vue.js"
        
        # Test database names
        assert skill_service.normalize_skill("postgresql") == "PostgreSQL"
        assert skill_service.normalize_skill("postgres") == "PostgreSQL"
        assert skill_service.normalize_skill("mysql") == "MySQL"
        assert skill_service.normalize_skill("mongodb") == "MongoDB"
        assert skill_service.normalize_skill("mongo") == "MongoDB"
    
    def test_extract_skills_from_text(self, skill_service: SkillOntologyService):
        """Test: Should extract skills from unstructured text."""
        # Arrange
        text = """
        Senior Python Developer with 5 years experience in Django and FastAPI.
        Strong knowledge of JavaScript, React, and Node.js.
        Experience with PostgreSQL, MongoDB, and Redis.
        Proficient in Docker, Kubernetes, and AWS.
        Good understanding of machine learning with TensorFlow and PyTorch.
        """
        
        # Act
        skills = skill_service.extract_skills_from_text(text)
        
        # Assert
        expected_skills = {
            "Python", "Django", "FastAPI", "JavaScript", "React", "Node.js",
            "PostgreSQL", "MongoDB", "Redis", "Docker", "Kubernetes", "AWS",
            "Machine Learning", "TensorFlow", "PyTorch"
        }
        assert set(skills) == expected_skills
    
    def test_get_related_skills(self, skill_service: SkillOntologyService):
        """Test: Should return related skills from ontology."""
        # Test Python ecosystem
        python_related = skill_service.get_related_skills("Python")
        assert "Django" in python_related
        assert "FastAPI" in python_related
        assert "Flask" in python_related
        assert "pandas" in python_related
        
        # Test JavaScript ecosystem
        js_related = skill_service.get_related_skills("JavaScript")
        assert "TypeScript" in js_related
        assert "React" in js_related
        assert "Vue.js" in js_related
        assert "Node.js" in js_related
        
        # Test DevOps tools
        docker_related = skill_service.get_related_skills("Docker")
        assert "Kubernetes" in docker_related
        assert "Docker Compose" in docker_related
        assert "Container Orchestration" in docker_related
    
    def test_get_skill_category(self, skill_service: SkillOntologyService):
        """Test: Should categorize skills correctly."""
        # Programming languages
        assert skill_service.get_skill_category("Python") == "Programming Language"
        assert skill_service.get_skill_category("JavaScript") == "Programming Language"
        assert skill_service.get_skill_category("Java") == "Programming Language"
        
        # Frameworks
        assert skill_service.get_skill_category("Django") == "Framework"
        assert skill_service.get_skill_category("React") == "Framework"
        assert skill_service.get_skill_category("Spring Boot") == "Framework"
        
        # Databases
        assert skill_service.get_skill_category("PostgreSQL") == "Database"
        assert skill_service.get_skill_category("MongoDB") == "Database"
        assert skill_service.get_skill_category("Redis") == "Database"
        
        # DevOps
        assert skill_service.get_skill_category("Docker") == "DevOps"
        assert skill_service.get_skill_category("Kubernetes") == "DevOps"
        assert skill_service.get_skill_category("Jenkins") == "DevOps"
        
        # Cloud
        assert skill_service.get_skill_category("AWS") == "Cloud Platform"
        assert skill_service.get_skill_category("Azure") == "Cloud Platform"
        assert skill_service.get_skill_category("Google Cloud") == "Cloud Platform"
    
    def test_calculate_skill_similarity(self, skill_service: SkillOntologyService):
        """Test: Should calculate similarity between skill sets."""
        # Arrange
        job_skills = ["Python", "Django", "PostgreSQL", "Docker", "AWS"]
        candidate_skills_1 = ["Python", "Django", "MySQL", "Docker", "AWS"]
        candidate_skills_2 = ["Java", "Spring Boot", "Oracle", "Kubernetes", "Azure"]
        candidate_skills_3 = ["Python", "Flask", "PostgreSQL", "Kubernetes", "AWS"]
        
        # Act
        similarity_1 = skill_service.calculate_skill_similarity(job_skills, candidate_skills_1)
        similarity_2 = skill_service.calculate_skill_similarity(job_skills, candidate_skills_2)
        similarity_3 = skill_service.calculate_skill_similarity(job_skills, candidate_skills_3)
        
        # Assert
        assert similarity_1 > similarity_2  # More direct matches
        assert similarity_3 > similarity_2  # Related skills count
        assert 0 <= similarity_1 <= 1
        assert 0 <= similarity_2 <= 1
        assert 0 <= similarity_3 <= 1
    
    def test_identify_transferable_skills(self, skill_service: SkillOntologyService):
        """Test: Should identify transferable skills between domains."""
        # Arrange
        candidate_skills = ["Java", "Spring Boot", "MySQL", "Git", "Agile", "Problem Solving"]
        target_role = "Python Developer"
        
        # Act
        transferable = skill_service.identify_transferable_skills(
            candidate_skills,
            target_role
        )
        
        # Assert
        assert "Git" in transferable["technical"]
        assert "MySQL" in transferable["technical"]  # Database skills transfer
        assert "Agile" in transferable["soft"]
        assert "Problem Solving" in transferable["soft"]
        assert transferable["score"] > 0
    
    def test_suggest_learning_path(self, skill_service: SkillOntologyService):
        """Test: Should suggest skills to learn for career transition."""
        # Arrange
        current_skills = ["Java", "Spring Boot", "MySQL"]
        target_skills = ["Python", "Django", "PostgreSQL", "Docker"]
        
        # Act
        learning_path = skill_service.suggest_learning_path(
            current_skills,
            target_skills
        )
        
        # Assert
        assert "Python" in learning_path["must_learn"]
        assert "Django" in learning_path["must_learn"]
        assert "Docker" in learning_path["recommended"]
        assert learning_path["transferable"] == ["MySQL"]  # Can transfer DB knowledge
        assert len(learning_path["learning_order"]) > 0
    
    def test_extract_skill_requirements(self, skill_service: SkillOntologyService):
        """Test: Should extract and categorize skills from job description."""
        # Arrange
        job_description = """
        We are looking for a Senior Full Stack Developer with:
        
        Required:
        - 5+ years of experience with Python and Django
        - Strong knowledge of React and TypeScript
        - Experience with PostgreSQL and Redis
        - Proficiency in Docker and Kubernetes
        
        Nice to have:
        - Experience with AWS or GCP
        - Knowledge of machine learning
        - GraphQL experience
        """
        
        # Act
        requirements = skill_service.extract_skill_requirements(job_description)
        
        # Assert
        assert "Python" in requirements["required"]
        assert "Django" in requirements["required"]
        assert "React" in requirements["required"]
        assert "Docker" in requirements["required"]
        
        assert "AWS" in requirements["nice_to_have"]
        assert "Machine Learning" in requirements["nice_to_have"]
        assert "GraphQL" in requirements["nice_to_have"]
        
        assert requirements["categories"]["Programming Language"] == ["Python", "TypeScript"]
        assert "Django" in requirements["categories"]["Framework"]
        assert "Docker" in requirements["categories"]["DevOps"]
    
    def test_skill_gap_analysis(self, skill_service: SkillOntologyService):
        """Test: Should analyze skill gaps between candidate and job."""
        # Arrange
        job_skills = {
            "required": ["Python", "Django", "React", "PostgreSQL", "Docker"],
            "nice_to_have": ["AWS", "Kubernetes", "Redis"]
        }
        candidate_skills = ["Python", "Flask", "JavaScript", "MySQL", "Git"]
        
        # Act
        gap_analysis = skill_service.analyze_skill_gaps(job_skills, candidate_skills)
        
        # Assert
        assert "Django" in gap_analysis["missing_required"]
        assert "React" in gap_analysis["missing_required"]
        assert "Docker" in gap_analysis["missing_required"]
        
        assert "Flask" in gap_analysis["related_skills"]  # Related to Django
        assert "MySQL" in gap_analysis["related_skills"]  # Related to PostgreSQL
        
        assert gap_analysis["match_percentage"] < 50  # Missing many required skills
        assert len(gap_analysis["recommendations"]) > 0
    
    def test_skill_normalization_edge_cases(self, skill_service: SkillOntologyService):
        """Test: Should handle edge cases in skill normalization."""
        # Test with special characters
        assert skill_service.normalize_skill("C++") == "C++"
        assert skill_service.normalize_skill("C#") == "C#"
        assert skill_service.normalize_skill("F#") == "F#"
        
        # Test with dots and hyphens
        assert skill_service.normalize_skill("ASP.NET") == "ASP.NET"
        assert skill_service.normalize_skill("asp.net") == "ASP.NET"
        assert skill_service.normalize_skill("scikit-learn") == "scikit-learn"
        
        # Test unknown skills (should return as-is but capitalized)
        assert skill_service.normalize_skill("unknownskill") == "Unknownskill"
        # Skills with special chars keep original case if unknown
        assert skill_service.normalize_skill("some-new-tech") == "some-new-tech"