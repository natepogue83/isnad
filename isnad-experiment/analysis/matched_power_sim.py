"""Power simulation behind MATCHED.md's choice of all 54 memory-only items at 2 runs over 30 items at 3 runs.

  python analysis/matched_power_sim.py      (needs numpy)

Written by the design-review checker on 2026-10-10, before any pilot call, and saved here afterwards so the numbers
in MATCHED.md can be checked. Assumptions:
- Each memory-only item's chance of false grounding under `plainmatch` is f times the share of four models
  (Opus, Sonnet, Haiku, gpt-5.4-mini) that false-grounded it under the published `plain-open` prompt.
  That share averages 27% (59 of 216), so f = 0.25 is a mean rate of about 7 points ("moderate") and
  f = 0.15 about 4 points ("small").
- `isnadmatch` is at zero on every item.
- "Power" is the share of 1,000 simulated pilots in which the item-bootstrap interval for C1 lies above zero
  (first number) or the exact sign test gives p < 0.05 (second number). The pre-registered call needs both,
  so its power is at most the smaller of the two.
"""

import json
from math import comb
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
matched30 = {"memory_only-%03d" % i for i in (1, 3, 4, 7, 10, 11, 12, 15, 17, 19, 21, 22, 23, 25, 26, 29, 30, 33, 36, 37,
                                              41, 42, 43, 46, 47, 49, 50, 51, 52, 54)}  # the first draft's seeded draw
allmem = sorted(json.loads(l)["id"] for l in (ROOT / "data" / "items.jsonl").read_text(encoding="utf-8").splitlines()
                if l.strip() and json.loads(l)["type"] == "memory_only")
models = ["claude-haiku-5-5", "claude-opus-5-5", "claude-sonnet-5-5", "gpt-5.4-mini"]
freq = {i: 0 for i in allmem}
for m in models:
    for l in (ROOT / "results" / m / "results.jsonl").read_text(encoding="utf-8").splitlines():
        r = json.loads(l)
        if r["condition"] == "plain-open" and r["type"] == "memory_only" and r["status"] == "ok" and r["grade"]["false_grounding"]:
            freq[r["item_id"]] += 1
p_all = np.array([freq[i] / 4 for i in allmem])
p_30 = np.array([freq[i] / 4 for i in allmem if i in matched30])
rng = np.random.default_rng(1)


def sign_p(pos, neg):
    n = pos + neg
    if n == 0:
        return 1.0
    k = min(pos, neg)
    return min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n)


def sim(p, reps, f, nsim=1000, boot=4000):
    hits = sig = 0
    for _ in range(nsim):
        d = rng.binomial(reps, np.clip(f * p, 0, 1)) / reps  # isnadmatch is 0, so the difference is plainmatch's rate
        idx = rng.integers(0, len(d), size=(boot, len(d)))
        lo = np.sort(d[idx].mean(1))[int(0.025 * boot)]
        hits += lo > 0
        sig += sign_p(int((d > 0).sum()), 0) < 0.05
    return round(float(hits) / nsim, 2), round(float(sig) / nsim, 2)


print(f"mean published plain-open rate across the 4 models: {p_all.mean():.3f}")
for f in (0.5, 0.25, 0.15):
    print(f"f={f}: 30 items x 3 runs {sim(p_30, 3, f)}   54 items x 2 runs {sim(p_all, 2, f)}")
