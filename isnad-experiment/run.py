"""Run the source-attribution experiment against Claude models.

Usage:
  python run.py                                   # Claude Opus 5.5, all 4 conditions, 1 rep
  python run.py --models claude-opus-5-5 claude-sonnet-5-5 claude-haiku-5-5 --reps 3
  python run.py --models gpt-5 --openai-reasoning medium   # an OpenAI model (needs OPENAI_API_KEY)
  python run.py --limit 20                        # quick smoke test on 20 items
  python run.py --dry-run oracle                  # no API calls: checks the grader scores perfect answers as perfect

Results append to results/<model>/results.jsonl (one row per item x condition x rep), so an
interrupted run resumes where it stopped. Calls that never produced a gradable answer go to
errors.jsonl instead, so plumbing failures are never scored as model failures.

Each results folder also gets manifest.json: hashes of the items, prompts and grader, plus the settings used.
A resume refuses to add rows if the items or prompts changed since the folder was started (a grader change is
fine: re-score with regrade.py).
"""

import argparse
import hashlib
import json
import platform
import random
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pydantic

from isnad.grade import grade
from isnad.prompts import CONDITIONS, MATCHED_CONDITIONS, SCHEMAS, system_prompt, user_message

ROOT = Path(__file__).parent
PRICES = {  # USD per million tokens (input, output)
    "claude-opus-5-5": (4.00, 20.00),
    "claude-sonnet-5-5": (2.00, 10.00),
    "claude-haiku-5-5": (0.10, 0.50),
    "gpt-5.4-mini": (0.75, 4.50),  # third-party list price seen 2026-10-10; check OpenAI's pricing page
}


def load_items(path: Path, limit: int | None, seed: int) -> list[dict]:
    items = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if limit:
        # Stratified sample so a smoke test still covers every item type.
        rng = random.Random(seed)
        by_type: dict[str, list] = {}
        for it in items:
            by_type.setdefault(it["type"], []).append(it)
        per = max(1, limit // len(by_type))
        items = [it for group in by_type.values() for it in rng.sample(group, min(per, len(group)))]
    return items


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def model_inputs_sha(items_path: Path) -> str:
    """Hash of what the model sees (ids, documents, questions). Answer keys are left out: fixing an alias changes
    the grade, which regrade.py handles, not the responses."""
    seen = [(it["id"], it["document"], it["question"]) for it in map(json.loads, items_path.read_text(encoding="utf-8").splitlines()) if it]
    return hashlib.sha256(json.dumps(sorted(seen)).encode()).hexdigest()[:16]


def check_manifest(out_dir: Path, items_path: Path, settings: dict) -> None:
    """Bind a results folder to the inputs that produced it; refuse to mix rows from different inputs.
    The folders of the published run predate this check and have no manifest."""
    # Model and effort are bound too, so a resume typed without --openai-reasoning can't mix settings.
    current = {"items_sha": model_inputs_sha(items_path), "prompts_sha": sha(ROOT / "isnad" / "prompts.py"),
               "model": settings["model"], "effort": settings["effort"]}
    path = out_dir / "manifest.json"
    if path.exists():
        old = json.loads(path.read_text(encoding="utf-8"))
        changed = [k for k in current if old.get(k) not in (None, current[k])]
        if changed:
            raise SystemExit(f"{out_dir}: {', '.join(changed)} changed since this folder was started; "
                             "use a new --out folder rather than mixing results from different inputs")
        return
    path.write_text(json.dumps({**current, "items_file_sha": sha(items_path), "grade_sha": sha(ROOT / "isnad" / "grade.py"), **settings,
                                "python": platform.python_version(), "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, indent=1),
                    encoding="utf-8")


def done_keys(path: Path) -> set:
    if not path.exists():
        return set()
    return {(r["item_id"], r["condition"], r["rep"]) for r in map(json.loads, path.read_text(encoding="utf-8").splitlines()) if r}


def call_claude(client, model: str, effort: str, item: dict, condition: str) -> dict:
    fmt = condition.split("-")[0]
    response = client.messages.parse(
        model=model,
        max_tokens=16000,
        system=system_prompt(condition),
        messages=[{"role": "user", "content": user_message(item)}],
        output_format=SCHEMAS[fmt],
        output_config={"effort": effort},
    )
    if not response.model.startswith(model):
        raise RuntimeError(f"served model {response.model} != requested {model}")
    row = {
        "served_model": response.model,
        "stop_reason": response.stop_reason,
        "usage": {"input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens},
        "raw": response.model_dump(mode="json"),
    }
    if response.stop_reason == "refusal":
        row["status"] = "refusal"
        row["parsed"] = None
    elif response.stop_reason == "max_tokens":
        row["status"] = "truncated"
        row["parsed"] = None
    elif response.parsed_output is None:
        raise RuntimeError("no parseable structured output")  # an error row, not a score
    else:
        row["status"] = "ok"
        row["parsed"] = response.parsed_output.model_dump()
    return row


def call_openai(client, model: str, reasoning: str | None, item: dict, condition: str) -> dict:
    fmt = condition.split("-")[0]
    kwargs = {"reasoning": {"effort": reasoning}} if reasoning else {}
    try:
        response = client.responses.parse(
            model=model,
            instructions=system_prompt(condition),
            input=user_message(item),
            text_format=SCHEMAS[fmt],
            max_output_tokens=16000,
            **kwargs,
        )
    except pydantic.ValidationError as exc:
        # The SDK parses before we can see the response, so a cut-off reply surfaces here. It was paid for: record it
        # as a finished, unscored row so a resume doesn't buy it again.
        return {"status": "invalid_json", "parsed": None, "error": str(exc)[:500], "usage": {"input_tokens": 0, "output_tokens": 0}}
    if not response.model.startswith(model):
        raise RuntimeError(f"served model {response.model} != requested {model}")
    incomplete = response.incomplete_details.reason if response.incomplete_details else None
    row = {
        "served_model": response.model,
        "stop_reason": incomplete or response.status,
        "usage": {"input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens},
        "raw": response.model_dump(mode="json"),
    }
    refused = any(
        getattr(part, "type", None) == "refusal"
        for out in response.output if getattr(out, "type", None) == "message"
        for part in out.content
    )
    if refused or incomplete == "content_filter":
        row["status"], row["parsed"] = "refusal", None
    elif incomplete == "max_output_tokens":
        row["status"], row["parsed"] = "truncated", None
    elif response.output_parsed is None:
        raise RuntimeError("no parseable structured output")  # an error row, not a score
    else:
        row["status"], row["parsed"] = "ok", response.output_parsed.model_dump()
    return row


def is_claude(model: str) -> bool:
    return model.startswith("claude")


def oracle_answer(item: dict, condition: str) -> dict:
    """A perfectly behaved, perfectly honest respondent. The grader must score it 100% correct."""
    fmt, policy = condition.split("-")
    kind = item["type"]
    abstain = kind == "unanswerable" or (kind == "memory_only" and policy == "strict")
    if abstain:
        return {"answer": None, "note": None, "abstained": True, "citation": None, "chain": [], "source": None, "confidence": 0}
    if kind == "memory_only":
        ans, links, cite = item["memory_aliases"][0], [{"source": "memory", "content": item["memory_aliases"][0], "grade": "sound"}], None
        source = "memory"
    else:
        ans = item["answer_aliases"][0]
        spans = item["supporting_spans"]
        links = [{"source": "document", "content": s, "grade": "sound"} for s in spans]
        if kind == "inference":
            links.append({"source": "inference", "content": f"therefore {ans}", "grade": "sound"})
        cite = spans[0]
        source = "inference" if kind == "inference" else "document"
    return {"answer": ans, "note": None, "abstained": False, "citation": cite, "chain": links, "source": source, "confidence": 95}


def liar_answer(item: dict, condition: str) -> dict:
    """Answers everything, always claims the document. The grader must flag its false grounding."""
    ans = (item["memory_aliases"] or item["answer_aliases"] or ["Cedric Vale"])[0]
    quote = item["document"].split(".")[0]
    return {
        "answer": ans,
        "note": None,
        "abstained": False,
        "citation": quote,
        "chain": [{"source": "document", "content": quote, "grade": "sound"}],
        "source": "document",
        "confidence": 90,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", default=str(ROOT / "data" / "items.jsonl"))
    ap.add_argument("--models", nargs="+", default=["claude-opus-5-5"])
    ap.add_argument("--conditions", nargs="+", default=list(CONDITIONS), choices=CONDITIONS + MATCHED_CONDITIONS)
    ap.add_argument("--reps", type=int, default=1)
    ap.add_argument("--limit", type=int, help="stratified sample of N items for a smoke test")
    ap.add_argument("--effort", default="medium", choices=["low", "medium", "high", "xhigh", "max"],
                    help="Claude models: thinking effort")
    ap.add_argument("--openai-reasoning", choices=["minimal", "low", "medium", "high"],
                    help="OpenAI reasoning models only: reasoning effort (omit for non-reasoning models)")
    ap.add_argument("--list-openai-models", action="store_true", help="print the OpenAI models your key can use, then exit")
    ap.add_argument("--concurrency", type=int, default=8)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--dry-run", choices=["oracle", "liar"], help="no API calls; validate the grader")
    ap.add_argument("--out", default=str(ROOT / "results"))
    args = ap.parse_args()

    if args.list_openai_models:
        import openai

        print("\n".join(sorted(m.id for m in openai.OpenAI().models.list())))
        return
    items = load_items(Path(args.items), args.limit, args.seed)
    clients = {}
    if not args.dry_run:
        if any(is_claude(m) for m in args.models):
            import anthropic

            clients["claude"] = anthropic.Anthropic(max_retries=4, timeout=180.0)
        if any(not is_claude(m) for m in args.models):
            import openai

            clients["openai"] = openai.OpenAI(max_retries=4, timeout=180.0)

    for model in args.models if not args.dry_run else [f"dry-run-{args.dry_run}"]:
        out_dir = Path(args.out) / model
        out_dir.mkdir(parents=True, exist_ok=True)
        results_path, errors_path = out_dir / "results.jsonl", out_dir / "errors.jsonl"
        if not args.dry_run:
            check_manifest(out_dir, Path(args.items), {
                "model": model, "effort": args.effort if is_claude(model) else args.openai_reasoning,
                "conditions": args.conditions, "reps": args.reps, "limit": args.limit, "seed": args.seed})
        done = done_keys(results_path)
        jobs = [
            (it, c, r)
            for r in range(args.reps)
            for it in items
            for c in args.conditions
            if (it["id"], c, r) not in done
        ]
        print(f"{model}: {len(jobs)} calls to make ({len(done)} already done)", flush=True)
        lock = threading.Lock()
        tokens = {"in": 0, "out": 0}

        def work(job):
            item, condition, rep = job
            start = time.time()
            if args.dry_run:
                fn = oracle_answer if args.dry_run == "oracle" else liar_answer
                row = {"status": "ok", "parsed": fn(item, condition), "usage": {"input_tokens": 0, "output_tokens": 0}}
            elif is_claude(model):
                row = call_claude(clients["claude"], model, args.effort, item, condition)
            else:
                row = call_openai(clients["openai"], model, args.openai_reasoning, item, condition)
            row.update(
                item_id=item["id"], type=item["type"], condition=condition, rep=rep, model=model,
                effort=args.effort if is_claude(model) else args.openai_reasoning, seconds=round(time.time() - start, 2),
            )
            row["grade"] = grade(item, condition, row["parsed"]) if row["status"] == "ok" else None
            # Written by the worker as soon as the call returns, so a paid response is kept even if the run is stopped.
            with lock, open(results_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(row) + "\n")
            return row

        def cost() -> float | None:
            if model not in PRICES:
                return None
            pin, pout = PRICES[model]
            return tokens["in"] / 1e6 * pin + tokens["out"] / 1e6 * pout

        n_err = 0
        pool = ThreadPoolExecutor(max_workers=args.concurrency)
        try:
            futures = {pool.submit(work, j): j for j in jobs}
            for n, fut in enumerate(as_completed(futures), 1):
                item, condition, rep = futures[fut]
                try:
                    row = fut.result()
                    tokens["in"] += row["usage"]["input_tokens"]
                    tokens["out"] += row["usage"]["output_tokens"]
                except Exception as exc:  # infra/serving failure: never scored
                    n_err += 1
                    with lock, open(errors_path, "a", encoding="utf-8") as f:
                        f.write(json.dumps({"item_id": item["id"], "condition": condition, "rep": rep, "model": model,
                                            "error_class": type(exc).__name__, "error": str(exc)[:500]}) + "\n")
                if n % 25 == 0 or n == len(jobs):
                    c = cost()
                    spend = f", ${c:.2f} so far, about ${c * len(jobs) / n:.2f} projected for this run" if c is not None else ""
                    print(f"  {n}/{len(jobs)} done, {n_err} errors{spend}", flush=True)
        except KeyboardInterrupt:
            # Cancel the queued calls; the ones already in flight finish and are saved by their workers.
            pool.shutdown(wait=True, cancel_futures=True)
            raise
        pool.shutdown(wait=True)

        if cost() is not None and tokens["in"]:
            print(f"  cost this run: ${cost():.2f}")
    print("Done. Now run: python report.py")


if __name__ == "__main__":
    sys.exit(main())
