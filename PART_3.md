# Chapter 3: System Design

## 3.1 System Requirements

Goal:

- `P1` Enhanced recall: generate a ranked shortlist of candidates with better recall than baseline ATS
- `P1` Explanable decisions: provide an auditable, transparent recommendations via logging and human-in-the-loop
- `P3` Controlled workload: maintain reviewer load at small fraction of total pool (15-25%)

Principles:

- Layered intelligences: autonomous agents handle bulk processing, while human handle edge cases
- Feedback loop to improve over time

## 3.2 Use-case Overview

### 3.2.1 System Actors

#### Primary Actors (External)

- **Recruiter**: Initiates job postings, defines evaluation criteria, manages candidate sourcing, and provides contextual input for complex cases
- **HR Manager**: Provides oversight, handles HITL reviews for uncertain/high-stakes decisions, makes final hiring approvals, and guides bias mitigation strategies
- **Job Candidate**: Submits applications, receives status updates, and may be contacted for additional information
- **System Administrator**: Manages system configuration, user access controls, monitors compliance metrics, and generates audit reports

#### Secondary Actor

- **External Data Sources**: Job boards, professional networks, and candidate databases that provide candidate information

#### System Actor (Internal)

- **Multi-Agent System**: Autonomous collaborative framework consisting of specialized agents for (described in detail in Section 3.3):
  - Candidate sourcing and discovery
  - Resume screening and evaluation
  - Bias detection and mitigation
  - Human-AI collaboration coordination
  - Audit trail and compliance management

### 3.2.2 System Use Case Model

#### Core Use Case Categories

##### 1. Job Management and Sourcing

- **UC-JM-01: Post Job Requirements** - Recruiter defines job criteria, required skills, and evaluation rubric
- **UC-JM-02: Source Candidates** - System automatically discovers candidates from multiple sources
- **UC-JM-03: Manage Candidate Pool** - Deduplication, standardization, and eligibility filtering
- **UC-JM-04: Manual Candidate Addition** - Recruiter adds candidates with contextual notes

##### 2. Candidate Screening and Evaluation

- **UC-CS-01: Screen Candidates** - Semantic analysis of resumes against job requirements
- **UC-CS-02: Detect Bias** - Critic agent reviews screening decisions for discriminatory patterns
- **UC-CS-03: Generate Candidate Scores** - Evidence-based scoring with detailed rationales
- **UC-CS-04: Validate Decisions** - Cross-agent validation of screening outcomes

##### 3. Human-in-the-Loop (HITL) Review

- **UC-HITL-01: Trigger HITL Review** - Automatic escalation based on confidence thresholds or bias flags
- **UC-HITL-02: Present Candidate Context** - Structured display of agent analysis and conflicts
- **UC-HITL-03: Capture Human Decisions** - Record approvals, rejections, and feedback
- **UC-HITL-04: Facilitate Multi-turn Discussion** - Support iterative clarification for complex cases

##### 4. Decision Making and Compliance

- **UC-DM-01: Generate Final Shortlist** - Produce ranked candidates with transparent rationales
- **UC-DM-02: Maintain Audit Trail** - Complete logging of all decisions and interactions
- **UC-DM-03: Monitor Bias Metrics** - Real-time diversity and fairness tracking
- **UC-DM-04: Continuous Learning** - Model improvement from human feedback

#### Use Case Relationships

- **Includes**: UC-JM-01 includes UC-CS-01; UC-CS-01 includes UC-CS-02
- **Extends**: UC-HITL-01 extends UC-CS-01 when confidence is low; UC-HITL-04 extends UC-HITL-03 for complex cases
- **Generalizes**: UC-CS-03 generalizes to all evaluation contexts

```mermaid
graph TB
    subgraph "Multi-Agent HITL Recruitment System"
        PostJob[Post Job Requirements]
        SourceCandidates[Source Candidates]
        ScreenCandidates[Screen Candidates]
        DetectBias[Detect Bias]
        HITLReview[HITL Review]
        GenerateShortlist[Generate Final Shortlist]
        AuditCompliance[Maintain Audit Compliance]
        MonitorBias[Monitor Bias Metrics]
    end

    Recruiter((Recruiter))
    HRManager((HR Manager))
    Candidate((Job Candidate))
    SysAdmin((System Admin))

    Recruiter --> PostJob
    Recruiter --> SourceCandidates
    SourceCandidates --> ScreenCandidates
    ScreenCandidates --> DetectBias
    DetectBias -.-> HITLReview
    HITLReview --> HRManager
    HRManager --> GenerateShortlist
    ScreenCandidates --> GenerateShortlist
    GenerateShortlist --> Candidate
    SysAdmin --> AuditCompliance
    SysAdmin --> MonitorBias

    %% Multi-agent system processes (internal)
    SourceCandidates -.- MAS[<<system>><br/>Multi-Agent<br/>Processing]
    ScreenCandidates -.- MAS
    DetectBias -.- MAS
    HITLReview -.- MAS
    AuditCompliance -.- MAS

    classDef actor fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef usecase fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef agent fill:#fff3e0,stroke:#e65100,stroke-width:1px

    class Recruiter,HRManager,Candidate,SysAdmin actor
    class PostJob,SourceCandidates,ScreenCandidates,DetectBias,HITLReview,GenerateShortlist,AuditCompliance,MonitorBias usecase
    class MAS agent
```

### 3.2.3 Key Operational Scenarios

#### Primary Use Case Scenarios

| UC-ID    | Name                             | Primary Actor        | Pre-conditions                                                                                   | Main Steps                                                                                                                                                                                                                                                                                                                  | Post-conditions                                                                                                |
| -------- | -------------------------------- | -------------------- | ------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| UC-OP-01 | Standard Automated Screening     | Multi-Agent System   | • Job requirements posted<br>• Candidate pool sourced<br>• Evaluation rubric defined             | 1. Retrieve candidate profiles from source pool<br>2. Analyze resumes against job rubric<br>3. Validate decisions via bias detection<br>4. Generate confidence scores and rationales<br>5. Process high-confidence decisions automatically<br>6. Send automated status updates to candidates<br>7. Log complete audit trail | • Candidates scored and categorized<br>• Audit trail recorded<br>• 70-80% processed without human intervention |
| UC-OP-02 | HITL Intervention for Edge Cases | HR Manager           | • Low confidence score (<0.7)<br>• Bias flag raised<br>• Agent disagreement detected             | 1. Detect uncertainty in evaluation<br>2. Escalate case with structured context<br>3. Present agent analyses and conflicts<br>4. Facilitate interactive discussion<br>5. Capture human decision and rationale<br>6. Update system models with feedback<br>7. Communicate decision to candidate                              | • Human-validated decision recorded<br>• System learning updated<br>• Complex case resolved                    |
| UC-OP-03 | Bias Detection and Mitigation    | System Administrator | • Bias patterns detected<br>• Discrimination threshold exceeded<br>• Compliance review triggered | 1. Identify potential discrimination patterns<br>2. Send alerts to HR Manager and Admin<br>3. Analyze historical decisions<br>4. Implement mitigation strategies<br>5. Re-evaluate affected candidates<br>6. Generate compliance report<br>7. Initiate ongoing monitoring                                                   | • Bias mitigation applied<br>• Compliance documented<br>• Monitoring activated                                 |

#### Supporting Use Case Scenarios

| UC-ID    | Name                       | Primary Actor | Pre-conditions                                                                             | Main Steps                                                                                                                                                                                                                                                                      | Post-conditions                                                                           |
| -------- | -------------------------- | ------------- | ------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| UC-OP-04 | Manual Candidate Addition  | Recruiter     | • Active job posting<br>• Candidate information available<br>• Recruiter has system access | 1. Add candidate profile manually<br>2. Validate profile completeness<br>3. Request missing information if needed<br>4. Enrich profile with context notes<br>5. Attach portfolio/work samples<br>6. Tag with manual source indicator<br>7. Route to standard screening workflow | • Candidate integrated into pool<br>• Enhanced context preserved<br>• Screening initiated |
| UC-OP-05 | Multi-turn HITL Discussion | HR Manager    | • Complex case flagged<br>• Initial review incomplete<br>• Clarification needed            | 1. Review initial case presentation<br>2. Request specific clarifications<br>3. System provides additional context<br>4. Iterative Q&A exchange<br>5. Reach informed decision<br>6. Document discussion thread<br>7. Finalize candidate status                                  | • Complex case clarified<br>• Decision trail complete<br>• Learning data captured         |

#### HITL Review Process Flow

```mermaid
graph TB
    subgraph "HITL Review Subsystem"
        TriggerReview[Trigger HITL Review]
        PresentContext[Present Candidate Context]
        CaptureDecision[Capture Human Decision]
        ProvideFeedback[Provide Learning Feedback]
        UpdateModels[Update Agent Models]
    end

    HRManager((HR Manager))
    MultiAgentSystem((Multi-Agent System))

    TriggerReview --> PresentContext
    PresentContext --> HRManager
    HRManager --> CaptureDecision
    CaptureDecision --> ProvideFeedback
    ProvideFeedback --> UpdateModels
    UpdateModels --> MultiAgentSystem

    %% Extension points
    TriggerReview -.-> BiasDetected[<<extend>><br/>Bias Detected]
    CaptureDecision -.-> MultiTurn[<<extend>><br/>Multi-turn Discussion]

    classDef actor fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef usecase fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef extend fill:#e8f5e8,stroke:#1b5e20,stroke-width:1px,stroke-dasharray: 5 5

    class HRManager,MultiAgentSystem actor
    class TriggerReview,PresentContext,CaptureDecision,ProvideFeedback,UpdateModels usecase
    class BiasDetected,MultiTurn extend
```

## 3.3 Multi-Agent Architecture

### 3.3.1 Subagent Specifications

The multi-agent recruitment system operates through a distributed plan where six specialized agents collaborate to transform job requirements and candidate pools into ranked shortlists. Each agent contributes a distinct capability—sourcing discovers candidates, screening evaluates fit, critic validates decisions, HITL handles ambiguity, supervisor orchestrates workflow, and data-steward ensures compliance—while maintaining shared context and advancing toward the common goal of identifying qualified candidates with minimal bias and maximal transparency.

#### a. Supervisor Agent (Orchestrator)

**Role**: Central coordinator implementing supervisor-router pattern for multi-agent recruitment workflows.

**Core Responsibilities**: The supervisor decomposes job descriptions into evaluation rubrics, orchestrates task distribution across agents, and synthesizes their outputs while maintaining human review rates at 15-25% through intelligent triage.

**Plan Contribution**: Establishes the shared evaluation framework and orchestrates agent collaboration to achieve recruitment goals.

**Inputs/Outputs**: Job descriptions, candidate pools, agent analyses, human feedback → evaluation rubrics, routing decisions, ranked shortlists.

**Memory**: Ephemeral—workflow states, candidate processing status, communication logs. Persistent—performance metrics, triage patterns, optimization data. Permissions—full read/write access to all agent outputs and system coordination data.

#### b. Sourcing Subagent

**Role**: Multi-channel candidate discovery specialist building comprehensive candidate pools from external sources.

**Core Responsibilities**: The sourcing agent discovers and aggregates candidates from multiple channels, deduplicates profiles, and tracks metadata while applying initial eligibility filters.

**Plan Contribution**: Provides the raw candidate pool that feeds into screening and evaluation workflows.

**Inputs/Outputs**: Job requirements, sourcing parameters, manual uploads → standardized candidate pools with metadata.

**Memory**: Ephemeral—search sessions, API rate limits. Persistent—sourcing patterns, channel effectiveness metrics. Permissions—read access to job requirements, write access to candidate pools.

#### c. Screening Subagent

**Role**: Semantic analysis specialist evaluating candidate-job fit.

**Core Responsibilities**: The screening agent transforms unstructured resumes into scored assessments, extracting skills and experience to generate evidence-based evaluations with cited rationales.

**Plan Contribution**: Transforms unstructured candidate data into scored assessments that feed into triage decisions.

**Inputs/Outputs**: Resumes, evaluation rubrics, job requirements → structured analyses with scores and rationales.

**Memory**: Ephemeral—analysis sessions, scoring calculations. Persistent—match patterns, skill recognition improvements. Permissions—read access to candidate data, write access to analysis results.

#### d. Critic Subagent

**Role**: Independent validator identifying overlooked candidates and bias patterns.

**Core Responsibilities**: The critic re-examines rejected candidates through alternative lenses to identify transferable skills—recognizing, for instance, that "community organizing" transfers to "project management" or "military logistics" maps to "supply chain management."

**Plan Contribution**: Acts as quality control, ensuring qualified candidates aren’t incorrectly filtered out.

**Inputs/Outputs**: Screening results, original candidate data → second opinions, bias flags, hidden gems, confidence assessments.

**Memory**: Ephemeral—review cases, detection results. Persistent—bias patterns, correction histories, fairness metrics. Permissions—read access to screening outputs, write access to validation flags.

#### e. Human-in-the-Loop (HITL) Subagent

**Role**: Human-AI collaboration interface for ambiguous case resolution.

**Core Responsibilities**: The HITL agent presents ambiguous cases with highlighted conflicts, captures human verdicts and rationales, and enables multi-turn clarification when needed.

**Plan Contribution**: Ensures human judgment guides edge cases while capturing feedback to improve agent performance.

**Inputs/Outputs**: Ambiguous cases, conflicting opinions → human decisions, corrected evaluations, clarification responses.

**Memory**: Ephemeral—active sessions, pending decisions, conversation contexts. Persistent—decision patterns, interaction flows, reviewer analytics. Permissions—read access to uncertain cases, write access to human feedback.

#### f. Data-Steward Subagent

**Role**: Compliance and continuous improvement specialist.

**Core Responsibilities**: The data-steward maintains immutable audit trails while anonymizing PII, monitoring bias metrics, and transforming human feedback into privacy-preserving training datasets.

**Plan Contribution**: Ensures all decisions are traceable and compliant while driving continuous improvement through learning loops.

**Inputs/Outputs**: All system interactions and decisions → audit trails, anonymized datasets, bias reports, training data.

**Memory**: Ephemeral—current audit records, monitoring alerts. Persistent—historical archives, bias trends, improvement metrics. Permissions—universal read access, restricted write to audit logs and anonymized data.

### 3.3.2 System Architecture Diagram

### 3.3.3 Communication Patterns

### 3.3.4 Workflow State Management

```mermaid
flowchart TD
    Start([Job Description + Resume Pool]) --> Supervisor{Supervisor Agent}
    Supervisor --> Decompose[Decompose JD into<br/>Evaluation Rubric]
    Decompose --> InitState[Initialize Workflow State<br/>- Candidates<br/>- ReviewQueue<br/>- Results]

    InitState --> ScreeningLoop{For Each Resume}
    ScreeningLoop --> Screen[Screening Agent<br/>Semantic Analysis]
    Screen --> ScreenOutput[Output:<br/>- Structured Data<br/>- Skill Scores<br/>- Evidence Citations<br/>- Initial Rating]

    ScreenOutput --> Critic[Critic Agent<br/>Bias Check & Review]
    Critic --> CriticOutput[Output:<br/>- Second Opinion<br/>- Bias Flags<br/>- Hidden Gems<br/>- Confidence Score]

    CriticOutput --> Triage{Triage Logic<br/>Confidence Scoring}

    Triage -->|High Confidence<br/>Agreement| AutoAccept[Auto-Accept<br/>Add to Shortlist]
    Triage -->|Low Confidence<br/>Clear Mismatch| AutoReject[Auto-Reject<br/>Log Decision]
    Triage -->|Medium Confidence<br/>or Agent Conflict| HITLQueue[Add to HITL<br/>Review Queue]

    HITLQueue --> HITLAgent[HITL Agent<br/>Human Interface]
    HITLAgent --> HITLDisplay[Present to Recruiter:<br/>- Resume + Context<br/>- Agent Opinions<br/>- Conflict Highlights]

    HITLDisplay --> HITLDecision{Human Decision}
    HITLDecision -->|Approve| HITLApprove[Accept with<br/>Human Validation]
    HITLDecision -->|Reject| HITLReject[Reject with<br/>Human Reasoning]
    HITLDecision -->|Edit/Annotate| HITLEdit[Edit Scores +<br/>Provide Feedback]
    HITLDecision -->|Need More Info| HITLQuery[Multi-turn<br/>Conversation]

    HITLQuery --> HITLAgent
    HITLApprove --> DataSteward[Data-Steward Agent]
    HITLReject --> DataSteward
    HITLEdit --> DataSteward
    AutoAccept --> DataSteward
    AutoReject --> DataSteward

    DataSteward --> Audit[Log Decision:<br/>- Full Agent Trail<br/>- Human Feedback<br/>- Reasoning Chain]
    Audit --> Privacy[PII Protection:<br/>- Anonymize Data<br/>- Secure Storage]
    Privacy --> Learning[Continuous Learning:<br/>- Collect Feedback<br/>- Update Models<br/>- Bias Monitoring]

    Learning --> MoreCandidates{More Candidates?}
    MoreCandidates -->|Yes| ScreeningLoop
    MoreCandidates -->|No| FinalRanking[Final Ranking<br/>& Compilation]

    FinalRanking --> Output[Deliver Results:<br/>- Ranked Shortlist<br/>- Decision Rationales<br/>- Diversity Metrics<br/>- Audit Trail]

    %% Parallel Processing Paths
    ScreeningLoop -.->|Batch Processing| Screen2[Screening Agent 2]
    ScreeningLoop -.->|Batch Processing| Screen3[Screening Agent N]
    Screen2 --> CriticOutput
    Screen3 --> CriticOutput

    %% Feedback Loop
    Learning -.->|Model Updates| Screen
    Learning -.->|Bias Adjustments| Critic
    Learning -.->|Threshold Tuning| Triage

    %% Monitoring
    DataSteward -.->|Real-time Monitoring| Monitor[Bias Metrics<br/>Performance KPIs<br/>α Rate Control]
    Monitor -.->|Alerts| Supervisor

    %% Styling
    classDef agentNode fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef humanNode fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef dataNode fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef decisionNode fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px

    class Supervisor,Screen,Critic,HITLAgent,DataSteward agentNode
    class HITLDisplay,HITLDecision,HITLApprove,HITLReject,HITLEdit,HITLQuery humanNode
    class Audit,Privacy,Learning,Monitor dataNode
    class Triage,MoreCandidates decisionNode
```

#### Phase 1: Initialization (Supervisor Agent)

- Decomposes job description into structured evaluation criteria
- Extracts required skills, experience levels, qualifications
- Sets up workflow state management for tracking progress

#### Phase 2: Parallel Screening (Multi-Agent Processing)

- Multiple screening agents process resumes concurrently
- Semantic analysis extracts structured data and initial scoring
- Load balancing across agent instances for scalability

#### Phase 3: Critical Review (Bias Mitigation)

- Critic agent provides independent second opinion
- Identifies potential biases in screening decisions
- Flags "hidden gems" that may have been undervalued

#### Phase 4: Intelligent Triage (Workload Control)

- Confidence scoring determines routing path
- Dynamic thresholds maintain review rate at small fraction (target: 15-25% to human review)
- Auto-decisions for clear cases, human review for ambiguous ones

#### Phase 5: Human-in-the-Loop (Quality Assurance)

- Structured interface presents conflicting opinions
- Multiple interaction patterns: approve/reject/edit/clarify
- Captures not just decisions but reasoning for learning

#### Phase 6: Continuous Learning (System Evolution)

- Data-Steward maintains complete audit trail
- Privacy protection through PII anonymization
- Feedback loops improve agent performance over time

### 3.3.5 Human-in-the-Loop (HITL) Interaction

#### Triage Criteria for Human Review:

- `|Screening_Score - Critic_Score|` > `disagreement_threshold`
- Confidence_Score < uncertainty_threshold
- Borderline candidates near acceptance boundary

#### HITL Patterns:

- Approve/Reject: Standard review workflow
- Edit/Annotate: Corrective feedback for learning
- Multi-turn: Complex case discussions

## 3.4 Evaluation Method

### Primary Metrics

- Recall@K: |(System_Shortlist ∩ Gold_Standard)| / |Gold_Standard|
- False Negative Rate: Qualified candidates in reject pile
- Human Review Rate: Percentage requiring human evaluation

### Success Criteria

- Recall Improvement: >20% increase vs baseline ATS
- Audit Compliance: 100% traceable decisions
- Workload Control: Human review rate ≤ small fraction (15-25%)

### Validation Approach

- Gold standard datasets from expert recruiters
