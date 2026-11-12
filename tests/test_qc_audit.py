import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import qc_audit as qa  # noqa: E402


def test_numeric_grounding_catches_hallucination():
    source = "Acme Engine v2.4 reduced latency by 38% and memory stayed at 120 MB."
    good = "Acme Engine v2.4 reduced latency by 38% with 120 MB peak memory."
    bad = "Acme Engine v2.4 reduced latency by 65% and saves $900/month."

    res_good = qa.audit_post(good, source_text=source)
    assert res_good["passed"] is True

    res_bad = qa.audit_post(bad, source_text=source)
    assert res_bad["passed"] is False
    num_check = next(c for c in res_bad["checks"] if c["code"] == "NUMERIC_GROUNDING")
    assert num_check["passed"] is False
    assert "65" in num_check["detail"]


def test_banned_phrase_and_char_limit():
    res = qa.audit_post("This tool gives 100% guaranteed profit! " + ("word " * 70))
    assert res["passed"] is False
    codes = {c["code"]: c["passed"] for c in res["checks"]}
    assert codes["CHAR_LIMIT"] is False
    assert codes["BANNED_PHRASES"] is False


def test_thread_splitter_keeps_every_post_within_limit():
    long_text = (
        "Open tooling works best when every output is auditable. "
        "Long posts frequently fail on free X accounts because links and citations inflate text length unexpectedly. "
        "Splitting along sentence boundaries preserves readability cleanly across numbered posts. "
        "Wait until each chunk passes weighted length validation before scheduling or opening the browser composer. "
        "Finally keep source URLs intact so readers can verify every claim independently."
    )
    posts = qa.split_into_thread(long_text, max_chars=160, add_numbering=True)
    assert len(posts) >= 3
    assert posts[0].startswith("1/")
    for p in posts:
        assert qa.count_x_weighted_chars(p) <= 160

    report = qa.audit_thread(posts, source_text=long_text, rules={"max_weighted_chars": 160})
    assert report["passed"] is True
