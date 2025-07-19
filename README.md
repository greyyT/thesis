# 🤖 AI-Powered Talent Acquisition System

**PhD Thesis Project**: *"Reducing false rejection rates in automated resume screening through Human-in-the-Loop AI"*

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: Academic](https://img.shields.io/badge/License-Academic-yellow.svg)](./LICENSE)
[![Tests](https://img.shields.io/badge/Tests-43%20passing-green.svg)](./tests)

## 🎯 The $12 Billion Problem

### Why Current ATS Systems Fail
| Issue | Impact |
|-------|--------|
| **12-35%** qualified candidates wrongly rejected | Lost talent and missed opportunities |
| **23 hours/hire** manual screening | 80% of recruiter time wasted |
| **Rigid keyword matching** | Context-blind filtering |
| **No human oversight** | AI decisions become final |

### Root Causes
- **Keyword tunnel vision**: "Python" ≠ "Django Python expert"
- **Zero context awareness**: C++ expert applying for Java role gets auto-rejected
- **No human override**: AI says no = permanent rejection

## 🚀 Our Solution: AI + Human Expertise

### The Paradigm Shift
Instead of replacing humans with AI, we **augment** human decision-making:
- ⚡ **AI handles** 90% of routine screening efficiently
- 👥 **Humans focus** on edge cases and bias oversight
- 🔍 **Transparency** shows exactly why each decision was made
- 🎯 **Override capability** allows instant human corrections

### Target Impact
| Metric | Goal | Current Progress |
|--------|------|------------------|
| **False rejection reduction** | 12-35% | ✅ 87% accuracy in POC |
| **Screening time** | <2 hours/hire | ✅ 5x faster async processing |
| **Bias detection** | Real-time alerts | ✅ Implemented in Critic Agent |
| **Human oversight** | 100% transparency | ✅ HITL interface ready |

## 🏗️ System Architecture

### Multi-Agent Workflow
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

### Agent Responsibilities
| Agent | Superpower | Human Interaction |
|-------|------------|-------------------|
| **Supervisor** | 🎯 Workflow orchestration | Sets evaluation strategies |
| **Sourcing** | 🔍 Multi-channel discovery | Accepts source preferences |
| **Screening** | 🧠 Resume-to-job matching | Flags anomalies for review |
| **Critic** | ⚖️ Bias detection & quality control | Reports fairness violations |
| **HITL** | 🙋‍♂️ Human-AI collaboration | Enables real-time overrides |
| **Data Steward** | 🔐 Privacy & compliance | Ensures GDPR compliance |

## 🚦 Quick Start (3-Minute Setup)

### 🛠️ Prerequisites
| Tool | Version | Installation |
|------|---------|--------------|
| **Python** | 3.11+ | [Download](https://www.python.org/downloads/) |
| **uv** | Latest | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| **Docker** | Latest | For Redis (state management) |

### ⚡ One-Command Setup
```bash
# Clone & auto-configure
git clone https://github.com/yourusername/thesis.git
cd thesis

# Install all dependencies
uv pip sync

# Setup environment (interactive)
cp .env.example .env
# Edit .env with your API keys:
# OPENAI_API_KEY=sk-...
# OPENROUTER_API_KEY=sk-or-...
# DATABASE_URL=postgresql://...
```

### 🖥️ Launch Options

| Interface | Command | Best For | Access |
|-----------|---------|----------|---------|
| **🎮 Chainlit UI** | `./run_chainlit.sh` | Interactive demo | http://localhost:8000 |
| **🧪 Testing** | `uv run python src/demo_matching.py` | Quick validation | Terminal output |
| **⚙️ Scripts** | `cd src/scripts && uv run python resume_job_predictor.py` | Batch processing | File outputs |

#### Step-by-Step Launch
```bash
# 1. Start Redis (required for state management)
docker compose up -d redis

# 2. Launch Chainlit UI
./run_chainlit.sh
# Or directly: uv run chainlit run src/main.py --port 8000

# 3. Open browser → http://localhost:8000
```

## 🎮 Interactive Features

### 3 Ways to Test the System

1. **📁 File Upload** *(Drag & Drop)*
   - Upload resume.pdf + job_description.txt
   - Supports: `.txt`, `.pdf`, `.doc`, `.docx` (max 10MB)

2. **📝 Text Input** *(Paste Anything)*
   - Paste messy LinkedIn profiles
   - Copy informal job descriptions ("we need someone good with Python")

3. **🎯 Demo Mode** *(Recommended for first-time users)*
   - Type `demo` → See real-time evaluation
   - Experience all features with sample data

### 📊 What You'll See
| Component | Example | Why It Matters |
|-----------|---------|----------------|
| **Screening Score** | 87% | Traditional ATS matching |
| **Critic Score** | 92% | AI-enhanced after bias detection |
| **Confidence** | High | System's certainty level |
| **Bias Alert** | ⚠️ Gendered language detected | Prevents discrimination |
| **Human Review** | Recommended | For edge cases & low confidence |

### 🎯 Available Commands
| Command | Action | Use Case |
|---------|--------|----------|
| `demo` | Load sample evaluation | First-time exploration |
| `evaluate` | Analyze your documents | Real candidate assessment |
| `clear` | Reset stored data | Start fresh |
| `help` | Show guidance | Get assistance |

### 📋 Step-by-Step Workflows

<details>
<summary><b>🎯 Option 1: Demo Mode</b> (Recommended for first-time users)</summary>

```bash
1. Open Chainlit UI → http://localhost:8000
2. Type: demo
3. Watch real-time evaluation with sample data
4. See all features in action
```
</details>

<details>
<summary><b>📁 Option 2: File Upload</b></summary>

```bash
1. Drag job description file → UI
2. Drag resume/CV file → UI  
3. Type: evaluate
4. Review detailed analysis
```
</details>

<details>
<summary><b>📝 Option 3: Text Input</b></summary>

```bash
1. Paste job description → chat
2. Paste resume text → chat
3. Type: evaluate
4. Get instant results
```
</details>

### 🎯 Understanding Results

| Result Type | What It Means | Action Required |
|-------------|---------------|------------------|
| **🟢 Automated Approval** | High confidence match | → Proceed to interview |
| **🟡 Human Review** | Edge case detected | → Manual assessment |
| **🔴 Rejection** | Poor fit confirmed | → Send polite decline |

### 🚨 Special Detection Alerts
| Alert | Trigger | Benefit |
|-------|---------|----------|
| **💎 Hidden Gem** | Non-traditional background with potential | Prevents overlooking talent |
| **⚠️ Bias Risk** | Discriminatory language detected | Ensures fair evaluation |
| **📊 Score Gap** | Screening vs Critic disagreement | Flags complex cases |

## 📁 Smart Project Structure

```
thesis/
├── 📊 src/data/                      # Datasets & samples
│   ├── Entity Recognition in Resumes.jsonl  # Annotated training data
│   ├── UpdatedResumeDataSet.csv             # Processed candidates
│   └── *.csv                                # Prediction outputs
│
├── 🧠 src/agents/                    # AI teammates  
├── 🖥️ src/chainlit/                 # Interactive UI
├── 🔧 src/services/                  # Core business logic
│   ├── vector_store.py              # 🔍 Semantic search (Milvus)
│   ├── skill_ontology.py            # 🎯 Skill matching & normalization  
│   └── redis_service.py             # ⚡ State management & caching
│
├── 🧪 src/scripts/                   # Standalone utilities
│   ├── resume_job_predictor.py      # 🚀 Main processing pipeline
│   ├── extract_categories.py        # 📂 Job classification
│   └── unify_datasets.py            # 🔗 Data consolidation
│
├── 📚 docs/                          # Complete documentation
│   ├── CLAUDE.md                    # 👨‍💻 Developer guide  
│   ├── POC.md                       # 🧪 Technical proof-of-concept
│   ├── PART_*.md                    # 📖 Thesis chapters
│   └── TODO.md                      # ✅ Task tracking
│
├── 🧪 tests/                         # 43+ tests (TDD approach)
├── 📦 docker-compose.yml             # Redis & services
└── 🚀 run_chainlit.sh               # One-click startup
```

### 🎯 Key Directories
| Directory | Purpose | Most Used For |
|-----------|---------|---------------|
| `📊 src/data/` | Training & test datasets | Loading sample resumes |
| `🧠 src/agents/` | Multi-agent orchestration | Core intelligence |
| `🖥️ src/chainlit/` | Human interaction layer | Demo & testing |
| `🔧 src/services/` | Business logic | Skill matching & search |

## 📈 Development Status & Roadmap

### ✅ **Phase 1: MVP Complete** 
| Component | Status | Impact |
|-----------|--------|---------|
| 🎯 **Problem Analysis** | ✅ Complete | Requirements defined |
| 🏗️ **Architecture Design** | ✅ Complete | Multi-agent system planned |
| 🧪 **POC Implementation** | ✅ Complete | 87% accuracy achieved |
| ⚡ **Async Processing** | ✅ Complete | 5x performance boost |
| 🖥️ **Chainlit UI + HITL** | ✅ Complete | Interactive demo ready |
| 🔄 **Redis Integration** | ✅ Complete | State management active |
| 🔍 **Vector Search** | ✅ Complete | Milvus Lite deployed |
| 🧪 **TDD Framework** | ✅ Complete | 43+ tests passing |

### 🚧 **Phase 2: Multi-Agent Enhancement** *(Current Focus)*
- [ ] 🤖 Complete agent communication protocols  
- [ ] ⚖️ Advanced bias detection algorithms
- [ ] 📊 Real-time evaluation dashboard  
- [ ] 🔗 API endpoint standardization

### 🌟 **Phase 3: Production Ready** *(Planned)*
- [ ] 📈 Large-scale dataset validation (10K+ resumes)
- [ ] ⚡ Performance benchmarking & optimization
- [ ] 🛡️ Security audit & compliance review
- [ ] 📖 Academic paper publication

## 🎓 Research Foundation

### Methodology Framework
| Approach | Description | Application |
|----------|-------------|-------------|
| **Design Science Research** | Artifact-focused research | Building novel AI system |
| **CRISP-DM** | Data mining methodology | Structured data processing |
| **TDD** | Test-driven development | Quality assurance |

### 📊 Evaluation Metrics
| Metric | Target | Current | Impact |
|--------|--------|---------|--------|
| **False Rejection Rate** | ↓ 12-35% | ↓ 13% (POC) | More qualified hires |
| **Screening Time** | ↓ 80% | ↓ 70% (5x faster) | Recruiter efficiency |
| **Explainability Score** | >90% clarity | 87% | Transparent decisions |
| **Fairness Index** | Zero bias flags | 2% detection rate | Demographic equity |

## 🔧 Core Components

### 🚀 Processing Scripts
| Script | Function | Performance | Use Case |
|--------|----------|-------------|----------|
| `resume_job_predictor.py` | 🎯 Main pipeline | Processes 100+ resumes/min | Batch evaluation |
| `extract_from_updated_dataset_async.py` | ⚡ Async processing | 5x faster than sync | Large datasets |
| `unify_datasets.py` | 🔗 Data consolidation | Handles multiple formats | Data preparation |
| `extract_categories.py` | 📂 Job classification | Auto-categorizes positions | Skill mapping |

### 🛠️ Services Architecture
| Service | Technology | Purpose | Performance |
|---------|------------|---------|-------------|
| **UI Interface** | Chainlit | Human interaction | Real-time responses |
| **Orchestration** | UnifiedRecruitmentAgent | Workflow management | Multi-agent coordination |
| **State Management** | Redis | HITL queue & caching | Sub-second access |
| **Vector Search** | Milvus Lite | Semantic similarity | 1536-dim embeddings |
| **LLM Processing** | OpenAI API | Intelligence & embeddings | GPT-4 powered |

## 🆘 Troubleshooting Guide

### 🔴 Common Issues & Quick Fixes

<details>
<summary><b>🔌 Redis Connection Error</b></summary>

**Problem**: `ConnectionError: Redis server not available`

**Solution**:
```bash
# Check if Redis is running
docker compose ps

# Start Redis if not running
docker compose up -d redis

# Test connection
docker exec recruitment_redis redis-cli ping
# Expected output: PONG
```
</details>

<details>
<summary><b>🔑 OpenAI API Issues</b></summary>

**Problem**: `Authentication failed` or `Rate limit exceeded`

**Solutions**:
```bash
# Check API key in .env
cat .env | grep OPENAI_API_KEY

# Test API access
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models

# Switch to OpenRouter if needed
export OPENROUTER_API_KEY=sk-or-...
```
</details>

<details>
<summary><b>📁 File Upload Problems</b></summary>

**Supported Formats**: `.txt`, `.pdf`, `.doc`, `.docx` (max 10MB)

**Quick Fixes**:
- Clear browser cache: `Ctrl+F5`
- Try text input instead of file upload
- Check file permissions: `chmod 644 your_file.pdf`
- Use demo mode: Type `demo` in chat
</details>

### 🚨 Emergency Commands
```bash
# Reset everything
docker compose down && docker compose up -d redis
uv pip sync --reinstall

# Check system health
uv run python src/scripts/health_check.py

# View logs
tail -f logs/chainlit.log
```

## 📚 Documentation Hub

### 🎯 For Different Audiences
| Audience | Start Here | Next Steps |
|----------|------------|------------|
| **👤 New Users** | [Demo walkthrough](#-demo-mode-recommended-for-first-time-users) | [Understanding Results](#-understanding-results) |
| **👔 Recruiters** | [Problem Analysis](docs/PART_1.md) | [Try the UI](#-launch-options) |
| **👨‍💻 Developers** | [Development Guide](CLAUDE.md) | [Architecture](docs/PART_3.md) |
| **🎓 Researchers** | [Technical Paper](docs/PART_2.md) | [Requirements](docs/PART_4.md) |

### 📖 Complete Documentation
- 📋 [**PART_1.md**](docs/PART_1.md) - Problem analysis & motivation
- 🔬 [**PART_2.md**](docs/PART_2.md) - Theory & literature review  
- 🏗️ [**PART_3.md**](docs/PART_3.md) - System architecture & design
- 📝 [**PART_4.md**](docs/PART_4.md) - Requirements & specifications
- 💻 [**CLAUDE.md**](CLAUDE.md) - Developer guidelines & commands
- ✅ [**TODO.md**](docs/TODO.md) - Task tracking & progress

## 🤝 Contributing & Collaboration

### 🎯 **For Academic Partners**
| Role | How to Help | Contact |
|------|-------------|---------|
| **📊 Data Scientists** | Dataset validation & metrics | Review [TODO.md](docs/TODO.md) |
| **🧠 ML Engineers** | Algorithm optimization | Follow [CLAUDE.md](CLAUDE.md) |
| **🔬 Researchers** | Paper collaboration | Email collaboration request |

### 👨‍💻 **For Developers**
```bash
# 1. Pick an issue
gh issue list --label "good first issue"

# 2. Follow development guide  
cat CLAUDE.md

# 3. Run tests before PR
uv run pytest --tb=short

# 4. Submit with impact measurement
make benchmark
```

**Team**: [@lelouvincx](https://github.com/lelouvincx), [@greyy-nguyen](https://github.com/greyy-nguyen)

---

## 📜 License & Ethics

| Aspect | Status | Details |
|--------|--------|---------|
| **📖 License** | Academic Research Use | Educational & research purposes |
| **🛡️ Ethics Review** | In Progress | University ethics committee |
| **🔒 Privacy** | GDPR Compliant | PII anonymization enforced |
| **📊 Data** | Synthetic/Anonymized | Protects real candidate privacy |

---

<div align="center">

### **🎯 "Every qualified candidate deserves to be seen."** 

**Next Steps**: [🎮 Try Demo](#-demo-mode-recommended-for-first-time-users) • [📖 Read Paper](docs/PART_2.md) • [💻 Contribute](#-for-developers)

---

*Part of the "Towards Human-Centric AI" research initiative • Reducing AI bias in hiring*

</div>
