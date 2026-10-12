# Isnad across hops (pilot)

Does an AI agent keep the source of each fact when it rewrites its own handoff notes, or does the source get lost or quietly "upgraded" (a third party's unverified claim turning into something the agent saw itself)? And does machine-like detail on a claim (a file path, a line number, a job name) make that upgrade more likely?

This is the follow-up to the isnad experiment (`../isnad-experiment/`), which showed that a source-label format fixes false grounding in a single answer. Here the question is whether labels survive the agent's own retelling. The design is P15 from an earlier research pass, included here in `design/` (P15.md plus the two red-team reviews, P15-A.md and P15-B.md), cut down to a pilot that fits about $10 of API credit.

The code was written by Claude (Anthropic's model) under Nate's direction, and checked by tests and an independent review agent. Nate picked this experiment from a set of candidate designs, asked for it to be checked before any credit was spent, and set the budget.

## What one chain looks like

1. The build script writes an agent's working notes about a task. Each of 8 facts carries a correct source tag: seen in the agent's own tool output, told by the user, claimed in a named colleague's document (unverified), or the agent's own unchecked assumption. Half the facts carry machine-like detail.
2. A writer model (Claude Haiku 5.5 or Claude Opus 5.5) rewrites the notes as a handoff for another agent (hop 2), then rewrites its own handoff again (hop 3).
3. A fixed reader (Claude Sonnet 5.5, never one of the writers) reads each version and says, per fact, what the value is, where the notes say it came from, and whether it would act on it without checking.

A Latin square rotates every fact through all 4 sources and both detail levels, so content is held constant. Three writing disciplines: free notes, notes told to say how each fact was obtained, and the isnad JSON chain (a mandatory source field per claim).

## Files

- `data/SPEC.md`, `data/scenarios.json`: the 6 pilot scenarios (48 facts) and the rules they pass.
- `hops/items.py`: item validator, Latin square, note sets. `hops/render.py`: planted notes. `hops/prompts.py`: every prompt and schema. `hops/grade.py`: deterministic scoring. `hops/fake.py`: offline fake models for tests.
- `run.py`: the runner (standard or batch API, resume, manifest, spend guard). `analyze.py`: scoring and report.
- `tests/test_all.py`: unit tests and full offline dry runs (`python tests/test_all.py`).
- `FINDINGS.md`: what the pilot found, in plain language. Start here.
- `PREREG-PILOT.md`: what the pilot measures and the checks fixed before any paid call.
- `results/<run>/`: `calls.jsonl` (every raw response), `facts.jsonl`, `RESULTS.md`, `summary.json`.

## Running it

```
pip install anthropic
python tests/test_all.py
python run.py --closed-book --key-file KEYFILE --budget 0.1 --out results/closedbook-forced
python run.py --out results/smoke --mode standard --notesets p1v0 p4v3 --disciplines free instructed chain free120 --key-file KEYFILE --budget 2
python analyze.py results/smoke
python run.py --out results/pilot --mode batch --token-means results/smoke --key-file KEYFILE --budget 8.4
python run.py --out results/pilot --writers haiku --disciplines free120 --mode batch --token-means results/smoke --key-file KEYFILE --budget 9.0
python analyze.py results/pilot
```

The budgets above are what this pilot used. `--budget` caps total spend in that folder, so the second pilot command raises the folder's cap from $8.40 to $9.00 to add Haiku's 120-word chains. With the smoke test's actual cost ($0.66) in place of its $2 cap, the total stays under $10. Add `--plan` to any run command to see its estimated cost without calling the API. If a batch create fails, the runner stops; rerunning the same command looks for the batch before submitting anything, and if it finds none it asks you to check the Claude Console and rerun with `--abandon-intent ID`.

`KEYFILE` is a text file containing an Anthropic API key (`sk-ant-...`). The runner never prints it.
