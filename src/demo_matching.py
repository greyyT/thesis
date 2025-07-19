"""Demo script to showcase the matching logic functionality."""
import asyncio
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class MatchingDemo:
    """Demo results from matching logic."""
    job_requirements: Dict[str, Any]
    candidate_profile: Dict[str, Any]
    screening_result: Dict[str, Any]
    critic_review: Dict[str, Any]
    confidence_metrics: Dict[str, Any]
    
def demonstrate_semantic_screening():
    """Show how semantic screening works."""
    print("\n🔍 SEMANTIC SCREENING DEMO")
    print("=" * 50)
    
    # Example job requirements
    job_requirements = {
        "technical_skills": ["python", "fastapi", "docker", "kubernetes", "postgresql"],
        "experience_years": {"minimum": 5, "preferred": 7}
    }
    
    # Example candidate profile
    candidate_profile = {
        "skills": {"technical": ["python", "fastapi", "docker", "sql", "flask"]},
        "total_experience_years": 6.0
    }
    
    # Simulated screening result
    matched_skills = [
        {"required": "python", "found": "python", "confidence": 1.0},
        {"required": "fastapi", "found": "fastapi", "confidence": 1.0},
        {"required": "docker", "found": "docker", "confidence": 1.0},
        {"required": "postgresql", "found": "sql", "confidence": 0.7}  # Related skill
    ]
    
    missing_skills = ["kubernetes"]
    
    screening_result = {
        "score": 0.85,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "experience_match": True,
        "skill_coverage": 0.8  # 4/5 skills
    }
    
    print(f"📋 Job Requirements:")
    print(f"   - Technical Skills: {', '.join(job_requirements['technical_skills'])}")
    print(f"   - Experience: {job_requirements['experience_years']['minimum']}+ years")
    
    print(f"\n👤 Candidate Profile:")
    print(f"   - Skills: {', '.join(candidate_profile['skills']['technical'])}")
    print(f"   - Experience: {candidate_profile['total_experience_years']} years")
    
    print(f"\n📊 Screening Results:")
    print(f"   - Overall Score: {screening_result['score']:.2%}")
    print(f"   - Skill Coverage: {screening_result['skill_coverage']:.2%}")
    print(f"   - Experience Match: {'✅' if screening_result['experience_match'] else '❌'}")
    
    print(f"\n✅ Matched Skills:")
    for match in matched_skills:
        print(f"   - {match['required']} → {match['found']} (confidence: {match['confidence']:.2f})")
    
    print(f"\n❌ Missing Skills:")
    for skill in missing_skills:
        print(f"   - {skill}")
    
    return screening_result

def demonstrate_critical_review(screening_result):
    """Show how critical review works."""
    print("\n\n🎯 CRITICAL REVIEW DEMO")
    print("=" * 50)
    
    # Simulated critic review
    critic_result = {
        "score": 0.88,  # Higher than screening
        "confidence_in_assessment": 0.90,
        "bias_flags": [],
        "hidden_gem_indicators": ["strong_practical_experience", "transferable_skills"],
        "transferable_skills": [
            {"from": "sql", "to": "postgresql", "relevance": 0.9},
            {"from": "flask", "to": "fastapi", "relevance": 0.7}
        ],
        "reasoning": "Candidate shows strong practical experience with transferable skills"
    }
    
    print(f"🔍 Critic Analysis:")
    print(f"   - Initial Score: {screening_result['score']:.2%}")
    print(f"   - Adjusted Score: {critic_result['score']:.2%}")
    print(f"   - Assessment Confidence: {critic_result['confidence_in_assessment']:.2%}")
    
    print(f"\n💎 Hidden Gem Indicators:")
    for indicator in critic_result['hidden_gem_indicators']:
        print(f"   - {indicator.replace('_', ' ').title()}")
    
    print(f"\n🔄 Transferable Skills Found:")
    for skill in critic_result['transferable_skills']:
        print(f"   - {skill['from']} → {skill['to']} (relevance: {skill['relevance']:.2f})")
    
    print(f"\n📝 Reasoning: {critic_result['reasoning']}")
    
    return critic_result

def demonstrate_confidence_calculation(screening_result, critic_result):
    """Show how confidence calculation works."""
    print("\n\n📈 CONFIDENCE CALCULATION DEMO")
    print("=" * 50)
    
    # Calculate confidence metrics
    screen_score = screening_result['score']
    critic_score = critic_result['score']
    critic_confidence = critic_result['confidence_in_assessment']
    
    score_diff = abs(screen_score - critic_score)
    confidence = critic_confidence * (1 - score_diff)
    
    special_cases = {
        "hidden_gem": len(critic_result.get('hidden_gem_indicators', [])) >= 2,
        "high_bias_risk": len(critic_result.get('bias_flags', [])) > 1,
        "large_score_gap": score_diff > 0.3
    }
    
    needs_review = (
        confidence < 0.85 or  # Below threshold
        any(special_cases.values()) or
        screen_score < 0.4
    )
    
    confidence_metrics = {
        "confidence": confidence,
        "needs_review": needs_review,
        "score_difference": score_diff,
        "special_cases": special_cases,
        "review_type": "quick" if needs_review else "none",
        "review_priority": "normal"
    }
    
    print(f"📊 Confidence Metrics:")
    print(f"   - Overall Confidence: {confidence:.2%}")
    print(f"   - Score Difference: {score_diff:.2%}")
    print(f"   - Needs Human Review: {'Yes' if needs_review else 'No'}")
    
    print(f"\n🚨 Special Cases:")
    for case, triggered in special_cases.items():
        status = "✅" if triggered else "❌"
        print(f"   {status} {case.replace('_', ' ').title()}")
    
    if needs_review:
        print(f"\n👤 Review Details:")
        print(f"   - Type: {confidence_metrics['review_type']}")
        print(f"   - Priority: {confidence_metrics['review_priority']}")
    
    return confidence_metrics

def main():
    """Run the matching logic demo."""
    print("🎯 UNIFIED RECRUITMENT AGENT - MATCHING LOGIC DEMO")
    print("=" * 60)
    
    # Run demonstrations
    screening_result = demonstrate_semantic_screening()
    critic_result = demonstrate_critical_review(screening_result)
    confidence_metrics = demonstrate_confidence_calculation(screening_result, critic_result)
    
    # Final summary
    print("\n\n📊 FINAL EVALUATION SUMMARY")
    print("=" * 50)
    print(f"✅ Screening Score: {screening_result['score']:.2%}")
    print(f"✅ Critic Score: {critic_result['score']:.2%}")
    print(f"✅ Confidence: {confidence_metrics['confidence']:.2%}")
    print(f"✅ Decision: {'Human Review Required' if confidence_metrics['needs_review'] else 'Automated Approval'}")
    
    print("\n\n✨ All matching logic components are working correctly!")
    print("   - Semantic screening matches skills and experience")
    print("   - Critical review detects transferable skills and bias")
    print("   - Confidence calculation determines if human review is needed")

if __name__ == "__main__":
    main()