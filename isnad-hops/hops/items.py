"""Scenarios, the item validator, the Latin square and note-set assembly.

A note set is one scenario in one Latin-square variant: each of its 8 facts gets one (source x cue) cell, and its
14 lines (8 facts + 6 distractors) get a seeded random order.
"""

import hashlib
import json
import random
import re
from pathlib import Path

SOURCES = ["OBS", "USER", "THIRD", "GUESS"]
CUES = ["plain", "detail"]
CELLS = [(s, c) for s in SOURCES for c in CUES]  # 8 cells, one per fact in every note set

BLOCKLIST = re.compile(
    r"\b(checked|check|verified|verify|confirmed|confirm|according|reports?|reported|shows|showed|shown|saw|seen|see|"
    r"observed|ran|said|says|told|claims?|claimed|mention|mentioned|stated|noted|notes?|per|apparently|allegedly|"
    r"supposedly|assumed?|guess|likely|probably|measured|found|returned|output|printed|displayed|wiki|email|readme|"
    r"documented|inspected|looked|read|query|queried|grep|tested)\b|\blogs show\b",
    re.IGNORECASE,
)
# Machine-like specifics: paths, file:line or "line N", backticked names, tokens mixing letters and digits, dotted
# hostnames, snake_case or kebab-case identifiers.
SPECIFIC = re.compile(
    r"`[^`]+`|(?:[\w.\-]*/[\w.\-/]+)|\bline \d+\b|\b\w+\.\w+:\d+\b|\b(?=[\w\-]*\d)(?=[\w\-]*[A-Za-z])[\w\-]{3,}\b|"
    r"\b[a-z]+(?:[_\-][a-z0-9]+)+\b|\b[a-z0-9]+(?:\.[a-z0-9\-]+){2,}\b"
)


def load_scenarios(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def _words(text: str) -> list[str]:
    return re.findall(r"[\w']+", text.lower())


def added_text(plain: str, detail: str) -> str | None:
    """The words detail adds to plain, or None if detail does not keep plain's words in order."""
    pw, dw = _words(plain), re.findall(r"\S+", detail)
    out, i = [], 0
    for tok in dw:
        tw = _words(tok)
        if i < len(pw) and tw and tw[0] == pw[i] and len(tw) == 1:
            i += 1
        elif i < len(pw) and tw and tw == pw[i:i + len(tw)]:
            i += len(tw)
        else:
            out.append(tok)
    return " ".join(out) if i == len(pw) else None


def problems(scenarios: list[dict]) -> list[str]:
    """Every rule in data/SPEC.md that can be checked mechanically. An empty list means the items pass."""
    out = []
    if len(scenarios) < 1:
        return ["no scenarios"]
    ids = [s["id"] for s in scenarios]
    if len(set(ids)) != len(ids):
        out.append("duplicate scenario ids")
    names_seen: dict[str, str] = {}
    for s in scenarios:
        sid = s["id"]
        facts, dis = s.get("facts", []), s.get("distractors", [])
        if len(facts) != 8:
            out.append(f"{sid}: {len(facts)} facts, need 8")
        if len(dis) != 6:
            out.append(f"{sid}: {len(dis)} distractors, need 6")
        if BLOCKLIST.search(s["task"]):
            out.append(f"{sid}: task has blocklisted word {BLOCKLIST.search(s['task']).group(0)!r}")
        all_text = {f["id"]: f["plain"] + " " + f["detail"] for f in facts}
        values = [f["value"] for f in facts]
        if len(set(v.lower() for v in values)) != len(values):
            out.append(f"{sid}: duplicate values")
        topics = [f["topic"].lower() for f in facts]
        if len(set(topics)) != len(topics):
            out.append(f"{sid}: duplicate topics")
        third_people = set()
        for f in facts:
            fid, val = f["id"], f["value"]
            if not fid.startswith(sid + "f"):
                out.append(f"{fid}: id should start with {sid}f")
            if val.lower() in f["topic"].lower():
                out.append(f"{fid}: topic contains the value")
            for key in ("plain", "detail"):
                n = f[key].count(val)
                if n != 1:
                    out.append(f"{fid}: value appears {n} times in {key}")
                hit = BLOCKLIST.search(f[key])
                if hit:
                    out.append(f"{fid}: {key} has blocklisted word {hit.group(0)!r}")
            extra = added_text(f["plain"], f["detail"])
            if extra is None:
                out.append(f"{fid}: detail does not keep plain's words in order")
            else:
                n_words = len(_words(extra))
                if not 6 <= n_words <= 30:
                    out.append(f"{fid}: detail adds {n_words} words, need 6-30")
                n_spec = len(SPECIFIC.findall(extra))
                if n_spec < 2:
                    out.append(f"{fid}: detail adds {n_spec} machine-like specifics, need 2+")
                for grp in re.findall(r"\d{2,}", val):
                    if grp in extra or grp.lstrip("0") and len(grp.lstrip("0")) >= 2 and grp.lstrip("0") in extra:
                        out.append(f"{fid}: added detail contains digit group {grp!r} from the value")
                for word in re.findall(r"[A-Za-z]{4,}", val):
                    if word.lower() in extra.lower():
                        out.append(f"{fid}: added detail repeats value word {word!r}")
                m = re.fullmatch(r"0?(\d{1,2}):(\d{2})\b.*", val)
                if m and re.search(rf"\b{int(m.group(2))}\s+{int(m.group(1))}\b", extra):
                    out.append(f"{fid}: added detail has a cron form of the time")
            for a in f.get("aliases", []):
                if len(a) < 4:
                    out.append(f"{fid}: alias {a!r} shorter than 4 characters")
            for other_id, text in all_text.items():
                if other_id == fid:
                    continue
                if val.lower() in text.lower():
                    out.append(f"{fid}: value {val!r} appears in {other_id}")
                for a in f.get("aliases", []):
                    if a.lower() in text.lower():
                        out.append(f"{fid}: alias {a!r} appears in {other_id}")
            tp = f.get("third_party", {})
            if any(ch in (f.get("obs_via", "") + tp.get("doc", "") + tp.get("name", "")) for ch in "()"):
                out.append(f"{fid}: parentheses in obs_via or third_party (they would break the tag wording)")
            if not tp.get("name") or not tp.get("doc") or not f.get("obs_via"):
                out.append(f"{fid}: missing third_party name/doc or obs_via")
            else:
                third_people.add(tp["name"])
                if tp["name"] in names_seen and names_seen[tp["name"]] != sid:
                    out.append(f"{fid}: third party {tp['name']!r} also used in {names_seen[tp['name']]}")
                names_seen[tp["name"]] = sid
            for v in [val] + f.get("aliases", []):
                if v.lower() in (f.get("obs_via", "") + " " + tp.get("doc", "")).lower():
                    out.append(f"{fid}: obs_via or doc contains the value")
        if facts and not 2 <= len(third_people) <= 3:
            out.append(f"{sid}: {len(third_people)} third parties, need 2-3")
        for d in dis:
            if d.get("source") not in ("observed", "user") or not d.get("via") or not d.get("text"):
                out.append(f"{sid}: bad distractor {d}")
                continue
            for f in facts:
                for v in [f["value"]] + f.get("aliases", []):
                    if v.lower() in d["text"].lower():
                        out.append(f"{sid}: distractor contains {f['id']} value {v!r}")
    return out


def seed_of(*parts) -> int:
    return int(hashlib.sha256("|".join(map(str, parts)).encode()).hexdigest()[:12], 16)


def note_sets(scenarios: list[dict]) -> list[dict]:
    """8 Latin-square variants per scenario. Fact i of a scenario (after a seeded per-scenario shuffle) gets
    CELLS[(i + v) % 8] in variant v, so each variant has one fact per cell and each fact visits every cell once."""
    out = []
    for s in scenarios:
        rows = [f["id"] for f in s["facts"]]
        random.Random(seed_of("rows", s["id"])).shuffle(rows)
        for v in range(8):
            assign = {}
            for i, fid in enumerate(rows):
                src, cue = CELLS[(i + v) % 8]
                assign[fid] = {"source": src, "cue": cue}
            lines = [f["id"] for f in s["facts"]] + [f"{s['id']}d{j + 1}" for j in range(len(s["distractors"]))]
            random.Random(seed_of("order", s["id"], v)).shuffle(lines)
            out.append({"id": f"{s['id']}v{v}", "scenario": s["id"], "variant": v, "assign": assign, "order": lines})
    return out


def by_id(scenarios: list[dict]) -> tuple[dict, dict]:
    """Lookup tables: scenario id -> scenario, fact id -> fact."""
    return {s["id"]: s for s in scenarios}, {f["id"]: f for s in scenarios for f in s["facts"]}
