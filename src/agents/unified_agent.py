"""Unified recruitment agent combining all agent functionalities."""
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4
import re

from openai import AsyncOpenAI
import numpy as np

from services.vector_store import VectorStoreService, VectorSearchResult
from services.skill_ontology import SkillOntologyService
from services.redis_service import RedisService
from models.database import Job, Resume, Candidate, ScreeningResult, AuditLog

logger = logging.getLogger(__name__)


@dataclass
class EvaluationResult:
    """Result of candidate evaluation."""
    screening_score: float
    critic_score: float
    confidence: float
    needs_review: bool
    explanation: str
    bias_flags: List[str]
    matched_skills: List[Dict[str, float]]
    missing_skills: List[str]
    transferable_skills: List[Dict[str, str]]
    workflow_id: str
    review_type: str = "none"
    review_priority: str = "normal"


class UnifiedRecruitmentAgent:
    """Unified agent handling all recruitment workflow steps."""
    
    def __init__(self, config: Dict[str, Any], llm_client: AsyncOpenAI):
        """Initialize the unified agent."""
        self.config = config
        self.llm = llm_client
        self.hitl_threshold = config.get("hitl_confidence_threshold", 0.85)
        
        # Initialize services
        self.vector_store = VectorStoreService(config, llm_client)
        self.skill_service = SkillOntologyService()
        self.redis_service = RedisService(config)
    
    async def initialize(self) -> None:
        """Initialize all services."""
        await self.vector_store.initialize()
        await self.redis_service.initialize()
        logger.info("UnifiedRecruitmentAgent initialized successfully")
    
    async def process_job_application(
        self,
        job_description: str,
        resume_text: str,
        job_id: str,
        candidate_id: str
    ) -> EvaluationResult:
        """Process a job application through all agent stages."""
        # Initialize workflow
        workflow_id = await self._init_workflow_state(job_id, candidate_id)
        
        try:
            # Supervisor: Decompose job requirements
            job_requirements = await self._decompose_job_requirements(
                job_description, workflow_id
            )
            
            # Sourcing: Parse resume
            parsed_resume = await self._parse_resume(resume_text, workflow_id)
            
            # Screening: Semantic matching
            screening_result = await self._semantic_screening(
                job_requirements, parsed_resume, workflow_id
            )
            
            # Critic: Review and bias detection
            critic_result = await self._critical_review(
                screening_result, parsed_resume, job_requirements, workflow_id
            )
            
            # Calculate confidence and determine if HITL needed
            confidence_metrics = self._calculate_confidence(
                screening_result, critic_result
            )
            
            # Generate explanation
            explanation = await self._generate_explanation(
                screening_result, critic_result, confidence_metrics
            )
            
            # Log evaluation
            await self._log_evaluation(
                workflow_id, job_id, candidate_id,
                screening_result, critic_result, confidence_metrics
            )
            
            return EvaluationResult(
                screening_score=screening_result["score"],
                critic_score=critic_result["score"],
                confidence=confidence_metrics["confidence"],
                needs_review=confidence_metrics["needs_review"],
                explanation=explanation,
                bias_flags=critic_result.get("bias_flags", []),
                matched_skills=screening_result.get("matched_skills", []),
                missing_skills=screening_result.get("missing_skills", []),
                transferable_skills=critic_result.get("transferable_skills", []),
                workflow_id=workflow_id,
                review_type=confidence_metrics.get("review_type", "none"),
                review_priority=confidence_metrics.get("review_priority", "normal")
            )
            
        except Exception as e:
            logger.error(f"Error in workflow {workflow_id}: {e}")
            raise
    
    async def _init_workflow_state(self, job_id: str, candidate_id: str) -> str:
        """Initialize workflow state in Redis."""
        workflow_id = f"wf_{uuid4().hex[:8]}"
        
        state = {
            "job_id": job_id,
            "candidate_id": candidate_id,
            "status": "started",
            "started_at": datetime.now(timezone.utc).isoformat()
        }
        
        await self.redis_service.set_workflow_state(workflow_id, state)
        return workflow_id
    
    async def _decompose_job_requirements(
        self,
        job_description: str,
        workflow_id: str
    ) -> Dict[str, Any]:
        """Supervisor: Decompose job into structured requirements."""
        prompt = f"""
        Analyze this job description and extract structured requirements:
        
        {job_description}
        
        Return a JSON object with:
        - technical_skills: list of required technical skills
        - experience_years: object with minimum and preferred years
        - education: object with level and fields
        - soft_skills: list of soft skills
        - domain: list of domain areas
        - nice_to_have: list of optional skills
        """
        
        response = await self.llm.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        requirements = json.loads(response.choices[0].message.content)
        
        # Ensure all required fields exist with defaults
        requirements.setdefault("technical_skills", [])
        requirements.setdefault("soft_skills", [])
        requirements.setdefault("experience_years", {"minimum": 0, "preferred": 0})
        requirements.setdefault("education", {"level": "", "fields": []})
        requirements.setdefault("domain", [])
        requirements.setdefault("nice_to_have", [])
        
        # Normalize skills
        requirements["technical_skills"] = [
            self.skill_service.normalize_skill(skill).lower()
            for skill in requirements.get("technical_skills", [])
        ]
        requirements["soft_skills"] = [
            skill.lower() for skill in requirements.get("soft_skills", [])
        ]
        
        # Generate embeddings for skills
        requirements["skill_embeddings"] = {}
        for skill in requirements["technical_skills"]:
            embedding = await self.vector_store.create_embedding(skill)
            requirements["skill_embeddings"][skill] = embedding
        
        # Update workflow state
        await self.redis_service.set_workflow_state(workflow_id, {
            "status": "requirements_decomposed",
            "requirements": requirements
        })
        
        return requirements
    
    async def _parse_resume(
        self,
        resume_text: str,
        workflow_id: str
    ) -> Dict[str, Any]:
        """Sourcing: Parse resume into structured format."""
        prompt = f"""
        Extract structured information from this resume:
        
        {resume_text}
        
        Return a JSON object with:
        - skills: object with technical and soft skill lists
        - experience: list of work experiences with company, title, duration, achievements
        - education: list of education entries
        - certifications: list of certifications
        - projects: list of notable projects
        """
        
        response = await self.llm.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        parsed = json.loads(response.choices[0].message.content)
        
        # Normalize skills
        parsed["skills"]["technical"] = [
            self.skill_service.normalize_skill(skill).lower()
            for skill in parsed.get("skills", {}).get("technical", [])
        ]
        
        # Calculate total experience
        total_years = 0.0
        for exp in parsed.get("experience", []):
            duration = exp.get("duration", "")
            total_years += self._parse_duration(duration)
        
        parsed["total_experience_years"] = total_years
        
        # Generate resume embedding
        resume_embedding = await self.vector_store.create_embedding(resume_text)
        parsed["resume_embedding"] = resume_embedding
        
        # Update workflow state
        await self.redis_service.set_workflow_state(workflow_id, {
            "status": "resume_parsed",
            "parsed_resume": parsed
        })
        
        return parsed
    
    async def _semantic_screening(
        self,
        job_requirements: Dict[str, Any],
        parsed_resume: Dict[str, Any],
        workflow_id: str
    ) -> Dict[str, Any]:
        """Screening: Perform semantic matching."""
        # Skill matching
        required_skills = set(job_requirements.get("technical_skills", []))
        candidate_skills = set(parsed_resume.get("skills", {}).get("technical", []))
        
        matched_skills = []
        missing_skills = list(required_skills - candidate_skills)
        
        # Direct matches
        for skill in required_skills & candidate_skills:
            matched_skills.append({
                "required": skill,
                "found": skill,
                "confidence": 1.0
            })
        
        # Check for related skills using ontology
        for missing in missing_skills[:]:
            related = self.skill_service.get_related_skills(missing)
            for related_skill in related:
                if related_skill.lower() in candidate_skills:
                    matched_skills.append({
                        "required": missing,
                        "found": related_skill.lower(),
                        "confidence": 0.7
                    })
                    missing_skills.remove(missing)
                    break
        
        # Experience matching
        min_exp = job_requirements.get("experience_years", {}).get("minimum", 0)
        candidate_exp = parsed_resume.get("total_experience_years", 0)
        experience_match = candidate_exp >= min_exp
        
        # Calculate overall score
        skill_score = self.skill_service.calculate_skill_similarity(
            list(required_skills),
            list(candidate_skills)
        )
        
        exp_score = min(1.0, candidate_exp / max(min_exp, 1))
        overall_score = (skill_score * 0.7 + exp_score * 0.3)
        
        result = {
            "score": overall_score,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "experience_match": experience_match,
            "skill_coverage": len(matched_skills) / max(len(required_skills), 1)
        }
        
        # Update workflow state
        await self.redis_service.set_workflow_state(workflow_id, {
            "status": "screening_completed",
            "screening_result": result
        })
        
        return result
    
    async def _critical_review(
        self,
        screening_result: Dict[str, Any],
        parsed_resume: Dict[str, Any],
        job_requirements: Dict[str, Any],
        workflow_id: str
    ) -> Dict[str, Any]:
        """Critic: Review screening with bias detection."""
        prompt = f"""
        Review this candidate evaluation for potential biases and hidden qualities:
        
        Screening Score: {screening_result['score']}
        Matched Skills: {screening_result['matched_skills']}
        Missing Skills: {screening_result['missing_skills']}
        
        Resume Info:
        Education: {parsed_resume.get('education', [])}
        Experience: {parsed_resume.get('experience', [])}
        
        Consider:
        1. Non-traditional backgrounds (bootcamps, self-taught)
        2. Transferable skills from other domains
        3. Potential biases in requirements
        4. Hidden gem indicators
        
        Return JSON with:
        - adjusted_score: float (0-1)
        - confidence_in_assessment: float (0-1)
        - bias_flags: list of detected biases
        - hidden_gem_indicators: list of positive signals
        - transferable_skills: list of objects with from, to, relevance
        - reasoning: explanation of adjustments
        """
        
        response = await self.llm.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            response_format={"type": "json_object"}
        )
        
        critic_result = json.loads(response.choices[0].message.content)
        
        # Determine if candidate is a hidden gem
        hidden_gem = (
            len(critic_result.get("hidden_gem_indicators", [])) >= 2 or
            critic_result.get("adjusted_score", 0) - screening_result["score"] > 0.3
        )
        
        critic_result["score"] = critic_result.pop("adjusted_score", screening_result["score"])
        critic_result["hidden_gem"] = hidden_gem
        
        # Update workflow state
        await self.redis_service.set_workflow_state(workflow_id, {
            "status": "critic_review_completed",
            "critic_result": critic_result
        })
        
        return critic_result
    
    def _calculate_confidence(
        self,
        screening_result: Dict[str, Any],
        critic_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate confidence and determine if HITL is needed."""
        screen_score = screening_result["score"]
        critic_score = critic_result["score"]
        critic_confidence = critic_result.get("confidence_in_assessment", 0.8)
        
        # Score difference indicates uncertainty
        score_diff = abs(screen_score - critic_score)
        
        # Base confidence
        confidence = critic_confidence * (1 - score_diff)
        
        # Special cases
        special_cases = {
            "hidden_gem": critic_result.get("hidden_gem", False),
            "high_bias_risk": len(critic_result.get("bias_flags", [])) > 1,
            "large_score_gap": score_diff > 0.3
        }
        
        # Determine if review needed
        needs_review = (
            confidence < self.hitl_threshold or
            any(special_cases.values()) or
            screen_score < 0.4  # Low initial score
        )
        
        # Determine review type
        review_type = "none"
        review_priority = "normal"
        
        if needs_review:
            if special_cases["hidden_gem"]:
                review_type = "deep"
                review_priority = "high"
            elif special_cases["large_score_gap"]:
                review_type = "score_reconciliation"
                review_priority = "high"
            elif confidence < 0.6:
                review_type = "full"
                review_priority = "medium"
            else:
                review_type = "quick"
                review_priority = "low"
        
        return {
            "confidence": confidence,
            "needs_review": needs_review,
            "score_difference": score_diff,
            "special_cases": special_cases,
            "review_type": review_type,
            "review_priority": review_priority
        }
    
    async def _generate_explanation(
        self,
        screening_result: Dict[str, Any],
        critic_result: Dict[str, Any],
        confidence_metrics: Dict[str, Any]
    ) -> str:
        """Generate human-readable explanation."""
        if confidence_metrics["special_cases"]["hidden_gem"]:
            return (
                f"Potential hidden gem candidate! Initial score: {screening_result['score']:.2f}, "
                f"Adjusted score: {critic_result['score']:.2f}. "
                f"Positive indicators: {', '.join(critic_result.get('hidden_gem_indicators', [])[:2])}"
            )
        
        matched_count = len(screening_result.get("matched_skills", []))
        missing_count = len(screening_result.get("missing_skills", []))
        
        if screening_result["score"] >= 0.8:
            return f"Strong match with {matched_count} skills aligned. Confidence: {confidence_metrics['confidence']:.2f}"
        elif screening_result["score"] >= 0.6:
            return f"Good candidate with {matched_count} matching skills, {missing_count} gaps. Consider for interview."
        else:
            return f"Limited match ({screening_result['score']:.2f}). Missing key skills: {', '.join(screening_result.get('missing_skills', [])[:3])}"
    
    async def _log_evaluation(
        self,
        workflow_id: str,
        job_id: str,
        candidate_id: str,
        screening_result: Dict[str, Any],
        critic_result: Dict[str, Any],
        confidence_metrics: Dict[str, Any]
    ) -> None:
        """Data-Steward: Log evaluation for audit."""
        # Log to Redis metrics
        await self.redis_service.increment_metric("evaluations_completed")
        
        if confidence_metrics["needs_review"]:
            await self.redis_service.increment_metric("evaluations_needing_review")
            
            # Publish HITL request
            await self.redis_service.publish_hitl_request(
                f"review_{workflow_id}",
                {
                    "workflow_id": workflow_id,
                    "job_id": job_id,
                    "candidate_id": candidate_id,
                    "review_type": confidence_metrics["review_type"],
                    "priority": confidence_metrics["review_priority"],
                    "scores": {
                        "screening": screening_result["score"],
                        "critic": critic_result["score"]
                    }
                }
            )
        
        # Update final workflow state
        await self.redis_service.set_workflow_state(workflow_id, {
            "status": "completed",
            "final_scores": {
                "screening": screening_result["score"],
                "critic": critic_result["score"],
                "confidence": confidence_metrics["confidence"]
            },
            "needs_review": confidence_metrics["needs_review"],
            "completed_at": datetime.now(timezone.utc).isoformat()
        })
    
    def _parse_duration(self, duration_str: str) -> float:
        """Parse duration string to years."""
        if not duration_str or duration_str.lower() in ["no experience", "n/a"]:
            return 0.0
        
        # Clean the string
        duration_str = duration_str.lower().strip()
        
        # Handle "X+ years" format
        if "+" in duration_str:
            match = re.search(r'(\d+)\+', duration_str)
            if match:
                return float(match.group(1))
        
        years = 0.0
        
        # Extract years
        year_match = re.search(r'(\d+)\s*year', duration_str)
        if year_match:
            years += float(year_match.group(1))
        
        # Extract months
        month_match = re.search(r'(\d+)\s*month', duration_str)
        if month_match:
            years += float(month_match.group(1)) / 12
        
        return years