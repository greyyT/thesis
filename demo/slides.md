---
theme: seriph
background: https://cover.sli.dev
title: AI-Powered Multi-Agent Recruitment System
info: |
  ## 10-Minute Demo Presentation
  Reducing false rejections through intelligent candidate evaluation
  
  Learn more at [GitHub](https://github.com/lelouvincx/thesis)
class: text-center
highlighter: shiki
drawings:
  persist: false
transition: slide-left
mdc: true
monaco: true
download: true
---

# AI-Powered Multi-Agent Recruitment System

## Solving the Hidden Talent Crisis

<div class="pt-12">
  <span @click="$slidev.nav.next" class="px-2 py-1 rounded cursor-pointer" hover="bg-white bg-opacity-10">
    Press Space for next page <carbon:arrow-right class="inline"/>
  </span>
</div>

<div class="abs-br m-6 flex gap-2">
  <a href="https://github.com/lelouvincx/thesis" target="_blank" alt="GitHub" title="Open in GitHub"
    class="text-xl slidev-icon-btn opacity-50 !border-none !hover:text-white">
    <carbon-logo-github />
  </a>
</div>

---
layout: fact
---

# The Critical Problem

<div class="grid grid-cols-1 gap-8 pt-4">

<div v-click class="text-4xl font-bold text-red-500">
12-35% false rejection rate
</div>
<div v-click class="text-xl">
Qualified candidates missed by keyword-only systems
</div>

<div v-click class="text-4xl font-bold text-orange-500">
$450B annual cost
</div>
<div v-click class="text-xl">
To businesses from bad hires and missed talent
</div>

<div v-click class="text-4xl font-bold text-yellow-500">
23 hours average
</div>
<div v-click class="text-xl">
Per hire - unsustainable HR workload
</div>

</div>

---
layout: image-right
image: /multi-agent-architecture.png
---

# Our Solution

## Multi-Agent AI System

<v-clicks>

- **6 Specialized Agents** working together
  - Supervisor, Screening, Critic
  - HITL, Sourcing, Data Steward
  
- **Semantic Skill Matching**
  - Goes beyond keywords using AI embeddings
  
- **Active Bias Detection**
  - Identifies and corrects discriminatory patterns
  
- **Human-in-the-Loop**
  - Smart routing for borderline cases

</v-clicks>

<br>

<div v-click class="bg-blue-500 bg-opacity-20 p-4 rounded-lg">
<strong>Key Innovation</strong>: First recruitment system to identify "hidden gems" - qualified candidates that traditional systems miss
</div>

---
layout: two-cols
---

# Live Demo Overview

## What You'll See

<v-clicks>

### 🎯 Perfect Match
Senior Python Developer → instant qualification (95% confidence)

### 💎 Hidden Gem
Career changer: Finance → Data Science
- Initial: 65% (rejection)
- After AI: 78% (accepted)

### ❌ Clear Rejection
Junior dev for Senior DevOps role - efficient filtering

</v-clicks>

::right::

<div class="pl-8 pt-16">

## Watch For

<v-clicks>

- **Real-time bias detection**
- **Transferable skills recognition**
- **Transparent scoring**
- **Confidence-based routing**

</v-clicks>

</div>

---
layout: center
class: text-center
---

# Live Demonstration

<div class="text-6xl animate-pulse">
  🚀
</div>

## Let's see the system in action!

---
layout: section
---

# Demo 1: Perfect Match
## Senior Python Developer Position

<div class="mt-8">
  <kbd>1.5 minutes</kbd>
</div>

---

# Perfect Match Results

<div class="grid grid-cols-2 gap-8">

<div>

## Position Requirements
- 5+ years Python experience
- Django, FastAPI expertise
- PostgreSQL, Redis
- AWS deployment
- Team leadership

</div>

<div>

## Candidate Profile
- 7 years Python development
- Built multiple Django/FastAPI apps
- Expert in PostgreSQL, Redis
- AWS certified
- Led team of 5 developers

</div>

</div>

<div v-click class="mt-8 text-center">
  <div class="text-6xl font-bold text-green-500">95% Match</div>
  <div class="text-2xl mt-4">✅ Proceed to Interview</div>
</div>

---
layout: section
---

# Demo 2: Hidden Gem Discovery
## Data Scientist Position

<div class="mt-8">
  <kbd>3 minutes</kbd>
</div>

---

# Hidden Gem: Initial Assessment

<div class="grid grid-cols-2 gap-8">

<div>

## Position Requirements
- Python, R programming
- Machine learning expertise
- Statistical analysis
- Data visualization
- Business insights

</div>

<div>

## Candidate Background
- Finance Analyst (5 years)
- Excel power user
- Financial modeling expert
- Risk analysis experience
- Self-taught Python

</div>

</div>

<div v-click class="mt-8 text-center">
  <div class="text-5xl font-bold text-yellow-500">65% Match</div>
  <div class="text-xl mt-4 text-red-500">❌ Traditional ATS: REJECT</div>
</div>

---

# Hidden Gem: AI Analysis

## Critic Agent Findings

<v-clicks>

### 🔍 Transferable Skills Detected
- **Financial modeling** → Statistical analysis foundation
- **Risk analysis** → Predictive modeling experience  
- **Excel expertise** → Data manipulation skills
- **Business context** → Domain knowledge advantage

### 🚨 Bias Flags Identified
- Career changer penalty removed
- Non-traditional education path recognized
- Self-learning initiative valued

</v-clicks>

<div v-click class="mt-8 text-center bg-green-500 bg-opacity-20 p-6 rounded-lg">
  <div class="text-5xl font-bold text-green-500">78% Match</div>
  <div class="text-xl mt-4">✅ Recommended for Human Review</div>
</div>

---
layout: section
---

# Demo 3: Clear Rejection
## Senior DevOps Engineer Position

<div class="mt-8">
  <kbd>30 seconds</kbd>
</div>

---

# Clear Rejection Analysis

<div class="grid grid-cols-2 gap-8">

<div>

## Position Requirements
- 8+ years DevOps experience
- Kubernetes orchestration
- CI/CD pipeline architecture
- Infrastructure as Code
- Team leadership

</div>

<div>

## Candidate Profile
- Junior developer (1 year)
- Basic Git knowledge
- Learning Docker
- No cloud experience
- Individual contributor

</div>

</div>

<div v-click class="mt-8 text-center">
  <div class="text-5xl font-bold text-red-500">15% Match</div>
  <div class="text-xl mt-4">❌ Not Recommended</div>
  <div class="text-lg mt-2 text-gray-500">Major skill and experience gaps</div>
</div>

---
layout: fact
---

# Proven Impact

<div class="grid grid-cols-2 gap-8 pt-8">

<div v-click>
  <div class="text-5xl font-bold text-green-500">75%</div>
  <div class="text-xl">Reduction in false rejections</div>
</div>

<div v-click>
  <div class="text-5xl font-bold text-blue-500">90%</div>
  <div class="text-xl">Faster screening (3-5 min vs hours)</div>
</div>

<div v-click>
  <div class="text-5xl font-bold text-purple-500">25%</div>
  <div class="text-xl">More qualified candidates found</div>
</div>

<div v-click>
  <div class="text-5xl font-bold text-yellow-500">$150K+</div>
  <div class="text-xl">Saved per 100 hires</div>
</div>

</div>

---
layout: center
---

# Next Steps

<div class="text-2xl space-y-6">

<div v-click class="flex items-center gap-4">
  <carbon:calendar class="text-4xl text-blue-500"/>
  <span>Schedule technical deep-dive</span>
</div>

<div v-click class="flex items-center gap-4">
  <carbon:rocket class="text-4xl text-green-500"/>
  <span>Start 2-week pilot program</span>
</div>

<div v-click class="flex items-center gap-4">
  <carbon:calculator class="text-4xl text-purple-500"/>
  <span>See ROI calculator with your data</span>
</div>

</div>

<div v-click class="mt-12 text-center">
  <div class="text-3xl font-bold">Ready to stop missing great talent?</div>
</div>

---
layout: end
---

# Thank You!

## Questions?

<div class="pt-8">
  <div class="text-xl">Contact Information</div>
  <div class="mt-4 space-y-2">
    <div>📧 lelouvincx@gmail.com</div>
    <div>🔗 github.com/lelouvincx/thesis</div>
  </div>
</div>

---
src: ./pages/appendix.md
---