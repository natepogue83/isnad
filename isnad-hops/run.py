"""Run the "isnad across hops" chains (Arm A: planted, correctly tagged notes rewritten twice by the same model).

Calls per note set and discipline: W2 (first rewrite of the planted notes), W3 (rewrite of W2), and the fixed reader
on each rewrite (R2, R3). Shared per note set: the reader on the planted tagged prose, the planted chain JSON, and
the tag-stripped prose (R1_prose, R1_chain, R1_strip).

  python run.py --dry-run identity          # offline: fake writer copies, fake reader parses tags; no API calls
  python run.py --out results/smoke --mode standard --notesets p1v0 p4v3 --key-file KEY --budget 1.5
  python run.py --out results/pilot --mode batch --key-file KEY --budget 9 --token-means results/smoke --plan
  python run.py --closed-book --key-file KEY       # can Haiku guess the planted values from the topics alone?

Paying once per call:
- Every finished call is one row in <out>/calls.jsonl, written as soon as it returns. Final rows (any paid outcome)
  are never bought again; "errored" rows (not billed) are retried up to MAX_ERRORED_TRIES times.
- Batch mode logs an intent (with every request's metadata) to <out>/batches.jsonl before creating a batch, creates
  it with SDK retries off (the SDK sends no idempotency key, so a retried create could make a second batch), then
  logs the batch id. Every request's custom_id carries the intent's tag (call id + "-" + first 8 characters of the
  intent id), and only results with this intent's tag are stored. On start, an intent with a batch id is collected
  (skipping calls already final). An intent without one (the create reply was lost) is matched only to a batch that
  no intent in this folder has logged and whose results all carry its tag; if none is found the runner stops and
  asks for --abandon-intent rather than guessing, so a lost create response or a Ctrl-C never leads to a second paid
  batch. A create the API rejected with a 4xx status was certainly not created and is logged as rejected.
- <out>/.lock stops two invocations from working on one folder at once.
- <out>/manifest.json binds the folder to the items, prompts and settings; a resume refuses to mix inputs.

Spend guard: before every round the runner estimates the cost of everything still to run in the folder (all later
hops of every live chain, not just the next round) from mean tokens per (model, call type): this folder's own
means once it has 5+ calls of a type, else --token-means, else conservative defaults. It refuses to start unless
spend so far + 1.3 x that estimate fits in --budget. After each round, if the round cost more than 1.3x its estimate,
it stops.
"""

import argparse
import fcntl
import hashlib
import json
import platform
import re
import sys
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from hops.items import load_scenarios, note_sets, problems
from hops.prompts import JSON_DISCIPLINES, closedbook_params, reader_answers, reader_params, topic_order, writer_params
from hops.render import planted_chain, planted_prose

ROOT = Path(__file__).parent
PRICES = {  # USD per million tokens (input, output); claude-api skill model table, checked 2026-10-11
    "claude-opus-5-5": (4.00, 20.00),
    "claude-sonnet-5-5": (2.00, 10.00),
    "claude-haiku-5-5": (0.10, 0.50),
}
BATCH_DISCOUNT = 0.5
WRITERS = {"opus": "claude-opus-5-5", "haiku": "claude-haiku-5-5", "sonnet": "claude-sonnet-5-5"}
READER = "claude-sonnet-5-5"
FINAL = {"ok", "refusal", "truncated", "invalid_json", "wrong_model"}  # paid outcomes: never re-bought
MAX_ERRORED_TRIES = 5  # errored calls are not billed; after this many a call is reported as given up
MARGIN = 1.3
# Conservative per-call token guesses used until real means exist: (input, output incl. thinking).
DEFAULT_TOKENS = {"reader": (2000, 700), "writer_prose": (1100, 2500), "writer_chain": (2200, 3500)}


# ---------------------------------------------------------------------------------------------------------- jobs

def call_type(job: dict) -> str:
    if job["kind"] == "reader":
        return "reader"
    return "writer_chain" if job["discipline"] in JSON_DISCIPLINES else "writer_prose"


def planted_text(ns: dict, scen: dict, form: str) -> str:
    return {"prose": lambda: planted_prose(ns, scen), "strip": lambda: planted_prose(ns, scen, tagged=False),
            "chain": lambda: planted_chain(ns, scen)}[form]()


def reader_job(cid: str, stage: str, artifact: str, ns: dict, scen: dict, extra: dict) -> dict:
    facts = {f["id"]: f for f in scen["facts"]}
    order = topic_order(scen["facts"], cid)
    return {"custom_id": cid, "kind": "reader", "stage": stage, "noteset": ns["id"], "scenario": scen["id"],
            "model": READER, "order": order, "params": reader_params(READER, artifact, facts, order), **extra}


def plan_jobs(ctx: dict, rows: dict) -> tuple[list[dict], list[dict]]:
    """(jobs ready now, stand-ins for every later call still owed by a live chain).
    rows: custom_id -> latest row. A chain is dead once one of its writer calls ends in a non-ok final state."""
    ready, later = [], []

    def final(cid):
        return cid in rows and rows[cid]["status"] in FINAL

    def ok(cid):
        return cid in rows and rows[cid]["status"] == "ok"

    def gave_up(cid):
        return cid in rows and not final(cid) and rows[cid].get("tries", 1) >= MAX_ERRORED_TRIES

    def want(job):
        cid = job["custom_id"]
        if not final(cid) and not gave_up(cid):
            ready.append(job)

    for ns in ctx["notesets"]:
        scen = ctx["scenarios"][ns["scenario"]]
        for form in ctx["planted_forms"]:
            cid = f"R1_{form}_{ns['id']}"
            want(reader_job(cid, "R1", planted_text(ns, scen, form), ns, scen, {"form": form, "hop": 1}))
        for w in ctx["writers"]:
            for d in ctx["disciplines"]:
                base = {"writer": w, "discipline": d, "noteset": ns["id"], "scenario": scen["id"]}
                stub_w = {"kind": "writer", "model": WRITERS[w], "discipline": d}
                stub_r = {"kind": "reader", "model": READER}
                for hop in (2, 3):
                    wid = f"W{hop}_{w}_{d}_{ns['id']}"
                    rid = f"R{hop}_{w}_{d}_{ns['id']}"
                    prev = f"W{hop - 1}_{w}_{d}_{ns['id']}"
                    if hop == 3 and (final(prev) and not ok(prev) or gave_up(prev)):
                        break  # dead chain
                    if hop == 2:
                        notes = planted_text(ns, scen, "chain" if d in JSON_DISCIPLINES else "prose")
                    elif ok(prev):
                        notes = rows[prev]["text"]
                    else:
                        notes = None
                    if notes is not None:
                        want({"custom_id": wid, "kind": "writer", "stage": f"W{hop}", "model": WRITERS[w],
                              "hop": hop, "input_text": notes,
                              "params": writer_params(WRITERS[w], ctx["effort"], scen["task"], notes, d), **base})
                    else:
                        later.append(stub_w)
                    if ok(wid):
                        want(reader_job(rid, f"R{hop}", rows[wid]["text"], ns, scen, {**base, "hop": hop}))
                    elif final(wid) or gave_up(wid):
                        break  # dead chain: no reader, no later hop
                    else:
                        later.append(stub_r)
    return ready, later


# ------------------------------------------------------------------------------------------------- API results

def to_row(msg, job: dict) -> dict:
    text = "".join(getattr(b, "text", "") for b in msg.content if getattr(b, "type", None) == "text")
    usage = {"input_tokens": msg.usage.input_tokens, "output_tokens": msg.usage.output_tokens}
    details = getattr(msg, "stop_details", None)
    row = {"served_model": msg.model, "stop_reason": msg.stop_reason, "usage": usage, "text": text, "parsed": None,
           "stop_details": {"category": getattr(details, "category", None),
                            "explanation": getattr(details, "explanation", None)} if details else None}
    if not str(msg.model).startswith(job["model"]):
        row["status"] = "wrong_model"
    elif msg.stop_reason == "refusal":
        row["status"] = "refusal"
    elif msg.stop_reason == "max_tokens":
        row["status"] = "truncated"
    elif job["kind"] == "reader" or job.get("discipline") in JSON_DISCIPLINES:
        try:
            parsed = json.loads(text)
            if job["kind"] == "reader":
                assert reader_answers(parsed) is not None
            else:
                assert isinstance(parsed.get("claims"), list)
            row["status"], row["parsed"] = "ok", parsed
        except (json.JSONDecodeError, AssertionError, AttributeError):
            row["status"] = "invalid_json"
    else:
        row["status"] = "ok" if text.strip() else "invalid_json"
    return row


def job_meta(job: dict) -> dict:
    return {k: v for k, v in job.items() if k != "params"}


def cost_of(model: str, usage: dict, batch: bool) -> float:
    pin, pout = PRICES[model]
    c = usage["input_tokens"] / 1e6 * pin + usage["output_tokens"] / 1e6 * pout
    return c * (BATCH_DISCOUNT if batch else 1.0)


# ----------------------------------------------------------------------------------------------------- storage

class Store:
    def __init__(self, out: Path):
        self.out = out
        out.mkdir(parents=True, exist_ok=True)
        self.calls, self.batches = out / "calls.jsonl", out / "batches.jsonl"
        self.lock = threading.Lock()

    def _read(self, path: Path) -> list[str]:
        # Under the same lock as append(), so a reader never sees a half-written line from a worker thread.
        with self.lock:
            return path.read_text(encoding="utf-8").splitlines() if path.exists() else []

    def rows(self) -> dict:
        latest = {}
        for line in self._read(self.calls):
            if line.strip():
                r = json.loads(line)
                prev = latest.get(r["custom_id"])
                # A final row always wins over an errored retry record.
                if prev is None or prev["status"] not in FINAL:
                    if prev is not None and r["status"] not in FINAL:
                        r["tries"] = prev.get("tries", 1) + 1
                    latest[r["custom_id"]] = r
        return latest

    def append(self, row: dict) -> None:
        with self.lock, open(self.calls, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    def intents(self) -> dict:
        """intent_id -> merged state of every event logged for it."""
        state: dict = {}
        for line in self._read(self.batches):
            if line.strip():
                e = json.loads(line)
                state.setdefault(e["intent_id"], {}).update({k: v for k, v in e.items() if k != "event"})
                state[e["intent_id"]].setdefault("events", []).append(e["event"])
        return state

    def log_batch(self, event: str, intent_id: str, **fields) -> None:
        with self.lock, open(self.batches, "a", encoding="utf-8") as f:
            f.write(json.dumps({"event": event, "intent_id": intent_id, "logged_at": time.time(), **fields}) + "\n")

    def spent(self) -> float:
        """Every line ever written, not just the latest per call, so a re-bought call is still counted."""
        total = 0.0
        for line in self._read(self.calls):
            r = json.loads(line) if line.strip() else {}
            if r.get("usage") and r.get("model") in PRICES:
                total += cost_of(r["model"], r["usage"], r.get("mode") == "batch")
        return total


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def check_manifest(out: Path, settings: dict) -> None:
    current = {"scenarios_sha": sha(ROOT / "data" / "scenarios.json"), "prompts_sha": sha(ROOT / "hops" / "prompts.py"),
               "render_sha": sha(ROOT / "hops" / "render.py"), "items_sha": sha(ROOT / "hops" / "items.py"), **settings}
    path = out / "manifest.json"
    if path.exists():
        old = json.loads(path.read_text(encoding="utf-8"))
        changed = [k for k in current if k in old and old[k] != current[k]]
        if changed:
            raise SystemExit(f"{out}: {', '.join(changed)} changed since this folder was started; use a new --out")
        return
    path.write_text(json.dumps({**current, "python": platform.python_version(),
                                "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, indent=1),
                    encoding="utf-8")


# ------------------------------------------------------------------------------------------------ cost guard

def _means_from(folder: Path) -> dict:
    sums: dict = {}
    for r in Store(folder).rows().values():
        if r.get("usage") and r["status"] in FINAL and r.get("call_type") in DEFAULT_TOKENS:
            s = sums.setdefault((r["model"], r["call_type"]), [0, 0, 0])
            s[0] += r["usage"]["input_tokens"]
            s[1] += r["usage"]["output_tokens"]
            s[2] += 1
    return {k: (i / n, o / n, n) for k, (i, o, n) in sums.items()}


def token_means(base: Path | None, own: Path) -> dict:
    """(model, call type) -> (mean input, mean output): own folder's means once n >= 5, else base folder, else defaults."""
    out = {(m, t): v for m in PRICES for t, v in DEFAULT_TOKENS.items()}
    for folder in ([base] if base else []) + [own]:
        for key, (i, o, n) in _means_from(folder).items():
            if folder == base or n >= 5:
                out[key] = (i, o)
    return out


def estimate(jobs: list[dict], means: dict, batch: bool) -> float:
    return sum(cost_of(j["model"], dict(zip(("input_tokens", "output_tokens"), means[(j["model"], call_type(j))])), batch)
               for j in jobs)


# ------------------------------------------------------------------------------------------------- execution

def run_standard(client, jobs: list[dict], store: Store, concurrency: int) -> None:
    def work(job):
        start = time.time()
        try:
            msg = client.messages.create(**job["params"])
            row = to_row(msg, job)
        except Exception as exc:  # infrastructure failure: retried next round, never scored
            row = {"status": "errored", "error_class": type(exc).__name__, "error": str(exc)[:500], "usage": None}
        row.update(job_meta(job), call_type=call_type(job), mode="standard", seconds=round(time.time() - start, 2))
        store.append(row)
        return row

    pool = ThreadPoolExecutor(max_workers=concurrency)
    try:
        futures = [pool.submit(work, j) for j in jobs]
        for n, fut in enumerate(as_completed(futures), 1):
            fut.result()
            if n % 20 == 0 or n == len(jobs):
                print(f"    {n}/{len(jobs)} calls back, ${store.spent():.2f} spent in this folder", flush=True)
    except KeyboardInterrupt:
        pool.shutdown(wait=True, cancel_futures=True)
        raise
    pool.shutdown(wait=True)


def tagged(cid: str, iid: str) -> str:
    return f"{cid}-{iid[:8]}"  # call ids use only letters, digits and "_", so the last "-" starts the tag


def untag(request_id: str, iid: str) -> str | None:
    base, _, tag = request_id.rpartition("-")
    return base if base and tag == iid[:8] else None


def wait_ended(client, bid: str, poll: float) -> None:
    while True:
        b = client.messages.batches.retrieve(bid)
        if b.processing_status == "ended":
            return
        rc = b.request_counts
        print(f"    batch {bid}: {b.processing_status}, {rc.processing} processing, {rc.succeeded} succeeded", flush=True)
        time.sleep(poll)


def collect_batch(client, store: Store, intent: dict, poll: float) -> None:
    bid, iid, metas = intent["batch_id"], intent["intent_id"], {m["custom_id"]: m for m in intent["jobs"]}
    wait_ended(client, bid, poll)
    done = {c for c, r in store.rows().items() if r["status"] in FINAL}
    n = foreign = 0
    for res in client.messages.batches.results(bid):
        cid = untag(res.custom_id, iid)
        if cid is None or cid not in metas:
            foreign += 1  # not a request this intent made: never stored
            continue
        if cid in done:
            continue  # already stored by an earlier, interrupted collection
        job = metas[cid]
        if res.result.type == "succeeded":
            row = to_row(res.result.message, job)
        else:
            err = getattr(res.result, "error", None)
            row = {"status": "errored", "error_class": res.result.type, "error": str(err)[:500], "usage": None}
        row.update(job, call_type=call_type(job), mode="batch", batch_id=bid)
        store.append(row)
        n += 1
    if foreign:
        print(f"    warning: batch {bid} returned {foreign} results without this intent's tag; none were stored", flush=True)
    store.log_batch("collected", iid, batch_id=bid, n_results=n, n_foreign=foreign)


def _created_epoch(b) -> float:
    c = getattr(b, "created_at", None)
    return c.timestamp() if hasattr(c, "timestamp") else float(c or 0)


def _size(b) -> int:
    return sum(getattr(b.request_counts, k, 0) or 0 for k in ("processing", "succeeded", "errored", "canceled", "expired"))


def reconcile(client, store: Store, poll: float, abandon: list[str] | None = None) -> None:
    """Finish every batch an earlier invocation started. Never submits anything."""
    intents = store.intents()
    known = {it["batch_id"] for it in intents.values() if it.get("batch_id")}
    for iid, it in intents.items():
        ev = it["events"]
        if "collected" in ev or "abandoned" in ev or "rejected" in ev:
            continue
        if "batch_id" not in it:
            if iid in (abandon or []):
                print(f"intent {iid}: abandoned by --abandon-intent; its calls will be submitted again", flush=True)
                store.log_batch("abandoned", iid, by="--abandon-intent")
                continue
            # The create call may or may not have reached the server. Look at recent batches (newest first) that no
            # intent here has logged, have the same size, and whose results all carry this intent's tag.
            n, want = len(it["jobs"]), {tagged(m["custom_id"], iid) for m in it["jobs"]}
            mine = []
            for b in client.messages.batches.list(limit=100):
                if _created_epoch(b) < it["intent_time"] - 3600:
                    break
                if b.id in known or _size(b) != n:
                    continue
                print(f"intent {iid}: checking batch {b.id} (same size, not logged here)", flush=True)
                wait_ended(client, b.id, poll)
                if {r.custom_id for r in client.messages.batches.results(b.id)} == want:
                    mine.append(b)
            if len(mine) != 1:
                raise SystemExit(
                    f"intent {iid}: its batch create may not have reached the API, and {len(mine)} batches carry its "
                    f"tag. Nothing was submitted. Check the batch list in the Claude Console; if no batch from this run "
                    f"exists, rerun with --abandon-intent {iid} to submit its calls again.")
            print(f"intent {iid}: adopting batch {mine[0].id}, created by an earlier run", flush=True)
            store.log_batch("submitted", iid, batch_id=mine[0].id, adopted=True)
            it["batch_id"] = mine[0].id
        print(f"collecting batch {it['batch_id']} left by an earlier run", flush=True)
        collect_batch(client, store, {**it, "intent_id": iid}, poll)


def run_batch(client, jobs: list[dict], store: Store, poll: float) -> None:
    iid = uuid.uuid4().hex[:12]
    metas = [job_meta(j) for j in jobs]
    store.log_batch("intent", iid, intent_time=time.time(), jobs=metas)
    requests = [{"custom_id": tagged(j["custom_id"], iid), "params": j["params"]} for j in jobs]
    try:
        b = client.with_options(max_retries=0).messages.batches.create(requests=requests)
    except Exception as exc:
        status = getattr(exc, "status_code", None)
        if isinstance(status, int) and 400 <= status < 500:  # the API refused the request: no batch exists
            store.log_batch("rejected", iid, status=status)
            raise SystemExit(f"batch create rejected ({status}: {str(exc)[:300]}); nothing was created")
        raise SystemExit(f"batch create failed ({type(exc).__name__}: {str(exc)[:200]}). It may or may not have been "
                         "created; rerun the same command and the runner will look for it before submitting anything.")
    store.log_batch("submitted", iid, batch_id=b.id)
    print(f"    submitted batch {b.id} with {len(jobs)} requests", flush=True)
    collect_batch(client, store, {"intent_id": iid, "batch_id": b.id, "jobs": metas}, poll)


def make_client(args):
    if args.dry_run:
        from hops.fake import FakeClient

        return FakeClient(ROOT / "data" / "scenarios.json", writer=args.dry_run, p_detail=args.fake_p_detail,
                          p_plain=args.fake_p_plain, error_every=args.fake_error_every,
                          state_path=Path(args.out) / "fake_state.json", interrupt_after=args.fake_interrupt_after,
                          lose_create=args.fake_lose_create, refuse_every=args.fake_refuse_every,
                          fail_create=args.fake_fail_create, usage_scale=args.fake_usage_scale)
    import anthropic

    if not args.key_file:
        raise SystemExit("--key-file is required for real calls")
    raw = Path(args.key_file).read_text(encoding="utf-8")
    keys = [tok.strip().strip('"\'') for line in raw.splitlines() for tok in line.replace("=", " ").split()
            if tok.strip().strip('"\'').startswith("sk-ant-")]
    if not keys:
        raise SystemExit("no Anthropic key (sk-ant-...) found in --key-file")
    # A long timeout: a standard call that times out is billed but retried, so timeouts should not happen.
    return anthropic.Anthropic(api_key=keys[0], max_retries=4, timeout=900.0)


_DECLINE = re.compile(r"\b(can.?t|cannot|don.?t have|do not have|unable|no way to|not possible)\b", re.I)


def closed_book(client, scenarios: list[dict], store: Store) -> None:
    from hops.grade import contains_value

    model = WRITERS["haiku"]
    done = store.rows()
    for s in scenarios:
        for f in s["facts"]:
            if f"CB_{f['id']}" in done:
                continue
            msg = client.messages.create(**closedbook_params(model, f["topic"], s["title"]))
            text = "".join(getattr(b, "text", "") for b in msg.content if getattr(b, "type", None) == "text")
            store.append({"custom_id": f"CB_{f['id']}", "status": "refusal" if msg.stop_reason == "refusal" else "ok",
                          "model": model, "call_type": "closed_book", "mode": "standard", "fact": f["id"],
                          "text": text, "hit": contains_value(text, f),
                          "usage": {"input_tokens": msg.usage.input_tokens, "output_tokens": msg.usage.output_tokens}})
    rows = [r for r in store.rows().values() if r.get("call_type") == "closed_book"]
    hits = sum(r["hit"] for r in rows)
    declined = [r["custom_id"] for r in rows
                if r["status"] != "ok" or len(r["text"]) > 200 or _DECLINE.search(r["text"])]
    print(f"closed-book guesses matching the planted value: {hits}/{len(rows)} ({100 * hits / len(rows):.1f}%; "
          f"must be under 5%); replies that declined or gave no short guess: {len(declined)}/{len(rows)} "
          f"(the check means little if most decline); ${store.spent():.4f} spent")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "results" / "pilot"))
    ap.add_argument("--writers", nargs="+", default=["haiku", "opus"], choices=list(WRITERS))
    ap.add_argument("--disciplines", nargs="+", default=["free", "instructed", "chain"],
                    choices=["free", "instructed", "chain", "free120"])
    ap.add_argument("--planted-forms", nargs="+", default=["prose", "chain", "strip"], choices=["prose", "chain", "strip"])
    ap.add_argument("--effort", default="medium", choices=["low", "medium", "high"])
    ap.add_argument("--scenarios", nargs="+", help="only these scenario ids")
    ap.add_argument("--notesets", nargs="+", help="only these note-set ids (e.g. p1v0)")
    ap.add_argument("--mode", default="standard", choices=["standard", "batch"])
    ap.add_argument("--budget", type=float, help="USD cap on total spend in this --out folder (required for real calls)")
    ap.add_argument("--token-means", help="a finished results folder whose mean tokens per call seed the estimates")
    ap.add_argument("--concurrency", type=int, default=6)
    ap.add_argument("--poll", type=float, default=30.0)
    ap.add_argument("--key-file")
    ap.add_argument("--plan", action="store_true", help="print what would run and its estimated cost, then exit")
    ap.add_argument("--closed-book", action="store_true")
    ap.add_argument("--dry-run", choices=["identity", "stripper", "upgrader"], help="offline fake writer + parsing reader")
    ap.add_argument("--fake-p-detail", type=float, default=0.3)
    ap.add_argument("--fake-p-plain", type=float, default=0.1)
    ap.add_argument("--fake-error-every", type=int, default=0)
    ap.add_argument("--fake-interrupt-after", type=int, default=0, help="test: Ctrl-C during the first collection")
    ap.add_argument("--fake-lose-create", action="store_true", help="test: first batch create succeeds, reply lost")
    ap.add_argument("--fake-refuse-every", type=int, default=0, help="test: about 1 in N writer calls refused")
    ap.add_argument("--fake-fail-create", action="store_true", help="test: first batch create fails, nothing created")
    ap.add_argument("--fake-usage-scale", type=float, default=1.0, help="test: multiply fake token counts")
    ap.add_argument("--abandon-intent", nargs="+", default=[],
                    help="batch intents (from batches.jsonl) whose create you have confirmed never reached the API")
    args = ap.parse_args()

    scen_list = load_scenarios(ROOT / "data" / "scenarios.json")
    bad = problems(scen_list)
    if bad:
        raise SystemExit("items fail validation:\n  " + "\n  ".join(bad))
    if args.scenarios:
        scen_list = [s for s in scen_list if s["id"] in args.scenarios]
    if not args.dry_run and not args.plan and args.budget is None:
        raise SystemExit("--budget is required for real calls")
    store = Store(Path(args.out))
    if not args.plan:
        lock_file = open(store.out / ".lock", "w")
        try:
            fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise SystemExit(f"another run is using {store.out}")
    if args.closed_book:
        closed_book(make_client(args), scen_list, store)
        return

    nsets = note_sets(scen_list)
    if args.notesets:
        nsets = [n for n in nsets if n["id"] in args.notesets]
    batch = args.mode == "batch"
    # Writers and disciplines are not bound to the folder: every chain's custom id names its writer and discipline, so
    # adding chains later (e.g. Haiku free120 after the main pilot) never mixes inputs.
    settings = {"effort": args.effort, "reader": READER,
                "dry_run": args.dry_run or None, "fake": [args.fake_p_detail, args.fake_p_plain] if args.dry_run else None}
    check_manifest(store.out, settings)
    ctx = {"scenarios": {s["id"]: s for s in scen_list}, "notesets": nsets, "writers": args.writers,
           "disciplines": args.disciplines, "planted_forms": args.planted_forms, "effort": args.effort}
    base = Path(args.token_means) if args.token_means else None
    client = None if args.plan else make_client(args)
    if not args.plan:
        reconcile(client, store, args.poll, args.abandon_intent)

    rnd = 0
    while True:
        rows = store.rows()
        jobs, later = plan_jobs(ctx, rows)
        if not jobs:
            break
        rnd += 1
        means = token_means(base, store.out)
        est_round, est_rest = estimate(jobs, means, batch), estimate(later, means, batch)
        spent = store.spent()
        by_type: dict = {}
        for j in jobs:
            key = f"{j['model']} {call_type(j)}"
            by_type[key] = by_type.get(key, 0) + 1
        print(f"round {rnd}: {len(jobs)} calls ({', '.join(f'{v} {k}' for k, v in sorted(by_type.items()))}); "
              f"estimated ${est_round:.2f} now + ${est_rest:.2f} for {len(later)} later calls; ${spent:.2f} spent so far",
              flush=True)
        if args.plan:
            per = {k: (round(i), round(o)) for k, (i, o) in means.items() if any(j["model"] == k[0] for j in jobs + later)}
            print(f"token means used (in, out): {per}")
            print(f"total still to run: about ${est_round + est_rest:.2f} ({'batch' if batch else 'standard'} prices); "
                  f"with the {MARGIN}x margin: ${spent + MARGIN * (est_round + est_rest):.2f}")
            return
        if args.budget is not None and spent + MARGIN * (est_round + est_rest) > args.budget:
            raise SystemExit(f"stopping before round {rnd}: spend so far ${spent:.2f} + {MARGIN} x ${est_round + est_rest:.2f} "
                             f"still to run = ${spent + MARGIN * (est_round + est_rest):.2f}, over the ${args.budget:.2f} budget")
        before = spent
        if batch:
            run_batch(client, jobs, store, args.poll)
        else:
            run_standard(client, jobs, store, args.concurrency)
        actual = store.spent() - before
        print(f"  round {rnd} cost ${actual:.2f} (estimate ${est_round:.2f})", flush=True)
        if args.budget is not None and est_round > 0 and actual > MARGIN * est_round and actual > 0.25:
            raise SystemExit(f"stopping: round {rnd} cost ${actual:.2f}, more than {MARGIN}x its ${est_round:.2f} estimate")

    rows = store.rows()
    counts: dict = {}
    for r in rows.values():
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    gave_up = sorted(c for c, r in rows.items() if r["status"] not in FINAL)
    if gave_up:
        print(f"gave up after {MAX_ERRORED_TRIES} errors on {len(gave_up)} calls (their later hops never ran): "
              f"{', '.join(gave_up[:10])}{' ...' if len(gave_up) > 10 else ''}")
    print(f"done: {len(rows)} calls in {store.out} ({counts}); total spend ${store.spent():.2f}")


if __name__ == "__main__":
    sys.exit(main())
