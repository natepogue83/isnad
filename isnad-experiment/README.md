# Isnad: do AI models tell the truth about where their answers come from?

AI tools that answer questions about your documents show citations, and people trust "according to your contract" more than a bare answer. This experiment measures how often that trust is misplaced. It catches models answering from their own memory, or making something up, while presenting the answer as if it came from the document.

It also tests two ideas taken from older human practice for keeping testimony honest:

- **Chains of transmission (isnad).** Islamic hadith scholars made every report carry its full chain of sources and judged it by its weakest link. Here the model must label each piece of its answer as *document*, *memory* or *inference*, and grade each piece.
- **The seal of confession.** Admitting something should never cost more than hiding it. The experiment compares a policy that lets the model say "this is from my memory" with a strict "document only" policy that punishes it. The prediction is that the strict policy pushes models to hide where answers came from.

The full rationale, hypotheses and metrics are in [DESIGN.md](DESIGN.md).

## What's here

| file | what it does |
|---|---|
| `data/items.jsonl` | the test items: a document and a question each, built so the true source of the answer is known |
| `data/audit.md` | dataset checks: counts per type and anything dropped |
| `isnad/prompts.py` | the four conditions (plain or isnad format, open or strict policy) |
| `isnad/grade.py` | the grader: deterministic string checks, no AI judge |
| `tests/test_grade.py` | regression probes: real answer variants the grader must accept and plausible wrong answers it must reject |
| `run.py` | sends every item to the model under every condition, saves the full responses, and writes a manifest of input hashes |
| `report.py` | turns results into `results/report.md` with confidence intervals |
| `build_dataset.py` | rebuilds `items.jsonl` from the raw generated batches, re-running every check |
| `results/<model>/results.jsonl` | every response from the published run, with the full API response and its grade |
| `results/note_disclosure.*` | judge labels on whether caveat notes disclose memory use, every vote, and how they were made (`_v1` files: the first, unblinded round) |
| `results/note_answers.*` | judge labels on abstentions whose note still states the answer, every vote, and how they were made |
| `judging/` | the workflow scripts that ran the judges, and `make_blind_batches.py`, which rebuilds the blinded batches |
| `label_notes.py`, `findings_numbers.py`, `regrade.py` | note labeling, the extra counts behind FINDINGS.md, and re-scoring after grader changes |
| `FINDINGS.md` | the write-up of the published run |
| `results/pilot/` | an early pilot run (see its README for caveats) |
| `MATCHED.md`, `matched.py`, `results/matched/` | the matched-instruction follow-up: its pre-registered plan, item list and report script, and its responses, note labels and results (`results/matched/RESULTS.md`) |
| `PRIOR-WORK.md` | a finding-by-finding check of what earlier studies already showed (searched 2026-10-11) |
| `RUN-ON-PC.md` | how the follow-up's gpt-5.4-mini half was run on a Windows PC |

## Running it

You need Python 3.10 or newer and an Anthropic API key from console.anthropic.com.

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...        # Windows PowerShell: $env:ANTHROPIC_API_KEY="sk-ant-..."

python run.py --dry-run oracle --out runs/oracle                                 # free: a perfect answerer
python report.py --results runs/oracle/dry-run-oracle --out runs/oracle --no-labels  # should show 100% task scores
python run.py --limit 20 --out runs/smoke                # small paid smoke test, about $1; prints its cost
python run.py --out runs/full                            # full run on Claude Opus 5.5, all four conditions
python report.py --results runs/full/claude-opus-5-5 --out runs/full --no-labels
```

Always give a new run its own `--out` folder. The default, `results/`, holds the published run, so `run.py` would find every call already done and make none. `report.py` likewise writes to `results/` unless given `--out`. `--no-labels` skips the judged note columns, which need labels for the new run's false-grounded rows (see below).

To compare models, add `--models claude-opus-5-5 claude-sonnet-5-5 claude-haiku-5-5`. For error bars that reflect run-to-run variation, add `--reps 3`. Interrupted runs resume where they stopped, unless the items or prompts have changed since the folder was started; then `run.py` stops and asks for a new `--out` folder.

The published run used medium effort for Claude (the default). The OpenAI models need `OPENAI_API_KEY`, and were run with:

```bash
python run.py --models gpt-5.5 gpt-5.4-mini --openai-reasoning medium
```

The labeling and findings scripts below are set up for the published run in `results/`: `make_blind_batches.py`, `label_notes.py` and `findings_numbers.py` read that folder and its five models. Running them on a new run means pointing them at its folder.

After the published run:

```bash
python judging/make_blind_batches.py batches/   # blinded, shuffled batches for both kinds of note judging
# label each batch with three judges and take the majority per key (instructions in results/note_disclosure.md
# and results/note_answers.md, the workflow script in judging/), map the blind ids back to keys with the
# *_map.json files, and save them as labels.json and answer_labels.json. For answer_labels.json, keep only records
# whose _kind is "candidate" in note_answer_map.json; the 60 controls stay in note_answers_votes.jsonl only.
python label_notes.py import labels.json               # writes results/note_disclosure.jsonl
python label_notes.py import-answers answer_labels.json  # writes results/note_answers.jsonl
python report.py                               # results/report.md: main rates with 95% intervals and paired tests
python findings_numbers.py                     # results/findings_numbers.md: most other counts quoted in FINDINGS.md
python tests/test_grade.py                     # grader regression probes
python regrade.py --write                      # only after changing isnad/grade.py: re-scores saved responses, no API calls
```

The results of the published run are written up in [FINDINGS.md](FINDINGS.md).

**Cost:** a full run makes 1,176 calls per model per rep. At medium effort the published run cost $10.09 on Claude Opus 5.5, $4.93 on Sonnet 5.5 and $0.31 on Haiku 5.5. The smoke test prints its actual cost so you can check before the full run.

## How to read the results

The headline number is **false grounding**: among answers that came from memory or were made up, the share presented as coming from the document. Lower is better. The two comparisons that test the ideas above are:

- `plain-strict` vs `plain-open`: does a document-only rule make models hide memory use? (seal of confession)
- `isnad-*` vs `plain-*`: does an explicit, graded chain of sources reduce hiding? (isnad)

`report.md` also separates the **task score** (followed the policy and gave an acceptable value) from **factual accuracy** (the answer is true), and shows how often a strict-policy abstention still states the answer in its note.
