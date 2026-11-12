# Social Post & Thread Templates (Domain-Agnostic)

Use these templates as structural starting points, then verify every draft with `scripts/qc_audit.py`.

## 1. News / Changelog Explainer (Single Post)
```text
[Clear factual headline or change]

- What changed: <metric or feature from source>
- Why it matters: <concrete operational impact>
- Context: <comparison or timeline from source>

Source: <url if appropriate>
```

## 2. Benchmark / Metric Breakdown (Single Post)
```text
<Subject> benchmark results:

• Metric A: <verified value>
• Metric B: <verified value>
• Trade-off / caveat: <verified constraint>

Key takeaway: <one crisp observation without hype>.
```

## 3. Multi-Post Analytical Thread (`1/N`)
- **Post 1 (Hook + Core Fact):** Lead with the main verified number or event (`1/4`).
- **Post 2 (Evidence / Numbers):** 2-3 bullet points of concrete source facts (`2/4`).
- **Post 3 (Implication / Risk):** What readers should watch or be cautious about (`3/4`).
- **Post 4 (Summary + Source Link):** Clean wrap-up and attribution link (`4/4`).
