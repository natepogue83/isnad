"""Build the blinded, shuffled batches for the second round of note judging (blind_note_judges.js).

  python judging/make_blind_batches.py OUT_DIR

Writes OUT_DIR/disclosure_{0,1,2}.json, OUT_DIR/note_answer_{0,1,2}.json and the two *_map.json files that map
each opaque record id back to its response. The batches carry no model name or condition, and records from all
models and conditions are shuffled together, so judges cannot tell whose note they are reading.

Disclosure: every false-grounded response with a non-empty note (139).
Answer in note: every abstention whose note asserts a keyed answer (grade field note_answer_candidate, 114), plus
60 controls drawn at random from the other 1,529 abstentions with a non-empty note, to check what the scan misses.
"""

import hashlib
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODELS = ["claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-5-5", "gpt-5.5", "gpt-5.4-mini"]


def main(out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    items = {json.loads(l)["id"]: json.loads(l) for l in (ROOT / "data" / "items.jsonl").open()}
    rows = [json.loads(l) for m in MODELS for l in (ROOT / "results" / m / "results.jsonl").open()]
    key = lambda r: f"{r['model']}|{r['condition']}|{r['item_id']}|{r['rep']}"
    bid = lambda k, salt: "r" + hashlib.sha1((salt + k).encode()).hexdigest()[:8]

    dis = []
    for r in rows:
        note = (r["parsed"].get("note") or "").strip()
        if r["grade"]["false_grounding"] and note:
            it = items[r["item_id"]]
            dis.append({"id": bid(key(r), "d"), "question": it["question"], "document": it["document"],
                        "answer": r["parsed"].get("answer"),
                        "presented_sources": r["parsed"].get("citation") or list(r["parsed"].get("chain") or []),
                        "note": note, "_key": key(r)})
    random.Random(2026).shuffle(dis)

    cand = [r for r in rows if r["grade"]["note_answer_candidate"]]
    pool = [r for r in rows if not r["grade"]["answered"] and (r["parsed"].get("note") or "").strip()
            and r["type"] in ("memory_only", "conflict", "unanswerable") and not r["grade"]["note_answer_candidate"]]
    ctrl = random.Random(7).sample(pool, 60)
    ain = []
    for r, kind in [(r, "candidate") for r in cand] + [(r, "control") for r in ctrl]:
        it = items[r["item_id"]]
        ain.append({"id": bid(key(r), "a"), "question": it["question"], "document": it["document"],
                    "answer_field": r["parsed"].get("answer"), "note": r["parsed"]["note"].strip(),
                    "_key": key(r), "_kind": kind})
    random.Random(2027).shuffle(ain)

    def write_batches(recs: list[dict], prefix: str, n: int) -> None:
        size = -(-len(recs) // n)
        for b in range(n):
            part = [{k: v for k, v in x.items() if not k.startswith("_")} for x in recs[b * size:(b + 1) * size]]
            (out / f"{prefix}_{b}.json").write_text(json.dumps(part, ensure_ascii=False, indent=1))
        (out / f"{prefix}_map.json").write_text(
            json.dumps({x["id"]: {k: x[k] for k in x if k.startswith("_")} for x in recs}, indent=1))

    write_batches(dis, "disclosure", 3)
    write_batches(ain, "note_answer", 3)
    print(f"disclosure records {len(dis)}; answer-in-note records {len(ain)} "
          f"(candidates {len(cand)}, controls {len(ctrl)} from a pool of {len(pool)})")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(Path(sys.argv[1]))
