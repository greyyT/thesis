#!/usr/bin/env python3
"""Evaluate multi-agent system FRR on the 1,182 candidate dataset."""

import asyncio
import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from evaluation.multiagent_evaluator import MultiAgentEvaluator
from evaluation.frr_comparison import FRRComparator


async def main():
    """Run multi-agent FRR evaluation on full dataset."""
    
    # Initialize multi-agent evaluator
    print("Initializing multi-agent evaluation system...")
    evaluator = MultiAgentEvaluator(
        qualification_threshold=0.4,  # Match baseline for fair comparison
        acceptance_threshold=0.5
    )
    
    # Load job descriptions
    job_descriptions_dir = Path(__file__).parent.parent / "src" / "data" / "job_descriptions"
    print(f"Loading job descriptions from {job_descriptions_dir}...")
    await evaluator.load_job_descriptions(str(job_descriptions_dir))
    print(f"Loaded {len(evaluator.job_descriptions)} job descriptions")
    
    # Evaluate candidates
    candidates_file = Path(__file__).parent.parent / "src" / "data" / "candidates.csv"
    results_file = Path(__file__).parent.parent / "results" / "multiagent_frr_results.json"
    
    print(f"Starting multi-agent evaluation of candidates from {candidates_file}...")
    print("This will take several minutes due to LLM API calls...")
    
    # Create results directory if it doesn't exist
    results_file.parent.mkdir(exist_ok=True)
    
    # Run evaluation with smaller batch size to avoid API rate limits
    results = await evaluator.evaluate_candidates_batch(
        candidates_file=str(candidates_file),
        results_file=str(results_file),
        batch_size=5  # Small batch to avoid rate limits
    )
    
    # Calculate FRR and statistics
    frr = evaluator.calculate_frr()
    stats = evaluator.get_evaluation_statistics()
    
    print("\\n" + "="*60)
    print("MULTI-AGENT SYSTEM FRR EVALUATION RESULTS")
    print("="*60)
    print(f"Total candidates processed: {stats['total_candidates']:,}")
    print(f"Qualified candidates: {stats['qualified_candidates']:,}")
    print(f"False rejections: {stats['false_rejections']:,}")
    print(f"Multi-Agent System FRR: {frr:.1%}")
    print(f"System accuracy: {stats['accuracy']:.1%}")
    print(f"Hidden gems detected: {sum(1 for r in results if r.hidden_gem_detected)}")
    
    # Validate against target
    target_frr = 0.06  # 6% target (50% improvement from 12% baseline)
    within_target = evaluator.validate_baseline_frr(target_frr=target_frr, tolerance=0.02)
    print(f"\\nTarget Achievement (≤{target_frr:.0%}): {'✅ ACHIEVED' if within_target else '❌ NOT ACHIEVED'}")
    
    # Save summary statistics
    summary_file = Path(__file__).parent.parent / "results" / "multiagent_frr_summary.json"
    summary_data = {
        'frr': frr,
        'statistics': stats,
        'target_frr': target_frr,
        'target_achieved': within_target,
        'evaluation_details': {
            'total_processed': len(results),
            'hidden_gems_detected': sum(1 for r in results if r.hidden_gem_detected),
            'avg_screening_score': sum(r.screening_score for r in results) / len(results) if results else 0,
            'avg_confidence_score': sum(r.confidence_score for r in results) / len(results) if results else 0
        }
    }
    
    with open(summary_file, 'w') as f:
        json.dump(summary_data, f, indent=2)
    
    print(f"\\nDetailed results saved to: {results_file}")
    print(f"Summary statistics saved to: {summary_file}")
    
    # Check for baseline comparison
    baseline_results_file = Path(__file__).parent.parent / "results" / "baseline_frr_results.json"
    if baseline_results_file.exists():
        print(f"\\nBaseline results found. Running FRR comparison...")
        
        # Load baseline results for comparison
        comparator = FRRComparator()
        comparator.load_evaluation_results(
            baseline_results_file=str(baseline_results_file),
            multiagent_results_file=str(results_file)
        )
        
        # Compare FRR
        comparison = comparator.compare_frr(
            expected_baseline=0.12,  # 12% baseline assumption
            target_improvement=0.06   # 6% target
        )
        
        # Validate against targets
        validation = comparator.validate_against_targets(comparison)
        
        # Generate and save comparison report
        report = comparator.generate_comparison_report(comparison, validation)
        
        report_file = Path(__file__).parent.parent / "results" / "frr_comparison_report.md"
        with open(report_file, 'w') as f:
            f.write(report)
        
        # Save detailed comparison data
        comparison_file = Path(__file__).parent.parent / "results" / "frr_comparison_data.json"
        comparator.save_comparison_results(comparison, validation, str(comparison_file))
        
        print("\\n" + "="*60)
        print("FRR COMPARISON: BASELINE vs MULTI-AGENT")
        print("="*60)
        print(f"Baseline FRR: {comparison.baseline_frr:.1%}")
        print(f"Multi-Agent FRR: {comparison.multiagent_frr:.1%}")
        print(f"Absolute Improvement: {comparison.absolute_improvement:.1%}")
        print(f"Relative Improvement: {comparison.relative_improvement:.1%}")
        print(f"Statistical Significance: {'Yes' if comparison.statistical_significance else 'No'}")
        print(f"Effect Size: {comparison.effect_size:.3f}")
        
        overall_success = validation.get('meets_all_criteria', False)
        print(f"\\nOverall Success: {'✅ ALL CRITERIA MET' if overall_success else '⚠️ SOME CRITERIA NOT MET'}")
        
        print(f"\\nFull comparison report saved to: {report_file}")
        print(f"Comparison data saved to: {comparison_file}")
    else:
        print(f"\\nBaseline results not found at {baseline_results_file}")
        print("Run evaluate_baseline_frr.py first to enable comparison")
    
    print("\\nMulti-agent FRR evaluation completed!")


if __name__ == "__main__":
    asyncio.run(main())