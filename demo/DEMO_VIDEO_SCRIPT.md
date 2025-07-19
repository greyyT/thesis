# Demo Video Script

## Video Overview
**Duration**: 8-10 minutes  
**Format**: Screen recording with voiceover  
**Resolution**: 1920x1080 minimum  
**Target Audience**: Technical stakeholders, hiring managers, demo viewers

## Recording Setup

### Technical Setup
```bash
# Ensure system is ready
docker compose up -d redis
uv run chainlit run src/main.py

# Open browser to localhost:8000
# Clear browser cache for clean demo
# Use incognito/private window for clean state
```

### Screen Recording Recommendations
- **Tool**: OBS Studio, QuickTime (macOS), or Windows Game Bar
- **Frame Rate**: 30fps minimum
- **Audio**: Record system audio + microphone
- **Mouse Cursor**: Show cursor, enable click highlights
- **Window**: Record full browser window or application area

## Script Outline

### [0:00-0:30] Introduction
**Visual**: Title slide or demo homepage  
**Voiceover**:
> "Welcome to the AI-powered Multi-Agent Recruitment System demonstration. I'm going to show you how our system reduces false rejection rates in hiring by using specialized AI agents to evaluate candidates more fairly and accurately than traditional keyword-based systems."

> "Today we'll see three scenarios: a perfect match, a hidden gem candidate who might be overlooked by traditional systems, and a clear rejection case."

### [0:30-1:00] System Overview
**Visual**: Navigate to application homepage, show welcome screen  
**Voiceover**:
> "The system uses a chat-based interface powered by Chainlit. Behind the scenes, we have multiple AI agents working together: a Supervisor agent that analyzes job requirements, a Screening agent that performs semantic matching, a Critic agent that detects bias and identifies transferable skills, and a Human-in-the-Loop agent that determines when human review is needed."

> "Let's start with our first scenario."

### [1:00-3:30] Scenario 1: Perfect Match
**Visual**: 
1. Type "demo" command
2. Show loading progression with step-by-step indicators
3. Display comprehensive results with confidence bars

**Voiceover**:
> "I'll use our built-in demo mode which loads a Senior Python Developer position and an experienced candidate's resume."

> *[While evaluation runs]* "Notice the loading indicators showing each step: job analysis, resume parsing, semantic matching, and critical review. This transparency helps build trust in the AI decision-making process."

> *[Results displayed]* "Here we see a perfect match with 95% confidence. The system identified all required skills with high confidence scores, the candidate exceeds experience requirements, and no bias flags were detected. The visual confidence bars make it easy to understand the strength of each match."

> "This candidate would proceed directly to the next round without human review."

### [3:30-6:30] Scenario 2: Hidden Gem
**Visual**:
1. Upload new job description (Data Scientist)
2. Upload career changer resume
3. Walk through evaluation process
4. Highlight bias detection and transferable skills

**Voiceover**:
> "Now let's look at a more complex case - a career changer applying for a Data Scientist position. I'll upload a job description and resume for someone transitioning from finance to data science."

> *[During upload]* "The system accepts both file uploads and pasted text, making it flexible for different workflows."

> *[During evaluation]* "Notice the evaluation takes longer this time - the Critic agent is working harder to analyze transferable skills and potential biases."

> *[Results displayed]* "This is fascinating - the initial screening score was moderate, but the critic review identified several transferable skills and flagged this as a potential hidden gem. The system detected bias flags around the career change and non-traditional education path."

> "Rather than rejecting this candidate outright, the system recommends human review. This is exactly how we reduce false rejections - by catching qualified candidates who might be overlooked by traditional keyword-based systems."

### [6:30-8:30] Scenario 3: Clear Rejection
**Visual**:
1. Upload Senior DevOps Engineer job description
2. Upload junior developer resume
3. Show quick evaluation and clear rejection

**Voiceover**:
> "Finally, let's see a clear rejection case - a junior developer applying for a senior DevOps position."

> *[During evaluation]* "The evaluation is faster this time because the skill gaps are immediately apparent."

> *[Results displayed]* "Here we see low confidence scores across all metrics. The system clearly identifies major skill gaps, experience level mismatches, and provides a confident 'not recommended' decision."

> "This shows the system can also make clear rejections when appropriate, focusing human review time on the more nuanced cases."

### [8:30-10:00] Conclusion & Technical Highlights
**Visual**: Show system architecture or key features summary  
**Voiceover**:
> "What makes this system unique is its multi-agent architecture. Each agent has specialized expertise - the Critic agent specifically looks for bias and transferable skills, helping identify hidden gems that traditional systems miss."

> "Key benefits include semantic skill matching using vector embeddings rather than keyword searches, active bias detection and mitigation, confidence-based routing to optimize human reviewer time, and transparent explanations for all decisions."

> "This system represents a significant advancement in fair and effective candidate evaluation, reducing false rejections while maintaining high standards for role requirements."

> "Thank you for watching this demonstration of our AI-powered Multi-Agent Recruitment System."

## Recording Checklist

### Pre-Recording
- [ ] System tested and running smoothly
- [ ] Browser cleared/private window opened
- [ ] Screen recording software configured
- [ ] Microphone tested and audio levels checked
- [ ] Demo scenarios ready and tested
- [ ] Script reviewed and practiced

### During Recording
- [ ] Speak clearly and at moderate pace
- [ ] Allow time for loading/processing
- [ ] Highlight key visual elements with cursor
- [ ] Maintain steady narration pace
- [ ] Show full evaluation results before moving on

### Post-Recording
- [ ] Review for audio/video quality
- [ ] Trim any dead time or errors
- [ ] Add captions if needed
- [ ] Export in appropriate format (MP4 recommended)
- [ ] Test playback on different devices

## Technical Notes for Recording

### Camera/Cursor Settings
- Enable cursor highlighting for clicks
- Use zoom to focus on important UI elements
- Keep consistent window size throughout recording

### Audio Settings
- Record in quiet environment
- Use headset/external microphone for better quality
- Maintain consistent volume levels
- Record separate audio track for easier editing

### Visual Focus Areas
1. **Loading Indicators**: Show step-by-step progress
2. **Confidence Bars**: Highlight visual scoring system
3. **Bias Flags**: Point out bias detection features
4. **Skill Matching**: Demonstrate semantic vs keyword matching
5. **Decision Reasoning**: Show clear explanations

### Common Mistakes to Avoid
- Speaking too fast during technical explanations
- Not allowing enough time for evaluation processing
- Skipping over important visual elements
- Inconsistent audio levels
- Not showing full results before moving to next scenario

## Alternative Recording Approach

If screen recording isn't available, consider:
1. **Slide-based presentation** with screenshots
2. **Live demo** during video call (recorded)
3. **Step-by-step documentation** with annotated screenshots
4. **Interactive demo** that others can run following the setup guide

## Video Delivery Formats

### Full Demo Video (8-10 minutes)
- Complete walkthrough of all scenarios
- Technical explanations and architecture overview
- Suitable for stakeholder presentations

### Quick Overview (3-4 minutes)
- Focus on one perfect scenario
- Highlight key differentiators
- Suitable for executive briefings

### Technical Deep Dive (15+ minutes)
- Include code walkthrough
- Explain multi-agent architecture
- Show configuration and setup
- Suitable for technical audiences