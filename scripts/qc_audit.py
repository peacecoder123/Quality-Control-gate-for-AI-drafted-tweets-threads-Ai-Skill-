#!/usr/bin/env python3
"""
Deterministic Quality Control (QC) Auditor & Thread Splitter for Social Posts.

Zero external dependencies (Python stdlib only). Works on any topic or industry:
- Enforces X weighted character count (http/https URLs count as 23 chars via t.co)
- Detects ungrounded/hallucinated numbers against a reference source text/JSON
- Blocks configurable banned hype or compliance phrases
- Caps hashtag density and checks optional required disclaimers/suffixes
- Splits long drafts cleanly at sentence boundaries into numbered X threads
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

URL_PATTERN = re.compile(r"https?://\S+", re.IGNORECASE)
HASHTAG_PATTERN = re.compile(r"(?<!\w)#([A-Za-z0-9_]+)")
THREAD_MARKER_PATTERN = re.compile(r"^\d+/\d+\s*")
INLINE_THREAD_COUNTER_PATTERN = re.compile(r"\b\d+/\d+\b")
# Matches numbers like 38%, 1,250.75, -4.5, $120M, v2.4 (excluding URLs first)
NUMBER_TOKEN_PATTERN = re.compile(r"(?<![A-Za-z0-9_])[-+]?\d[\d,]*(?:\.\d+)?(?=[%A-Za-z\s.,;:!?)}\]]|$)")

DEFAULT_RULES: Dict[str, Any] = {
    "max_weighted_chars": 280,
    "max_hashtags": 3,
    "require_numeric_grounding": True,
    "banned_phrases": [
        "guaranteed profit",
        "sure shot",
        "buy now",
        "financial advice",
        "100% guaranteed",
    ],
    "required_suffix": "",
}


def count_x_weighted_chars(text: str) -> int:
    """Count X post length treating each http(s) URL as 23 weighted characters."""
    if not text:
        return 0
    return len(URL_PATTERN.sub("X" * 23, text))


def _normalize_numeric_token(tok: str) -> str:
    """Canonicalize numeric tokens for matching (strip commas & leading '+')."""
    cleaned = tok.replace(",", "").strip()
    if cleaned.startswith("+"):
        cleaned = cleaned[1:]
    return cleaned


def extract_numbers(text: str) -> Set[str]:
    """Extract normalized numbers from text while ignoring URLs and thread markers (e.g. 1/4)."""
    if not text:
        return set()
    without_urls = URL_PATTERN.sub(" ", text)
    without_counters = INLINE_THREAD_COUNTER_PATTERN.sub(" ", without_urls)
    found = set()
    for match in NUMBER_TOKEN_PATTERN.findall(without_counters):
        norm = _normalize_numeric_token(match)
        if norm and norm not in ("-", "+"):
            found.add(norm)
    return found


def audit_post(
    text: str,
    source_text: str = "",
    rules: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Run deterministic QC checks on a single post."""
    cfg = dict(DEFAULT_RULES)
    if rules:
        cfg.update(rules)

    clean_text = (text or "").strip()
    checks: List[Dict[str, Any]] = []

    # 1. Non-empty check
    if not clean_text:
        checks.append({"code": "EMPTY_POST", "passed": False, "detail": "Post text is empty."})
        return {"passed": False, "weighted_chars": 0, "checks": checks}

    # 2. Weighted character limit
    max_chars = int(cfg.get("max_weighted_chars", 280))
    weighted_len = count_x_weighted_chars(clean_text)
    checks.append({
        "code": "CHAR_LIMIT",
        "passed": weighted_len <= max_chars,
        "detail": f"{weighted_len} / {max_chars} weighted chars",
    })

    # 3. Banned phrases
    lower_text = clean_text.lower()
    hits = [p for p in cfg.get("banned_phrases", []) if p and p.lower() in lower_text]
    checks.append({
        "code": "BANNED_PHRASES",
        "passed": len(hits) == 0,
        "detail": "None found" if not hits else f"Blocked phrases found: {hits}",
    })

    # 4. Hashtag limit
    max_tags = int(cfg.get("max_hashtags", 3))
    hashtags = HASHTAG_PATTERN.findall(clean_text)
    checks.append({
        "code": "HASHTAG_LIMIT",
        "passed": len(hashtags) <= max_tags,
        "detail": f"{len(hashtags)} / {max_tags} hashtags",
    })

    # 5. Required suffix / attribution
    req_suffix = str(cfg.get("required_suffix") or "").strip()
    if req_suffix:
        checks.append({
            "code": "REQUIRED_SUFFIX",
            "passed": req_suffix.lower() in lower_text,
            "detail": f"Expected suffix containing '{req_suffix}'",
        })

    # 6. Numeric grounding (when source text is provided)
    if cfg.get("require_numeric_grounding", True) and source_text.strip():
        draft_nums = extract_numbers(clean_text)
        source_nums = extract_numbers(source_text)
        ungrounded = sorted(n for n in draft_nums if n not in source_nums)
        checks.append({
            "code": "NUMERIC_GROUNDING",
            "passed": len(ungrounded) == 0,
            "detail": "All numbers match source" if not ungrounded else f"Ungrounded numbers: {ungrounded}",
        })

    overall_passed = all(c["passed"] for c in checks)
    return {
        "passed": overall_passed,
        "weighted_chars": weighted_len,
        "checks": checks,
    }


def split_into_thread(
    long_text: str,
    max_chars: int = 280,
    add_numbering: bool = True,
) -> List[str]:
    """
    Split long text into valid X posts strictly <= max_chars (X weighted),
    preserving sentence/paragraph boundaries where possible.
    """
    raw = re.sub(r"\n{3,}", "\n\n", (long_text or "").strip())
    if not raw:
        return []

    reserve = 6 if add_numbering else 0  # room for "12/12 "
    limit = max(40, max_chars - reserve)

    paragraphs = [p.strip() for p in raw.split("\n\n") if p.strip()]
    sentences: List[str] = []
    for para in paragraphs:
        parts = re.split(r"(?<=[.!?])\s+", para)
        sentences.extend([s.strip() for s in parts if s.strip()])

    chunks: List[str] = []
    current = ""
    for sent in sentences:
        candidate = f"{current} {sent}".strip() if current else sent
        if count_x_weighted_chars(candidate) <= limit:
            current = candidate
            continue

        if current:
            chunks.append(current)
            current = ""

        # If a single sentence is still longer than limit, split by words
        if count_x_weighted_chars(sent) > limit:
            words = sent.split()
            word_buf = ""
            for w in words:
                wc = f"{word_buf} {w}".strip() if word_buf else w
                if count_x_weighted_chars(wc) <= limit:
                    word_buf = wc
                else:
                    if word_buf:
                        chunks.append(word_buf)
                    word_buf = w
            current = word_buf
        else:
            current = sent

    if current:
        chunks.append(current)

    if add_numbering and len(chunks) > 1:
        total = len(chunks)
        return [f"{idx}/{total} {chunk}" for idx, chunk in enumerate(chunks, start=1)]
    return chunks


def audit_thread(
    posts: List[str],
    source_text: str = "",
    rules: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Run deterministic QC across an entire multi-post thread."""
    results = []
    for idx, p in enumerate(posts, start=1):
        res = audit_post(p, source_text=source_text, rules=rules)
        res["post_index"] = idx
        results.append(res)
    return {
        "passed": bool(results) and all(r["passed"] for r in results),
        "post_count": len(results),
        "posts": results,
    }


def _load_text(path_str: str) -> str:
    return Path(path_str).expanduser().read_text(encoding="utf-8")


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Deterministic QC Auditor & Thread Splitter for social posts.")
    src_group = parser.add_mutually_exclusive_group(required=True)
    src_group.add_argument("--text", help="Single draft post text.")
    src_group.add_argument("--file", help="Path to draft text file.")
    src_group.add_argument("--thread-json", help="Path to JSON file containing a list of thread post strings.")

    parser.add_argument("--source", help="Optional path to reference source text/JSON for numeric grounding.")
    parser.add_argument("--rules", help="Optional path to QC rules JSON file.")
    parser.add_argument("--split", action="store_true", help="Split long input into a numbered thread.")
    parser.add_argument("--max-chars", type=int, default=None, help="Override max weighted characters per post.")
    parser.add_argument("--json", action="store_true", help="Output structured JSON.")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    rules = json.loads(_load_text(args.rules)) if args.rules else dict(DEFAULT_RULES)
    if args.max_chars is not None:
        rules["max_weighted_chars"] = args.max_chars

    source_text = _load_text(args.source) if args.source else ""

    if args.thread_json:
        posts = json.loads(_load_text(args.thread_json))
        if not isinstance(posts, list):
            print("Error: --thread-json must contain a JSON array of strings.", file=sys.stderr)
            return 2
        report = audit_thread([str(p) for p in posts], source_text=source_text, rules=rules)
        output: Any = report
    else:
        raw_text = args.text if args.text is not None else _load_text(args.file)
        if args.split:
            posts = split_into_thread(raw_text, max_chars=int(rules.get("max_weighted_chars", 280)))
            report = audit_thread(posts, source_text=source_text, rules=rules)
            output = {"thread_posts": posts, "audit": report}
        else:
            report = audit_post(raw_text, source_text=source_text, rules=rules)
            output = report

    if args.json:
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        if "thread_posts" in output:
            print(f"Split into {len(output['thread_posts'])} post(s) | QC Passed: {output['audit']['passed']}")
            for idx, p in enumerate(output["thread_posts"], start=1):
                print(f"\n[{idx}] ({count_x_weighted_chars(p)} chars)\n{p}")
        elif "posts" in output:
            print(f"Thread QC Passed: {output['passed']} ({output['post_count']} posts)")
            for item in output["posts"]:
                failed = [c["detail"] for c in item["checks"] if not c["passed"]]
                print(f" - Post {item['post_index']}: {'OK' if item['passed'] else 'FAIL -> ' + '; '.join(failed)}")
        else:
            print(f"QC Passed: {output['passed']} ({output['weighted_chars']} weighted chars)")
            for chk in output["checks"]:
                mark = "PASS" if chk["passed"] else "FAIL"
                print(f" [{mark}] {chk['code']}: {chk['detail']}")

    passed = output["audit"]["passed"] if "audit" in output else output["passed"]
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
