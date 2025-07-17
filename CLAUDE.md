# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a thesis project developing an AI-powered Multi-Agent System for Talent Acquisition Automation. The project aims to reduce false rejection rates in hiring processes (targeting 12-35% improvement) by using AI agents to automate resume screening and job matching.

## Development Commands

```bash
# Install dependencies (using uv package manager)
uv pip sync

# Run the main resume job predictor
python resume_job_predictor.py

# Extract job categories from dataset
python extract_categories.py

# Set required environment variable
export OPENROUTER_API_KEY="your-api-key"
```

## Current Implementation Architecture

### Proof-of-Concept Status

The project currently has a working single-model implementation that demonstrates the core concept. The full multi-agent system described in PART_3.md is not yet implemented.

### Implementation Flow

```
Entity Recognition in Resumes.jsonl
            ↓
    resume_job_predictor.py
    ├── Extract annotations (skills, education, companies, designations)
    ├── Format prompt for Google Gemini
    ├── Call OpenRouter API
    └── Predict job position
            ↓
    resume_job_predictions.csv
```

### Key Technical Details

1. **OpenRouter Integration**:

   - Model: `google/gemini-pro-1.5`
   - Temperature: 0.3 (for consistent predictions)
   - Single prediction per resume (no confidence scores yet)

2. **Data Processing**:

   - Input: JSONL with annotated resumes containing labeled entities
   - Processing: Extracts 4 entity types from annotations
   - Output: CSV with ID, extracted features, and predicted job position

3. **Job Categories**: 24 distinct categories including:
   - Technical: Java Developer, Python Developer, Data Science, DevOps Engineer
   - Business: Business Analyst, Sales, Operations Manager
   - Creative: Advocate, Arts, Designer
   - Support: HR, Accountant, Health and Fitness

## Architectural Gap Analysis

### Currently Implemented

- Basic resume parsing and entity extraction
- Single LLM-based job prediction
- CSV data pipeline

### Not Yet Implemented (from PART_3.md design)

- Multi-agent orchestration (Supervisor Agent)
- Specialized agents (Sourcing, Screening, Critic, HITL, Data-Steward)
- AgentCore infrastructure layer
- Inter-agent communication protocols
- Human-in-the-loop interfaces
- Evaluation metrics and false rejection measurement
- Bias detection and mitigation
- Explainability features

## Development Priorities

When implementing new features:

1. **Maintain research focus**: Every change should contribute to reducing false rejection rates
2. **Build toward multi-agent architecture**: New code should be modular and agent-ready
3. **Measure impact**: Add metrics to track false rejection improvements
4. **Consider ethics**: Implement bias detection for any new matching algorithms

## Data Model

### Input Format (Entity Recognition in Resumes.jsonl)

```json
{
  "id": "unique_id",
  "content": "resume text...",
  "annotation": [
    {"label": "Skills", "points": [{"start": X, "end": Y, "text": "Python"}]},
    {"label": "Designation", "points": [{"start": X, "end": Y, "text": "Software Engineer"}]}
  ]
}
```

### Output Format (resume_job_predictions.csv)

```csv
ID,Skills,Designation,Companies,Education,Predicted Job Position
```

## Technical Constraints

- No testing framework yet - implement pytest when adding tests
- No CI/CD pipeline - consider GitHub Actions when ready
- Single-threaded processing - consider batch processing for production
- No caching of API calls - implement to reduce costs during development
- No error recovery - API failures cause full script failure

## Research Alignment

Every code change should consider:

1. **False Rejection Impact**: Will this reduce the 12-35% false rejection rate?
2. **Explainability**: Can HR professionals understand why a decision was made?
3. **Bias Mitigation**: Does this introduce or reduce bias in screening?
4. **Efficiency**: Does this improve the ~23 hours per hire metric?
