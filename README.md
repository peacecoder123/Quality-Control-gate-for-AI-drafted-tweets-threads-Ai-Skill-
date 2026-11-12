# QC Tweet Composer

> **Developer:** Radhe Wankhade · [@RadheWankhade01](https://x.com/RadheWankhade01) on X

Topic-agnostic AI & human **Tweet / Thread Composer** with a **deterministic Quality Control (QC) gate** built in pure Python (zero pip dependencies).

Stops AI-drafted posts from hallucinating fake numbers, exceeding X's `t.co`-weighted 280-character budget, using banned compliance/hype phrases, or shipping messy unnumbered threads.

## Why Use This?

LLMs are great at summarizing articles, changelogs, and reports into punchy social posts — until they invent a `35%` metric that wasn't in your text or write a 310-character tweet that breaks X free accounts.

This toolkit adds a **deterministic verification layer** between drafting and publishing:

- **Numeric Grounding Check:** Extracts numbers, currency values, and percentages from the draft and verifies every figure appears in your source text (while ignoring thread counters like `1/4`).
- **Exact X Character Weighting:** Counts every `http(s)://...` link as `23` chars (`t.co` behavior).
- **Configurable Compliance / Hype Guardrail:** Flags banned phrases, excessive hashtags, or missing attribution/disclaimer suffixes via JSON rules.
- **Smart Thread Splitter:** Splits long commentary at sentence boundaries into `1/N` numbered posts strictly under your character cap.
- **Agent Skill Ready:** Drop straight into `.agents/skills/qc-tweet-composer` so AI coding assistants automatically QC-check every social draft.

## Quick Start

### Audit a single post against a source file

```bash
python scripts/qc_audit.py \
  --text "Acme v2.4 cut p99 latency by 38% while keeping memory under 120 MB." \
  --source examples/sample_source.json \
  --rules examples/sample_rules.json
```

### Split a long breakdown into a valid X thread

```bash
python scripts/qc_audit.py \
  --file long_notes.txt \
  --split \
  --json
```

### Use as an Agent Skill

```bash
git clone https://github.com/<your-username>/qc-tweet-composer.git .agents/skills/qc-tweet-composer
```

## Running Tests

```bash
pytest -v
```

## License

MIT

