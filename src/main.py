"""Main entry point for Chainlit UI."""
import chainlit as cl
from typing import Optional
from openai import AsyncOpenAI

from agents.unified_agent import UnifiedRecruitmentAgent, EvaluationResult
from config import get_config

# Initialize configuration
config = get_config()

# Initialize OpenAI client
openai_client = AsyncOpenAI(api_key=config["openai_api_key"])

# Global agent instance (will be initialized on chat start)
agent: Optional[UnifiedRecruitmentAgent] = None


@cl.on_chat_start
async def start():
    """Initialize the chat session."""
    global agent
    
    # Show welcome message
    await cl.Message(
        content="# 🎯 AI Recruitment Assistant\n\n"
        "Welcome! I'm here to help evaluate candidates against job descriptions.\n\n"
        "**How to use:**\n"
        "1. Upload a job description file (or paste it)\n"
        "2. Upload a resume/CV file (or paste it)\n"
        "3. Type 'evaluate' to start the analysis\n"
        "4. Or type 'demo' to see a sample evaluation\n\n"
        "Ready to begin!"
    ).send()
    
    # Initialize the agent
    try:
        agent = UnifiedRecruitmentAgent(config, openai_client)
        await agent.initialize()
        
        # Store in session
        cl.user_session.set("agent", agent)
        cl.user_session.set("job_description", None)
        cl.user_session.set("resume", None)
        
        await cl.Message(
            content="✅ System initialized successfully!"
        ).send()
        
    except Exception as e:
        await cl.Message(
            content=f"❌ Error initializing system: {str(e)}\n\n"
            "Please check your configuration and try again."
        ).send()


@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages."""
    # Get stored data
    job_desc = cl.user_session.get("job_description")
    resume = cl.user_session.get("resume")
    
    # Handle commands
    if message.content.lower() == "demo":
        await run_demo_evaluation()
        return
    
    elif message.content.lower() == "evaluate":
        if job_desc and resume:
            await evaluate_candidate(job_desc, resume)
        else:
            await cl.Message(
                content="⚠️ Please upload both a job description and a resume first!"
            ).send()
        return
    
    elif message.content.lower() == "clear":
        cl.user_session.set("job_description", None)
        cl.user_session.set("resume", None)
        await cl.Message(
            content="🗑️ Cleared stored documents. Ready for new uploads!"
        ).send()
        return
    
    elif message.content.lower() == "help":
        await show_help()
        return
    
    # Handle file uploads
    if message.elements:
        await process_file_uploads(message.elements)
        return
    
    # Handle text input as job description or resume
    if message.content.strip():
        await handle_text_input(message.content)
        return
    
    # Default response
    await cl.Message(
        content="Please upload files or type 'help' for more information."
    ).send()


async def process_file_uploads(elements):
    """Process uploaded files."""
    job_desc = cl.user_session.get("job_description")
    resume = cl.user_session.get("resume")
    
    for element in elements:
        if element.type == "file":
            # Read file content
            with open(element.path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Determine file type based on name
            if "job" in element.name.lower() or "jd" in element.name.lower():
                cl.user_session.set("job_description", content)
                await cl.Message(
                    content=f"📋 Job description uploaded: {element.name}"
                ).send()
            elif "resume" in element.name.lower() or "cv" in element.name.lower():
                cl.user_session.set("resume", content)
                await cl.Message(
                    content=f"📄 Resume uploaded: {element.name}"
                ).send()
            else:
                # Ask user to specify
                res = await cl.AskActionMessage(
                    content=f"What type of document is '{element.name}'?",
                    actions=[
                        cl.Action(name="job", value="job", label="Job Description"),
                        cl.Action(name="resume", value="resume", label="Resume/CV")
                    ]
                ).send()
                
                if res and res.get("value") == "job":
                    cl.user_session.set("job_description", content)
                    await cl.Message(content="📋 Stored as job description").send()
                elif res and res.get("value") == "resume":
                    cl.user_session.set("resume", content)
                    await cl.Message(content="📄 Stored as resume").send()
    
    # Check if both documents are ready
    job_desc = cl.user_session.get("job_description")
    resume = cl.user_session.get("resume")
    
    if job_desc and resume:
        await cl.Message(
            content="✅ Both documents uploaded! Type 'evaluate' to start the analysis."
        ).send()


async def handle_text_input(text: str):
    """Handle pasted text input."""
    job_desc = cl.user_session.get("job_description")
    resume = cl.user_session.get("resume")
    
    # Try to detect what type of text this is
    if not job_desc and any(keyword in text.lower() for keyword in ["requirements", "responsibilities", "qualifications", "position", "role"]):
        cl.user_session.set("job_description", text)
        await cl.Message(
            content="📋 Stored as job description. Now please provide the resume."
        ).send()
    elif not resume and any(keyword in text.lower() for keyword in ["experience", "education", "skills", "email", "phone"]):
        cl.user_session.set("resume", text)
        await cl.Message(
            content="📄 Stored as resume. Type 'evaluate' to start the analysis."
        ).send()
    else:
        # Ask user to specify
        res = await cl.AskActionMessage(
            content="What type of document is this?",
            actions=[
                cl.Action(name="job", value="job", label="Job Description"),
                cl.Action(name="resume", value="resume", label="Resume/CV"),
                cl.Action(name="cancel", value="cancel", label="Cancel")
            ]
        ).send()
        
        if res and res.get("value") == "job":
            cl.user_session.set("job_description", text)
            await cl.Message(content="📋 Stored as job description").send()
        elif res and res.get("value") == "resume":
            cl.user_session.set("resume", text)
            await cl.Message(content="📄 Stored as resume").send()


async def evaluate_candidate(job_desc: str, resume: str):
    """Run the evaluation and display results with enhanced loading indicators."""
    import asyncio
    
    agent = cl.user_session.get("agent")
    
    if not agent:
        await cl.Message(
            content="❌ System not initialized. Please refresh the page."
        ).send()
        return
    
    # Show enhanced loading message
    loading_msg = cl.Message(content="🚀 **Starting Evaluation Process**\n\n🔄 Initializing AI agents...")
    await loading_msg.send()
    
    try:
        # Step 1: Job requirement analysis
        await loading_msg.update(
            content="🚀 **Starting Evaluation Process**\n\n"
            "📋 **Step 1/4**: Analyzing job requirements...\n"
            "🔄 Breaking down skills, experience, and qualifications"
        )
        await asyncio.sleep(0.5)  # Small delay for better UX
        
        # Step 2: Resume parsing
        await loading_msg.update(
            content="🚀 **Starting Evaluation Process**\n\n"
            "✅ **Step 1/4**: Job requirements analyzed\n"
            "👤 **Step 2/4**: Parsing candidate resume...\n"
            "🔄 Extracting skills, experience, and background"
        )
        await asyncio.sleep(0.5)
        
        # Step 3: Semantic matching
        await loading_msg.update(
            content="🚀 **Starting Evaluation Process**\n\n"
            "✅ **Step 1/4**: Job requirements analyzed\n"
            "✅ **Step 2/4**: Resume parsed successfully\n"
            "🧠 **Step 3/4**: Running AI-powered matching...\n"
            "🔄 Comparing skills and calculating compatibility"
        )
        
        # Run evaluation
        result = await agent.process_job_application(
            job_description=job_desc,
            resume_text=resume,
            job_id="JOB_001",
            candidate_id="CAND_001"
        )
        
        # Step 4: Final analysis
        await loading_msg.update(
            content="🚀 **Starting Evaluation Process**\n\n"
            "✅ **Step 1/4**: Job requirements analyzed\n"
            "✅ **Step 2/4**: Resume parsed successfully\n"
            "✅ **Step 3/4**: AI matching completed\n"
            "🎯 **Step 4/4**: Generating final report...\n"
            "🔄 Preparing comprehensive analysis"
        )
        await asyncio.sleep(0.3)
        
        # Format and display results
        await loading_msg.update(content=format_evaluation_results(result))
        
        # If human review is needed, show additional info
        if result.needs_review:
            await show_review_details(result)
            
    except Exception as e:
        await loading_msg.update(
            content=f"❌ **Evaluation Failed**\n\n"
            f"Error: {str(e)}\n\n"
            "Please try again or contact support if the issue persists."
        )


def format_evaluation_results(result: EvaluationResult) -> str:
    """Format evaluation results for display with enhanced styling."""
    confidence_emoji = "🟢" if result.confidence > 0.85 else "🟡" if result.confidence > 0.65 else "🔴"
    decision_emoji = "✅" if not result.needs_review else "👤"
    
    # Create confidence bar
    confidence_bar = create_confidence_bar(result.confidence)
    screening_bar = create_score_bar(result.screening_score, "Screening")
    critic_bar = create_score_bar(result.critic_score, "Critic")
    
    return f"""# 📊 **Recruitment Evaluation Report**

---

## 🎯 **Overall Assessment**

### Confidence Level
{confidence_emoji} **{result.confidence:.1%}** {confidence_bar}

### Scores Breakdown
🔍 **Screening Score**: {result.screening_score:.1%} {screening_bar}
🔎 **Critic Review**: {result.critic_score:.1%} {critic_bar}

### Final Decision
{decision_emoji} **{"PROCEED TO NEXT ROUND" if not result.needs_review else "HUMAN REVIEW REQUIRED"}**

---

## 📋 **Key Findings**
{result.explanation}

---

## 🎯 **Skill Analysis Dashboard**

### ✅ **Matched Skills** ({len(result.matched_skills)} found)
{format_matched_skills(result.matched_skills)}

### ❌ **Missing Skills** ({len(result.missing_skills)} gaps)
{format_missing_skills(result.missing_skills)}

### 🔄 **Transferable Skills** ({len(result.transferable_skills)} identified)
{format_transferable_skills(result.transferable_skills)}

---

## 🛡️ **Bias Detection Report**
{format_bias_flags(result.bias_flags)}

---
*Report generated by AI-powered Multi-Agent Recruitment System*
"""


def create_confidence_bar(confidence: float) -> str:
    """Create a visual confidence bar."""
    filled = int(confidence * 10)
    bar = "🟩" * filled + "⬜" * (10 - filled)
    return f"`{bar}`"


def create_score_bar(score: float, label: str = "") -> str:
    """Create a visual score bar."""
    filled = int(score * 10)
    if score >= 0.8:
        filled_char = "🟩"
    elif score >= 0.6:
        filled_char = "🟨"
    else:
        filled_char = "🟥"
    
    bar = filled_char * filled + "⬜" * (10 - filled)
    return f"`{bar}`"


def format_matched_skills(matched_skills):
    """Format matched skills for display with enhanced styling."""
    if not matched_skills:
        return "🎉 **No specific requirements - all good!**"
    
    lines = []
    for i, skill in enumerate(matched_skills[:5], 1):  # Show top 5
        confidence = skill.get('confidence', 1.0)
        required = skill.get('required', 'Unknown')
        found = skill.get('found', required)
        
        # Choose emoji based on confidence
        if confidence >= 0.95:
            emoji = "🎯"
            status = "Perfect Match"
        elif confidence >= 0.85:
            emoji = "✅"
            status = "Strong Match"
        elif confidence >= 0.75:
            emoji = "✓"
            status = "Good Match"
        else:
            emoji = "⚡"
            status = "Partial Match"
        
        confidence_bar = create_score_bar(confidence)
        
        lines.append(
            f"**{i}.** {emoji} **{required}**\n"
            f"   └ Found: `{found}` ({status}: {confidence:.0%}) {confidence_bar}"
        )
    
    if len(matched_skills) > 5:
        lines.append(f"\n📊 **+{len(matched_skills) - 5} more skills matched** (showing top 5)")
    
    return "\n\n".join(lines) if lines else "No matches found"


def format_missing_skills(missing_skills):
    """Format missing skills for display with enhanced styling."""
    if not missing_skills:
        return "🎉 **All requirements met!** No skills gaps identified."
    
    lines = []
    for i, skill in enumerate(missing_skills[:5], 1):
        lines.append(f"**{i}.** ❌ **{skill}**\n   └ *Consider training or hiring for this skill*")
    
    if len(missing_skills) > 5:
        lines.append(f"\n⚠️ **+{len(missing_skills) - 5} more skills needed** (showing top 5)")
    
    return "\n\n".join(lines)


def format_transferable_skills(transferable_skills):
    """Format transferable skills for display with enhanced styling."""
    if not transferable_skills:
        return "🔍 **No transferable skills identified**\n   └ *Candidate skills closely match requirements*"
    
    lines = []
    for i, skill in enumerate(transferable_skills[:3], 1):
        from_skill = skill.get('from', 'N/A')
        to_skill = skill.get('to', 'N/A')
        confidence = skill.get('confidence', skill.get('relevance', 0.8))
        
        # Choose emoji based on confidence
        if confidence >= 0.9:
            emoji = "🔄"
            status = "Highly Transferable"
        elif confidence >= 0.75:
            emoji = "↗️"
            status = "Good Transfer"
        else:
            emoji = "⚡"
            status = "Potential Transfer"
        
        confidence_bar = create_score_bar(confidence)
        
        lines.append(
            f"**{i}.** {emoji} **{from_skill}** → **{to_skill}**\n"
            f"   └ {status} ({confidence:.0%}) {confidence_bar}"
        )
    
    if len(transferable_skills) > 3:
        lines.append(f"\n🔍 **+{len(transferable_skills) - 3} more transferable skills** (showing top 3)")
    
    return "\n\n".join(lines)


def format_bias_flags(bias_flags):
    """Format bias detection results with enhanced styling."""
    if not bias_flags:
        return "✅ **No bias indicators detected**\n   └ *Evaluation appears fair and unbiased*"
    
    bias_explanations = {
        "non_traditional_education": "Alternative education path (bootcamp, online courses)",
        "career_gaps": "Gaps in employment history detected",
        "career_changer": "Transitioning from different field/industry",
        "age_bias": "Potential age-related bias in evaluation",
        "gender_bias": "Potential gender-related bias detected",
        "name_bias": "Potential bias based on name/ethnicity"
    }
    
    lines = []
    for i, flag in enumerate(bias_flags, 1):
        explanation = bias_explanations.get(flag, "Bias pattern detected")
        formatted_flag = flag.replace('_', ' ').title()
        
        lines.append(
            f"**{i}.** ⚠️ **{formatted_flag}**\n"
            f"   └ *{explanation}*"
        )
    
    result = "\n\n".join(lines)
    result += f"\n\n🛡️ **Recommendation**: Consider human review to ensure fair evaluation."
    
    return result


async def show_review_details(result: EvaluationResult):
    """Show additional details for human review."""
    review_msg = f"""## 👤 Human Review Required

**Review Type**: {result.review_type.replace('_', ' ').title()}
**Priority**: {result.review_priority.upper()}

**Why this needs review:**
"""
    
    reasons = []
    if result.confidence < 0.85:
        reasons.append(f"- Low confidence score ({result.confidence:.1%})")
    
    if abs(result.screening_score - result.critic_score) > 0.15:
        reasons.append(f"- Large score discrepancy ({abs(result.screening_score - result.critic_score):.1%})")
    
    if result.bias_flags:
        reasons.append(f"- Potential bias detected in {len(result.bias_flags)} areas")
    
    if result.review_type == "deep":
        reasons.append("- Candidate may be a hidden gem")
    
    review_msg += "\n".join(reasons)
    
    await cl.Message(content=review_msg).send()


async def run_demo_evaluation():
    """Run a demonstration with sample data."""
    demo_job = """
    Senior Python Developer
    
    We are looking for an experienced Python developer to join our team.
    
    Requirements:
    - 5+ years of Python development experience
    - Strong knowledge of FastAPI, Django, or Flask
    - Experience with microservices architecture
    - Understanding of ML/AI concepts
    - AWS or cloud platform experience
    - Bachelor's degree in Computer Science or related field
    
    Nice to have:
    - Open source contributions
    - Experience with Docker and Kubernetes
    - Knowledge of React or Vue.js
    """
    
    demo_resume = """
    Jane Smith
    Email: jane.smith@email.com | GitHub: github.com/janesmith
    
    SUMMARY
    Experienced software engineer with 6 years building scalable web applications.
    Self-taught programmer who transitioned from data analysis to full-stack development.
    
    SKILLS
    Programming: Python, JavaScript, SQL
    Frameworks: FastAPI, Express.js, React
    Tools: Docker, Git, Jenkins, AWS EC2/S3/Lambda
    Concepts: RESTful APIs, Microservices, Machine Learning basics
    
    EXPERIENCE
    Senior Developer | TechStartup Inc. | 2021-Present
    - Architected microservices platform handling 1M+ daily requests
    - Reduced API response time by 60% through optimization
    - Mentored team of 3 junior developers
    
    Full Stack Developer | DataCorp | 2019-2021  
    - Built customer analytics dashboard using Python/React
    - Implemented ML models for customer churn prediction
    - Deployed applications on AWS with 99.9% uptime
    
    Data Analyst | FinanceGlobal | 2018-2019
    - Automated reporting with Python scripts
    - Created data pipelines processing 500GB+ daily
    
    EDUCATION
    Data Science Bootcamp | DataCamp | 2018
    B.A. Economics | State University | 2017
    
    PROJECTS
    - Contributed to popular open-source Python ORM (500+ stars)
    - Built personal finance tracker with FastAPI backend
    """
    
    # Store demo data
    cl.user_session.set("job_description", demo_job)
    cl.user_session.set("resume", demo_resume)
    
    await cl.Message(
        content="🎭 Demo mode: Loaded sample job description and resume.\n"
        "Running evaluation..."
    ).send()
    
    # Run evaluation
    await evaluate_candidate(demo_job, demo_resume)


async def show_help():
    """Show help information."""
    help_text = """# 📚 Help Guide

## Quick Start
1. **Upload Documents**: Drag and drop or paste your job description and resume
2. **Run Evaluation**: Type 'evaluate' to analyze the match
3. **View Results**: See detailed scoring, skill matching, and recommendations

## Commands
- `evaluate` - Run evaluation on uploaded documents
- `demo` - See a sample evaluation with pre-loaded data
- `clear` - Clear uploaded documents
- `help` - Show this help message

## Understanding Results
- **Screening Score**: Traditional keyword and requirement matching
- **Critic Score**: Advanced analysis including transferable skills
- **Confidence**: How certain the system is about its evaluation
- **Human Review**: Required when confidence is low or special cases detected

## Tips
- Upload clear, well-formatted job descriptions
- Include complete resumes with skills and experience
- The system detects transferable skills and hidden gems
- Bias detection helps ensure fair evaluation
"""
    
    await cl.Message(content=help_text).send()


if __name__ == "__main__":
    # This file should be run with: chainlit run src/main.py
    pass