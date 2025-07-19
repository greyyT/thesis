"""Unit tests for baseline evaluator - integrated TDD testing."""
import pytest
from typing import List, Dict, Any
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import tempfile
import json

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tests.fixtures.evaluation_data import (
    SAMPLE_CANDIDATES,
    SAMPLE_JOB_DESCRIPTIONS,
    EXPECTED_FRR_RESULTS
)


class TestBaselineEvaluator:
    """Test the integrated baseline evaluation system."""
    
    def test_baseline_evaluator_interface(self):
        """Test that BaselineEvaluator implements required methods."""
        from evaluation.baseline_evaluator import BaselineEvaluator
        
        evaluator = BaselineEvaluator()
        
        # Test required method interfaces
        assert hasattr(evaluator, 'load_job_descriptions')
        assert hasattr(evaluator, 'evaluate_candidate')
        assert hasattr(evaluator, 'evaluate_candidates_batch')
        assert hasattr(evaluator, 'calculate_frr')
        assert hasattr(evaluator, 'get_evaluation_statistics')
        assert hasattr(evaluator, 'validate_baseline_frr')
    
    def test_baseline_evaluator_initialization(self):
        """Test evaluator initialization with custom weights."""
        from evaluation.baseline_evaluator import BaselineEvaluator
        
        # Test default weights
        evaluator_default = BaselineEvaluator()
        assert evaluator_default.weights['skills'] == 0.4
        assert evaluator_default.weights['experience'] == 0.3
        assert evaluator_default.weights['education'] == 0.15
        assert evaluator_default.weights['domain'] == 0.15
        
        # Test custom weights
        evaluator_custom = BaselineEvaluator(
            skill_weight=0.5,
            experience_weight=0.3,
            education_weight=0.1,
            domain_weight=0.1
        )
        assert evaluator_custom.weights['skills'] == 0.5
        assert evaluator_custom.weights['education'] == 0.1
    
    def test_load_job_descriptions_from_files(self):
        """Test loading job descriptions from mock files."""
        from evaluation.baseline_evaluator import BaselineEvaluator
        
        evaluator = BaselineEvaluator()
        
        # Create temporary job description files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Python Developer JD
            python_jd_file = Path(temp_dir) / "JD_Python_Developer_job_description.md"
            with open(python_jd_file, 'w') as f:
                f.write(SAMPLE_JOB_DESCRIPTIONS["python_developer"]["description"])
            
            # Data Science JD  
            ds_jd_file = Path(temp_dir) / "JD_Data_Scientist_job_description.md"
            with open(ds_jd_file, 'w') as f:
                f.write(SAMPLE_JOB_DESCRIPTIONS["data_science"]["description"])
            
            # Load job descriptions
            evaluator.load_job_descriptions(temp_dir)
            
            # Verify job descriptions loaded
            assert "Python Developer" in evaluator.job_descriptions
            assert "Data Scientist" in evaluator.job_descriptions
            
            # Verify parsed content
            python_jd = evaluator.job_descriptions["Python Developer"]
            assert "required_skills" in python_jd
            assert "experience_years" in python_jd
            assert "category" in python_jd
            assert python_jd["category"] == "Python Developer"
    
    def test_evaluate_single_candidate(self):
        """Test evaluation of single candidate against job requirements."""
        from evaluation.baseline_evaluator import BaselineEvaluator
        
        evaluator = BaselineEvaluator()
        
        # Mock job descriptions
        evaluator.job_descriptions["Python Developer"] = {
            "required_skills": ["Python", "MySQL", "HTML"],
            "experience_years": 3,
            "education_level": "Bachelor's",
            "nice_to_have": ["Docker"],
            "category": "Python Developer",
            "raw_text": "Sample job description"
        }
        
        # Test candidate from fixtures
        perfect_match = SAMPLE_CANDIDATES["python_expert"]
        
        evaluation = evaluator.evaluate_candidate(perfect_match, "Python Developer")
        
        # Verify evaluation structure
        assert evaluation.candidate_id == perfect_match["id"]
        assert evaluation.job_category == "Python Developer"
        assert isinstance(evaluation.is_qualified, bool)
        assert evaluation.system_decision in ["accept", "reject"]
        assert isinstance(evaluation.skills_matched, list)
        assert isinstance(evaluation.overall_score, float)
        
        # Perfect match should be qualified and accepted
        assert evaluation.is_qualified is True
        assert evaluation.system_decision == "accept"
        assert evaluation.overall_score >= 0.7  # Above acceptance threshold
    
    def test_evaluate_candidate_skill_matching(self):
        """Test skill matching evaluation component."""
        from evaluation.baseline_evaluator import BaselineEvaluator
        
        evaluator = BaselineEvaluator()
        
        # Mock simple job requirements
        evaluator.job_descriptions["Test Job"] = {
            "required_skills": ["Python", "SQL"],
            "experience_years": 2,
            "education_level": "Bachelor's",
            "nice_to_have": [],
            "category": "Test Job",
            "raw_text": "Test JD"
        }
        
        # Test candidates with different skill matches
        test_candidates = [
            {
                "id": "full_match",
                "skills": "Python, SQL, JavaScript",
                "experience": "3 years software development",
                "education": "Bachelor's in Computer Science",
                "predicted_position": "Software Developer"
            },
            {
                "id": "partial_match", 
                "skills": "Python, JavaScript",
                "experience": "2 years",
                "education": "Bachelor's degree",
                "predicted_position": "Developer"
            },
            {
                "id": "no_match",
                "skills": "Java, C++",
                "experience": "1 year",
                "education": "High school",
                "predicted_position": "Junior Developer"
            }
        ]
        
        evaluations = []
        for candidate in test_candidates:
            eval_result = evaluator.evaluate_candidate(candidate, "Test Job")
            evaluations.append(eval_result)
        
        # Full match should have highest score
        assert evaluations[0].overall_score > evaluations[1].overall_score
        assert evaluations[1].overall_score > evaluations[2].overall_score
        
        # Verify skill matching results
        assert len(evaluations[0].skills_matched) == 2  # Python + SQL
        assert len(evaluations[1].skills_matched) == 1  # Python only
        assert len(evaluations[2].skills_matched) == 0  # No matches
    
    def test_evaluate_experience_scoring(self):
        """Test experience evaluation scoring."""
        from evaluation.baseline_evaluator import BaselineEvaluator
        
        evaluator = BaselineEvaluator()
        
        # Test experience evaluation directly
        test_cases = [
            ("5 years experience", 3, 1.0),    # Exceeds requirement, capped at 1.0
            ("3 years experience", 3, 1.0),    # Meets requirement exactly
            ("2 years experience", 3, 2/3),    # Below requirement
            ("1 year experience", 3, 1/3),     # Well below requirement
            ("fresh graduate", 3, 0.0),        # No experience
        ]
        
        for experience_text, required_years, expected_score in test_cases:
            score = evaluator._evaluate_experience(experience_text, required_years)
            assert abs(score - expected_score) < 0.01, \
                f"Experience '{experience_text}' failed: expected {expected_score}, got {score}"
    
    def test_evaluate_education_scoring(self):
        """Test education level evaluation scoring."""
        from evaluation.baseline_evaluator import BaselineEvaluator
        
        evaluator = BaselineEvaluator()
        
        # Test education evaluation directly
        test_cases = [
            ("PhD in Computer Science", "Bachelor's", 1.0),      # Exceeds requirement
            ("Master's degree", "Bachelor's", 1.0),              # Exceeds requirement
            ("Bachelor's degree", "Bachelor's", 1.0),            # Meets requirement
            ("Associate degree", "Bachelor's", 2/3),              # Below requirement
            ("High school diploma", "Bachelor's", 1/3),          # Well below requirement
            ("Bachelor's degree", None, 1.0),                    # No requirement
        ]
        
        for education_text, required_education, expected_score in test_cases:
            score = evaluator._evaluate_education(education_text, required_education)
            assert abs(score - expected_score) < 0.01, \
                f"Education '{education_text}' vs '{required_education}' failed"
    
    def test_domain_relevance_scoring(self):
        """Test domain/industry relevance evaluation."""
        from evaluation.baseline_evaluator import BaselineEvaluator
        
        evaluator = BaselineEvaluator()
        
        # Test domain relevance evaluation
        test_cases = [
            ({"predicted_position": "Python Developer", "actual_category": ""}, "Python Developer", 1.0),
            ({"predicted_position": "Software Engineer", "actual_category": "Python Developer"}, "Python Developer", 1.0),
            ({"predicted_position": "Software Developer", "actual_category": ""}, "Data Scientist", 0.5),
            ({"predicted_position": "Marketing Manager", "actual_category": ""}, "Python Developer", 0.3),
        ]
        
        for candidate_data, job_category, expected_score in test_cases:
            score = evaluator._evaluate_domain_relevance(candidate_data, job_category)
            assert abs(score - expected_score) < 0.01, \
                f"Domain relevance failed for {candidate_data} vs {job_category}"
    
    def test_batch_evaluation_with_mock_data(self):
        """Test batch evaluation with mock CSV data."""
        from evaluation.baseline_evaluator import BaselineEvaluator
        import pandas as pd
        
        evaluator = BaselineEvaluator()
        
        # Setup mock job descriptions
        evaluator.job_descriptions["Python Developer"] = {
            "required_skills": ["Python", "MySQL"],
            "experience_years": 2,
            "education_level": "Bachelor's",
            "nice_to_have": [],
            "category": "Python Developer",
            "raw_text": "Mock Python JD"
        }
        
        # Create mock candidate data
        mock_candidates = [
            {
                "id": "001",
                "skills": "Python, MySQL, JavaScript",
                "experience": "3 years",
                "education": "Bachelor's in CS",
                "actual_category": "Python Developer",
                "predicted_position": "Python Developer"
            },
            {
                "id": "002", 
                "skills": "Java, C++",
                "experience": "1 year",
                "education": "High school",
                "actual_category": "Python Developer",
                "predicted_position": "Junior Developer"
            }
        ]
        
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            df = pd.DataFrame(mock_candidates)
            df.to_csv(temp_file.name, index=False)
            temp_csv_path = temp_file.name
        
        try:
            # Test batch evaluation
            results = evaluator.evaluate_candidates_batch(temp_csv_path)
            
            # Verify results
            assert len(results) == 2
            assert all(hasattr(result, 'candidate_id') for result in results)
            assert all(hasattr(result, 'overall_score') for result in results)
            assert all(result.job_category == "Python Developer" for result in results)
            
            # First candidate should score higher than second
            assert results[0].overall_score > results[1].overall_score
            
        finally:
            # Clean up temp file
            Path(temp_csv_path).unlink()
    
    def test_frr_calculation_integration(self):
        """Test FRR calculation with integrated evaluation."""
        from evaluation.baseline_evaluator import BaselineEvaluator
        
        evaluator = BaselineEvaluator()
        
        # Setup job description
        evaluator.job_descriptions["Test Job"] = {
            "required_skills": ["Python"],
            "experience_years": 2,
            "education_level": "Bachelor's",
            "nice_to_have": [],
            "category": "Test Job", 
            "raw_text": "Test JD"
        }
        
        # Evaluate test candidates to generate FRR data
        test_candidates = [
            {"id": "q1", "skills": "Python, MySQL", "experience": "3 years", "education": "Bachelor's"},  # Qualified, should accept
            {"id": "q2", "skills": "Python", "experience": "2 years", "education": "Bachelor's"},        # Qualified, should accept
            {"id": "q3", "skills": "Python", "experience": "1 year", "education": "Associate"},          # Qualified but lower score
            {"id": "u1", "skills": "Java", "experience": "1 year", "education": "High school"},           # Unqualified
        ]
        
        for candidate in test_candidates:
            eval_result = evaluator.evaluate_candidate(candidate, "Test Job")
            # Add to FRR calculator manually since we're testing integration
            evaluator.frr_calculator.add_evaluation_result(
                candidate_id=eval_result.candidate_id,
                is_qualified=eval_result.is_qualified, 
                system_decision=eval_result.system_decision
            )
        
        # Calculate FRR
        frr = evaluator.calculate_frr()
        stats = evaluator.get_evaluation_statistics()
        
        # Verify FRR calculation
        assert isinstance(frr, float)
        assert 0.0 <= frr <= 1.0
        assert stats['total_candidates'] == 4
        assert stats['qualified_candidates'] >= 1  # At least one qualified
        assert 'false_rejections' in stats
        assert 'accuracy' in stats
    
    def test_baseline_frr_validation_integration(self):
        """Test baseline FRR validation in integrated system."""
        from evaluation.baseline_evaluator import BaselineEvaluator
        
        evaluator = BaselineEvaluator()
        
        # Manually add evaluation results to achieve target FRR
        for i in range(100):
            # 12% false rejection rate (12 out of 100 qualified rejected)
            is_falsely_rejected = i < 12
            evaluator.frr_calculator.add_evaluation_result(
                candidate_id=f"test_{i}",
                is_qualified=True,
                system_decision="reject" if is_falsely_rejected else "accept"
            )
        
        # Test baseline validation
        frr = evaluator.calculate_frr()
        assert abs(frr - 0.12) < 0.001  # Should be exactly 12%
        
        # Test validation method
        is_valid = evaluator.validate_baseline_frr(target_frr=0.12, tolerance=0.02)
        assert is_valid is True
        
        # Test outside tolerance
        is_valid_strict = evaluator.validate_baseline_frr(target_frr=0.12, tolerance=0.005)
        assert is_valid_strict is True  # Should still be valid with exact match
    
    def test_results_export_functionality(self):
        """Test detailed results export to JSON."""
        from evaluation.baseline_evaluator import BaselineEvaluator
        
        evaluator = BaselineEvaluator()
        
        # Setup simple evaluation
        evaluator.job_descriptions["Test Job"] = {
            "required_skills": ["Python"],
            "experience_years": 1,
            "education_level": None,
            "nice_to_have": [],
            "category": "Test Job",
            "raw_text": "Test"
        }
        
        candidate = {
            "id": "test_001",
            "skills": "Python, JavaScript",
            "experience": "2 years",
            "education": "Bachelor's"
        }
        
        evaluation = evaluator.evaluate_candidate(candidate, "Test Job")
        
        # Test results saving
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_json_path = temp_file.name
        
        try:
            evaluator._save_results([evaluation], temp_json_path)
            
            # Verify JSON file was created and contains correct data
            with open(temp_json_path, 'r') as f:
                saved_data = json.load(f)
            
            assert len(saved_data) == 1
            result = saved_data[0]
            assert result['candidate_id'] == 'test_001'
            assert result['job_category'] == 'Test Job'
            assert 'overall_score' in result
            assert 'skills_matched' in result
            
        finally:
            Path(temp_json_path).unlink()
    
    def test_evaluator_reset_functionality(self):
        """Test reset functionality for evaluator."""
        from evaluation.baseline_evaluator import BaselineEvaluator
        
        evaluator = BaselineEvaluator()
        
        # Add some evaluation results
        evaluator.frr_calculator.add_evaluation_result("test_1", True, "reject")
        evaluator.frr_calculator.add_evaluation_result("test_2", False, "accept")
        
        # Verify results exist
        assert evaluator.calculate_frr() > 0
        stats = evaluator.get_evaluation_statistics()
        assert stats['total_candidates'] > 0
        
        # Reset and verify clean state
        evaluator.reset_evaluations()
        assert evaluator.calculate_frr() == 0.0
        
        stats_after_reset = evaluator.get_evaluation_statistics()
        assert stats_after_reset['total_candidates'] == 0


class TestBaselineEvaluatorEdgeCases:
    """Test edge cases and error handling."""
    
    def test_invalid_job_category_error(self):
        """Test error handling for invalid job category."""
        from evaluation.baseline_evaluator import BaselineEvaluator
        
        evaluator = BaselineEvaluator()
        
        candidate = {"id": "test", "skills": "Python"}
        
        # Should raise error for non-existent job category
        with pytest.raises(ValueError, match="Job category 'NonExistent' not found"):
            evaluator.evaluate_candidate(candidate, "NonExistent")
    
    def test_empty_candidate_data_handling(self):
        """Test handling of candidates with missing data."""
        from evaluation.baseline_evaluator import BaselineEvaluator
        
        evaluator = BaselineEvaluator()
        
        # Setup minimal job description
        evaluator.job_descriptions["Test Job"] = {
            "required_skills": ["Python"],
            "experience_years": 0,
            "education_level": None,
            "nice_to_have": [],
            "category": "Test Job",
            "raw_text": "Test"
        }
        
        # Test candidate with minimal data
        empty_candidate = {"id": "empty"}
        
        evaluation = evaluator.evaluate_candidate(empty_candidate, "Test Job")
        
        # Should handle gracefully without errors
        assert evaluation.candidate_id == "empty"
        assert isinstance(evaluation.overall_score, float)
        assert evaluation.overall_score >= 0.0
        assert evaluation.skills_matched == []
        assert len(evaluation.skills_missing) > 0  # Should show missing required skills
    
    def test_rejection_reason_generation(self):
        """Test rejection reason generation for failed candidates."""
        from evaluation.baseline_evaluator import BaselineEvaluator
        
        evaluator = BaselineEvaluator()
        
        # Setup challenging job requirements
        evaluator.job_descriptions["Senior Role"] = {
            "required_skills": ["Python", "AWS", "Docker", "Kubernetes"],
            "experience_years": 5,
            "education_level": "Master's",
            "nice_to_have": [],
            "category": "Senior Role",
            "raw_text": "Senior requirements"
        }
        
        # Candidate with significant gaps
        weak_candidate = {
            "id": "weak",
            "skills": "Python",  # Only 1 of 4 required skills
            "experience": "1 year",  # Much less than 5 years required
            "education": "High school",  # Less than Master's required
            "predicted_position": "Junior Developer"
        }
        
        evaluation = evaluator.evaluate_candidate(weak_candidate, "Senior Role")
        
        # Should be rejected with detailed reason
        assert evaluation.system_decision == "reject"
        assert evaluation.rejection_reason is not None
        assert len(evaluation.rejection_reason) > 0
        
        # Rejection reason should mention specific gaps
        reason = evaluation.rejection_reason.lower()
        assert any(keyword in reason for keyword in ['skill', 'experience', 'education'])
