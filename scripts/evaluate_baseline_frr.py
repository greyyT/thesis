#!/usr/bin/env python3
"""Evaluate baseline system FRR on the 1,182 candidate dataset."""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from evaluation.baseline_evaluator import BaselineEvaluator


def main():
    """Run baseline FRR evaluation on full dataset."""
    
    # Initialize baseline evaluator
    print("Initializing baseline evaluation system...")
    evaluator = BaselineEvaluator(
        skill_weight=0.4,
        experience_weight=0.3,
        education_weight=0.15,
        domain_weight=0.15
    )
    
    # Load job descriptions
    job_descriptions_dir = Path(__file__).parent.parent / "src" / "data" / "job_descriptions"
    print(f"Loading job descriptions from {job_descriptions_dir}...")
    evaluator.load_job_descriptions(str(job_descriptions_dir))
    print(f"Loaded {len(evaluator.job_descriptions)} job descriptions")
    
    # Evaluate candidates
    candidates_file = Path(__file__).parent.parent / "src" / "data" / "candidates.csv"
    results_file = Path(__file__).parent.parent / "results" / "baseline_frr_results.json"
    
    print(f"Starting baseline evaluation of candidates from {candidates_file}...")
    
    # Create results directory if it doesn't exist
    results_file.parent.mkdir(exist_ok=True)
    
    # Run evaluation
    results = evaluator.evaluate_candidates_batch(
        candidates_file=str(candidates_file),
        results_file=str(results_file)
    )
    
    # Calculate FRR and statistics
    frr = evaluator.calculate_frr()
    stats = evaluator.get_evaluation_statistics()
    
    print("\\n" + "="*60)
    print("BASELINE SYSTEM FRR EVALUATION RESULTS")
    print("="*60)
    print(f"Total candidates processed: {stats['total_candidates']:,}")
    print(f"Qualified candidates: {stats['qualified_candidates']:,}")
    print(f"False rejections: {stats['false_rejections']:,}")
    print(f"Baseline System FRR: {frr:.1%}")
    print(f"System accuracy: {stats['accuracy']:.1%}")
    
    # Validate against 12% baseline assumption
    baseline_target = 0.12  # 12% baseline from literature
    within_baseline = evaluator.validate_baseline_frr(target_frr=baseline_target, tolerance=0.05)
    print(f"\\nBaseline Validation ({baseline_target:.0%} ± 5%): {'✅ VALIDATED' if within_baseline else '❌ OUTSIDE RANGE'}")
    
    if not within_baseline:
        print(f"Note: Actual FRR ({frr:.1%}) differs from literature baseline ({baseline_target:.0%})")
        print("This is acceptable as we use the measured baseline for comparison")
    
    # Show top rejection reasons
    print(f"\\nTop rejection reasons from {len(results)} evaluations:")
    rejection_reasons = {}
    for result in results:
        if result.rejection_reason:
            reason = result.rejection_reason.split(';')[0].strip()  # Take first reason
            rejection_reasons[reason] = rejection_reasons.get(reason, 0) + 1
    
    for reason, count in sorted(rejection_reasons.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"- {reason}: {count} candidates")
    
    # Save summary statistics
    summary_file = Path(__file__).parent.parent / "results" / "baseline_frr_summary.json"
    summary_data = {
        'frr': frr,
        'statistics': stats,
        'baseline_target': baseline_target,
        'baseline_validated': within_baseline,
        'evaluation_details': {
            'total_processed': len(results),
            'avg_overall_score': sum(r.overall_score for r in results) / len(results) if results else 0,
            'qualification_rate': stats['qualified_candidates'] / stats['total_candidates'] if stats['total_candidates'] > 0 else 0,
            'top_rejection_reasons': dict(sorted(rejection_reasons.items(), key=lambda x: x[1], reverse=True)[:10])
        }
    }
    
    with open(summary_file, 'w') as f:
        json.dump(summary_data, f, indent=2)
    
    print(f"\\nDetailed results saved to: {results_file}")
    print(f"Summary statistics saved to: {summary_file}")
    print("\\nBaseline FRR evaluation completed!")
    print(f"Ready for multi-agent comparison. Run: uv run python scripts/evaluate_multiagent_frr.py")


if __name__ == "__main__":
    main()