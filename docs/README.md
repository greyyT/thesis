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

# Run scripts from the scripts directory
cd src/scripts
uv run python resume_job_predictor.py
```

## Project Structure

```
thesis/
├── src/                              # Source code
│   ├── data/                         # All datasets
│   │   ├── Entity Recognition in Resumes.jsonl
│   │   ├── UpdatedResumeDataSet.csv
│   │   ├── candidates.csv
│   │   ├── resume_job_predictions.csv
│   │   ├── updated_dataset_predictions_async.csv
│   │   └── unified_resume_predictions.csv
│   │
│   ├── scripts/                      # Python scripts
│   │   ├── resume_job_predictor.py  # Main resume processing
│   │   ├── extract_categories.py    # Category extraction
│   │   ├── extract_from_updated_dataset_async.py  # Async processing
│   │   └── unify_datasets.py        # Dataset unification
│   │
│   └── notebooks/                    # Jupyter notebooks
│       └── poc.ipynb                # Proof of concept
│
├── docs/                             # Documentation
│   ├── README.md                    # This file
│   ├── CLAUDE.md                    # Development guide
│   ├── PART_1.md                    # Introduction
│   ├── PART_2.md                    # Theory (WIP)
│   ├── PART_3.md                    # System Design
│   ├── PART_4.md                    # Requirements
│   ├── PART_5.md                    # Implementation (WIP)
│   └── TODO.md                      # Task tracking
│
├── media/                            # Images and diagrams
├── distinct_categories.txt           # Job categories list
├── pyproject.toml                   # Project dependencies
└── uv.lock                          # Dependency lock file
```

## Current Status

✅ **Completed**

- Problem analysis and system requirements
- Multi-agent architecture design
- Initial prototype (single-model proof of concept)
- Async processing implementation for batch operations
- Dataset unification tool for multiple data sources

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

## Key Scripts

- **`resume_job_predictor.py`**: Processes annotated resumes from JSONL, extracts features, and predicts job positions using OpenRouter API
- **`extract_from_updated_dataset_async.py`**: Async processing for UpdatedResumeDataSet.csv with concurrent API calls (5x faster)
- **`unify_datasets.py`**: Combines multiple resume datasets into a unified format for analysis
- **`extract_categories.py`**: Extracts unique job categories from the dataset

## Documentation

- [Introduction & Problem Analysis](PART_1.md)
- [System Architecture & Design](PART_3.md)
- [System Requirements](PART_4.md)
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
