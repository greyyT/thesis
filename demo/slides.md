---
layout: center
title: AI-Powered Multi-Agent Recruitment System
info: |
  ## 10-Minute Demo Presentation
  Reducing false rejections through intelligent candidate evaluation

  Learn more at [GitHub](https://github.com/greyyT/thesis)
class: text-center
highlighter: shiki
css: unocss
colorSchema: dark
transition: fade-out
lineNumbers: false
drawings:
  persist: true
mdc: true
monaco: true
download: true
exportFilename: "AI-Powered Multi-Agent Recruitment System Demo"
fonts:
  sans: DM Sans
  serif: Noto Serif SC
  mono: Fira Code
clicks: 0
preload: true
glowSeed: 228
routerMode: hash
---

# Title Slide

<Toc minDepth="1" maxDepth="1" />

---

# Content Slide

---

## src: ./pages/appendix.md

---

# Use Case Diagram

<!--
- Job posting automatically triggers candidate sourcing
- All screening includes mandatory bias detection
- Low-confidence cases escalate to human review
- Complex reviews may require multiple discussion rounds
-->

<div class="flex justify-center items-center h-full">

```mermaid {theme: 'neutral', scale: 0.4}
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

</div>

---

# Test

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Chainlit UI   │────│    Agent     │────│   Vector Store  │
│  (Web Interface)│    │ (src/agents) │    │ (Milvus Lite)   │
└─────────────────┘    └──────────────┘    └─────────────────┘
                              │
                       ┌──────────────┐    ┌─────────────────┐
                       │  OpenAI API  │    │      Redis      │
                       │(LLM+Embeddings)│   │ (State Mgmt)    │
                       └──────────────┘    └─────────────────┘
```
