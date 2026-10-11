"""Offline tests: the Latin square, renderers, validator, grader, and full dry runs through run.py and analyze.py
with fake models whose right answers are known. No API calls.

  python tests/test_all.py          # everything
  python tests/test_all.py --unit   # skip the dry runs
"""

import copy
import json
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from hops.grade import (chain_flags, chain_lookup, contains_value, new_specifics, parse_reader, prose_markers,  # noqa: E402
                        score_fact, specifics)
from hops.items import CELLS, added_text, load_scenarios, note_sets, problems  # noqa: E402
from hops.prompts import TOPIC_KEYS, reader_message, topic_order, writer_message  # noqa: E402
from hops.render import planted_chain, planted_prose  # noqa: E402

FAILS = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"{'PASS' if ok else 'FAIL'}  {name}{('  ' + detail) if detail and not ok else ''}")
    if not ok:
        FAILS.append(name)


def synthetic() -> list[dict]:
    """A valid two-scenario item set for unit tests."""
    out = []
    people = [["Ada Quillfeather", "Bruno Ostrava"], ["Cleo Varga", "Dmitri Lund", "Edith Narr"]]
    for si, sid in enumerate(["x1", "x2"]):
        facts = []
        for i in range(8):
            val = f"ZQ-{si}{i}{7 + i}{3 + si}"
            facts.append({
                "id": f"{sid}f{i + 1}", "topic": f"code for widget {i + 1} in batch {sid}", "value": val,
                "aliases": [val.replace("-", " ")],
                "plain": f"Widget {i + 1} carries code {val}.",
                "detail": f"Widget {i + 1} carries code {val} (field widget_code, /srv/conf/widgets.yaml line {40 + i}).",
                "obs_via": f"`widgetctl show w{i + 1}` listing",
                "third_party": {"name": people[si][i % len(people[si])], "doc": "handover memo"},
            })
        out.append({"id": sid, "title": f"Widget audit {sid}", "task": "Audit the widget codes before the release.",
                    "facts": facts,
                    "distractors": [{"text": f"The release train has {j + 3} carriages.", "source": "user",
                                     "via": "user message"} for j in range(6)]})
    return out


def test_items() -> None:
    sc = synthetic()
    check("validator accepts the synthetic items", problems(sc) == [], str(problems(sc)))
    bad = copy.deepcopy(sc)
    bad[0]["facts"][0]["plain"] = bad[0]["facts"][0]["plain"].replace("carries", "was checked to carry")
    check("validator rejects a blocklisted word", any("blocklisted" in p for p in problems(bad)))
    bad = copy.deepcopy(sc)
    f = bad[0]["facts"][1]
    f["detail"] = f["plain"].rstrip(".") + f" (record r{f['value'][-4:]}, /srv/a/b.yaml)."
    check("validator rejects detail that repeats a digit group of the value",
          any("digit group" in p for p in problems(bad)), str(problems(bad)))
    bad = copy.deepcopy(sc)
    bad[0]["facts"][2]["detail"] = "Code " + bad[0]["facts"][2]["value"] + " is on widget 3 (field x_y, /a/b line 2)."
    check("validator rejects detail that reorders plain", any("in order" in p for p in problems(bad)))
    bad = copy.deepcopy(sc)
    bad[1]["facts"][0]["third_party"]["name"] = "Ada Quillfeather"
    check("validator rejects a third party reused across scenarios", any("also used" in p for p in problems(bad)))
    bad = copy.deepcopy(sc)
    bad[0]["facts"][0]["obs_via"] = "`widgetctl` (prod) listing"
    check("validator rejects parentheses in obs_via", any("parentheses" in p for p in problems(bad)))
    check("added_text returns the inserted words",
          added_text("A b c.", "A b c (x_y, /p/q line 7).") == "(x_y, /p/q line 7).")

    ns = note_sets(sc)
    check("8 note sets per scenario", len(ns) == 16)
    ok_rows = all(sorted((a["source"], a["cue"]) for a in n["assign"].values()) == sorted(CELLS) for n in ns)
    check("each note set has exactly one fact per (source x cue) cell", ok_rows)
    visits = Counter((fid, a["source"], a["cue"]) for n in ns for fid, a in n["assign"].items())
    check("each fact visits each cell exactly once across 8 variants", set(visits.values()) == {1} and len(visits) == 128)
    check("each note set orders all 14 lines", all(len(n["order"]) == 14 and len(set(n["order"])) == 14 for n in ns))
    check("note-set construction is deterministic", note_sets(sc) == ns)


def test_render() -> None:
    sc = synthetic()
    s, ns = sc[0], note_sets(sc)[3]
    prose, strip, chain = planted_prose(ns, s), planted_prose(ns, s, tagged=False), planted_chain(ns, s)
    good = True
    for f in s["facts"]:
        a = ns["assign"][f["id"]]
        line = next(ln for ln in prose.splitlines() if f["value"] in ln)
        good &= f[a["cue"]] in line
        good &= {"OBS": "I saw this myself in the", "USER": "The user told me this.",
                 "THIRD": f"{f['third_party']['name']}'s handover memo says this; I have not verified it.",
                 "GUESS": "My own assumption; I have not checked it."}[a["source"]] in line
    check("tagged prose carries each fact's sentence and correct tag", good)
    check("stripped prose has no tags", not any(t in strip for t in ("I saw this", "told me", "says this", "My own")))
    check("stripped prose keeps every value", all(f["value"] in strip for f in s["facts"]))
    data = json.loads(chain)
    want = {"OBS": "observed", "USER": "user", "THIRD": "third_party", "GUESS": "own_guess"}
    good = all(next(c for c in data["claims"] if c["value"] == f["value"])["source"] == want[ns["assign"][f["id"]]["source"]]
               for f in s["facts"])
    check("planted chain has correct source fields", good)
    check("planted chain has 14 claims", len(data["claims"]) == 14)
    msg = writer_message(s["task"], prose, "free")
    check("writer message has task, notes and instruction", s["task"] in msg and prose in msg and msg.endswith("300 words."))
    order = topic_order(s["facts"], "R2_opus_free_x1v3")
    check("topic order is a permutation and deterministic",
          sorted(order) == sorted(f["id"] for f in s["facts"]) and order == topic_order(s["facts"], "R2_opus_free_x1v3"))
    check("topic order differs between calls", order != topic_order(s["facts"], "R3_opus_free_x1v3"))
    rm = reader_message(prose, {f["id"]: f for f in s["facts"]}, order)
    check("reader message lists t1..t8 with topics", all(f"{k}: " in rm for k in TOPIC_KEYS))
    check("reader message never shows a value in the topics block",
          not any(f["value"] in rm.split("Topics:")[1] for f in s["facts"]))


def test_grade() -> None:
    f = {"value": "02:14 UTC", "aliases": ["2:14 UTC", "02:14"], "third_party": {"name": "Dana Whitfield", "doc": "memo"}}
    probes = [("starts at 02:14 UTC.", True), ("starts at 2:14 UTC", True), ("at 02:14", True),
              ("at 02:15 UTC", False), ("at 12:14 UTC", False), ("at 102:14", False), ("", False)]
    for text, want in probes:
        check(f"contains_value({text!r}) == {want}", contains_value(text, f) == want)
    t = {"value": "7.42 seconds", "aliases": ["7.42 s"], "third_party": {"name": "A B", "doc": "x"}}
    t = {"value": "7.42 seconds", "aliases": [], "third_party": {"name": "A B", "doc": "x"}}
    for text in ("a 7.42-second timeout", "7.42 sec", "7.42 secs", "7.42s", "took 7.42s.", "7.42 s"):
        check(f"unit spelling: {text!r} matches 7.42 seconds", contains_value(text, t))
    check("unit spelling: 7.42 ms does not match 7.42 seconds", not contains_value("7.42 ms", t))
    hrs = {"value": "41 hours", "aliases": [], "third_party": {"name": "A B", "doc": "x"}}
    for text in ("41h", "41 h", "41 hrs", "41-hour"):
        check(f"unit spelling: {text!r} matches 41 hours", contains_value(text, hrs))
    check("unit spelling: 141h does not match 41 hours", not contains_value("141h", hrs))
    deg = {"value": "-41.7 °C", "aliases": [], "third_party": {"name": "A B", "doc": "x"}}
    check("negative value: '-41.7C' matches -41.7 °C", contains_value("peaked at -41.7C", deg))
    check("negative value: '41.7C' (sign dropped) does not match", not contains_value("peaked at 41.7C", deg))
    m = {"value": "-41.7 °C", "aliases": ["-41.7"], "third_party": {"name": "A B", "doc": "x"}}
    check("negative value: '−41.7°C' matches", contains_value("peaked at −41.7°C", m))
    check("negative value: '41.7 °C' (sign dropped) does not match", not contains_value("peaked at 41.7 °C", m))
    check("dates: 2026-09-28 is not split as a negative", contains_value("on 2026-09-28", {"value": "2026-09-28", "aliases": [], "third_party": {"name": "A B", "doc": "x"}}))
    g = {"value": "$18,940", "aliases": ["18940 USD"], "third_party": {"name": "A B", "doc": "x"}}
    check("thousands separator normalized", contains_value("total of 18940 dollars", g))
    h = {"value": "INV-48213", "aliases": [], "third_party": {"name": "A B", "doc": "x"}}
    check("ID matches with different punctuation", contains_value("invoice inv 48213 is", h))
    check("ID does not match a longer ID", not contains_value("INV-482135", h))

    s = score_fact("THIRD", f, {"value": "02:14 UTC", "source": "observed_by_agent", "rely": "rely_without_checking"})
    check("third read as observed is an upgrade", s["upgrade"] and s["read_as_observed"] and not s["correct_source"])
    s = score_fact("THIRD", f, {"value": "", "source": "observed_by_agent", "rely": "verify_first"})
    check("lost value never counts as an upgrade", not s["upgrade"] and not s["reader_value_ok"])
    s = score_fact("GUESS", f, {"value": "02:14", "source": "not_stated", "rely": "verify_first"})
    check("not_stated is loss, not upgrade", s["loss"] and not s["upgrade"])
    s = score_fact("OBS", f, {"value": "02:14 UTC", "source": "claimed_by_third_party", "rely": "verify_first"})
    check("observed read as third party is a downgrade", s["downgrade"] and not s["upgrade"])
    s = score_fact("USER", f, {"value": "02:14 UTC", "source": "stated_by_user", "rely": "verify_first"})
    check("user read as user is correct", s["correct_source"] and not s["downgrade"])
    ans = [{"topic": f"t{i}", "value": f"v{i}", "source": "not_stated", "rely": "verify_first"} for i in range(8, 0, -1)]
    order = [f"f{i}" for i in range(1, 9)]
    got = parse_reader({"answers": ans}, order)
    check("parse_reader maps topic keys back to facts regardless of answer order",
          all(got[f"f{i}"]["value"] == f"v{i}" for i in range(1, 9)))
    check("parse_reader rejects a missing topic", parse_reader({"answers": ans[:7]}, order) == {})
    check("parse_reader rejects a duplicated topic", parse_reader({"answers": ans[:7] + [ans[0]]}, order) == {})

    art = json.dumps({"summary": "s", "claims": [
        {"claim": "Backup at 02:14 UTC.", "value": "02:14 UTC", "source": "observed", "via": "x", "verified": "yes"}]})
    look = chain_lookup(art, f)
    check("chain lookup finds the claim", look["chain_found"] and look["chain_source"] == "observed")
    fl = chain_flags("THIRD", look)
    check("chain third->observed is a chain upgrade and a verified flip", fl["chain_upgrade"] and fl["chain_verified_flip"])
    check("chain lookup tolerates junk", not chain_lookup("not json", f)["chain_found"])

    got = specifics("see /etc/cron.d/pg-nightly on pg-17 via `kubectl get pods`, at line 42 of main.py:118")
    for want in ("/etc/cron.d/pg-nightly", "pg-17", "kubectl get pods", "line 42", "main.py:118"):
        check(f"specifics finds {want!r}", want in got, str(got))
    check("specifics ignores hyphenated English, single digits and plain numbers or durations",
          specifics("the on-call rota has 3 people, 1,286 rows, 11:47 PM, 3h41m, 9/28 and 1.29M") == set(),
          str(specifics("the on-call rota has 3 people, 1,286 rows, 11:47 PM, 3h41m, 9/28 and 1.29M")))
    fx = [{"value": "INV-48213", "aliases": [], "third_party": {"name": "A B", "doc": "x"}}]
    check("new_specifics drops a reformatted planted value", new_specifics("ticket inv48213 and job q7", ["x"], fx) == ["q7"]
          or new_specifics("ticket INV 48213 and job q7", ["x"], fx) == ["q7"])
    check("new_specifics ignores what the writer was shown",
          new_specifics("job pg-17 at /var/x/y and ticket OPS-4410", ["job pg-17 at /var/x/y"]) == ["ops-4410"])
    m = prose_markers("- Backup at 02:14 UTC (per Dana's memo; unverified)\n- other", f)
    check("prose markers see the name and the hedge", m["third_name_kept"] and m["hedge_kept"])
    m = prose_markers("- Backup at 02:14 UTC.\n- Dana Whitfield wrote the memo; unverified.", f)
    check("prose markers only look at the value's own line", not m["third_name_kept"] and not m["hedge_kept"])


def run_cmd(tmp: Path, writer: str, extra: list[str] | None = None, mode: str = "standard"):
    cmd = [sys.executable, str(ROOT / "run.py"), "--dry-run", writer, "--out", str(tmp), "--mode", mode, "--poll", "0",
           "--disciplines", "free", "instructed", "chain", "free120"] + (extra or [])
    return subprocess.run(cmd, capture_output=True, text=True)


def dry_run(writer: str, extra: list[str] | None = None, mode: str = "standard") -> dict:
    tmp = Path(tempfile.mkdtemp(prefix=f"hops-{writer}-"))
    p = run_cmd(tmp, writer, extra, mode)
    if p.returncode != 0:
        raise RuntimeError(p.stdout + p.stderr)
    p2 = subprocess.run([sys.executable, str(ROOT / "analyze.py"), str(tmp)], capture_output=True, text=True)
    if p2.returncode != 0:
        raise RuntimeError(p2.stdout + p2.stderr)
    return {"dir": tmp, "summary": json.loads((tmp / "summary.json").read_text()), "log": p.stdout,
            "facts": [json.loads(x) for x in (tmp / "facts.jsonl").read_text().splitlines()]}


def frac(rows, key):
    return sum(bool(r[key]) for r in rows) / len(rows) if rows else float("nan")


def test_dry_runs() -> None:
    if not (ROOT / "data" / "scenarios.json").exists():
        check("data/scenarios.json exists for the dry runs", False)
        return
    real = load_scenarios(ROOT / "data" / "scenarios.json")
    check("real items pass the validator", problems(real) == [], "; ".join(problems(real)[:8]))
    n_ns = 8 * len(real)

    r = dry_run("identity")
    facts = r["facts"]
    ok_reads = [x for x in facts if x["form"] != "strip"]
    check("identity: every fact retained in text", frac(ok_reads, "retained_text") == 1.0)
    check("identity: every source read correctly", frac(ok_reads, "correct_source") == 1.0)
    check("identity: no upgrades or downgrades", not any(x["upgrade"] or x["downgrade"] for x in facts))
    strip = [x for x in facts if x["form"] == "strip"]
    check("identity: stripped notes read as not stated", len(strip) == 8 * n_ns and frac(strip, "loss") == 1.0)
    check("identity: reader gate passes", r["summary"]["reader_gate_pass"])
    w_calls = 2 * 4 * 2 * n_ns  # writers x disciplines x hops x note sets
    calls = [json.loads(x) for x in (r["dir"] / "calls.jsonl").read_text().splitlines()]
    check("identity: expected number of calls", len(calls) == 3 * n_ns + 2 * w_calls, f"{len(calls)}")
    check("identity: three rounds", r["log"].count("round ") >= 3 and "round 4:" not in r["log"])
    chain = [x for x in facts if x["discipline"] == "chain" and x["stage"] != "R1"]
    check("identity: chain tags parsed correctly at every hop", frac(chain, "chain_correct") == 1.0)
    check("identity: no new specifics added", all(not x.get("fact_new_specifics") for x in facts))

    r = dry_run("stripper")
    prose = [x for x in r["facts"] if x["writer"] and x["discipline"] != "chain"]
    check("stripper: prose sources all lost after rewrite", frac(prose, "loss") == 1.0 and frac(prose, "retained_text") == 1.0)

    r = dry_run("upgrader", ["--fake-p-detail", "0.5", "--fake-p-plain", "0.1"], mode="batch")
    h1 = r["summary"]["h1"]["hop 3, free + instructed (primary population)"]
    expect = (1 - 0.5 ** 2) - (1 - 0.9 ** 2)  # 0.75 - 0.19 = 0.56
    check(f"upgrader (batch mode): H1 delta near {expect:.2f}", abs(h1["delta"] - expect) < 0.15, f"{h1}")
    lo, hi = h1["boot95"]
    check("upgrader: bootstrap interval excludes 0", lo > 0, f"{h1}")
    third3 = [x for x in r["facts"] if x["writer"] and x["hop"] == 3 and x["source"] == "THIRD" and x["discipline"] == "chain"]
    check("upgrader: chain parse sees upgrades", frac(third3, "chain_upgrade") > 0.2)
    other = [x for x in r["facts"] if x["writer"] and x["source"] != "THIRD"]
    check("upgrader: no upgrades on other sources", not any(x["upgrade"] for x in other))

    r = dry_run("upgrader", ["--fake-p-detail", "0.2", "--fake-p-plain", "0.2"])
    h1 = r["summary"]["h1"]["hop 3, free + instructed (primary population)"]
    check("null upgrader: H1 delta near 0", abs(h1["delta"]) < 0.12, f"{h1}")

    r = dry_run("identity", ["--fake-error-every", "17"], mode="batch")
    calls = [json.loads(x) for x in (r["dir"] / "calls.jsonl").read_text().splitlines()]
    final = {c["custom_id"] for c in calls if c["status"] == "ok"}
    errored = [c for c in calls if c["status"] == "errored"]
    check("transient errors are retried until every call is final", len(final) == 3 * n_ns + 2 * w_calls and errored,
          f"{len(final)} final, {len(errored)} errored")

    # Resume: a second invocation over a finished folder must make no calls.
    tmp = r["dir"]
    p = subprocess.run([sys.executable, str(ROOT / "run.py"), "--dry-run", "identity", "--out", str(tmp), "--mode",
                        "batch", "--poll", "0", "--disciplines", "free", "instructed", "chain", "free120",
                        "--fake-error-every", "17"], capture_output=True, text=True)
    n_after = len((tmp / "calls.jsonl").read_text().splitlines())
    check("resume over a finished folder makes no new calls", p.returncode == 0 and n_after == len(calls), p.stdout[-300:])
    p = subprocess.run([sys.executable, str(ROOT / "run.py"), "--dry-run", "identity", "--out", str(tmp), "--effort", "low"],
                       capture_output=True, text=True)
    check("resume with changed settings is refused", p.returncode != 0 and "changed" in (p.stdout + p.stderr))
    expected = 3 * n_ns + 2 * w_calls

    def finals(folder):
        rows = [json.loads(x) for x in (folder / "calls.jsonl").read_text().splitlines()]
        ok_ids = [r["custom_id"] for r in rows if r["status"] != "errored"]
        return rows, ok_ids

    def n_batches(folder):
        return len(json.loads((folder / "fake_state.json").read_text())["batches"])

    # Spend guard: the whole pipeline is estimated before round 1. $12 covers round 1 alone with the margin (about
    # $8.77 x 1.3) but not the whole pipeline (about $22 x 1.3), so only a whole-pipeline guard stops here.
    tmp = Path(tempfile.mkdtemp(prefix="hops-budget-"))
    p = run_cmd(tmp, "identity", ["--budget", "12"], mode="batch")
    check("budget below the whole-pipeline estimate stops before round 1",
          p.returncode != 0 and "stopping before round 1" in (p.stdout + p.stderr) and not (tmp / "calls.jsonl").exists(),
          (p.stdout + p.stderr)[-300:])
    tmp = Path(tempfile.mkdtemp(prefix="hops-budget-"))
    p = run_cmd(tmp, "identity", ["--budget", "50"], mode="batch")
    check("ample budget runs to the end", p.returncode == 0 and "done:" in p.stdout, (p.stdout + p.stderr)[-300:])
    tmp = Path(tempfile.mkdtemp(prefix="hops-plan-"))
    p = subprocess.run([sys.executable, str(ROOT / "run.py"), "--plan", "--out", str(tmp), "--mode", "batch"],
                       capture_output=True, text=True)
    check("--plan prints the total still to run and makes no calls",
          p.returncode == 0 and "total still to run" in p.stdout and not (tmp / "calls.jsonl").exists(), p.stdout[-300:])

    # Ctrl-C in the middle of collecting a batch, then resume: nothing is bought twice and nothing is lost.
    tmp = Path(tempfile.mkdtemp(prefix="hops-interrupt-"))
    p1 = run_cmd(tmp, "identity", ["--fake-interrupt-after", "10"], mode="batch")
    rows1, _ = finals(tmp)
    p2 = run_cmd(tmp, "identity", ["--fake-interrupt-after", "10"], mode="batch")
    rows2, ids2 = finals(tmp)
    check("interrupted collection: first run stopped after 10 stored results", p1.returncode != 0 and len(rows1) == 10,
          f"{p1.returncode} {len(rows1)}")
    check("interrupted collection: resume finishes with every call stored once and no extra batch",
          p2.returncode == 0 and len(ids2) == len(set(ids2)) == expected and n_batches(tmp) == 3,
          f"{p2.returncode} {len(ids2)} {len(set(ids2))} {n_batches(tmp)} {p2.stdout[-200:]}{p2.stderr[-300:]}")

    # A batch create whose reply is lost: the rerun adopts the batch instead of buying it again.
    tmp = Path(tempfile.mkdtemp(prefix="hops-lost-"))
    p1 = run_cmd(tmp, "identity", ["--fake-lose-create"], mode="batch")
    p2 = run_cmd(tmp, "identity", ["--fake-lose-create"], mode="batch")
    _, ids = finals(tmp)
    check("lost create reply: first run stops without resubmitting", p1.returncode != 0 and n_batches(tmp) >= 1)
    check("lost create reply: rerun adopts the batch; 3 batches in total, every call once",
          p2.returncode == 0 and "adopting batch" in p2.stdout and n_batches(tmp) == 3 and len(ids) == len(set(ids)) == expected,
          f"{p2.returncode} {n_batches(tmp)} {len(ids)} {p2.stdout[-300:]}{p2.stderr[-300:]}")

    # A batch create that never reached the API: the rerun stops rather than guess; --abandon-intent resubmits.
    def intent_ids(folder):
        return [json.loads(x)["intent_id"] for x in (folder / "batches.jsonl").read_text().splitlines()
                if json.loads(x)["event"] == "intent"]

    tmp = Path(tempfile.mkdtemp(prefix="hops-failed-"))
    p1 = run_cmd(tmp, "identity", ["--fake-fail-create"], mode="batch")
    p2 = run_cmd(tmp, "identity", ["--fake-fail-create"], mode="batch")
    check("failed create: rerun stops, submits nothing, and names --abandon-intent",
          p1.returncode != 0 and p2.returncode != 0 and "--abandon-intent" in (p2.stdout + p2.stderr)
          and n_batches(tmp) == 0, f"{n_batches(tmp)} {p2.stdout[-200:]}{p2.stderr[-300:]}")
    p3 = run_cmd(tmp, "identity", ["--fake-fail-create", "--abandon-intent", intent_ids(tmp)[0]], mode="batch")
    _, ids = finals(tmp)
    check("failed create: --abandon-intent resubmits; every call once, 3 batches",
          p3.returncode == 0 and n_batches(tmp) == 3 and len(ids) == len(set(ids)) == expected,
          f"{p3.returncode} {n_batches(tmp)} {len(ids)} {p3.stdout[-200:]}{p3.stderr[-300:]}")

    def add_foreign(folder, n):
        st = json.loads((folder / "fake_state.json").read_text()) if (folder / "fake_state.json").exists() else \
            {"batches": {}, "interrupted": False, "lost": False, "failed": True}
        reqs = [{"custom_id": f"R2_haiku_free_x{i}-deadbeef",
                 "params": {"model": "claude-haiku-5-5", "messages": [{"role": "user", "content": "hello"}]}}
                for i in range(n)]
        import time as _t
        st["batches"]["msgbatch_other"] = {"requests": reqs, "polls": 0, "created_at": _t.time()}
        (folder / "fake_state.json").write_text(json.dumps(st))

    def intent_size(folder):
        return len(next(json.loads(x)["jobs"] for x in (folder / "batches.jsonl").read_text().splitlines()
                        if json.loads(x)["event"] == "intent"))

    # Someone else's batch of the same size is never adopted.
    tmp = Path(tempfile.mkdtemp(prefix="hops-foreign-"))
    p1 = run_cmd(tmp, "identity", ["--fake-fail-create"], mode="batch")
    add_foreign(tmp, intent_size(tmp))
    p2 = run_cmd(tmp, "identity", ["--fake-fail-create"], mode="batch")
    check("foreign batch of the same size: not adopted, nothing stored, run stops",
          p2.returncode != 0 and not (tmp / "calls.jsonl").exists() and "adopting" not in p2.stdout,
          f"{p2.stdout[-300:]}{p2.stderr[-300:]}")

    # Lost create reply plus a foreign batch of the same size: only this run's batch is adopted.
    tmp = Path(tempfile.mkdtemp(prefix="hops-twocands-"))
    p1 = run_cmd(tmp, "identity", ["--fake-lose-create"], mode="batch")
    add_foreign(tmp, intent_size(tmp))
    p2 = run_cmd(tmp, "identity", ["--fake-lose-create"], mode="batch")
    rows, ids = finals(tmp)
    check("two same-size candidates: adopts the tagged one; every call once, nothing foreign stored",
          p2.returncode == 0 and "adopting batch msgbatch_fake1" in p2.stdout and len(ids) == len(set(ids)) == expected
          and not any(r.get("batch_id") == "msgbatch_other" for r in rows),
          f"{p2.returncode} {len(ids)} {p2.stdout[-300:]}{p2.stderr[-300:]}")

    # A round that costs far more than estimated stops the run.
    tmp = Path(tempfile.mkdtemp(prefix="hops-overrun-"))
    p = run_cmd(tmp, "identity", ["--notesets", "p1v0", "--budget", "1000", "--fake-usage-scale", "60"])
    check("a round costing over 1.3x its estimate stops the run",
          p.returncode != 0 and "more than 1.3x" in (p.stdout + p.stderr), (p.stdout + p.stderr)[-300:])

    # Token means: a folder's own means replace the seed once it has 5 calls of a type.
    import importlib
    run_mod = importlib.import_module("run")
    for n_rows, want_own in ((4, False), (5, True)):
        tmp = Path(tempfile.mkdtemp(prefix="hops-means-"))
        with open(tmp / "calls.jsonl", "w") as fh:
            for i in range(n_rows):
                fh.write(json.dumps({"custom_id": f"R2_x_{i}", "status": "ok", "model": "claude-haiku-5-5",
                                     "call_type": "reader", "usage": {"input_tokens": 11, "output_tokens": 22}}) + "\n")
        got = run_mod.token_means(None, tmp)[("claude-haiku-5-5", "reader")]
        check(f"token means with {n_rows} own calls: {'own' if want_own else 'default'} used",
              (got == (11, 22)) == want_own, f"{got}")

    # Writers that gave up after repeated errors stay in the content denominators.
    r = dry_run("identity", ["--fake-error-every", "2"])
    gave_up = [c for c, row in __import__("collections").OrderedDict(
        (json.loads(x)["custom_id"], json.loads(x)) for x in (r["dir"] / "calls.jsonl").read_text().splitlines()).items()
        if c.startswith("W") and row["status"] == "errored"]
    s4 = r["summary"]["main"]
    bad = {k: v["content"] for k, v in s4.items() if k.endswith("|3") and not k.startswith("planted")
           and v["content"][1] != 8 * n_ns}
    check("gave-up writers: some writer calls gave up in this run", bool(gave_up), f"{len(gave_up)}")
    check("gave-up writers: every hop-3 content denominator is the full 8 x note sets", not bad, f"{bad}")

    # Adding chains to a finished folder (Haiku free120 after the main pilot) reruns nothing already done.
    tmp = Path(tempfile.mkdtemp(prefix="hops-add-"))
    base = [sys.executable, str(ROOT / "run.py"), "--dry-run", "identity", "--out", str(tmp), "--mode", "batch", "--poll", "0"]
    p1 = subprocess.run(base + ["--disciplines", "free", "instructed", "chain"], capture_output=True, text=True)
    n1 = len((tmp / "calls.jsonl").read_text().splitlines())
    p2 = subprocess.run(base + ["--writers", "haiku", "--disciplines", "free120"], capture_output=True, text=True)
    rows = [json.loads(x) for x in (tmp / "calls.jsonl").read_text().splitlines()]
    new_ids = [r["custom_id"] for r in rows[n1:]]
    check("added free120 chains: only Haiku free120 calls are made, each once",
          p1.returncode == 0 and p2.returncode == 0 and len(new_ids) == len(set(new_ids)) == 4 * n_ns
          and all("_haiku_free120_" in c for c in new_ids), f"{p2.returncode} {len(new_ids)} {p2.stderr[-300:]}")
    p3 = subprocess.run([sys.executable, str(ROOT / "analyze.py"), str(tmp)], capture_output=True, text=True)
    s4 = json.loads((tmp / "summary.json").read_text())["main"] if p3.returncode == 0 else {}
    check("analysis covers the added free120 chains", "haiku|free120|3" in s4 and "opus|chain|3" in s4, p3.stderr[-300:])

    # Two runs on one folder at once: the second is refused by the lock.
    import fcntl
    tmp = Path(tempfile.mkdtemp(prefix="hops-lock-"))
    fh = open(tmp / ".lock", "w")
    fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
    p = run_cmd(tmp, "identity")
    fh.close()
    check("a second run on a locked folder is refused", p.returncode != 0 and "another run" in (p.stdout + p.stderr))

    # Failed writer calls are counted, not dropped (survivorship).
    r = dry_run("identity", ["--fake-refuse-every", "5"])
    s4 = r["summary"]["main"]
    k, n = s4["haiku|free|3"]["content"]
    check("refused writer calls count as content not kept, with the full denominator",
          n == 8 * n_ns and 0.4 < k / n < 0.9, f"{k}/{n}")
    k, n = s4["haiku|free|3"]["u_third_plain"]
    check("refused chains stay in the upgrade denominator", n == n_ns, f"{k}/{n}")


if __name__ == "__main__":
    test_items()
    test_render()
    test_grade()
    if "--unit" not in sys.argv:
        test_dry_runs()
    print(f"\n{'ALL PASS' if not FAILS else f'{len(FAILS)} FAILED: ' + ', '.join(FAILS)}")
    sys.exit(1 if FAILS else 0)
