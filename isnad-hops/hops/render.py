"""Planted hop-1 notes in three forms: tagged prose (free and instructed disciplines), tag-stripped prose (the
reader-prior control), and the isnad chain JSON (chain discipline). Every tag is correct by construction."""

import json

CHAIN_SOURCE = {"OBS": "observed", "USER": "user", "THIRD": "third_party", "GUESS": "own_guess"}


def _via(phrase: str) -> str:
    phrase = phrase.strip()
    return phrase[4:] if phrase.lower().startswith("the ") else phrase


def prose_tag(source: str, fact_or_distractor: dict) -> str:
    if source == "OBS":
        return f"(I saw this myself in the {_via(fact_or_distractor['obs_via'])}.)"
    if source == "USER":
        return "(The user told me this.)"
    if source == "THIRD":
        tp = fact_or_distractor["third_party"]
        return f"({tp['name']}'s {tp['doc']} says this; I have not verified it.)"
    if source == "GUESS":
        return "(My own assumption; I have not checked it.)"
    raise ValueError(source)


def _lines(ns: dict, scenario: dict):
    """Yield (line_id, kind, sentence, source, item) in the note set's order. Distractor sources map to OBS/USER."""
    facts = {f["id"]: f for f in scenario["facts"]}
    dis = {f"{scenario['id']}d{j + 1}": d for j, d in enumerate(scenario["distractors"])}
    for lid in ns["order"]:
        if lid in facts:
            f, a = facts[lid], ns["assign"][lid]
            yield lid, "fact", f[a["cue"]], a["source"], f
        else:
            d = dis[lid]
            src = "OBS" if d["source"] == "observed" else "USER"
            yield lid, "distractor", d["text"], src, {"obs_via": d["via"]}


def planted_prose(ns: dict, scenario: dict, tagged: bool = True) -> str:
    out = [f"Working notes: {scenario['title']}", "", "What I have so far:"]
    for _, _, sentence, src, item in _lines(ns, scenario):
        out.append(f"- {sentence} {prose_tag(src, item)}" if tagged else f"- {sentence}")
    return "\n".join(out)


def chain_entry(sentence: str, value: str, source: str, item: dict) -> dict:
    if source == "OBS":
        via, verified = _via(item["obs_via"]), "yes"
    elif source == "USER":
        via, verified = "user message", "no"
    elif source == "THIRD":
        via, verified = f"{item['third_party']['name']}'s {item['third_party']['doc']}", "no"
    else:
        via, verified = "none (my own assumption)", "no"
    return {"claim": sentence, "value": value, "source": CHAIN_SOURCE[source], "via": via, "verified": verified}


def planted_chain(ns: dict, scenario: dict) -> str:
    claims = []
    for lid, kind, sentence, src, item in _lines(ns, scenario):
        value = item["value"] if kind == "fact" else ""
        claims.append(chain_entry(sentence, value, src, item))
    return json.dumps({"summary": f"Working notes: {scenario['title']}.", "claims": claims}, indent=1, ensure_ascii=False)
