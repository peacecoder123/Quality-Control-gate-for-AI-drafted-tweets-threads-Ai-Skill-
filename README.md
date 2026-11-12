# QC Tweet Composer

> **Developer:** Radhe Wankhade · [@RadheWankhade01](https://x.com/RadheWankhade01) on X

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python) ![Zero pip deps](https://img.shields.io/badge/pip%20deps-zero%20(stdlib%20only)-brightgreen) ![License: MIT](https://img.shields.io/badge/License-MIT-yellow) ![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

Topic-agnostic **Tweet / Thread Composer** with a **deterministic Quality Control (QC) gate** — zero pip dependencies, pure Python stdlib.

Stops AI-drafted posts from hallucinating fake numbers, exceeding X's `t.co`-weighted 280-character budget, using banned compliance/hype phrases, or shipping messy unnumbered threads.

---

## The Problem

LLMs are great at summarizing articles, changelogs, and reports into punchy social posts — until they:

- Invent a **`38%` metric** that wasn't in your source text
- Write a **310-character tweet** that breaks on X free accounts
- Use phrases like **"guaranteed profit"** that violate financial compliance rules
- Generate a thread where **post 3 is 295 chars** but post 4 is 12 chars

This toolkit adds a **deterministic verification layer** between drafting and publishing — no LLM, no randomness, no hallucinations in the QC step itself.

---

## How It Works

```
Your draft text + source document
         │
         ▼
┌──────────────────────────────────────────┐
│  CHECK 1: Weighted char count ≤ 280?     │  ← URLs count as 23 chars (t.co)
│  CHECK 2: Any banned/hype phrases?       │  ← "guaranteed profit", "sure shot"...
│  CHECK 3: Hashtag count ≤ limit?         │  ← Default max: 3
│  CHECK 4: Required suffix present?       │  ← e.g. "Not financial advice"
│  CHECK 5: Every number in source text?   │  ← "38%" must exist in your article
└──────────────────────────────────────────┘
         │
    PASS ✅ or FAIL ❌ (with specific reason)
```

**All checks are deterministic** — same input always gives same output. No API calls, no LLM, no network.

---

## Features

| Feature | Detail |
|---|---|
| **Numeric Grounding** | Extracts every number, %, currency from draft and verifies each exists in source text |
| **Exact t.co Counting** | Every `http(s)://...` URL counted as exactly **23 chars** — matches X composer |
| **Configurable Guardrails** | Banned phrases, hashtag cap, required suffixes — all JSON-configurable |
| **Thread Splitter** | Splits long text at sentence/paragraph boundaries into `1/N` numbered posts |
| **Thread Auditor** | QC-checks every post in a multi-post thread individually |
| **Zero Dependencies** | Python stdlib only — no `pip install` needed |
| **Agent Skill Ready** | `SKILL.md` at repo root for Antigravity, Gemini CLI, Claude Code, Cursor |

---

## Quick Start

### 1. Audit a single post

```bash
python scripts/qc_audit.py \
  --text "Acme Q3 results: revenue up 38%, net profit ₹1,250 Cr. Not financial advice." \
  --source examples/sample_source.json \
  --rules examples/sample_rules.json
```

**Terminal output — PASS:**

```
QC Passed: True (71 weighted chars)
 [PASS] CHAR_LIMIT: 71 / 280 weighted chars
 [PASS] BANNED_PHRASES: None found
 [PASS] HASHTAG_LIMIT: 0 / 3 hashtags
 [PASS] NUMERIC_GROUNDING: All numbers match source
```

---

**Terminal output — FAIL (hallucinated number):**

```bash
python scripts/qc_audit.py \
  --text "Acme Q3: revenue up 42%, profit ₹1,250 Cr. Not financial advice." \
  --source examples/sample_source.json \
  --rules examples/sample_rules.json
```

```
QC Passed: False (63 weighted chars)
 [PASS] CHAR_LIMIT: 63 / 280 weighted chars
 [PASS] BANNED_PHRASES: None found
 [PASS] HASHTAG_LIMIT: 0 / 3 hashtags
 [FAIL] NUMERIC_GROUNDING: Ungrounded numbers: ['42']
```

> `42` is not in the source text — the LLM made it up. QC blocked it. ✅

---

**Terminal output — FAIL (banned phrase + too long):**

```bash
python scripts/qc_audit.py \
  --text "GUARANTEED PROFIT setup on NIFTY 50! Buy now before the breakout. #stocks #trading #nse #sensex #bull"
```

```
QC Passed: False (104 weighted chars)
 [PASS] CHAR_LIMIT: 104 / 280 weighted chars
 [FAIL] BANNED_PHRASES: Blocked phrases found: ['guaranteed profit', 'buy now']
 [FAIL] HASHTAG_LIMIT: 5 / 3 hashtags
```

---

### 2. Split a long article breakdown into a thread

```bash
python scripts/qc_audit.py \
  --file long_analysis.txt \
  --split \
  --max-chars 240
```

**Terminal output:**

```
Split into 4 post(s) | QC Passed: True

[1] (218 chars)
1/4 Acme Technologies Q3 FY26 results are out. Revenue came in at ₹4,820 Cr — up 38% YoY, beating
analyst estimates of ₹4,500 Cr by a healthy margin.

[2] (231 chars)
2/4 Net profit stood at ₹1,250 Cr (+22% YoY). EBITDA margin expanded 180 bps to 24.3%. Management
guided for continued double-digit growth through FY27, citing strong deal pipeline.

[3] (198 chars)
3/4 Key risk: 62% of revenue still from top 5 clients. Any churn would hurt disproportionately.
Forex headwinds also flagged — ₹15 Cr impact expected next quarter.

[4] (67 chars)
4/4 Verdict: solid execution, manageable risks. Not financial advice.
```

---

### 3. Audit an entire thread from a JSON file

```bash
python scripts/qc_audit.py \
  --thread-json my_thread.json \
  --source examples/sample_source.json \
  --rules examples/sample_rules.json
```

**Terminal output:**

```
Thread QC Passed: True (4 posts)
 - Post 1: OK
 - Post 2: OK
 - Post 3: OK
 - Post 4: OK
```

---

### 4. JSON output (pipe into other tools)

```bash
python scripts/qc_audit.py \
  --text "Revenue up 38%, profit ₹1,250 Cr." \
  --source examples/sample_source.json \
  --json
```

**Terminal output:**

```json
{
  "passed": true,
  "weighted_chars": 44,
  "checks": [
    {"code": "CHAR_LIMIT", "passed": true, "detail": "44 / 280 weighted chars"},
    {"code": "BANNED_PHRASES", "passed": true, "detail": "None found"},
    {"code": "HASHTAG_LIMIT", "passed": true, "detail": "0 / 3 hashtags"},
    {"code": "NUMERIC_GROUNDING", "passed": true, "detail": "All numbers match source"}
  ]
}
```

---

## Rules Configuration

The QC behavior is fully configurable via a JSON file (see `examples/sample_rules.json`):

```json
{
  "max_weighted_chars": 280,
  "max_hashtags": 3,
  "require_numeric_grounding": true,
  "banned_phrases": [
    "guaranteed profit",
    "sure shot",
    "buy now",
    "financial advice",
    "100% guaranteed"
  ],
  "required_suffix": "Not financial advice"
}
```

| Rule | Type | Description |
|---|---|---|
| `max_weighted_chars` | `int` | Max t.co-weighted characters (default: 280) |
| `max_hashtags` | `int` | Max hashtags allowed in a single post (default: 3) |
  | `require_numeric_grounding` | `bool` | Fail if draft contains numbers not in source |
| `banned_phrases` | `list[str]` | Case-insensitive phrases that cause instant FAIL |
| `required_suffix` | `str` | String that must appear somewhere in the post |

---

## Numeric Grounding — How It Works

The grounding check extracts every number-like token from the draft and verifies each one appears in the source text:

**Extracted tokens:**
- `38%` → `38`
- `₹1,250 Cr` → `1250`
- `v2.4` → `2`, `4`
- `1/4` (thread counter) → **ignored** ✅

**Thread counters like `1/4`, `2/5` are automatically excluded** — they're structural, not factual claims.

```
Draft: "Revenue up 42%, profit ₹1,250 Cr."
        ↑              ↑
      "42" ← NOT in source → FAIL
                     "1250" ← IS in source → PASS
```

---

## CLI Reference

```
usage: qc_audit.py [--text TEXT | --file FILE | --thread-json FILE]
                   [--source SOURCE]
                   [--rules RULES]
                   [--split] [--max-chars MAX_CHARS]
                   [--json]

Input (pick one):
  --text TEXT          Single draft post text (inline)
  --file FILE          Path to UTF-8 draft text file
  --thread-json FILE   Path to JSON array of thread post strings

Options:
  --source FILE        Reference source text/JSON for numeric grounding
  --rules FILE         JSON config file for QC rules
  --split              Split --text or --file into a numbered thread
  --max-chars INT      Override max weighted chars per post (default: 280)
  --json               Output structured JSON

Exit codes: 0 = QC passed, 1 = QC failed, 2 = input error
```

---

## Install as an Agent Skill

```bash
# Workspace skill
git clone https://github.com/RadheWankhade01/qc-tweet-composer.git \
  .agents/skills/qc-tweet-composer

# Global skill (Antigravity / Gemini CLI)
git clone https://github.com/RadheWankhade01/qc-tweet-composer.git \
  ~/.gemini/config/skills/qc-tweet-composer
```

---

## Running Tests

```bash
pytest -v
```

**Expected output:**

```
tests/test_qc_audit.py::test_char_count_with_url PASSED
tests/test_qc_audit.py::test_qc_pass_grounded_post PASSED
tests/test_qc_audit.py::test_qc_fail_ungrounded_number PASSED

3 passed in 0.01s
```

---

## Project Structure

```
qc-tweet-composer/
├── SKILL.md                        ← Agent skill definition
├── README.md                       ← This file
├── LICENSE                         ← MIT
├── .gitignore
├── scripts/
│   └── qc_audit.py                 ← Main CLI (zero pip dependencies)
├── examples/
│   ├── sample_rules.json           ← Example QC rules configuration
│   └── sample_source.json          ← Example source text for grounding
├── references/
│   └── post_templates.md           ← Reusable tweet/thread templates
└── tests/
    └── test_qc_audit.py            ← Pytest tests (stdlib only)
```

---

## Use Cases

| Who | How they use it |
|---|---|
| **Developers** | QC-check changelogs/release notes before tweeting |
| **Finance accounts** | Verify earnings numbers, block compliance violations |
| **AI automation pipelines** | Add as a gate between LLM draft and X publisher |
| **Marketers** | Enforce brand voice rules, hashtag limits, required disclaimers |
| **Journalists** | Verify numbers in social post match article before publishing |

---

## License

MIT — free to use, modify, and distribute.

---

> Built by [Radhe Wankhade](https://x.com/RadheWankhade01) as an open-source contribution.
> Star ⭐ the repo if it caught a hallucinated number before it went live!
