"""Unit tests for FRR calculator - Core FRR calculation logic."""
import pytest
from typing import List, Dict, Any
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tests.fixtures.evaluation_data import (
    SAMPLE_CANDIDATES, 
    EXPECTED_FRR_RESULTS,
    get_qualified_test_candidates,
    get_expected_false_rejections
)


class TestFRRCalculator:
    """Test the core FRR calculation functionality."""
    
    def test_frr_calculator_interface(self):
        """Test that FRRCalculator implements required methods."""
        # RED: This will fail until we implement FRRCalculator
        from evaluation.frr_calculator import FRRCalculator
        
        calculator = FRRCalculator()
        
        # Test required method interfaces
        assert hasattr(calculator, 'calculate_frr')
        assert hasattr(calculator, 'add_evaluation_result') 
        assert hasattr(calculator, 'get_qualification_stats')
        assert hasattr(calculator, 'reset_results')
    
    def test_frr_calculation_formula(self):
        """Test basic FRR calculation: (Qualified Rejected) / (Total Qualified)."""
        # RED: Will fail until implementation exists
        from evaluation.frr_calculator import FRRCalculator
        
        calculator = FRRCalculator()
        
        # Test data: 10 qualified candidates, 2 falsely rejected
        qualified_candidates = 10
        falsely_rejected = 2
        expected_frr = 2 / 10  # 20%
        
        # Simulate evaluation results
        for i in range(qualified_candidates):
            is_falsely_rejected = i < falsely_rejected
            calculator.add_evaluation_result(
                candidate_id=f"candidate_{i}",
                is_qualified=True,
                system_decision="reject" if is_falsely_rejected else "accept"
            )
        
        frr = calculator.calculate_frr()
        assert frr == expected_frr
        assert frr == 0.2
    
    def test_frr_with_no_qualified_candidates(self):
        """Test FRR calculation when no candidates are qualified."""
        from evaluation.frr_calculator import FRRCalculator
        
        calculator = FRRCalculator()
        
        # Add only unqualified candidates
        for i in range(5):
            calculator.add_evaluation_result(
                candidate_id=f"candidate_{i}",
                is_qualified=False,
                system_decision="reject"
            )
        
        frr = calculator.calculate_frr()
        assert frr == 0.0  # No qualified candidates means no false rejections possible
    
    def test_frr_with_perfect_system(self):
        """Test FRR when system makes no false rejections."""
        from evaluation.frr_calculator import FRRCalculator
        
        calculator = FRRCalculator()
        
        # Perfect system: all qualified candidates accepted
        for i in range(5):
            calculator.add_evaluation_result(
                candidate_id=f"qualified_{i}",
                is_qualified=True,
                system_decision="accept"
            )
        
        frr = calculator.calculate_frr()
        assert frr == 0.0
    
    def test_qualification_statistics(self):
        """Test detailed qualification statistics tracking."""
        from evaluation.frr_calculator import FRRCalculator
        
        calculator = FRRCalculator()
        
        # Add mixed results
        test_cases = [
            ("qual_1", True, "accept"),   # Qualified, correctly accepted
            ("qual_2", True, "reject"),   # Qualified, falsely rejected  
            ("qual_3", True, "accept"),   # Qualified, correctly accepted
            ("unqual_1", False, "reject"), # Unqualified, correctly rejected
            ("unqual_2", False, "accept"), # Unqualified, falsely accepted
        ]
        
        for candidate_id, is_qualified, decision in test_cases:
            calculator.add_evaluation_result(candidate_id, is_qualified, decision)
        
        stats = calculator.get_qualification_stats()
        
        assert stats["total_candidates"] == 5
        assert stats["qualified_candidates"] == 3
        assert stats["unqualified_candidates"] == 2
        assert stats["false_rejections"] == 1
        assert stats["false_acceptances"] == 1
        assert stats["correct_decisions"] == 3
    
    def test_twelve_percent_baseline_validation(self):
        """Test validation against 12% baseline FRR assumption."""
        from evaluation.frr_calculator import FRRCalculator
        
        calculator = FRRCalculator()
        
        # Simulate dataset with 12% FRR
        total_qualified = 100
        expected_false_rejections = 12  # 12% of qualified
        
        # Add qualified candidates with 12% false rejection rate
        for i in range(total_qualified):
            is_falsely_rejected = i < expected_false_rejections
            calculator.add_evaluation_result(
                candidate_id=f"candidate_{i}",
                is_qualified=True,
                system_decision="reject" if is_falsely_rejected else "accept"
            )
        
        frr = calculator.calculate_frr()
        assert abs(frr - 0.12) < 0.001  # Should be exactly 12%
        
        # Test baseline validation method
        is_valid_baseline = calculator.validate_baseline_frr(target_frr=0.12, tolerance=0.02)
        assert is_valid_baseline is True
    
    def test_frr_calculator_reset(self):
        """Test calculator reset functionality."""
        from evaluation.frr_calculator import FRRCalculator
        
        calculator = FRRCalculator()
        
        # Add some results
        calculator.add_evaluation_result("test_1", True, "reject")
        calculator.add_evaluation_result("test_2", False, "accept")
        
        # Verify results exist
        assert calculator.calculate_frr() > 0
        stats = calculator.get_qualification_stats()
        assert stats["total_candidates"] > 0
        
        # Reset and verify clean state
        calculator.reset_results()
        assert calculator.calculate_frr() == 0.0
        
        stats_after_reset = calculator.get_qualification_stats()
        assert stats_after_reset["total_candidates"] == 0
    
    def test_frr_with_sample_test_data(self):
        """Test FRR calculation using sample test fixtures."""
        from evaluation.frr_calculator import FRRCalculator
        
        calculator = FRRCalculator()
        
        # Use predefined test candidates
        for candidate_name, candidate_data in SAMPLE_CANDIDATES.items():
            is_qualified = candidate_data["expected_qualification"]
            will_be_falsely_rejected = candidate_data["expected_frr_contribution"]
            
            # Simulate system decision
            if is_qualified and will_be_falsely_rejected:
                system_decision = "reject"  # False rejection
            elif is_qualified and not will_be_falsely_rejected:
                system_decision = "accept"  # Correct acceptance
            else:
                system_decision = "reject"  # Correct rejection
            
            calculator.add_evaluation_result(
                candidate_id=candidate_data["id"],
                is_qualified=is_qualified,
                system_decision=system_decision
            )
        
        frr = calculator.calculate_frr()
        expected_frr = EXPECTED_FRR_RESULTS["expected_frr"]
        
        assert abs(frr - expected_frr) < 0.001
        
        stats = calculator.get_qualification_stats()
        assert stats["qualified_candidates"] == EXPECTED_FRR_RESULTS["qualified_candidates"]
        assert stats["false_rejections"] == EXPECTED_FRR_RESULTS["falsely_rejected"]


class TestFRRValidation:
    """Test FRR validation and statistical methods."""
    
    def test_baseline_frr_validation_within_range(self):
        """Test validation of FRR within acceptable baseline range."""
        from evaluation.frr_calculator import FRRCalculator
        
        calculator = FRRCalculator()
        
        # Test various FRR values against 12% baseline
        test_cases = [
            (0.10, True),   # 10% - within tolerance
            (0.11, True),   # 11% - within tolerance  
            (0.12, True),   # 12% - exact baseline
            (0.13, True),   # 13% - within tolerance
            (0.139, True),  # 13.9% - just within tolerance
            (0.08, False),  # 8% - too low (outside 2% tolerance)
            (0.15, False),  # 15% - too high (outside 2% tolerance)
        ]
        
        for test_frr, expected_valid in test_cases:
            # Simulate results to achieve target FRR
            calculator.reset_results()
            qualified_count = 100
            false_rejections = int(test_frr * qualified_count)
            
            for i in range(qualified_count):
                is_rejected = i < false_rejections
                calculator.add_evaluation_result(
                    candidate_id=f"test_{i}",
                    is_qualified=True,
                    system_decision="reject" if is_rejected else "accept"
                )
            
            is_valid = calculator.validate_baseline_frr(
                target_frr=0.12, 
                tolerance=0.02
            )
            assert is_valid == expected_valid, f"FRR {test_frr} validation failed"
    
    def test_statistical_power_calculation(self):
        """Test statistical power calculation for sample size validation.""" 
        from evaluation.frr_calculator import FRRCalculator
        
        calculator = FRRCalculator()
        
        # Test with 1182 candidates (actual dataset size)
        sample_size = 1182
        baseline_frr = 0.12
        target_frr = 0.06  # 50% reduction
        
        # This will be implemented to validate statistical significance
        power = calculator.calculate_statistical_power(
            sample_size=sample_size,
            baseline_frr=baseline_frr,
            target_frr=target_frr,
            alpha=0.05
        )
        
        # With large sample size and substantial effect, power should be high
        assert power > 0.80  # Standard 80% power threshold