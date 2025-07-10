# To do

## Part 1 - introduction

### 1.1 - reasons for choosing the topic

- [x] Add government/academic sources (ILO, OECD, Bureau of Labor Statistics) @lelouvincx
- [x] Technology is proposed as the solution. However, the insights from survey emphasize "quality candidates" and "retention" @greyy-nguyen (the old version didn't mention that using AI will give time for HR to do strategic tasks, but the new version does).
- [ ] Assumes AI automation is superior without comparing to improved human processes @greyy-nguyen

### 1.2 - problem statement

- [ ] Content for this part @greyy-nguyen
  - Current ATS fail because of rigid keyword matching → Multi-agent system uses contextual understanding
  - Single-point decisions create bias → Multiple specialized agents provide checks and balances
  - Lack of transparency → Explainable AI with audit trails

- [ ] Problem space @lelouvincx
  - Slow mannual processes lead to delays in hiring (27%)
    - In this case, companies still increase headcount, but the hiring process itself is slow
    - Emphasize this point to highlight the need for automation => technical value
    - If go with this pain point, we can focus on automating the entire hiring process, not candidate screening
      - Available datasets: none
      - Complexity of implementation: high
      - Design more subagents such as sourcing, screening, engagement, compliance, etc
      - Most feasible approach: create synthetic workflow simulations using existing resume/job description pairs with generated timestamp sequences
  - High false rejection rate leads to loss of talent (12-35%)
    - Because of ATS and human process
    - Focus more on pre-screening functionality rather than the entire hiring process
    - Emphasize the importance of retaining quality candidates and reducing bias in the hiring process => business value
    - If go with this pain point, we can focus on augmenting human recruiters by automating top-of-funnel screening while ensuring viable candidates reach human review
      - Available datasets: some datasets on kaggle
      - Complexity of implementation: medium
      - Subagents such as sourcing, screening, criticizing output of the screening agent, HITL agent, etc
      - Success metrics: reduction in false rejection rate vs baseline, explanation coverage, time-to-shortlist
      - Feasible statements "Given a batch of job descriptions J and a pool of resumes R, output a ranked shortlist S ⊂ R for each job j ∈ J.  
A human reviewer (simulated or real) then labels the shortlist as “interview / no-interview”. The system must optimise for high recall of truly qualified candidates while minimising recruiter review load."
    - Datasets:
      - [Resume Dataset](https://www.kaggle.com/datasets/jithinjagadeesh/resume-dataset)
      - [Resume Entities for NER](https://www.kaggle.com/datasets/dataturks/resume-entities-for-ner)

- [ ] Find suitable dataset for evaluating success metrics: Time-to-hire reduction percentage, Quality-of-hire scores, Diversity metrics improvement, False negative reduction rate @lelouvincx
    - [ ] Approach: Since no time, Find datasets first, find out the evaluation method of those datasets, then design the problem statement based on the evaluation method

- [ ] Reference OECD AI Principles explicitly when discussing your human-in-the-loop system design, particularly Principles 2 (human-centered values) and 5 (accountability), https://www.oecd.org/en/topics/sub-issues/ai-principles.html

- [ ] Write problem statement @lelouvincx