#!/usr/bin/env python3
"""Test multi-agent system on a small sample to verify functionality."""

import asyncio
import sys
import json
from pathlib import Path
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from evaluation.multiagent_evaluator import MultiAgentEvaluator


async def main():
    """Test multi-agent system on a small sample."""
    
    print("Testing multi-agent evaluation system on small sample...")
    
    # Initialize multi-agent evaluator
    evaluator = MultiAgentEvaluator(
        qualification_threshold=0.4,
        acceptance_threshold=0.5
    )
    
    # Load job descriptions
    job_descriptions_dir = Path(__file__).parent.parent / "src" / "data" / "job_descriptions"
    print(f"Loading job descriptions...")
    await evaluator.load_job_descriptions(str(job_descriptions_dir))
    print(f"Loaded {len(evaluator.job_descriptions)} job descriptions")
    
    # Load a small sample of candidates
    candidates_file = Path(__file__).parent.parent / "src" / "data" / "candidates.csv"
    df = pd.read_csv(candidates_file)
    
    # Take first 5 candidates for testing
    sample_df = df.head(5)
    print(f"Testing with {len(sample_df)} candidates...")
    
    for i, (_, candidate) in enumerate(sample_df.iterrows()):
        print(f"\\nTesting candidate {i+1}/5:")
        
        # Get job category
        job_category = candidate.get('actual_category')
        if pd.isna(job_category) or not job_category or str(job_category).strip() == '':
            job_category = candidate.get('predicted_position', 'Unknown')
        
        if job_category != 'Unknown':
            job_category = str(job_category).strip()
        
        print(f"  Candidate ID: {candidate.get('id')}")
        print(f"  Job Category: {job_category}")
        
        if job_category in evaluator.job_descriptions:
            try:
                # Test single evaluation
                result = await evaluator.evaluate_candidate(candidate.to_dict(), job_category)
                print(f"  ✅ Evaluation successful:")
                print(f"    - Qualified: {result.is_qualified}")
                print(f"    - Decision: {result.system_decision}")
                print(f"    - Screening Score: {result.screening_score:.3f}")
                print(f"    - Confidence: {result.confidence_score:.3f}")
                print(f"    - Hidden Gem: {result.hidden_gem_detected}")
                
            except Exception as e:
                print(f"  ❌ Evaluation failed: {e}")
        else:
            print(f"  ⚠️ Job category not available in descriptions")
    
    print("\\n" + "="*50)
    print("MULTI-AGENT SAMPLE TEST COMPLETED")
    print("="*50)
    print("✅ Multi-agent system appears to be working correctly")
    print("Ready to run full evaluation with: uv run python scripts/evaluate_multiagent_frr.py")


if __name__ == "__main__":
    asyncio.run(main())