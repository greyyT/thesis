---
layout: section
---

# Appendix

## Additional Resources

---

# Quick Reference: Key Talking Points

<div class="grid grid-cols-1 gap-6">

<div v-click>
  <h3 class="text-blue-500">For Executives</h3>
  <ul>
    <li>ROI of $150K+ per 100 hires</li>
    <li>75% reduction in missed talent</li>
    <li>Competitive advantage through hidden talent pools</li>
  </ul>
</div>

<div v-click>
  <h3 class="text-green-500">For HR Teams</h3>
  <ul>
    <li>90% time reduction</li>
    <li>Enhances (not replaces) human judgment</li>
    <li>Complete audit trail</li>
  </ul>
</div>

<div v-click>
  <h3 class="text-purple-500">For Technical Audience</h3>
  <ul>
    <li>API-first architecture</li>
    <li>OpenAI GPT-4 + Milvus vector DB</li>
    <li>Cloud-native scalable design</li>
  </ul>
</div>

</div>

---

# Top 3 FAQs

<v-clicks>

## Q: How does this integrate with our ATS?
**A:** API-first design works with Workday, Greenhouse, Lever, and others. 2-week integration.

## Q: What about bias and compliance?
**A:** Built-in bias detection, full audit trail, GDPR/EEOC compliant, explainable AI decisions.

## Q: Implementation timeline?
**A:** 2-week pilot → 6-8 week full deployment. We handle everything.

</v-clicks>

---

# Technical Architecture

```mermaid {scale: 0.8}
graph TB
    A[User Interface] --> B[Supervisor Agent]
    B --> C[Sourcing Agent]
    B --> D[Screening Agent]
    B --> E[Critic Agent]
    E --> F[HITL Agent]
    F --> G[Data Steward Agent]
    
    D --> H[Milvus Vector DB]
    D --> I[OpenAI GPT-4]
    F --> J[Redis State Store]
    G --> K[Audit Logs]
    
    style A fill:#f9f,stroke:#333,stroke-width:4px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style E fill:#fbf,stroke:#333,stroke-width:2px
```

---

# Contact & Resources

<div class="grid grid-cols-2 gap-8">

<div>

## Get in Touch
- 📧 lelouvincx@gmail.com
- 🔗 github.com/lelouvincx/thesis
- 💼 LinkedIn: /in/lelouvincx

</div>

<div>

## Resources Available
- 📊 ROI Calculator
- 📄 Integration Guide
- 🎥 Demo Recording
- 📚 Technical Documentation
- 🧪 Pilot Program Details

</div>

</div>

<div class="mt-8 text-center">
  <div class="text-2xl font-bold">Ready to transform your hiring process?</div>
</div>