"""Skill ontology service for normalizing and analyzing skills."""
import re
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class SkillOntologyService:
    """Service for skill normalization, extraction, and analysis."""
    
    def __init__(self):
        """Initialize skill ontology with predefined mappings."""
        # Skill normalization mappings
        self.skill_aliases = {
            # Programming Languages
            "python": "Python",
            "py": "Python",
            "javascript": "JavaScript",
            "js": "JavaScript",
            "typescript": "TypeScript",
            "ts": "TypeScript",
            "java": "Java",
            "c++": "C++",
            "cpp": "C++",
            "c#": "C#",
            "csharp": "C#",
            "golang": "Go",
            "ruby": "Ruby",
            "php": "PHP",
            "swift": "Swift",
            "kotlin": "Kotlin",
            "rust": "Rust",
            "r": "R",
            "matlab": "MATLAB",
            "scala": "Scala",
            "f#": "F#",
            "fsharp": "F#",
            
            # Web Frameworks
            "react": "React",
            "reactjs": "React",
            "react.js": "React",
            "vue": "Vue.js",
            "vuejs": "Vue.js",
            "vue.js": "Vue.js",
            "angular": "Angular",
            "angularjs": "AngularJS",
            "django": "Django",
            "flask": "Flask",
            "fastapi": "FastAPI",
            "express": "Express.js",
            "expressjs": "Express.js",
            "express.js": "Express.js",
            "spring": "Spring",
            "spring boot": "Spring Boot",
            "springboot": "Spring Boot",
            "rails": "Ruby on Rails",
            "ruby on rails": "Ruby on Rails",
            "laravel": "Laravel",
            "asp.net": "ASP.NET",
            "aspnet": "ASP.NET",
            
            # Databases
            "postgres": "PostgreSQL",
            "postgresql": "PostgreSQL",
            "mysql": "MySQL",
            "mongodb": "MongoDB",
            "mongo": "MongoDB",
            "redis": "Redis",
            "elasticsearch": "Elasticsearch",
            "elastic": "Elasticsearch",
            "cassandra": "Cassandra",
            "oracle": "Oracle",
            "sql server": "SQL Server",
            "mssql": "SQL Server",
            "sqlite": "SQLite",
            "dynamodb": "DynamoDB",
            "neo4j": "Neo4j",
            
            # Cloud & DevOps
            "aws": "AWS",
            "amazon web services": "AWS",
            "gcp": "Google Cloud",
            "google cloud": "Google Cloud",
            "google cloud platform": "Google Cloud",
            "azure": "Azure",
            "microsoft azure": "Azure",
            "docker": "Docker",
            "kubernetes": "Kubernetes",
            "k8s": "Kubernetes",
            "jenkins": "Jenkins",
            "gitlab ci": "GitLab CI",
            "github actions": "GitHub Actions",
            "terraform": "Terraform",
            "ansible": "Ansible",
            "helm": "Helm",
            
            # Other Technologies
            "node": "Node.js",
            "nodejs": "Node.js",
            "node.js": "Node.js",
            "git": "Git",
            "github": "GitHub",
            "gitlab": "GitLab",
            "bitbucket": "Bitbucket",
            "jira": "Jira",
            "confluence": "Confluence",
            "ml": "Machine Learning",
            "machine learning": "Machine Learning",
            "ai": "Artificial Intelligence",
            "artificial intelligence": "Artificial Intelligence",
            "deep learning": "Deep Learning",
            "tensorflow": "TensorFlow",
            "pytorch": "PyTorch",
            "scikit-learn": "scikit-learn",
            "sklearn": "scikit-learn",
            "pandas": "pandas",
            "numpy": "NumPy",
            "graphql": "GraphQL",
            "rest": "REST",
            "restful": "REST",
            "soap": "SOAP",
            "microservices": "Microservices",
            "agile": "Agile",
            "scrum": "Scrum",
            "kanban": "Kanban",
        }
        
        # Skill relationships (for finding related skills)
        self.skill_relationships = {
            "Python": ["Django", "Flask", "FastAPI", "pandas", "NumPy", "scikit-learn", "PyTorch", "TensorFlow"],
            "JavaScript": ["TypeScript", "React", "Vue.js", "Angular", "Node.js", "Express.js"],
            "Java": ["Spring", "Spring Boot", "Hibernate", "Maven", "Gradle"],
            "React": ["JavaScript", "TypeScript", "Redux", "Next.js", "React Native"],
            "Django": ["Python", "Django REST Framework", "PostgreSQL", "Celery"],
            "Docker": ["Kubernetes", "Docker Compose", "Container Orchestration", "Podman"],
            "AWS": ["EC2", "S3", "Lambda", "CloudFormation", "ECS", "EKS"],
            "PostgreSQL": ["SQL", "Database Design", "Query Optimization", "MySQL", "Database"],
            "MySQL": ["SQL", "Database Design", "Query Optimization", "PostgreSQL", "Database"],
            "Machine Learning": ["Python", "TensorFlow", "PyTorch", "scikit-learn", "pandas", "NumPy"],
        }
        
        # Skill categories
        self.skill_categories = {
            "Programming Language": ["Python", "JavaScript", "Java", "C++", "C#", "Go", "Ruby", "PHP", "Swift", "Kotlin", "Rust", "TypeScript", "R", "MATLAB", "Scala", "F#"],
            "Framework": ["Django", "Flask", "FastAPI", "React", "Vue.js", "Angular", "Express.js", "Spring", "Spring Boot", "Ruby on Rails", "Laravel", "ASP.NET"],
            "Database": ["PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "Cassandra", "Oracle", "SQL Server", "SQLite", "DynamoDB", "Neo4j"],
            "DevOps": ["Docker", "Kubernetes", "Jenkins", "GitLab CI", "GitHub Actions", "Terraform", "Ansible", "Helm", "CI/CD"],
            "Cloud Platform": ["AWS", "Google Cloud", "Azure", "Heroku", "DigitalOcean"],
            "Version Control": ["Git", "GitHub", "GitLab", "Bitbucket", "SVN"],
            "Data Science": ["Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "scikit-learn", "pandas", "NumPy", "Data Analysis"],
            "Soft Skills": ["Communication", "Leadership", "Problem Solving", "Teamwork", "Agile", "Scrum", "Project Management"],
        }
        
        # Build reverse mapping for categories
        self.skill_to_category = {}
        for category, skills in self.skill_categories.items():
            for skill in skills:
                self.skill_to_category[skill] = category
    
    def normalize_skill(self, skill: str) -> str:
        """Normalize skill name to canonical form."""
        if not skill:
            return ""
        
        # Convert to lowercase for lookup
        skill_lower = skill.lower().strip()
        
        # Check if it's in our aliases
        if skill_lower in self.skill_aliases:
            return self.skill_aliases[skill_lower]
        
        # If not found, return with proper capitalization
        # Handle special cases like ASP.NET, scikit-learn
        if "." in skill or "-" in skill:
            # For unknown skills with special chars, keep original case
            return skill
        
        # Default: capitalize first letter of each word
        return skill.title()
    
    def extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills from unstructured text."""
        if not text:
            return []
        
        skills = set()
        text_lower = text.lower()
        
        # Check for each known skill (including aliases)
        all_skills = set()
        all_skills.update(self.skill_aliases.keys())
        all_skills.update(self.skill_aliases.values())
        
        # Also check skill categories
        for category_skills in self.skill_categories.values():
            all_skills.update([s.lower() for s in category_skills])
        
        for skill in all_skills:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                normalized = self.normalize_skill(skill)
                skills.add(normalized)
        
        return sorted(list(skills))
    
    def get_related_skills(self, skill: str) -> List[str]:
        """Get skills related to the given skill."""
        normalized = self.normalize_skill(skill)
        
        related = set()
        
        # Direct relationships
        if normalized in self.skill_relationships:
            related.update(self.skill_relationships[normalized])
        
        # Reverse relationships
        for key, values in self.skill_relationships.items():
            if normalized in values:
                related.add(key)
                related.update(values)
        
        # Remove the original skill
        related.discard(normalized)
        
        return sorted(list(related))
    
    def get_skill_category(self, skill: str) -> str:
        """Get the category of a skill."""
        normalized = self.normalize_skill(skill)
        return self.skill_to_category.get(normalized, "Other")
    
    def calculate_skill_similarity(
        self,
        job_skills: List[str],
        candidate_skills: List[str]
    ) -> float:
        """Calculate similarity between two skill sets."""
        if not job_skills or not candidate_skills:
            return 0.0
        
        # Normalize all skills
        job_set = {self.normalize_skill(s) for s in job_skills}
        candidate_set = {self.normalize_skill(s) for s in candidate_skills}
        
        # Direct matches
        direct_matches = len(job_set.intersection(candidate_set))
        
        # Related skill matches
        related_matches = 0
        for job_skill in job_set:
            if job_skill not in candidate_set:
                related = set(self.get_related_skills(job_skill))
                if related.intersection(candidate_set):
                    related_matches += 0.5  # Partial credit for related skills
        
        total_matches = direct_matches + related_matches
        similarity = total_matches / len(job_set)
        
        return min(1.0, similarity)
    
    def identify_transferable_skills(
        self,
        candidate_skills: List[str],
        target_role: str
    ) -> Dict[str, any]:
        """Identify transferable skills for a target role."""
        transferable = {
            "technical": [],
            "soft": [],
            "score": 0.0
        }
        
        # Normalize candidate skills
        normalized_skills = [self.normalize_skill(s) for s in candidate_skills]
        
        # Identify soft skills (always transferable)
        for skill in normalized_skills:
            if self.get_skill_category(skill) == "Soft Skills":
                transferable["soft"].append(skill)
        
        # Identify technical transferable skills
        # Version control, databases, and general concepts are often transferable
        transferable_categories = ["Version Control", "Database", "DevOps", "Cloud Platform"]
        
        for skill in normalized_skills:
            category = self.get_skill_category(skill)
            if category in transferable_categories:
                transferable["technical"].append(skill)
        
        # Calculate transferability score
        total_transferable = len(transferable["technical"]) + len(transferable["soft"])
        if normalized_skills:
            transferable["score"] = total_transferable / len(normalized_skills)
        
        return transferable
    
    def suggest_learning_path(
        self,
        current_skills: List[str],
        target_skills: List[str]
    ) -> Dict[str, List[str]]:
        """Suggest learning path from current to target skills."""
        current_set = {self.normalize_skill(s) for s in current_skills}
        target_set = {self.normalize_skill(s) for s in target_skills}
        
        # Skills already possessed
        already_have = current_set.intersection(target_set)
        
        # Skills to learn
        to_learn = target_set - current_set
        
        # Categorize skills to learn
        must_learn = []
        recommended = []
        
        for skill in to_learn:
            category = self.get_skill_category(skill)
            if category in ["Programming Language", "Framework"]:
                must_learn.append(skill)
            else:
                recommended.append(skill)
        
        # Transferable skills
        transferable = []
        for current in current_set:
            if current not in target_set:
                # Check if it's in a transferable category
                category = self.get_skill_category(current)
                if category in ["Database", "Version Control", "Soft Skills"]:
                    transferable.append(current)
        
        # Suggest learning order (languages first, then frameworks)
        learning_order = []
        
        # Learn programming languages first
        for skill in must_learn:
            if self.get_skill_category(skill) == "Programming Language":
                learning_order.append(skill)
        
        # Then frameworks
        for skill in must_learn:
            if self.get_skill_category(skill) == "Framework":
                learning_order.append(skill)
        
        # Then other skills
        learning_order.extend(recommended)
        
        return {
            "must_learn": must_learn,
            "recommended": recommended,
            "already_have": list(already_have),
            "transferable": transferable,
            "learning_order": learning_order
        }
    
    def extract_skill_requirements(self, job_description: str) -> Dict[str, any]:
        """Extract and categorize skill requirements from job description."""
        requirements = {
            "required": [],
            "nice_to_have": [],
            "categories": defaultdict(list)
        }
        
        # Split into sections
        text_lower = job_description.lower()
        
        # Find required section
        required_section = ""
        nice_to_have_section = ""
        
        if "required" in text_lower:
            parts = re.split(r'required[:\s]', text_lower, flags=re.IGNORECASE)
            if len(parts) > 1:
                required_section = parts[1].split("nice to have")[0].split("preferred")[0]
        
        if "nice to have" in text_lower or "preferred" in text_lower:
            parts = re.split(r'(?:nice to have|preferred)[:\s]', text_lower, flags=re.IGNORECASE)
            if len(parts) > 1:
                nice_to_have_section = parts[1]
        
        # Extract skills from each section
        if required_section:
            requirements["required"] = self.extract_skills_from_text(required_section)
        
        if nice_to_have_section:
            requirements["nice_to_have"] = self.extract_skills_from_text(nice_to_have_section)
        
        # If no clear sections, extract all skills
        if not requirements["required"] and not requirements["nice_to_have"]:
            all_skills = self.extract_skills_from_text(job_description)
            requirements["required"] = all_skills
        
        # Categorize all skills
        all_found_skills = requirements["required"] + requirements["nice_to_have"]
        for skill in all_found_skills:
            category = self.get_skill_category(skill)
            if skill not in requirements["categories"][category]:
                requirements["categories"][category].append(skill)
        
        # Convert defaultdict to regular dict
        requirements["categories"] = dict(requirements["categories"])
        
        return requirements
    
    def analyze_skill_gaps(
        self,
        job_skills: Dict[str, List[str]],
        candidate_skills: List[str]
    ) -> Dict[str, any]:
        """Analyze gaps between job requirements and candidate skills."""
        # Normalize all skills
        required_set = {self.normalize_skill(s) for s in job_skills.get("required", [])}
        nice_to_have_set = {self.normalize_skill(s) for s in job_skills.get("nice_to_have", [])}
        candidate_set = {self.normalize_skill(s) for s in candidate_skills}
        
        # Calculate gaps
        missing_required = list(required_set - candidate_set)
        missing_nice = list(nice_to_have_set - candidate_set)
        
        # Find related skills the candidate has
        related_skills = []
        for missing in missing_required:
            related = set(self.get_related_skills(missing))
            candidate_related = related.intersection(candidate_set)
            if candidate_related:
                for skill in candidate_related:
                    if skill not in related_skills:
                        related_skills.append(skill)
        
        # Calculate match percentage
        if required_set:
            matched_required = len(required_set.intersection(candidate_set))
            match_percentage = (matched_required / len(required_set)) * 100
        else:
            match_percentage = 100
        
        # Generate recommendations
        recommendations = []
        if missing_required:
            recommendations.append(f"Focus on learning: {', '.join(missing_required[:3])}")
        if related_skills:
            recommendations.append(f"Leverage your experience with: {', '.join(related_skills[:3])}")
        
        return {
            "missing_required": missing_required,
            "missing_nice_to_have": missing_nice,
            "related_skills": related_skills,
            "match_percentage": match_percentage,
            "recommendations": recommendations
        }