"""Helpers for the pilot run, which used Claude subagents in place of API calls.

  python pilot_tools.py prepare --per-type 6 > pilot_jobs.json   # stratified jobs with rendered prompts
  python pilot_tools.py ingest pilot_outputs.json                 # grade outputs into results/pilot/results.jsonl

The pilot validates the dataset and pipeline end to end. Its numbers are not API results: the
subagents ran inside an agent harness with its own system prompt. Use run.py for real measurements.
"""

import json
import random
import sys
from pathlib import Path

from isnad.grade import grade
from isnad.prompts import CONDITIONS, system_prompt, user_message

ROOT = Path(__file__).parent


def prepare(per_type: int, seed: int = 0) -> list[dict]:
    items = [json.loads(line) for line in (ROOT / "data" / "items.jsonl").read_text().splitlines() if line.strip()]
    rng = random.Random(seed)
    by_type: dict[str, list] = {}
    for it in items:
        by_type.setdefault(it["type"], []).append(it)
    chosen = [it for t in sorted(by_type) for it in rng.sample(by_type[t], min(per_type, len(by_type[t])))]
    return [
        {"item_id": it["id"], "condition": c, "format": c.split("-")[0], "system": system_prompt(c), "user": user_message(it)}
        for it in chosen
        for c in CONDITIONS
    ]


def ingest(outputs_path: str) -> None:
    items = {json.loads(l)["id"]: json.loads(l) for l in (ROOT / "data" / "items.jsonl").read_text().splitlines() if l.strip()}
    outputs = json.loads(Path(outputs_path).read_text())
    out_dir = ROOT / "results" / "pilot"
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "results.jsonl", "w") as f, open(out_dir / "errors.jsonl", "w") as ferr:
        for o in outputs:
            item = items[o["item_id"]]
            if not o.get("parsed"):
                ferr.write(json.dumps({"item_id": o["item_id"], "condition": o["condition"], "rep": 0, "model": "pilot",
                                       "error_class": "NoOutput", "error": "subagent returned nothing"}) + "\n")
                continue
            row = {
                "item_id": item["id"], "type": item["type"], "condition": o["condition"], "rep": 0, "model": "pilot",
                "status": "ok", "parsed": o["parsed"], "usage": {"input_tokens": 0, "output_tokens": 0},
            }
            row["grade"] = grade(item, o["condition"], o["parsed"])
            f.write(json.dumps(row) + "\n")


if __name__ == "__main__":
    if sys.argv[1] == "prepare":
        per = int(sys.argv[sys.argv.index("--per-type") + 1]) if "--per-type" in sys.argv else 6
        print(json.dumps(prepare(per)))
    elif sys.argv[1] == "ingest":
        ingest(sys.argv[2])
