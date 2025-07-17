# To do

## Part 1 - introduction

### 1.1 - reasons for choosing the topic

- [x] Add government/academic sources (ILO, OECD, Bureau of Labor Statistics) @lelouvincx
- [x] Technology is proposed as the solution. However, the insights from survey emphasize "quality candidates" and "retention" @greyy-nguyen (the old version didn't mention that using AI will give time for HR to do strategic tasks, but the new version does).
- [ ] Assumes AI automation is superior without comparing to improved human processes @greyy-nguyen

### 1.2 - problem space

- [ ] Content for this part @greyy-nguyen

  - Current ATS fail because of rigid keyword matching → Multi-agent system uses contextual understanding
  - Single-point decisions create bias → Multiple specialized agents provide checks and balances
  - Lack of transparency → Explainable AI with audit trails

- [x] Problem space @lelouvincx

- [ ] @lelouvincx to find suitable dataset for evaluating success metrics: Time-to-hire reduction percentage, Quality-of-hire scores, Diversity metrics improvement, False negative reduction rate

  - [x] Approach: Since no time, Find datasets first, find out the evaluation method of those datasets, then design the problem statement based on the evaluation method

- [ ] @lelouvincx to reference OECD AI Principles explicitly when discussing your human-in-the-loop system design, particularly Principles 2 (human-centered values) and 5 (accountability), https://www.oecd.org/en/topics/sub-issues/ai-principles.html

### 1.3 - problem statement

- [x] @lelouvincx to write problem statement

## Part 2 - Theory

- [ ] @greyy-nguyen to write the theory part
  - [ ] Multi-agent system
  - [ ] Explainable AI
  - [ ] Human-in-the-loop
  - [ ] Human resources management

## Part 3 - Methodology

### 3.1 - Understanding Existing ATS Systems

#### Research Phase (Week 1)

- [x] @lelouvincx Select 5 major ATS platforms for analysis (based on market share and OECD AI concerns):
  - **Workday** (22.6% Fortune 500) - Enterprise leader, examine AI screening features
  - **Taleo/Oracle** (22.4% Fortune 500) - Legacy system, document rigid matching issues
  - **Greenhouse** (7.81% enterprise, fastest growing) - Modern approach, examine bias controls
  - **iCIMS** (7.4% Fortune 500) - Mid-market leader, AI-powered matching
  - **Lever** (2.92% market share) - Tech startup favorite, collaborative hiring focus
- [x] @lelouvincx For each ATS, document AI/ML usage and transparency features (see ATS_AI_Analysis.md):
  - [x] Does it use AI for screening? If yes, what type?
  - [x] Are screening criteria transparent to candidates?
  - [x] What bias mitigation features exist?
  - [x] Is there human review capability built-in?
  - [x] Compliance with OECD AI Principles (human-centered, accountability)
- [x] @lelouvincx For Taleo/Oracle - create 1-page summary covering (added to ATS_AI_Analysis.md):
  - [x] Primary screening algorithms used (keyword matching, boolean search, etc.)
  - [x] Resume parsing capabilities and supported formats
  - [x] Filtering/ranking mechanisms
  - [x] API/integration options and limitations
  - [x] Document known discrimination risks:
    - [x] Language/gender bias in keyword matching
    - [x] Resume gap penalties (OECD: 50% companies reject 6+ month gaps)
    - [x] Implicit bias in scoring algorithms
    - [x] Disability accommodation failures
    - [x] False rejection mechanisms and rates
- [x] @lelouvincx For Workday - create 1-page summary with same structure
- [x] @lelouvincx For Greenhouse - create 1-page summary with same structure
- [x] @lelouvincx For Lever - create 1-page summary with same structure
- [x] @lelouvincx For iCIMS - create 1-page summary with same structure

#### Documentation Phase (Week 2)

- [x] @lelouvincx Build visual flowchart showing common ATS workflow stages:
  - [x] Job posting creation → Resume submission
  - [x] Initial parsing → Keyword extraction
  - [x] Screening/filtering → Ranking/scoring
  - [x] Decision points and rejection triggers

### 3.2 - False Rejection Rate Analysis

#### Literature Review (Week 1)

- [x] @lelouvincx Search IEEE Xplore for "ATS false rejection" papers (target: 3-4 papers)
- [x] @lelouvincx Search Google Scholar for industry reports on ATS effectiveness (target: 2-3 papers)
  - Fuller, J., Raman, M., et al. (2021). "Hidden Workers: Untapped Talent." Harvard Business School. https://www.hbs.edu/managing-the-future-of-work/Documents/research/hiddenworkers09032021.pdf
    - Key finding: 88% of employers acknowledge their ATS systems reject qualified, high-skilled candidates
  - Nanajkar, J., Sable, A., et al. (2023). "AI Powered Application Tracking System With NLP Based Resume Scoring." IJCRT. https://www.ijcrt.org/papers/IJCRT2506299.pdf
    - Key finding: 75% of resumes disqualified by ATS before human review; false negatives from keyword matching
  - IAXOV Inc. (2025). "STRATEVITA: Intelligence Revolutionizes Talent Management." https://www1.iaxov.com/publications/STRATEVITA_%20Intelligence%20Revolutionizes%20Talent%20Management.pdf
    - Key finding: 99.7% recruiter ATS usage creates systematic exclusion through "keyword fallacy"
- [ ] @lelouvincx Extract and tabulate FRR statistics from each source:
  - [ ] Study name, year, sample size
  - [ ] Reported FRR percentage
  - [ ] Methodology used
  - [ ] Key findings
  - [ ] Note: Be aware of "75% rejection rate" myth from 2012 Preptel sales pitch - no valid research backs this claim
- [ ] @lelouvincx Research Harvard Business School 2021 study findings:
  - [ ] 88% of companies' tech screens out qualified applicants due to search term mismatches
  - [ ] 50%+ companies reject candidates with 6+ month resume gaps
- [ ] @lelouvincx Create annotated bibliography with 2-3 sentence methodology summaries

#### Metrics Definition (Week 2)

- [ ] @lelouvincx Define "qualified candidate" criteria (minimum 5 attributes):
  - [ ] Required skills match percentage threshold
  - [ ] Experience level alignment
  - [ ] Education requirements met
  - [ ] Location/availability match
  - [ ] Salary expectations alignment
- [ ] @lelouvincx Document FRR calculation formula with concrete example:
  - [ ] Formula: FRR = (False Rejections / Total Qualified Candidates) × 100
  - [ ] Example calculation with sample data
  - [ ] Sensitivity analysis on threshold changes
- [ ] @lelouvincx Identify 3 validation approaches:
  - [ ] Expert recruiter review (gold standard)
  - [ ] Historical hiring outcome analysis
  - [ ] A/B testing with control group

#### Dataset Research (Week 3)

- [ ] @lelouvincx Evaluate Resume Dataset from Kaggle:
  - [ ] Dataset size and diversity metrics
  - [ ] Available features and annotations
  - [ ] Presence of hiring outcome labels
  - [ ] Data quality assessment
- [ ] @lelouvincx Evaluate Indeed/LinkedIn public datasets (if available)
- [ ] @lelouvincx Evaluate academic resume datasets (e.g., from prior research)
- [ ] @lelouvincx Document dataset gaps requiring synthetic data:
  - [ ] Missing hiring outcomes
  - [ ] Lack of diversity in roles/industries
  - [ ] Insufficient edge cases
- [ ] @lelouvincx Create dataset requirements specification:
  - [ ] Minimum size: X resumes
  - [ ] Required features list
  - [ ] Label requirements
  - [ ] Diversity requirements

### 3.3 - ATS System Drawbacks Documentation

#### Categorization (Week 1)

- [ ] @lelouvincx Create detailed limitation categories:
  - [ ] Keyword Dependency Issues (3-5 examples):
    - [ ] Synonym blindness (e.g., "software engineer" vs "developer")
    - [ ] Context ignorance (e.g., "Java" coffee vs programming)
    - [ ] Abbreviation misses (e.g., "ML" vs "Machine Learning")
  - [ ] Format Parsing Failures (3-5 examples):
    - [ ] Complex PDF layouts breaking parsers
    - [ ] Table/column formatting issues
    - [ ] Non-standard section headers
  - [ ] Bias Amplification (3-5 examples):
    - [ ] University name bias
    - [ ] Years of experience over-weighting
    - [ ] Geographic discrimination
  - [ ] Context Blindness (3-5 examples):
    - [ ] Career transition penalties
    - [ ] Transferable skills ignored
    - [ ] Project-based experience missed
- [ ] @lelouvincx Build visual failure taxonomy diagram
- [ ] @lelouvincx Map limitations to affected candidate groups (veterans, career changers, etc.)

#### Case Study Collection (Week 2)

- [ ] @lelouvincx Find and document 5 ATS failure cases from:
  - [ ] News articles and investigative reports
  - [ ] Reddit/forum testimonials
  - [ ] Academic case studies
- [ ] @lelouvincx Interview 3 recruiters about ATS frustrations:
  - [ ] Prepare interview questions
  - [ ] Conduct 30-minute interviews
  - [ ] Transcribe key insights
- [ ] @lelouvincx Compile pattern analysis report:
  - [ ] Common failure patterns
  - [ ] Frequency estimates
  - [ ] Impact assessment

### 3.4 - Proposed System Methodology

#### Agent Mapping (Week 1)

- [ ] @lelouvincx Create agent-to-limitation mapping table:
  - [ ] Sourcing Agent → addresses limited candidate discovery
  - [ ] Screening Agent → addresses rigid keyword matching
  - [ ] Critic Agent → addresses bias amplification
  - [ ] HITL Agent → addresses context blindness
  - [ ] Data-Steward Agent → addresses lack of transparency
- [ ] @lelouvincx Design agent interaction sequence diagram:
  - [ ] Message flow between agents
  - [ ] Decision handoff points
  - [ ] Feedback loops
- [ ] @lelouvincx Write 1-page specification for each agent:
  - [ ] Supervisor Agent logic and coordination rules
  - [ ] Sourcing Agent search strategies
  - [ ] Screening Agent evaluation criteria
  - [ ] Critic Agent bias detection methods
  - [ ] HITL Agent escalation triggers

#### Evaluation Design (Week 2)

- [ ] @lelouvincx Define 5 quantitative success metrics:
  - [ ] False Rejection Rate reduction (target: 50% improvement)
  - [ ] Recall@K for top candidates (target: >80%)
  - [ ] Human review workload (target: <25% of applications)
  - [ ] Time-to-shortlist (target: <24 hours)
  - [ ] Diversity metric improvement (target: 20% increase)
- [ ] @lelouvincx Design baseline measurement protocol:
  - [ ] Control group using traditional ATS
  - [ ] Test group using multi-agent system
  - [ ] Measurement timeline and checkpoints
- [ ] @lelouvincx Create A/B test framework outline:
  - [ ] Random assignment methodology
  - [ ] Sample size calculations
  - [ ] Statistical significance thresholds

#### Proof of Concept (Week 3)

- [ ] @lelouvincx Select 3 core features for MVP:
  - [ ] Basic multi-agent orchestration
  - [ ] Semantic resume screening
  - [ ] Simple HITL interface
- [ ] @lelouvincx Create 2-week implementation sprint plan:
  - [ ] Week 1: Agent framework and basic screening
  - [ ] Week 2: HITL integration and testing
- [ ] @lelouvincx Define pilot success criteria:
  - [ ] Process 100 resumes successfully
  - [ ] Achieve 70% recall on test set
  - [ ] Complete end-to-end workflow demo

## Part 4 - High-level Design

- [x] @lelouvincx to write the high-level system architecture design
- [x] @lelouvincx to draw use-case diagram
- [x] @lelouvincx to describe the use-case diagram
- [x] @lelouvincx to synthesize all diagrams to one System Architecture Diagram

## Part 5 - Experiment and Evaluation

- [ ] @lelouvincx to prepare dataset
- [ ] @lelouvincx process dataset
- [ ] @lelouvincx implementation
- [ ] @lelouvincx evaluate
- [ ] @lelouvincx result
