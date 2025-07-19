"""FRR Calculator - Core False Rejection Rate calculation functionality."""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import math


@dataclass
class EvaluationResult:
    """Single candidate evaluation result."""
    candidate_id: str
    is_qualified: bool
    system_decision: str  # "accept" or "reject"


class FRRCalculator:
    """Calculate False Rejection Rate (FRR) for recruitment systems.
    
    FRR = (Qualified Applicants Rejected by System) ÷ (Total Qualified Applicants)
    """
    
    def __init__(self):
        """Initialize empty calculator."""
        self.results: List[EvaluationResult] = []
    
    def add_evaluation_result(
        self, 
        candidate_id: str, 
        is_qualified: bool, 
        system_decision: str
    ) -> None:
        """Add a single candidate evaluation result."""
        if system_decision not in ["accept", "reject"]:
            raise ValueError("system_decision must be 'accept' or 'reject'")
        
        result = EvaluationResult(
            candidate_id=candidate_id,
            is_qualified=is_qualified,
            system_decision=system_decision
        )
        self.results.append(result)
    
    def calculate_frr(self) -> float:
        """Calculate False Rejection Rate.
        
        Returns:
            FRR as float between 0.0 and 1.0
        """
        qualified_candidates = [r for r in self.results if r.is_qualified]
        
        if not qualified_candidates:
            return 0.0  # No qualified candidates means no false rejections possible
        
        false_rejections = [
            r for r in qualified_candidates 
            if r.system_decision == "reject"
        ]
        
        return len(false_rejections) / len(qualified_candidates)
    
    def get_qualification_stats(self) -> Dict[str, int]:
        """Get detailed qualification statistics."""
        total_candidates = len(self.results)
        qualified_candidates = len([r for r in self.results if r.is_qualified])
        unqualified_candidates = total_candidates - qualified_candidates
        
        # False rejections: qualified candidates rejected
        false_rejections = len([
            r for r in self.results 
            if r.is_qualified and r.system_decision == "reject"
        ])
        
        # False acceptances: unqualified candidates accepted
        false_acceptances = len([
            r for r in self.results 
            if not r.is_qualified and r.system_decision == "accept"
        ])
        
        # Correct decisions
        correct_decisions = len([
            r for r in self.results
            if (r.is_qualified and r.system_decision == "accept") or
               (not r.is_qualified and r.system_decision == "reject")
        ])
        
        return {
            "total_candidates": total_candidates,
            "qualified_candidates": qualified_candidates,
            "unqualified_candidates": unqualified_candidates,
            "false_rejections": false_rejections,
            "false_acceptances": false_acceptances,
            "correct_decisions": correct_decisions
        }
    
    def reset_results(self) -> None:
        """Reset all evaluation results."""
        self.results.clear()
    
    def validate_baseline_frr(
        self, 
        target_frr: float = 0.12, 
        tolerance: float = 0.02
    ) -> bool:
        """Validate if current FRR is within acceptable range of target baseline.
        
        Args:
            target_frr: Expected baseline FRR (default 12%)
            tolerance: Acceptable deviation (default ±2%)
            
        Returns:
            True if FRR is within target_frr ± tolerance
        """
        current_frr = self.calculate_frr()
        lower_bound = target_frr - tolerance
        upper_bound = target_frr + tolerance
        
        return lower_bound <= current_frr <= upper_bound
    
    def calculate_statistical_power(
        self,
        sample_size: int,
        baseline_frr: float,
        target_frr: float,
        alpha: float = 0.05
    ) -> float:
        """Calculate statistical power for detecting FRR difference.
        
        Args:
            sample_size: Number of candidates in study
            baseline_frr: Current system FRR (e.g., 0.12)
            target_frr: Target improved FRR (e.g., 0.06)
            alpha: Significance level (default 0.05)
            
        Returns:
            Statistical power as float between 0.0 and 1.0
        """
        # Estimate number of qualified candidates (assuming ~70% qualification rate)
        estimated_qualified = int(sample_size * 0.7)
        
        if estimated_qualified == 0:
            return 0.0
        
        # Expected false rejections under each condition
        baseline_false_rejections = baseline_frr * estimated_qualified
        target_false_rejections = target_frr * estimated_qualified
        
        # Effect size (Cohen's h for proportions)
        p1 = baseline_frr
        p2 = target_frr
        effect_size = 2 * (math.asin(math.sqrt(p1)) - math.asin(math.sqrt(p2)))
        effect_size = abs(effect_size)
        
        # Approximate power calculation using normal approximation
        # For large samples, the test statistic follows normal distribution
        # Using standard normal approximation: z_alpha ≈ 1.96 for α = 0.05
        z_alpha = 1.96 if alpha == 0.05 else 2.58  # Simplified for common alpha values
        z_beta = effect_size * math.sqrt(estimated_qualified / 4) - z_alpha
        
        # Approximate normal CDF using error function approximation
        # P(Z < z) ≈ 0.5 * (1 + erf(z / sqrt(2)))
        power = 0.5 * (1 + math.erf(z_beta / math.sqrt(2)))
        
        # Ensure power is between 0 and 1
        return max(0.0, min(1.0, power))
    
    def get_frr_confidence_interval(self, confidence_level: float = 0.95) -> tuple:
        """Calculate confidence interval for FRR estimate.
        
        Args:
            confidence_level: Confidence level (default 95%)
            
        Returns:
            (lower_bound, upper_bound) tuple
        """
        qualified_candidates = [r for r in self.results if r.is_qualified]
        n = len(qualified_candidates)
        
        if n == 0:
            return (0.0, 0.0)
        
        false_rejections = len([
            r for r in qualified_candidates 
            if r.system_decision == "reject"
        ])
        
        frr = false_rejections / n
        
        # Wilson score interval for binomial proportion
        alpha = 1 - confidence_level
        z = 1.96 if confidence_level == 0.95 else 2.58  # Common z-values
        
        denominator = 1 + z**2 / n
        center = (frr + z**2 / (2*n)) / denominator
        margin = z * math.sqrt((frr * (1 - frr) + z**2 / (4*n)) / n) / denominator
        
        lower_bound = max(0.0, center - margin)
        upper_bound = min(1.0, center + margin)
        
        return (lower_bound, upper_bound)