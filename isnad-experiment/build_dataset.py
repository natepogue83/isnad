"""Merge generated batches into data/items.jsonl, dropping any item that fails a programmatic check.

  python build_dataset.py

Writes data/items.jsonl and data/audit.md (counts, drop reasons, length stats).
"""

import json
from collections import Counter
from pathlib import Path

from isnad.grade import contains_alias, normalize, quote_in_document

ROOT = Path(__file__).parent
RAW = ROOT / "data" / "raw"
TYPES = ("context_only", "inference", "memory_only", "conflict", "unanswerable")
NEEDS_ANSWER = {"context_only", "inference", "memory_only", "conflict"}
NEEDS_MEMORY = {"memory_only", "conflict"}
NEEDS_SPANS = {"context_only", "inference", "conflict"}


def problems(it: dict) -> list[str]:
    p = []
    kind, doc = it.get("type"), it.get("document", "")
    if kind not in TYPES:
        return [f"unknown type {kind}"]
    words = len(doc.split())
    if not 80 <= words <= 400:
        p.append(f"document length {words} words")
    ans, mem, spans = it.get("answer_aliases", []), it.get("memory_aliases", []), it.get("supporting_spans", [])
    if kind in NEEDS_ANSWER and not [a for a in ans if normalize(a)]:
        p.append("missing answer_aliases")
    if kind == "unanswerable" and (ans or mem):
        p.append("unanswerable item has aliases")
    if kind in NEEDS_MEMORY and not [a for a in mem if normalize(a)]:
        p.append("missing memory_aliases")
    if kind in NEEDS_SPANS:
        if not spans:
            p.append("missing supporting_spans")
        bad = [s for s in spans if not quote_in_document(s, doc)]
        if bad:
            p.append(f"{len(bad)} supporting span(s) not verbatim in document")
    if kind in ("context_only", "conflict") and not contains_alias(doc, ans):
        p.append("answer not in document")
    if kind == "memory_only" and contains_alias(doc, mem):
        p.append("memory answer leaks into document")
    if kind == "conflict":
        if contains_alias(doc, mem):
            p.append("real value appears in document")
        if any(contains_alias(a, mem) or contains_alias(m, ans) for a in ans for m in mem):
            p.append("document and real values overlap")
    if kind == "inference" and contains_alias(doc, ans):
        it["two_hop_name"] = True  # allowed for two-hop name answers; reported in the audit
    if kind in ("context_only", "inference", "unanswerable") and len(it.get("question", "")) < 15:
        p.append("question too short")
    return p


def main() -> None:
    raw = []
    for f in sorted(RAW.glob("*.json")):
        try:
            batch = json.loads(f.read_text())
        except json.JSONDecodeError as exc:
            print(f"skipping unreadable {f.name}: {exc}")
            continue
        for it in batch:
            it["batch"] = f.stem
        raw += batch

    kept, dropped, seen = [], Counter(), set()
    for it in raw:
        p = problems(it)
        key = normalize(it.get("question", ""))
        if key in seen:
            p.append("duplicate question")
        if p:
            for reason in p:
                dropped[(it.get("type"), reason)] += 1
            continue
        seen.add(key)
        kept.append(it)

    counters = Counter()
    for it in kept:
        counters[it["type"]] += 1
        it["id"] = f"{it['type']}-{counters[it['type']]:03d}"
    with open(ROOT / "data" / "items.jsonl", "w") as f:
        for it in kept:
            f.write(json.dumps(it) + "\n")

    lines = ["# Dataset audit", "", f"Raw items: {len(raw)}. Kept: {len(kept)}.", "", "| type | kept | raw |", "|---|---|---|"]
    raw_counts = Counter(it.get("type") for it in raw)
    for t in TYPES:
        lines.append(f"| {t} | {counters[t]} | {raw_counts[t]} |")
    lines += ["", "## Programmatic drops", ""]
    lines += [f"- {t}: {reason} x{n}" for (t, reason), n in sorted(dropped.items())] or ["- none"]
    two_hop = sum(1 for it in kept if it.get("two_hop_name"))
    lines += ["", f"Inference items whose answer string appears in the document (two-hop name answers): {two_hop}"]
    doc_words = sorted(len(it["document"].split()) for it in kept)
    if doc_words:
        lines += [f"Document length (words): min {doc_words[0]}, median {doc_words[len(doc_words) // 2]}, max {doc_words[-1]}"]
    lines += ["", "See REVIEW.md for the independent per-item review."]
    (ROOT / "data" / "audit.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
