---
name: qc-tweet-composer
description: >-
  Draft and deterministically quality-check (QC) social posts and threads against verified source
  facts, character limits (with t.co 23-char URL weighting), banned hype/compliance terms, and
  hallucinated numbers. Use when the user asks to write or review a tweet, announcement, or thread
  from an article, changelog, report, or dataset before publishing.
---

# Evidence-Grounded Tweet & Thread Composer

Compose crisp single posts or numbered threads grounded in provided source facts, then pass every draft through a deterministic Quality Control (QC) validator before showing or publishing it.

## Workflow Steps

1. **Gather Grounding Source & Rules**
   - Read the user's source material (article summary, JSON facts, release notes, or dataset).
   - Consult [references/post_templates.md](./references/post_templates.md) for structure presets.
   - Use default QC rules or load a custom rules JSON (see [examples/sample_rules.json](./examples/sample_rules.json)).

2. **Draft Within Evidence Constraints**
   - Cite only figures, names, percentages, and URLs present in the provided source text.
   - Avoid hype, clickbait, or prohibited phrases configured in the ruleset.
   - Keep standard single posts `<= 280` X-weighted characters (every `http(s)` URL counts as `23` chars).

3. **Run Deterministic QC Audit**
   - Run [scripts/qc_audit.py](./scripts/qc_audit.py):
     ```bash
     python scripts/qc_audit.py --text "Draft post..." --source path/to/source.txt --rules path/to/rules.json
     ```
   - For multi-paragraph text that exceeds 280 weighted chars, use `--split` to chunk cleanly into a numbered thread:
     ```bash
     python scripts/qc_audit.py --file long_draft.txt --split --json
     ```

4. **Fix Any Failed Checks**
   - If QC reports `HALUCINATED_OR_UNGROUNDED_NUMBERS`, `OVER_CHAR_LIMIT`, `BANNED_PHRASE`, or `TOO_MANY_HASHTAGS`, revise the draft and re-run `qc_audit.py` until `"passed": true`.

## Verification
- Confirm `qc_audit.py` exits with code `0` (`PASSED`).
- Run `pytest -v` in the repo root to validate all QC and thread-splitting unit tests.
