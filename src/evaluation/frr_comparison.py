"""FRR comparison between baseline and multi-agent systems."""
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
import json
import pandas as pd
from pathlib import Path
import math

from .frr_calculator import FRRCalculator


@dataclass
class FRRComparisonResult:
    """Results of FRR comparison between systems."""
    baseline_frr: float
    multiagent_frr: float
    absolute_improvement: float
    relative_improvement: float
    statistical_significance: bool
    effect_size: float
    confidence_interval: Tuple[float, float]
    sample_size: int
    baseline_stats: Dict[str, Any]
    multiagent_stats: Dict[str, Any]


class FRRComparator:
    """Compare FRR between baseline and multi-agent systems."""
    
    def __init__(self):
        """Initialize FRR comparator."""
        self.baseline_calculator = FRRCalculator()
        self.multiagent_calculator = FRRCalculator()
    
    def load_evaluation_results(self, 
                               baseline_results_file: str, 
                               multiagent_results_file: str) -> None:
        """Load evaluation results from both systems.
        
        Args:
            baseline_results_file: JSON file with baseline evaluation results
            multiagent_results_file: JSON file with multi-agent evaluation results
        """
        # Load baseline results
        with open(baseline_results_file, 'r') as f:
            baseline_data = json.load(f)
        
        for result in baseline_data:
            self.baseline_calculator.add_evaluation_result(
                candidate_id=result['candidate_id'],
                is_qualified=result['is_qualified'],
                system_decision=result['system_decision']
            )
        
        # Load multi-agent results
        with open(multiagent_results_file, 'r') as f:
            multiagent_data = json.load(f)
        
        for result in multiagent_data:
            self.multiagent_calculator.add_evaluation_result(
                candidate_id=result['candidate_id'],
                is_qualified=result['is_qualified'],
                system_decision=result['system_decision']
            )
    
    def load_from_calculators(self, 
                             baseline_calculator: FRRCalculator,
                             multiagent_calculator: FRRCalculator) -> None:
        """Load data from existing calculator objects.
        
        Args:
            baseline_calculator: FRR calculator with baseline results
            multiagent_calculator: FRR calculator with multi-agent results
        """
        self.baseline_calculator = baseline_calculator
        self.multiagent_calculator = multiagent_calculator
    
    def compare_frr(self, 
                   expected_baseline: float = 0.12,
                   target_improvement: float = 0.06,
                   significance_level: float = 0.05) -> FRRComparisonResult:
        """Compare FRR between baseline and multi-agent systems.
        
        Args:
            expected_baseline: Expected baseline FRR (default 12%)
            target_improvement: Target multi-agent FRR (default 6%)
            significance_level: Statistical significance level (default 0.05)
            
        Returns:
            FRRComparisonResult with comprehensive comparison
        """
        # Calculate FRR for both systems
        baseline_frr = self.baseline_calculator.calculate_frr()
        multiagent_frr = self.multiagent_calculator.calculate_frr()
        
        # Calculate improvements
        absolute_improvement = baseline_frr - multiagent_frr
        relative_improvement = (absolute_improvement / baseline_frr) if baseline_frr > 0 else 0
        
        # Get statistics from both systems
        baseline_stats = self.baseline_calculator.get_qualification_stats()
        multiagent_stats = self.multiagent_calculator.get_qualification_stats()
        
        # Calculate effect size (Cohen's h for proportions)
        effect_size = self._calculate_effect_size(baseline_frr, multiagent_frr)
        
        # Test statistical significance
        is_significant = self._test_statistical_significance(
            baseline_frr, multiagent_frr,
            baseline_stats['qualified_candidates'],
            multiagent_stats['qualified_candidates'],
            significance_level
        )
        
        # Calculate confidence interval for improvement
        confidence_interval = self._calculate_improvement_confidence_interval(
            baseline_frr, multiagent_frr,
            baseline_stats['qualified_candidates'],
            multiagent_stats['qualified_candidates']
        )
        
        return FRRComparisonResult(
            baseline_frr=baseline_frr,
            multiagent_frr=multiagent_frr,
            absolute_improvement=absolute_improvement,
            relative_improvement=relative_improvement,
            statistical_significance=is_significant,
            effect_size=effect_size,
            confidence_interval=confidence_interval,
            sample_size=min(baseline_stats['total_candidates'], multiagent_stats['total_candidates']),
            baseline_stats=baseline_stats,
            multiagent_stats=multiagent_stats
        )
    
    def validate_against_targets(self, 
                                comparison_result: FRRComparisonResult,
                                baseline_target: float = 0.12,
                                improvement_target: float = 0.06) -> Dict[str, bool]:
        """Validate results against expected targets.
        
        Args:
            comparison_result: FRR comparison result
            baseline_target: Expected baseline FRR (12%)
            improvement_target: Target improved FRR (6%)
            
        Returns:
            Dictionary of validation results
        """
        return {
            'baseline_matches_literature': abs(comparison_result.baseline_frr - baseline_target) < 0.05,
            'achieves_target_frr': comparison_result.multiagent_frr <= improvement_target + 0.02,
            'significant_improvement': comparison_result.statistical_significance,
            'large_effect_size': comparison_result.effect_size > 0.5,  # Medium to large effect
            'practical_significance': comparison_result.relative_improvement > 0.25,  # >25% relative improvement
            'meets_all_criteria': all([
                abs(comparison_result.baseline_frr - baseline_target) < 0.05,
                comparison_result.multiagent_frr <= improvement_target + 0.02,
                comparison_result.statistical_significance,
                comparison_result.effect_size > 0.5,
                comparison_result.relative_improvement > 0.25
            ])
        }
    
    def generate_comparison_report(self, 
                                 comparison_result: FRRComparisonResult,
                                 validation_result: Dict[str, bool]) -> str:
        """Generate comprehensive comparison report.
        
        Args:
            comparison_result: FRR comparison result
            validation_result: Validation against targets
            
        Returns:
            Formatted comparison report
        """
        report = []
        report.append("# FRR Comparison Report: Baseline vs Multi-Agent System")
        report.append("")
        
        # Summary statistics
        report.append("## Summary Statistics")
        report.append(f"- **Baseline System FRR**: {comparison_result.baseline_frr:.1%}")
        report.append(f"- **Multi-Agent System FRR**: {comparison_result.multiagent_frr:.1%}")
        report.append(f"- **Absolute Improvement**: {comparison_result.absolute_improvement:.1%}")
        report.append(f"- **Relative Improvement**: {comparison_result.relative_improvement:.1%}")
        report.append(f"- **Sample Size**: {comparison_result.sample_size:,} candidates")
        report.append("")
        
        # Statistical analysis
        report.append("## Statistical Analysis")
        report.append(f"- **Effect Size (Cohen's h)**: {comparison_result.effect_size:.3f}")
        effect_magnitude = "Large" if comparison_result.effect_size > 0.8 else "Medium" if comparison_result.effect_size > 0.5 else "Small"
        report.append(f"- **Effect Magnitude**: {effect_magnitude}")
        report.append(f"- **Statistical Significance**: {'Yes' if comparison_result.statistical_significance else 'No'}")
        report.append(f"- **95% Confidence Interval**: [{comparison_result.confidence_interval[0]:.1%}, {comparison_result.confidence_interval[1]:.1%}]")
        report.append("")
        
        # Detailed comparison
        report.append("## Detailed Comparison")
        
        # Baseline system details
        baseline_stats = comparison_result.baseline_stats
        report.append("### Baseline System (Keyword-Based)")
        report.append(f"- Total Candidates: {baseline_stats['total_candidates']:,}")
        report.append(f"- Qualified Candidates: {baseline_stats['qualified_candidates']:,}")
        report.append(f"- False Rejections: {baseline_stats['false_rejections']:,}")
        report.append(f"- Accuracy: {baseline_stats['correct_decisions'] / baseline_stats['total_candidates']:.1%}")
        report.append("")
        
        # Multi-agent system details
        multiagent_stats = comparison_result.multiagent_stats
        report.append("### Multi-Agent System (Semantic Analysis)")
        report.append(f"- Total Candidates: {multiagent_stats['total_candidates']:,}")
        report.append(f"- Qualified Candidates: {multiagent_stats['qualified_candidates']:,}")
        report.append(f"- False Rejections: {multiagent_stats['false_rejections']:,}")
        report.append(f"- Accuracy: {multiagent_stats['correct_decisions'] / multiagent_stats['total_candidates']:.1%}")
        report.append("")
        
        # Business impact
        false_rejection_reduction = baseline_stats['false_rejections'] - multiagent_stats['false_rejections']
        report.append("## Business Impact")
        report.append(f"- **Fewer False Rejections**: {false_rejection_reduction:,} qualified candidates no longer incorrectly rejected")
        report.append(f"- **Improved Candidate Experience**: {comparison_result.relative_improvement:.1%} reduction in qualified candidate rejections")
        report.append(f"- **Hiring Efficiency**: Better identification of qualified candidates")
        report.append("")
        
        # Target validation
        report.append("## Target Validation")
        for criterion, passed in validation_result.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            criterion_name = criterion.replace('_', ' ').title()
            report.append(f"- **{criterion_name}**: {status}")
        report.append("")
        
        # Overall assessment
        overall_success = validation_result.get('meets_all_criteria', False)
        report.append("## Overall Assessment")
        if overall_success:
            report.append("✅ **SUCCESS**: Multi-agent system significantly reduces FRR and meets all evaluation criteria.")
        else:
            report.append("⚠️ **PARTIAL SUCCESS**: Some criteria not fully met, but improvement demonstrated.")
        
        return "\\n".join(report)
    
    def _calculate_effect_size(self, baseline_frr: float, multiagent_frr: float) -> float:
        """Calculate Cohen's h effect size for proportion difference.
        
        Args:
            baseline_frr: Baseline system FRR
            multiagent_frr: Multi-agent system FRR
            
        Returns:
            Effect size (Cohen's h)
        """
        if baseline_frr == 0 and multiagent_frr == 0:
            return 0.0
        
        # Cohen's h for proportions
        p1 = max(0.001, min(0.999, baseline_frr))  # Avoid edge cases
        p2 = max(0.001, min(0.999, multiagent_frr))
        
        h = 2 * (math.asin(math.sqrt(p1)) - math.asin(math.sqrt(p2)))
        return abs(h)
    
    def _test_statistical_significance(self, 
                                     baseline_frr: float, 
                                     multiagent_frr: float,
                                     baseline_n: int,
                                     multiagent_n: int,
                                     alpha: float = 0.05) -> bool:
        """Test statistical significance of FRR difference.
        
        Args:
            baseline_frr: Baseline system FRR
            multiagent_frr: Multi-agent system FRR
            baseline_n: Sample size for baseline
            multiagent_n: Sample size for multi-agent
            alpha: Significance level
            
        Returns:
            True if difference is statistically significant
        """
        if baseline_n == 0 or multiagent_n == 0:
            return False
        
        # Pooled proportion for two-proportion z-test
        p1, p2 = baseline_frr, multiagent_frr
        n1, n2 = baseline_n, multiagent_n
        
        # Pool the proportions
        p_pool = (p1 * n1 + p2 * n2) / (n1 + n2)
        
        # Standard error of difference
        se_diff = math.sqrt(p_pool * (1 - p_pool) * (1/n1 + 1/n2))
        
        if se_diff == 0:
            return p1 != p2
        
        # Z-statistic
        z_stat = abs(p1 - p2) / se_diff
        
        # Critical value for two-tailed test
        z_critical = 1.96 if alpha == 0.05 else 2.58  # Common values
        
        return z_stat > z_critical
    
    def _calculate_improvement_confidence_interval(self, 
                                                 baseline_frr: float,
                                                 multiagent_frr: float,
                                                 baseline_n: int,
                                                 multiagent_n: int,
                                                 confidence: float = 0.95) -> Tuple[float, float]:
        """Calculate confidence interval for FRR improvement.
        
        Args:
            baseline_frr: Baseline system FRR
            multiagent_frr: Multi-agent system FRR
            baseline_n: Sample size for baseline
            multiagent_n: Sample size for multi-agent
            confidence: Confidence level
            
        Returns:
            (lower_bound, upper_bound) of improvement confidence interval
        """
        if baseline_n == 0 or multiagent_n == 0:
            return (0.0, 0.0)
        
        # Standard error for difference of proportions
        p1, p2 = baseline_frr, multiagent_frr
        n1, n2 = baseline_n, multiagent_n
        
        se1 = math.sqrt(p1 * (1 - p1) / n1)
        se2 = math.sqrt(p2 * (1 - p2) / n2)
        se_diff = math.sqrt(se1**2 + se2**2)
        
        # Critical value
        z_critical = 1.96 if confidence == 0.95 else 2.58
        
        # Improvement (difference in FRR)
        improvement = p1 - p2
        margin_error = z_critical * se_diff
        
        lower_bound = improvement - margin_error
        upper_bound = improvement + margin_error
        
        return (lower_bound, upper_bound)
    
    def save_comparison_results(self, 
                               comparison_result: FRRComparisonResult,
                               validation_result: Dict[str, bool],
                               output_file: str) -> None:
        """Save comparison results to JSON file.
        
        Args:
            comparison_result: FRR comparison result
            validation_result: Target validation results
            output_file: Path to output JSON file
        """
        output_data = {
            'frr_comparison': {
                'baseline_frr': comparison_result.baseline_frr,
                'multiagent_frr': comparison_result.multiagent_frr,
                'absolute_improvement': comparison_result.absolute_improvement,
                'relative_improvement': comparison_result.relative_improvement,
                'statistical_significance': comparison_result.statistical_significance,
                'effect_size': comparison_result.effect_size,
                'confidence_interval': comparison_result.confidence_interval,
                'sample_size': comparison_result.sample_size
            },
            'baseline_statistics': comparison_result.baseline_stats,
            'multiagent_statistics': comparison_result.multiagent_stats,
            'target_validation': validation_result
        }
        
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)