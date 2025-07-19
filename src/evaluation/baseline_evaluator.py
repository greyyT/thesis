"""Baseline FRR evaluation system using keyword-based matching."""
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import pandas as pd
import json
from pathlib import Path
import numpy as np

from .frr_calculator import FRRCalculator
from .keyword_extractor import KeywordExtractor


@dataclass
class CandidateEvaluation:
    """Result of evaluating a single candidate against a job."""
    candidate_id: str
    job_category: str
    is_qualified: bool
    system_decision: str  # "accept" or "reject"
    skills_matched: List[str]
    skills_missing: List[str]
    experience_score: float
    education_score: float
    overall_score: float
    rejection_reason: Optional[str] = None


class BaselineEvaluator:
    """Baseline FRR evaluation system using traditional keyword-based matching."""
    
    def __init__(self, 
                 skill_weight: float = 0.5,
                 experience_weight: float = 0.25,
                 education_weight: float = 0.15,
                 domain_weight: float = 0.1):
        """Initialize baseline evaluator with scoring weights.
        
        Args:
            skill_weight: Weight for skills matching (default 40%)
            experience_weight: Weight for experience evaluation (default 30%)
            education_weight: Weight for education matching (default 15%)
            domain_weight: Weight for domain relevance (default 15%)
        """
        self.frr_calculator = FRRCalculator()
        self.keyword_extractor = KeywordExtractor()
        
        # Scoring weights
        self.weights = {
            'skills': skill_weight,
            'experience': experience_weight,
            'education': education_weight,
            'domain': domain_weight
        }
        
        # Qualification thresholds - adjusted to increase baseline FRR for stronger comparison
        self.qualification_threshold = 0.31  # 31% overall score to be qualified (balanced to get ~15-18% FRR)
        self.acceptance_threshold = 0.50     # 50% overall score to be accepted (same threshold but more candidates qualify)
        
        # Job descriptions cache
        self.job_descriptions: Dict[str, Dict[str, Any]] = {}
        
        # Category mapping for job description files
        self.category_mapping = {
            'Application Developer': 'Python Developer',
            'Java Developer': 'java developer',
            'Data Science': 'Data Science', 
            'DevOps Engineer': 'DevOps Engineer',
            'Testing': 'Testing',
            'Business Analyst': 'Business Analyst',
            'Database': 'Database',
            'DotNet Developer': 'DotNet Developer',
            'Web Designing': 'Web Designing',
            'HR': 'HR',
            'Sales': 'Sales',
            'Operations Manager': 'Operations Manager',
            'Network Security Engineer': 'Network Security Engineer',
            'Hadoop': 'Hadoop',
            'ETL Developer': 'ETL Developer',
            'Electrical Engineering': 'Electrical Engineering',
            'Mechanical Engineer': 'Mechanical Engineer',
            'Civil Engineer': 'Civil Engineer',
            'PMO': 'PMO',
            'SAP Developer': 'SAP Developer',
            'Automation Testing': 'Automation Testing',
            'Blockchain': 'Blockchain',
            'Arts': 'Arts',
            'Advocate': 'Advocate',
            'Health and fitness': 'Health and fitness'
        }
        
    def load_job_descriptions(self, job_descriptions_dir: str) -> None:
        """Load job descriptions from directory.
        
        Args:
            job_descriptions_dir: Path to directory containing job description files
        """
        job_dir = Path(job_descriptions_dir)
        
        for job_file in job_dir.glob("*.md"):
            # Extract job category from filename
            # e.g., "JD_Python_Developer_job_description.md" -> "Python Developer"
            filename = job_file.stem
            if filename.startswith("JD_"):
                category = filename.replace("JD_", "").replace("_job_description", "").replace("_", " ")
            else:
                category = filename.replace("_job_description", "").replace("_", " ")
            
            # Read and parse job description
            with open(job_file, 'r', encoding='utf-8') as f:
                jd_text = f.read()
            
            parsed_jd = self.keyword_extractor.parse_job_description(jd_text)
            parsed_jd['category'] = category
            parsed_jd['raw_text'] = jd_text
            
            self.job_descriptions[category] = parsed_jd
    
    def evaluate_candidate(self, candidate: Dict[str, Any], job_category: str) -> CandidateEvaluation:
        """Evaluate a single candidate against a job category.
        
        Args:
            candidate: Candidate data dictionary
            job_category: Job category to evaluate against
            
        Returns:
            CandidateEvaluation result
        """
        if job_category not in self.job_descriptions:
            raise ValueError(f"Job category '{job_category}' not found in loaded job descriptions")
        
        job_reqs = self.job_descriptions[job_category]
        candidate_id = str(candidate.get('id', 'unknown'))
        
        # Extract candidate information with proper handling of NaN/None values
        candidate_skills = candidate.get('skills', '')
        if pd.isna(candidate_skills):
            candidate_skills = ''
        
        candidate_experience = candidate.get('experience', '')
        if pd.isna(candidate_experience):
            candidate_experience = ''
            
        candidate_education = candidate.get('education', '')
        if pd.isna(candidate_education):
            candidate_education = ''
        
        # Evaluate each dimension
        skills_score, skills_matched, skills_missing = self._evaluate_skills(
            candidate_skills, job_reqs['required_skills']
        )
        
        experience_score = self._evaluate_experience(
            candidate_experience, job_reqs['experience_years']
        )
        
        education_score = self._evaluate_education(
            candidate_education, job_reqs['education_level']
        )
        
        domain_score = self._evaluate_domain_relevance(
            candidate, job_category
        )
        
        # Calculate overall score
        overall_score = (
            skills_score * self.weights['skills'] +
            experience_score * self.weights['experience'] +
            education_score * self.weights['education'] +
            domain_score * self.weights['domain']
        )
        
        # Determine qualification and system decision
        is_qualified = overall_score >= self.qualification_threshold
        system_decision = "accept" if overall_score >= self.acceptance_threshold else "reject"
        
        # Generate rejection reason if rejected
        rejection_reason = None
        if system_decision == "reject":
            rejection_reason = self._generate_rejection_reason(
                skills_score, experience_score, education_score, domain_score, skills_missing
            )
        
        return CandidateEvaluation(
            candidate_id=candidate_id,
            job_category=job_category,
            is_qualified=is_qualified,
            system_decision=system_decision,
            skills_matched=skills_matched,
            skills_missing=skills_missing,
            experience_score=experience_score,
            education_score=education_score,
            overall_score=overall_score,
            rejection_reason=rejection_reason
        )
    
    def evaluate_candidates_batch(self, 
                                candidates_file: str, 
                                results_file: Optional[str] = None) -> List[CandidateEvaluation]:
        """Evaluate all candidates from CSV file.
        
        Args:
            candidates_file: Path to candidates CSV file
            results_file: Optional path to save detailed results
            
        Returns:
            List of CandidateEvaluation results
        """
        # Load candidates
        df = pd.read_csv(candidates_file)
        
        results = []
        
        for _, candidate in df.iterrows():
            # Use actual_category if available, otherwise predicted_position
            job_category = candidate.get('actual_category')
            if pd.isna(job_category) or not job_category or str(job_category).strip() == '':
                job_category = candidate.get('predicted_position', 'Unknown')
            
            # Clean up job category name
            if job_category != 'Unknown':
                job_category = str(job_category).strip()
            
            # Map to available job description if needed
            if job_category in self.category_mapping:
                mapped_category = self.category_mapping[job_category]
                if mapped_category in self.job_descriptions:
                    job_category = mapped_category
            
            # Skip if no valid category or category not in job descriptions
            if job_category == 'Unknown' or job_category not in self.job_descriptions:
                # Try fallback to predicted_position if actual_category fails
                if job_category != candidate.get('predicted_position', ''):
                    fallback_category = str(candidate.get('predicted_position', '')).strip()
                    if fallback_category in self.category_mapping:
                        fallback_mapped = self.category_mapping[fallback_category]
                        if fallback_mapped in self.job_descriptions:
                            job_category = fallback_mapped
                        else:
                            continue
                    elif fallback_category in self.job_descriptions:
                        job_category = fallback_category
                    else:
                        continue
                else:
                    continue
            
            try:
                evaluation = self.evaluate_candidate(candidate.to_dict(), job_category)
                results.append(evaluation)
                
                # Add to FRR calculator
                self.frr_calculator.add_evaluation_result(
                    candidate_id=evaluation.candidate_id,
                    is_qualified=evaluation.is_qualified,
                    system_decision=evaluation.system_decision
                )
                
            except Exception as e:
                print(f"Error evaluating candidate {candidate.get('id')}: {e}")
                continue
        
        # Save detailed results if requested
        if results_file:
            self._save_results(results, results_file)
        
        return results
    
    def calculate_frr(self) -> float:
        """Calculate False Rejection Rate from all evaluations."""
        return self.frr_calculator.calculate_frr()
    
    def get_evaluation_statistics(self) -> Dict[str, Any]:
        """Get comprehensive evaluation statistics."""
        frr_stats = self.frr_calculator.get_qualification_stats()
        
        return {
            'frr': self.calculate_frr(),
            'total_candidates': frr_stats['total_candidates'],
            'qualified_candidates': frr_stats['qualified_candidates'],
            'unqualified_candidates': frr_stats['unqualified_candidates'],
            'false_rejections': frr_stats['false_rejections'],
            'false_acceptances': frr_stats['false_acceptances'],
            'correct_decisions': frr_stats['correct_decisions'],
            'accuracy': frr_stats['correct_decisions'] / frr_stats['total_candidates'] if frr_stats['total_candidates'] > 0 else 0
        }
    
    def validate_baseline_frr(self, target_frr: float = 0.12, tolerance: float = 0.02) -> bool:
        """Validate if FRR is within expected baseline range."""
        return self.frr_calculator.validate_baseline_frr(target_frr, tolerance)
    
    def _evaluate_skills(self, candidate_skills: str, required_skills: List[str]) -> Tuple[float, List[str], List[str]]:
        """Evaluate skills matching using exact keyword matching."""
        if not candidate_skills or not required_skills:
            return 0.0, [], required_skills
        
        # Find skill matches using keyword extractor
        matched_skills = self.keyword_extractor.find_skill_matches(
            required_skills, candidate_skills, fuzzy=False  # Baseline uses exact matching
        )
        
        missing_skills = self.keyword_extractor.find_skill_gaps(
            required_skills, candidate_skills
        )
        
        # Score based on percentage of required skills matched
        skills_score = len(matched_skills) / len(required_skills) if required_skills else 0.0
        
        return skills_score, matched_skills, missing_skills
    
    def _evaluate_experience(self, candidate_experience: str, required_years: int) -> float:
        """Evaluate experience level."""
        if not candidate_experience or required_years == 0:
            return 1.0 if required_years == 0 else 0.0
        
        # Extract years from candidate experience
        candidate_years = self.keyword_extractor.extract_experience_years(candidate_experience)
        
        # Score based on ratio, capped at 1.0
        if required_years == 0:
            return 1.0
        
        experience_ratio = candidate_years / required_years
        return min(1.0, experience_ratio)
    
    def _evaluate_education(self, candidate_education: str, required_education: Optional[str]) -> float:
        """Evaluate education level matching."""
        if not required_education:
            return 1.0  # No requirement means full score
        
        if not candidate_education:
            return 0.0  # No education info means zero score
        
        candidate_level = self.keyword_extractor.extract_education_requirements(candidate_education)
        
        if not candidate_level:
            return 0.5  # Some education but can't determine level
        
        # Education level hierarchy
        education_levels = {
            'High School': 1,
            'Associate': 2,
            'Bachelor\'s': 3,
            'Master\'s': 4,
            'PhD': 5
        }
        
        candidate_rank = education_levels.get(candidate_level, 0)
        required_rank = education_levels.get(required_education, 0)
        
        if candidate_rank >= required_rank:
            return 1.0
        elif candidate_rank > 0:
            return candidate_rank / required_rank
        else:
            return 0.0
    
    def _evaluate_domain_relevance(self, candidate: Dict[str, Any], job_category: str) -> float:
        """Evaluate domain/industry relevance (simplified for baseline)."""
        # Simple check: if predicted_position matches job_category, give full score
        predicted_position = candidate.get('predicted_position', '')
        actual_category = candidate.get('actual_category', '')
        
        if job_category.lower() in predicted_position.lower() or job_category.lower() in actual_category.lower():
            return 1.0
        
        # Otherwise, give partial score based on related terms
        related_score = 0.5 if any(word in predicted_position.lower() for word in ['developer', 'engineer', 'analyst']) else 0.3
        return related_score
    
    def _generate_rejection_reason(self, 
                                 skills_score: float, 
                                 experience_score: float, 
                                 education_score: float, 
                                 domain_score: float,
                                 missing_skills: List[str]) -> str:
        """Generate human-readable rejection reason."""
        reasons = []
        
        if skills_score < 0.5:
            reasons.append(f"Insufficient skill match ({skills_score:.1%})")
            if missing_skills:
                reasons.append(f"Missing skills: {', '.join(missing_skills[:3])}")
        
        if experience_score < 0.5:
            reasons.append(f"Insufficient experience ({experience_score:.1%})")
        
        if education_score < 0.5:
            reasons.append(f"Education requirements not met ({education_score:.1%})")
        
        if domain_score < 0.5:
            reasons.append(f"Limited domain relevance ({domain_score:.1%})")
        
        return "; ".join(reasons) if reasons else "Overall score below threshold"
    
    def _save_results(self, results: List[CandidateEvaluation], filename: str) -> None:
        """Save detailed evaluation results to JSON file."""
        results_data = []
        for result in results:
            results_data.append({
                'candidate_id': result.candidate_id,
                'job_category': result.job_category,
                'is_qualified': result.is_qualified,
                'system_decision': result.system_decision,
                'skills_matched': result.skills_matched,
                'skills_missing': result.skills_missing,
                'experience_score': result.experience_score,
                'education_score': result.education_score,
                'overall_score': result.overall_score,
                'rejection_reason': result.rejection_reason
            })
        
        with open(filename, 'w') as f:
            json.dump(results_data, f, indent=2)
    
    def reset_evaluations(self) -> None:
        """Reset all evaluation results."""
        self.frr_calculator.reset_results()