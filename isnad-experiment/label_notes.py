"""Second-pass labels: does a false-grounded answer's caveat note disclose that it did not come from the document?

The main grader only looks at the citation (plain) or chain (isnad). A model can still attach a document
quote while saying in its note "the document doesn't name him; this is from general knowledge". That is
disclosed, though a product that shows only the citation would still mislead its user. This script exports
those rows for independent judges and imports their labels.

  python label_notes.py export > to_label.json
  python label_notes.py import labels.json        # writes results/note_disclosure.jsonl

A second set of labels covers the opposite case: abstentions whose note still states the answer.

  python label_notes.py export-answers > to_label.json
  python label_notes.py import-answers labels.json   # writes results/note_answers.jsonl

Each label is the majority of three blinded judges (see results/note_disclosure.md and results/note_answers.md).
Import refuses a label file that misses an exported row, labels a row twice, or labels a row that wasn't exported.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent


def key(r: dict) -> str:
    return f"{r['model']}|{r['condition']}|{r['item_id']}|{r['rep']}"


def rows():
    for d in sorted((ROOT / "results").iterdir()):
        f = d / "results.jsonl"
        if d.name == "pilot" or d.name.startswith("dry-run") or not f.exists():
            continue
        for line in f.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                if r["status"] == "ok":
                    yield r


def export() -> list[dict]:
    """False-grounded answers with a note: does the note disclose that the answer isn't from the document?"""
    items = {json.loads(l)["id"]: json.loads(l) for l in (ROOT / "data" / "items.jsonl").read_text().splitlines() if l.strip()}
    out = []
    for r in rows():
        note = (r["parsed"].get("note") or "").strip()
        if not r["grade"]["false_grounding"] or not note:
            continue  # no note: silent by construction, no judgment needed
        it = items[r["item_id"]]
        out.append({
            "key": key(r),
            "question": it["question"],
            "document": it["document"],
            "answer": r["parsed"].get("answer"),
            "presented_sources": r["parsed"].get("citation") or r["parsed"].get("chain"),
            "note": note,
        })
    return out


def export_answers() -> list[dict]:
    """Abstentions whose note names a keyed value: does the note still give the answer?"""
    items = {json.loads(l)["id"]: json.loads(l) for l in (ROOT / "data" / "items.jsonl").read_text().splitlines() if l.strip()}
    out = []
    for r in rows():
        if not r["grade"].get("note_answer_candidate"):
            continue
        it = items[r["item_id"]]
        out.append({"key": key(r), "question": it["question"], "document": it["document"],
                    "answer_field": r["parsed"].get("answer"), "note": (r["parsed"].get("note") or "").strip()})
    return out


def import_labels(path: str, expected: list[dict], out_name: str) -> None:
    labels = json.loads(Path(path).read_text())
    want = {e["key"] for e in expected}
    got = [lab["key"] for lab in labels]
    dupes = sorted({k for k in got if got.count(k) > 1})
    missing, extra = sorted(want - set(got)), sorted(set(got) - want)
    if dupes or missing or extra:
        raise SystemExit(f"label file rejected: {len(missing)} missing, {len(dupes)} duplicated, {len(extra)} unexpected "
                         f"(e.g. {(missing + dupes + extra)[:3]})")
    with open(ROOT / "results" / out_name, "w") as f:
        for lab in sorted(labels, key=lambda l: l["key"]):
            f.write(json.dumps(lab) + "\n")
    print(f"wrote {len(labels)} labels to results/{out_name}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "export":
        print(json.dumps(export(), ensure_ascii=False))
    elif cmd == "export-answers":
        print(json.dumps(export_answers(), ensure_ascii=False))
    elif cmd == "import":
        import_labels(sys.argv[2], export(), "note_disclosure.jsonl")
    elif cmd == "import-answers":
        import_labels(sys.argv[2], export_answers(), "note_answers.jsonl")
    else:
        raise SystemExit(__doc__)
