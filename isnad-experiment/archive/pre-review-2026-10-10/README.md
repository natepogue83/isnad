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
| `run.py` | sends every item to the model under every condition and saves the full responses |
| `report.py` | turns results into `results/report.md` with confidence intervals |
| `build_dataset.py` | rebuilds `items.jsonl` from the raw generated batches, re-running every check |
| `results/<model>/results.jsonl` | every response from the published run, with the full API response and its grade |
| `results/note_disclosure.*` | judge labels on whether caveat notes disclose memory use, every vote, and how they were made |
| `label_notes.py`, `findings_numbers.py`, `regrade.py` | note labeling, the extra counts behind FINDINGS.md, and re-scoring after grader changes |
| `FINDINGS.md` | the write-up of the published run |
| `results/pilot/` | an early pilot run (see its README for caveats) |

## Running it

You need Python 3.10 or newer and an Anthropic API key from console.anthropic.com.

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...        # Windows PowerShell: $env:ANTHROPIC_API_KEY="sk-ant-..."

python run.py --dry-run oracle             # free: confirms the grader scores a perfect answerer as perfect
python run.py --limit 20                   # small paid smoke test, about $1
python run.py                              # full run on Claude Opus 5.5, all four conditions
python report.py                           # writes results/report.md
```

To compare models, add `--models claude-opus-5-5 claude-sonnet-5-5 claude-haiku-5-5`. For error bars that reflect run-to-run variation, add `--reps 3`. Interrupted runs resume where they stopped.

The published run used medium effort for Claude (the default). The OpenAI models need `OPENAI_API_KEY`, and were run with:

```bash
python run.py --models gpt-5.5 gpt-5.4-mini --openai-reasoning medium
```

After a run:

```bash
python label_notes.py export > to_label.json   # notes on false-grounded answers, for the disclosure judges
# label each row with three judges and take the majority per key (instructions in results/note_disclosure.md,
# the workflow scripts used for the published run in judging/), saved as labels.json
python label_notes.py import labels.json       # writes results/note_disclosure.jsonl
python report.py                               # results/report.md: main rates with 95% intervals
python findings_numbers.py                     # results/findings_numbers.md: every other count quoted in FINDINGS.md
python regrade.py --write                      # only after changing isnad/grade.py: re-scores saved responses, no API calls
```

The results of the published run are written up in [FINDINGS.md](FINDINGS.md).

**Cost:** a full run makes 1,176 calls per model per rep. At medium effort the published run cost $10.09 on Claude Opus 5.5, $4.93 on Sonnet 5.5 and $0.31 on Haiku 5.5. The smoke test prints its actual cost so you can check before the full run.

## How to read the results

The headline number is **false grounding**: among answers that came from memory or were made up, the share presented as coming from the document. Lower is better. The two comparisons that test the ideas above are:

- `plain-strict` vs `plain-open`: does a document-only rule make models hide memory use? (seal of confession)
- `isnad-*` vs `plain-*`: does an explicit, graded chain of sources reduce hiding? (isnad)
