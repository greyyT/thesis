# AI-Powered Multi-Agent System for Talent Acquisition

> Thesis project: Reducing false rejection rates in automated resume screening through Human-in-the-Loop AI

## The Problem

Current ATS systems reject **12-35% of qualified candidates** due to:

- Rigid keyword matching
- Poor understanding of context
- Lack of human oversight

HR teams waste **~23 hours per hire** on manual screening.

## Our Solution

A Multi-Agent System that combines AI efficiency with human expertise for **top-of-funnel optimization**.

### Key Results

- Target: **12-35% reduction** in false rejections
- Explainable AI decisions
- Bias detection and mitigation
- Human override capability

## System Architecture

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

**Core Agents:**

- **Supervisor**: Workflow orchestration
- **Sourcing**: Multi-channel candidate discovery
- **Screening**: Resume analysis and job matching
- **Critic**: Quality control and bias detection
- **HITL**: Human-AI collaboration interface
- **Data-Steward**: Privacy compliance and logging

## Quick Start

```bash
# Prerequisites: Python 3.11+, uv package manager

# Clone and setup
git clone https://github.com/yourusername/thesis.git
cd thesis

# Install dependencies
uv pip sync

# Configure environment
export OPENROUTER_API_KEY="your-api-key"

# Run prototype
python resume_job_predictor.py
```

## Project Structure

```
thesis/
├── src/                      # Core implementation
│   ├── resume_job_predictor.py
│   └── extract_categories.py
├── docs/                     # Documentation
│   ├── PART_1.md            # Introduction
│   ├── PART_2.md            # Theory (WIP)
│   └── PART_3.md            # System Design
├── data/                     # Datasets
└── CLAUDE.md                 # Development guide
```

## Current Status

✅ **Completed**

- Problem analysis and system requirements
- Multi-agent architecture design
- Initial prototype (single-model proof of concept)

🚧 **In Progress**

- Full multi-agent implementation
- Evaluation framework
- Integration testing

📋 **Planned**

- Large-scale dataset validation
- Performance benchmarking
- Ethical review and bias testing

## Research Approach

**Methodology**: Design Science Research with CRISP-DM  
**Dataset**: Entity Recognition in Resumes (annotated samples)  
**Evaluation Metrics**:

- False rejection rate reduction
- Screening time efficiency
- Decision explainability score
- Demographic fairness metrics

## Documentation

- [Introduction & Problem Analysis](PART_1.md)
- [System Architecture & Design](PART_3.md)
- [Development Guidelines](CLAUDE.md)
- [Task Tracking](TODO.md)

## Contributing

Academic thesis project. For collaboration:

- Review current tasks in [TODO.md](TODO.md)
- Follow guidelines in [CLAUDE.md](CLAUDE.md)
- Contact: @lelouvincx, @greyy-nguyen

## License

Academic research project. No warranty implied.

---

_"Optimizing talent acquisition through intelligent automation"_
