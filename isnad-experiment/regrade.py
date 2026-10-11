"""Re-score saved responses with the current grader, without calling any API.

  python regrade.py            # show which rows would change
  python regrade.py --write    # rewrite every results/**/results.jsonl with the new grades

Use this after changing isnad/grade.py. Only the "grade" field of each row changes.
"""

import json
import sys
from pathlib import Path

from isnad.grade import grade

ROOT = Path(__file__).parent


def main(write: bool) -> None:
    items = {json.loads(l)["id"]: json.loads(l) for l in (ROOT / "data" / "items.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()}
    changed = 0
    # Every results.jsonl under results/, including the matched pilot's results/matched/<model>/; the subagent pilot is skipped.
    for f in sorted((ROOT / "results").glob("**/results.jsonl")):
        if "pilot" in f.relative_to(ROOT / "results").parts:
            continue
        rows = [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]
        for r in rows:
            if r["status"] != "ok":
                continue
            new = grade(items[r["item_id"]], r["condition"], r["parsed"])
            if new != r["grade"]:
                changed += 1
                diff = {k: (r["grade"].get(k), new.get(k)) for k in new if r["grade"].get(k) != new.get(k)}
                print(f"{r['model']} {r['condition']} {r['item_id']}: {diff}")
                r["grade"] = new
        if write:
            f.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    print(f"{changed} rows {'re-graded' if write else 'would change'}")


if __name__ == "__main__":
    main("--write" in sys.argv)
