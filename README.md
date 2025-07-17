# AI-Powered Multi-Agent System for Talent Acquisition Automation

A thesis project developing an intelligent system to reduce false rejection rates in hiring processes through AI-powered resume screening and job matching.

## Project Overview

This research addresses a critical problem in modern hiring: **high false rejection rates (12-35%)** in automated resume screening systems. We propose a **Human-in-the-Loop Multi-Agent System** that combines AI efficiency with human expertise to optimize the top-of-funnel screening process.

### Key Objectives

- **Primary Goal**: Reduce false rejection rates by 12-35% in initial screening
- **Secondary Goals**:
  - Improve screening efficiency while maintaining quality
  - Provide explainable AI decisions for HR professionals
  - Ensure ethical and unbiased candidate evaluation

## Problem Statement

Current Applicant Tracking Systems (ATS) suffer from two main issues:

1. **High False Rejection Rates**: 12-35% of qualified candidates are incorrectly filtered out
2. **Inefficient Screening**: HR professionals spend ~23 hours per hire on manual screening

Our solution focuses on the **top-of-funnel optimization** - improving initial resume screening accuracy rather than attempting full automation of the hiring process.

## System Architecture

### Multi-Agent System Design

The system employs specialized AI agents working collaboratively:

```
┌─────────────────┐
│   Supervisor    │ ← Orchestrates workflow
└────────┬────────┘
         │
    ┌────┴────┬──────────┬─────────┬──────────┐
    │         │          │         │          │
┌───▼───┐ ┌──▼───┐ ┌────▼───┐ ┌──▼───┐ ┌───▼────┐
│Sourcing│ │Screen│ │ Critic │ │ HITL │ │  Data  │
│ Agent  │ │Agent │ │ Agent  │ │Agent │ │Steward │
└────────┘ └──────┘ └────────┘ └──────┘ └────────┘
```

#### Core Agents

1. **Supervisor Agent**: Workflow orchestration and decision routing
2. **Sourcing Agent**: Multi-channel candidate discovery
3. **Screening Agent**: Resume analysis and job matching
4. **Critic Agent**: Quality control and bias detection
5. **HITL (Human-in-the-Loop) Agent**: Human-AI collaboration interface
6. **Data-Steward Agent**: Data management and privacy compliance

### AgentCore Infrastructure

All agents share a common runtime providing:

- **Policy Enforcement**: Authentication, rate limiting, compliance
- **Data Access Layer**: Unified database interface
- **State Management**: Workflow tracking and recovery
- **Communication Hub**: Inter-agent messaging
- **Monitoring**: Performance metrics and logging

## Getting Started

### Prerequisites

- Python >= 3.11
- uv package manager
- OpenRouter API key

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/thesis.git
cd thesis

# Install dependencies
uv pip sync

# Set up environment
export OPENROUTER_API_KEY="your-api-key"
```

### Running the Prototype

```bash
# Run the resume job predictor
python resume_job_predictor.py

# Extract job categories
python extract_categories.py
```

## Project Structure

```
thesis/
├── resume_job_predictor.py    # Main AI module prototype
├── extract_categories.py      # Data processing utility
├── pyproject.toml            # Python dependencies
├── uv.lock                   # Locked dependencies
│
├── docs/                     # Thesis documentation
│   ├── PART_1.md            # Chapter 1: Introduction
│   ├── PART_2.md            # Chapter 2: Theory (WIP)
│   ├── PART_3.md            # Chapter 3: System Design
│   └── TODO.md              # Task tracking
│
├── data/                     # Dataset files
│   ├── Entity Recognition in Resumes.jsonl
│   ├── UpdatedResumeDataSet.csv
│   └── resume_job_predictions.csv
│
└── CLAUDE.md                 # AI assistant instructions
```

## Current Progress

### Completed

- Problem space analysis and definition
- System requirements specification
- High-level multi-agent architecture design
- Use case modeling and scenarios
- Initial prototype implementation

### In Progress

- Theoretical foundation documentation (Chapter 2)
- Detailed agent implementation
- Evaluation framework design
- Integration testing

### Planned

- Complete agent system implementation
- Comprehensive testing with real datasets
- Performance evaluation against baselines
- Ethical review and bias testing

## Research Methodology

### Evaluation Metrics

- **False Rejection Rate**: Target reduction of 12-35%
- **Screening Efficiency**: Time saved per hire
- **Decision Explainability**: Quality of AI reasoning
- **Bias Detection**: Fairness across demographics

### Dataset

Using the "Entity Recognition in Resumes" dataset containing:

- Annotated resume samples
- Extracted skills, education, and experience
- Job category mappings

## Contributing

This is an academic thesis project. For questions or collaboration:

- Review [TODO.md](TODO.md) for current tasks
- Check [CLAUDE.md](CLAUDE.md) for development guidelines
- Contact the research team for specific assignments

## Documentation

- **[PART_1.md](PART_1.md)**: Introduction and problem analysis
- **[PART_2.md](PART_2.md)**: Theoretical foundation (in progress)
- **[PART_3.md](PART_3.md)**: System architecture and design
- **[IDEA.md](IDEA.md)**: Initial brainstorming and statistics
- **[DRAFT_PROBLEM_SPACE.md](DRAFT_PROBLEM_SPACE.md)**: Team problem analysis

## Academic Context

This thesis explores the intersection of:

- Multi-Agent Systems (MAS)
- Explainable AI (XAI)
- Human-in-the-Loop (HITL) systems
- HR Technology and Talent Acquisition

## License

This is an academic research project. No warranty or liability is assumed. Contact @lelouvincx and @greyy-nguyen for inquiries.

---

_"Thesis đỉnh nhất hệ mặt trời"_
