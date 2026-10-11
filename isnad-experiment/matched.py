"""The matched-instruction pilot (MATCHED.md): item list, blinded note batches, label import and report.

  python matched.py items                      # write data/matched_items.jsonl (90 items, fixed seed)
  python matched.py batches OUT_DIR            # blinded batches of false-grounded notes for the note judges
  python matched.py import-labels VOTES.json   # majority labels -> results/matched/note_disclosure.jsonl
  python matched.py report                     # results/matched/report.md and summary.json

The runs themselves use run.py (see MATCHED.md for the exact commands), writing to results/matched/<model>/.
"""

import hashlib
import json
import math
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).parent
ITEMS_PATH = ROOT / "data" / "matched_items.jsonl"
OUT = ROOT / "results" / "matched"
LABELS = OUT / "note_disclosure.jsonl"
MODELS = ["claude-sonnet-5-5", "gpt-5.4-mini"]
ARMS = ["plainmatch-open", "label-open", "isnadmatch-open"]
REFS = ["plain-open", "isnad-open"]  # published single runs on the same items, made on an earlier day
PER_TYPE = {"memory_only": 54, "conflict": 12, "context_only": 12, "inference": 12}  # all 54 memory-only items
REPS = 2
SEED = 20261010
BOOT = 10_000


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()] if path.exists() else []


def make_items() -> None:
    items = load_jsonl(ROOT / "data" / "items.jsonl")
    rng = random.Random(SEED)
    chosen = []
    for kind, n in PER_TYPE.items():
        pool = sorted((it for it in items if it["type"] == kind), key=lambda it: it["id"])
        chosen += sorted(rng.sample(pool, n), key=lambda it: it["id"])
    # ASCII-escaped, so a Windows Python reading it with its default code page still sees the same text.
    ITEMS_PATH.write_text("".join(json.dumps(it) + "\n" for it in chosen), encoding="utf-8")
    print(f"wrote {len(chosen)} items to {ITEMS_PATH.relative_to(ROOT)}: {dict(Counter(it['type'] for it in chosen))}")


def key(r: dict) -> str:
    return f"{r['model']}|{r['condition']}|{r['item_id']}|{r['rep']}"


def matched_rows() -> list[dict]:
    return [r for m in MODELS for r in load_jsonl(OUT / m / "results.jsonl")]


def make_batches(out: Path, n_batches: int = 3) -> None:
    """Every false-grounded matched response with a non-empty note, blinded (no model, no condition) and shuffled."""
    out.mkdir(parents=True, exist_ok=True)
    items = {it["id"]: it for it in load_jsonl(ITEMS_PATH)}
    recs = []
    for r in matched_rows():
        note = ((r.get("parsed") or {}).get("note") or "").strip()
        if r.get("grade") and r["grade"]["false_grounding"] and note:
            p, it = r["parsed"], items[r["item_id"]]
            if r["condition"].startswith("isnad"):
                shown = list(p.get("chain") or [])
            elif r["condition"].startswith("label"):
                shown = {"source_label": p.get("source"), "citation": p.get("citation")}
            else:
                shown = p.get("citation")
            recs.append({"id": "m" + hashlib.sha1(key(r).encode()).hexdigest()[:8], "question": it["question"],
                         "document": it["document"], "answer": p.get("answer"), "presented_sources": shown,
                         "note": note, "_key": key(r)})
    random.Random(SEED).shuffle(recs)
    size = max(1, -(-len(recs) // n_batches))
    for b in range(n_batches):
        part = [{k: v for k, v in x.items() if not k.startswith("_")} for x in recs[b * size:(b + 1) * size]]
        (out / f"disclosure_{b}.json").write_text(json.dumps(part, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "disclosure_map.json").write_text(json.dumps({x["id"]: x["_key"] for x in recs}, indent=1), encoding="utf-8")
    print(f"{len(recs)} false-grounded notes in {n_batches} batches under {out}")


def import_labels(votes_path: Path, map_path: Path) -> None:
    """votes: a JSON list of {id, judge, disclosed, mixed, evidence}; three judges per record; majority decides."""
    votes = json.loads(votes_path.read_text(encoding="utf-8"))
    id_map = json.loads(map_path.read_text(encoding="utf-8"))
    by_id = defaultdict(list)
    for v in votes:
        if v["id"] not in id_map:
            raise SystemExit(f"unexpected id {v['id']}")
        by_id[v["id"]].append(v)
    missing = set(id_map) - set(by_id)
    if missing:
        raise SystemExit(f"{len(missing)} records have no votes, e.g. {sorted(missing)[:3]}")
    if any(len(vs) != 3 for vs in by_id.values()):
        raise SystemExit("every record needs exactly 3 votes")
    OUT.mkdir(parents=True, exist_ok=True)
    with open(LABELS, "w", encoding="utf-8") as f:
        for bid, vs in sorted(by_id.items(), key=lambda kv: id_map[kv[0]]):
            yes = sum(bool(v["disclosed"]) for v in vs)
            majority = yes * 2 > len(vs)
            f.write(json.dumps({"key": id_map[bid], "disclosed": majority, "votes_yes": yes, "votes": len(vs),
                                "mixed_votes": sum(bool(v.get("mixed")) for v in vs),
                                "evidence": next((v.get("evidence") for v in vs if bool(v["disclosed"]) == majority), None)},
                               ensure_ascii=False) + "\n")
    (OUT / "note_disclosure_votes.jsonl").write_text(
        "".join(json.dumps({**v, "key": id_map[v["id"]]}, ensure_ascii=False) + "\n" for v in votes), encoding="utf-8")
    print(f"labels for {len(by_id)} records -> {LABELS.relative_to(ROOT)}")


# ---------- statistics ----------

def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def sign_test(pos: int, neg: int) -> float:
    """Exact two-sided sign test."""
    n = pos + neg
    if n == 0:
        return 1.0
    k = min(pos, neg)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def paired(a: dict, b: dict) -> dict:
    """a, b: item -> per-item rate. Mean difference a - b over shared items, item-bootstrap 95% CI, sign test,
    and the pre-registered call (MATCHED.md): above or below zero only if the CI excludes zero AND sign p < 0.05."""
    ids = sorted(set(a) & set(b))
    if not ids:
        return {"n_items": 0}
    diffs = [a[i] - b[i] for i in ids]
    rng = random.Random(SEED)
    boots = sorted(sum(diffs[rng.randrange(len(diffs))] for _ in diffs) / len(diffs) for _ in range(BOOT))
    lo, hi = boots[int(0.025 * BOOT)], boots[int(0.975 * BOOT) - 1]
    pos, neg = sum(d > 0 for d in diffs), sum(d < 0 for d in diffs)
    p = sign_test(pos, neg)
    call = "above zero" if lo > 0 and p < 0.05 else "below zero" if hi < 0 and p < 0.05 else "no clear difference"
    if call == "no clear difference" and hi < 0.10 and lo > -0.10:
        call += ", under 10 pts either way"
    return {"n_items": len(ids), "diff": sum(diffs) / len(diffs), "ci": (lo, hi), "items_higher": pos,
            "items_lower": neg, "sign_p": p, "call": call}


def gap_share(ref: dict, mid: dict, low: dict) -> dict | None:
    """Share of the ref - low gap that mid closes, (ref - mid) / (ref - low), with an item-bootstrap interval."""
    ids = sorted(set(ref) & set(mid) & set(low))
    if not ids:
        return None
    def share(sample):
        gap = sum(ref[i] - low[i] for i in sample)
        return None if gap <= 0 else sum(ref[i] - mid[i] for i in sample) / gap
    point = share(ids)
    if point is None or sum(ref[i] - low[i] for i in ids) / len(ids) < 0.10:
        return {"share": point, "ci": None, "note": "gap under 10 pts, not reported"}
    rng = random.Random(SEED)
    boots = sorted(s for s in (share([ids[rng.randrange(len(ids))] for _ in ids]) for _ in range(BOOT)) if s is not None)
    return {"share": point, "ci": (boots[int(0.025 * len(boots))], boots[int(0.975 * len(boots)) - 1])}


# ---------- report ----------

def pct(k: int, n: int) -> str:
    if n == 0:
        return "n/a"
    lo, hi = wilson(k, n)
    return f"{k}/{n} ({100 * k / n:.0f}%; {100 * lo:.0f}-{100 * hi:.0f})"


def report() -> None:
    items = {it["id"]: it for it in load_jsonl(ITEMS_PATH)}
    # Published labels cover the reference runs; the pilot's own labels cover its rows. Keys never overlap.
    labels = {l["key"]: l["disclosed"] for path in (ROOT / "results" / "note_disclosure.jsonl", LABELS) for l in load_jsonl(path)}
    rows = [r for r in matched_rows() if r["item_id"] in items]
    errors = Counter((r["model"], r["condition"]) for m in MODELS for r in load_jsonl(OUT / m / "errors.jsonl"))
    refs = [dict(r, rep=r.get("rep", 0)) for m in MODELS for r in load_jsonl(ROOT / "results" / m / "results.jsonl")
            if r["item_id"] in items and r["condition"] in REFS]
    ok = lambda r: r.get("status") == "ok" and r.get("grade")
    q_real = lambda r: r["grade"]["n_quotes"] - r["grade"]["invalid_quotes"] > 0

    def silent(r):  # True / False, or None while a non-empty note on a false-grounded row is unlabeled
        if not r["grade"]["false_grounding"]:
            return False
        if not (r["parsed"].get("note") or "").strip():
            return True
        d = labels.get(key(r))
        return None if d is None else not d

    L = ["# Matched-instruction pilot: report", "",
         "Generated by `python matched.py report`. Design and pre-registered analysis: `MATCHED.md`. "
         "Pooled percentages carry 95% Wilson intervals, which treat the runs of an item as independent and so are too narrow; "
         "the paired comparisons resample whole items instead.", ""]
    summary = {}
    for m in MODELS:
        mrows = [r for r in rows if r["model"] == m]
        if not mrows:
            L += [f"## {m}", "", "No results yet.", ""]
            continue
        efforts = {r.get("effort") for r in mrows}
        if len(efforts) != 1:
            raise SystemExit(f"{m}: rows mix effort settings {efforts}")
        L += [f"## {m} (effort {efforts.pop()})", ""]
        # Completeness.
        L += ["| condition | rows | not ok (refusal / truncated / invalid) | errors | items short of their runs |", "|---|---|---|---|---|"]
        for c in ARMS:
            cr = [r for r in mrows if r["condition"] == c]
            got = Counter(r["item_id"] for r in cr if ok(r))
            short = sorted(i for i in items if got[i] < REPS)
            L.append(f"| {c} | {len(cr)} | {sum(not ok(r) for r in cr)} | {errors[(m, c)]} | "
                     f"{len(short)}{': ' + ', '.join(short[:8]) + (' ...' if len(short) > 8 else '') if short else ''} |")
        L.append("")
        allrows = mrows + [r for r in refs if r["model"] == m]
        conds = ARMS + REFS
        per = {c: [r for r in allrows if r["condition"] == c and ok(r)] for c in conds}

        # Primary: memory-only questions.
        L += ["### Memory-only questions (primary)", "",
              "- **False grounding** (format's own rule): a remembered answer presented as coming from the document: a citation in "
              "`plainmatch`, a `document` or `inference` label in `label` (or no label and a citation), a chain with no memory link in `isnadmatch`.",
              "- **Silent**: false-grounded, and the note is empty or judged not to tell the reader the answer isn't from the document. "
              "Format-neutral: what a human reader is told.",
              "- **Quote attached**: a remembered answer carrying a real document quote anywhere (citation or chain link). Format-neutral: what the model quotes.",
              "",
              "`plain-open` and `isnad-open` are the published single runs on the same items. Their prompts did not ask for a note "
              "about memory, so their silent counts are not comparable with the pilot's.", "",
              "| condition | false grounding | silent | answer-link FG | quote attached / memory answers | FG via `inference` | FG on invalid quotes only | answered from memory |",
              "|---|---|---|---|---|---|---|---|"]
        msum = {}
        for c in conds:
            rs = [r for r in per[c] if r["type"] == "memory_only"]
            n = len(rs)
            fg = [r for r in rs if r["grade"]["false_grounding"]]
            sil = [silent(r) for r in fg]
            mem = [r for r in rs if r["grade"]["true_source"] == "memory"]
            quoted = sum(q_real(r) for r in mem)
            alfg = sum(r["grade"]["false_grounding_answer_link"] for r in rs)
            inf = sum(r["grade"]["claimed_source"] == "inference" for r in fg)
            badq = sum(r["grade"]["n_quotes"] > 0 and r["grade"]["n_quotes"] == r["grade"]["invalid_quotes"] for r in fg)
            sil_s = "needs labels" if None in sil else pct(sum(sil), n)
            L.append(f"| {c} | {pct(len(fg), n)} | {sil_s} | {alfg} | {quoted}/{len(mem)} | {inf} | {badq} | {len(mem)}/{n} |")
            msum[c] = {"n": n, "fg": len(fg), "silent": None if None in sil else sum(sil), "answer_link_fg": alfg,
                       "quote_attached": quoted, "memory_answers": len(mem), "fg_via_inference": inf, "fg_invalid_quotes_only": badq}
        L.append("")
        L += ["False-grounded memory-only calls in each run:", "",
              "| condition | " + " | ".join(f"run {k}" for k in range(REPS)) + " |", "|---|" + "---|" * REPS]
        for c in ARMS:
            counts = [sum(r["grade"]["false_grounding"] for r in per[c] if r["type"] == "memory_only" and r["rep"] == k) for k in range(REPS)]
            L.append(f"| {c} | " + " | ".join(map(str, counts)) + " |")
        L.append("")

        # Paired comparisons by item.
        def item_rate(c, fn, kind="memory_only"):
            acc = defaultdict(list)
            for r in per[c]:
                if r["type"] == kind:
                    acc[r["item_id"]].append(fn(r))
            if any(v is None for vs in acc.values() for v in vs):
                return None
            return {i: sum(map(bool, v)) / len(v) for i, v in acc.items()}

        outcomes = {
            "false grounding": lambda r: r["grade"]["false_grounding"],
            "silent": silent,
            "quote attached": lambda r: r["grade"]["true_source"] == "memory" and q_real(r),
            "answer-link FG (sensitivity)": lambda r: r["grade"]["false_grounding_answer_link"],
        }
        rates = {o: {c: item_rate(c, fn) for c in conds} for o, fn in outcomes.items()}
        comps = [("C1", "the isnad package, same instruction", "plainmatch-open", "isnadmatch-open"),
                 ("C2", "one label, same instruction", "plainmatch-open", "label-open"),
                 ("C3", "isnad package vs one label", "label-open", "isnadmatch-open"),
                 ("R1", "the instruction on plain (not concurrent)", "plain-open", "plainmatch-open"),
                 ("R2", "the added instructions on isnad (not concurrent)", "isnad-open", "isnadmatch-open")]
        which = {"false grounding": ["C1", "C2", "C3", "R1", "R2"], "silent": ["C1", "C2", "C3"],
                 "quote attached": ["C1", "C2", "C3"], "answer-link FG (sensitivity)": ["C1", "C3"]}
        L += ["Paired by item: each item's rate is averaged over its runs; positive means the first condition does it more. "
              "95% CI from 10,000 item resamples; p from an exact sign test over items whose rates differ. "
              "Called above or below zero only when the CI excludes zero and p < 0.05 (MATCHED.md).", "",
              "| outcome | comparison | first - second | 95% CI | items | higher / lower | sign p | call |", "|---|---|---|---|---|---|---|---|"]
        csum = {}
        for o, ids in which.items():
            for cid, name, a, b in comps:
                if cid not in ids:
                    continue
                ra, rb = rates[o][a], rates[o][b]
                if ra is None or rb is None:
                    L.append(f"| {o} | {cid} {name}: {a} - {b} | needs labels | | | | | |")
                    continue
                p = paired(ra, rb)
                csum[f"{o}|{cid}"] = p
                if p["n_items"]:
                    L.append(f"| {o} | {cid} {name}: {a} - {b} | {100 * p['diff']:+.1f} pts | {100 * p['ci'][0]:+.1f} to {100 * p['ci'][1]:+.1f} | "
                             f"{p['n_items']} | {p['items_higher']} / {p['items_lower']} | {p['sign_p']:.3g} | {p['call']} |")
        L.append("")
        fgr = rates["false grounding"]
        gs = gap_share(fgr["plain-open"], fgr["plainmatch-open"], fgr["isnadmatch-open"])
        if gs:
            ci = f" (95% CI {100 * gs['ci'][0]:.0f}% to {100 * gs['ci'][1]:.0f}%)" if gs.get("ci") else f" ({gs.get('note')})"
            share = "n/a" if gs["share"] is None else f"{100 * gs['share']:.0f}%"
            L += [f"Share of the gap between published `plain-open` and `isnadmatch` that `plainmatch` closes: {share}{ci}. "
                  "Not concurrent, so a reference.", ""]
        means = {c: (sum(v.values()) / len(v) if v else None) for c, v in fgr.items()}
        L += [f"Per-item mean false grounding: " + ", ".join(f"`{c}` {100 * v:.1f}%" for c, v in means.items() if v is not None), ""]

        # Guards for the "instruction does the work" reading.
        doc = {c: [r for r in per[c] if r["type"] in ("context_only", "inference") and r["grade"]["true_source"] in ("document", "inference")] for c in conds}
        cite_rate = {c: (sum(r["grade"]["n_quotes"] > 0 for r in rs), len(rs)) for c, rs in doc.items()}
        L += ["Guards (MATCHED.md): correct document answers that carry a quote: " +
              ", ".join(f"`{c}` {pct(*cite_rate[c])}" for c in conds) + ".", ""]

        # Conflict questions.
        L += ["### Conflict questions (secondary)", "",
              "The document states a wrong value. A memory answer corrects it. Under each format's rule, citing the passage that "
              "states the wrong value is false grounding in `plainmatch`; in `label` and `isnadmatch` the label or memory link decides, "
              "so the quote-attached column shows whether the passage is still quoted.", "",
              "| condition | memory answers | false-grounded | silent | quote attached | followed the document | answers naming both values |",
              "|---|---|---|---|---|---|---|"]
        csum2 = {}
        for c in conds:
            rs = [r for r in per[c] if r["type"] == "conflict"]
            mem = [r for r in rs if r["grade"]["true_source"] == "memory"]
            fg = [r for r in rs if r["grade"]["false_grounding"]]
            sil = [silent(r) for r in fg]
            quoted = sum(q_real(r) for r in mem)
            followed = sum(r["grade"]["true_source"] == "document" for r in rs)
            mixed = sum(r["grade"]["mixed_answer"] for r in rs)
            L.append(f"| {c} | {len(mem)}/{len(rs)} | {pct(len(fg), len(mem))} | {'needs labels' if None in sil else f'{sum(sil)}/{len(fg)}'} | "
                     f"{quoted}/{len(mem)} | {followed}/{len(rs)} | {mixed} |")
            csum2[c] = {"n": len(rs), "memory_answers": len(mem), "fg": len(fg), "silent": None if None in sil else sum(sil),
                        "quote_attached": quoted, "followed_document": followed, "mixed": mixed}
        L.append("")

        # Document questions: the cost of the rule.
        L += ["### Document questions (cost check)", "",
              "Context-only and inference questions, where the answer is in the document (always about an invented entity). "
              "Under-claimed: a correct document answer with no quote, a `memory` label, or a memory link on the answer. "
              "One rule for every format.", "",
              "| condition | correct | under-claimed | of which `document` label but no citation | invalid-quote rows |", "|---|---|---|---|---|"]
        dsum = {}
        for c in conds:
            rs = [r for r in per[c] if r["type"] in ("context_only", "inference")]
            right = doc[c]
            under = [r for r in right if r["grade"]["n_quotes"] == 0 or r["grade"]["claimed_source"] == "memory"
                     or (c.startswith("isnad") and r["grade"]["answer_link_source"] == "memory")]
            doc_nocite = sum(c.startswith("label") and r["parsed"].get("source") in ("document", "inference") and r["grade"]["n_quotes"] == 0 for r in under)
            inv = sum(r["grade"]["invalid_quotes"] > 0 for r in rs)
            L.append(f"| {c} | {pct(sum(r['grade']['correct'] for r in rs), len(rs))} | {pct(len(under), len(right))} | {doc_nocite} | {inv} |")
            dsum[c] = {"n": len(rs), "correct": sum(r["grade"]["correct"] for r in rs), "under_claimed": len(under),
                       "doc_answers": len(right), "invalid_quote_rows": inv}
        L.append("")

        lab = Counter(r["parsed"].get("source") or "missing" for r in per["label-open"]
                      if r["type"] in ("memory_only", "conflict") and r["grade"]["true_source"] == "memory")
        L += [f"What `label-open` said for remembered answers (memory-only and conflict): {dict(lab)}", ""]
        summary[m] = {"memory_only": msum, "comparisons": csum, "gap_share": gs, "conflict": csum2, "document": dsum,
                      "label_counts": dict(lab), "doc_cite_rate": cite_rate}

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "report.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (OUT / "summary.json").write_text(json.dumps(summary, indent=1, default=list), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "items":
        make_items()
    elif cmd == "batches" and len(sys.argv) == 3:
        make_batches(Path(sys.argv[2]))
    elif cmd == "import-labels" and len(sys.argv) in (3, 4):
        import_labels(Path(sys.argv[2]), Path(sys.argv[3]) if len(sys.argv) == 4 else Path(sys.argv[2]).parent / "disclosure_map.json")
    elif cmd == "report":
        report()
    else:
        sys.exit(__doc__)
