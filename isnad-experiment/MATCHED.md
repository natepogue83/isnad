# Matched-instruction pilot: design and analysis plan

Written 2026-10-10, before any pilot call was made, and revised once, still before any call, after a five-agent design review (see "Design review" at the bottom). Results go in `results/matched/`. After the first paid call this file changes only in the "Deviations" section.

## Why

In the published run, the isnad format cut false grounding on memory-only questions to zero for four of five models. But the isnad prompt differed from the plain prompt in two ways at once: it asked for a chain of labeled sources, and it said "a fact you recalled is 'memory' even when the document is about the same topic". The plain prompt had neither. So the drop could come from the chain, from that sentence, or from both (FINDINGS.md, caution 2; the outside review by Astra made the same point).

There is a second question behind the first. For Opus and Sonnet, the published plain-format false grounding was almost always disclosed in the note, so the chain may have moved a disclosure into a checkable field rather than changed what the model does. A fair comparison has to look at both.

This pilot holds the instruction fixed and varies only the format.

## Question

With the same source instruction in every prompt, does a structured source field (one label, or the isnad chain) reduce false grounding compared with a plain citation, and does it change what a reader is told, or only where the disclosure is written?

## Conditions

All three use the open policy, word for word as published, and share the same two sentences about sources (`SOURCE_RULE` in `isnad/prompts.py`):

> Be accurate about where your answer came from: a fact you recalled is memory even when the document is about the same topic, and a passage that is only related to the answer does not support it. If your answer came from memory, say so in the note.

The first sentence extends the published isnad sentence with the related-passage clause that FINDINGS.md's "What to try next" proposed. The second gives every format the same way to disclose memory in words. Neither was in any published prompt, so the pilot tests this stronger instruction, not the published sentence alone.

| condition | format | what it changes from the one before |
|---|---|---|
| `plainmatch-open` | answer, note, citation (the published plain schema) plus `SOURCE_RULE` | the instruction alone, on plain |
| `label-open` | `plainmatch` plus one field, `source`: document / memory / inference | one answer-level label |
| `isnadmatch-open` | the published isnad prompt, with its memory sentence replaced by `SOURCE_RULE` | the whole isnad package: a chain instead of one label, link grades, the weakest-link sentence, no separate citation field, and "inference" defined as derived from earlier links rather than from the document |

So `label` vs `isnadmatch` compares one label with the whole isnad package, not chaining alone. The full prompts print with `python -c "from isnad.prompts import system_prompt; print(system_prompt('label-open'))"`.

## Outcomes

Each is computed per call on memory-only questions, then compared by item.

1. **False grounding, by the format's own rule** (what a machine check of the format sees; `isnad/grade.py`, probes in `tests/test_grade.py`):
   - `plainmatch`: a memory answer with any citation, as in plain.
   - `label`: a memory answer labeled `document` or `inference`, whatever the citation. With no label, the citation decides, as in plain.
   - `isnadmatch`: a memory answer whose chain has no memory link (the published definition). The answer-link reading, which looks only at the link that carries the answer, is reported as a sensitivity check.
2. **Silent false grounding** (what a human reader is told; format-neutral): false grounding whose note is empty or does not tell the reader that the answer isn't from the document. Notes are labeled with the round-2 protocol in `results/note_disclosure.md`: blinded and shuffled records, 3 Claude Opus 5.5 judges per batch, the same rubric and precedence rule, majority label. The judges' framing sentence says the answer was presented "as coming from the document (a quote, a source label, or a chain)", since label rows can be false-grounded without a quote. `python matched.py batches DIR` builds the batches.
3. **Quote attached** (what the model quotes; format-neutral): a memory answer that carries a real document quote anywhere, as the citation or as a chain link.

Outcomes 1 and 2 are co-primary. Outcome 3 is secondary.

## Models and settings

- `claude-sonnet-5-5` at medium effort, run from the cloud.
- `gpt-5.4-mini` at medium reasoning effort, run on Nate's PC (the cloud can't reach OpenAI).

These match the published run's settings. Under the published `plain-open` prompt, Sonnet false-grounded 13 of the 54 memory-only questions and gpt-5.4-mini 14, so both have room to move.

## Items

90 items, written by `python matched.py items` (seed 20261010) to `data/matched_items.jsonl` (ASCII-escaped, so a Windows Python reads the same text):

- all 54 memory-only items (the primary measure)
- 12 conflict items (secondary: does the rule stop the model citing the passage it corrects?)
- 12 context-only and 12 inference items (cost check: does the rule make models stop citing real document answers?)

Unanswerable items are left out. Fabrication was rare in the published run (5 of 60 for mini, 0 for Sonnet), too rare to measure here.

## Runs

2 runs of each item under each condition at the API's default sampling: 90 × 3 × 2 = 540 calls per model, 1,080 in all.

Estimated cost from the published run's token use: about $2.40 for Sonnet and about $0.65 for gpt-5.4-mini. Each model starts with a 24-call smoke test (`--limit 8`, two items per type), checked for errors, schema failures and cost before the full run. A run stops if its projected cost passes $3.50 (Sonnet) or $1.00 (mini). `run.py` prints the spend so far and the projection every 25 calls.

```
python run.py --models claude-sonnet-5-5 --items data/matched_items.jsonl --conditions plainmatch-open label-open isnadmatch-open --limit 8 --out runs/matched-smoke
python run.py --models claude-sonnet-5-5 --items data/matched_items.jsonl --conditions plainmatch-open label-open isnadmatch-open --reps 2 --out results/matched
python run.py --models gpt-5.4-mini --openai-reasoning medium --items data/matched_items.jsonl --conditions plainmatch-open label-open isnadmatch-open --limit 8 --out runs/matched-smoke
python run.py --models gpt-5.4-mini --openai-reasoning medium --items data/matched_items.jsonl --conditions plainmatch-open label-open isnadmatch-open --reps 2 --out results/matched
python matched.py report
```

On Windows, run Python with `-X utf8` as a second guard on text encoding.

## Comparisons, fixed in advance

For each model and outcome, each item's rate is averaged over its runs, and two conditions are compared on the paired per-item difference: the mean difference, a 95% interval from 10,000 item resamples (seed 20261010), and an exact two-sided sign test over items whose rates differ.

A difference is called **above zero** only if the interval lies above zero and the sign test gives p < 0.05, and **below zero** by the same rule in the other direction. Otherwise it is **no clear difference**. When the two disagree (which happens when only a handful of items differ), the call is no clear difference.

- **C1 (primary): `plainmatch` vs `isnadmatch`,** on outcomes 1 and 2. Does the isnad package help beyond the instruction?
- C2: `plainmatch` vs `label`, on outcomes 1 to 3. Does one label help?
- C3: `label` vs `isnadmatch`, on outcomes 1 to 3. Does the isnad package add anything over one label?
- Sensitivity: C1 and C3 on the answer-link reading, and C1 to C3 on outcome 3.
- R1: published `plain-open` vs `plainmatch`, on outcome 1, plus the share of the published `plain-open` to `isnadmatch` gap that `plainmatch` closes, with an item-bootstrap interval.
- R2: published `isnad-open` vs `isnadmatch`, on outcome 1 (the added instructions on isnad).

R1 and R2 compare against single runs made on an earlier day, with prompts that didn't ask for a note about memory, so they are references, not tests, and their silent counts aren't comparable with the pilot's. C1 is the primary test per model. Everything else is exploratory, with no correction for multiple comparisons.

## How the results will be read

Written before the runs. Each model is read separately.

- **The isnad package changes what the reader is told** if C1 is above zero on both false grounding and silent false grounding.
- **It moves the disclosure into a checkable field** if C1 is above zero on false grounding but not on silent false grounding. Then the format makes the source machine-checkable without changing what a reader of the note learns.
- **The instruction does the work** if C1 is no clear difference on false grounding with its interval's upper end under 10 points, and these guards hold: `plainmatch` answers memory-only questions from memory at least as often as `isnadmatch` (within 5 points), and it still cites at least 90% of its correct context-only and inference answers (published `plain-open`: 24 of 24 for both models).
- **The instruction does little** if `plainmatch`'s per-item mean false grounding is at least two thirds of published `plain-open`'s on the same items.
- **The isnad package does worse** if C1 is below zero.
- Anything else is reported as inconclusive, with the numbers.

With 54 items and 2 runs, the pilot can show a large effect but cannot rule out a small one, and the write-up will say so.

## Secondary measures

- Conflict questions: memory answers, how many are false-grounded, how many still quote the passage they correct (in any format), how many follow the document instead, and answers that name both values (hand-checked if any).
- Cost of the rule on document questions: correct rate; correct document answers with no quote, a `memory` label, or a memory link on the answer ("under-claimed", one rule for every format); and `label` rows marked `document` with no citation.
- What `label` says for remembered answers (document / inference / memory / missing).
- False grounding resting only on invalid quotes (for example a citation of "N/A"); any non-zero count is hand-checked before C1 is read.
- Run-to-run spread: false-grounded memory-only calls in each run, which also shows how far a single run, like the published one, can be trusted.
- Items missing runs are kept, averaged over the runs they have, listed in the report, and logged below as a deviation.

## Not tested

- The strict policy, other models, and real documents.
- Whether the published isnad sentence alone, without the related-passage and note sentences, would close the gap.
- Whether `SOURCE_RULE` makes models label document-stated facts they also know as memory. Every document-answer item is about an invented entity (FINDINGS.md caveat), so the cost check can't detect this.
- The published Sonnet rows don't store the request, so their prompt can only be checked against the code, not the rows.

## Design review (before any call)

Five Claude agents reviewed the first version: four with one lens each (prompts, grader, statistics, operations) and one checking every finding. Of 29 findings, 3 were duplicates, 3 were refuted and 23 held up. Changes made:

- **Fairer outcomes.** The first version compared formats only by each format's own scoring rule. Plain counts any citation on a memory answer; isnad is cleared by any memory link, even next to a quoted passage. In the published run, Sonnet's isnad chains quoted the document for 50 of 54 memory answers. Silent false grounding is now co-primary and "quote attached" is secondary, so a format can't win only by where it records the disclosure.
- **All 54 memory-only items at 2 runs** instead of 30 at 3, for the same 540 calls per model. The seeded 30-item draw happened to leave out all four items on which gpt-5.4-mini's published isnad chain failed (a 3% chance). A simulation put the power for C1 at 0.95 against 0.84 for a moderate effect, and 0.64 against 0.47 for a small one.
- **Decision rules.** The first version's "no more than 5 of 90" threshold and its interval rule could disagree on a one-item difference. Calls now need the interval and the sign test to agree, and every reading has a numeric definition.
- **Claims.** The reading "the published drop is mostly the sentence" was dropped, because `SOURCE_RULE` is stronger than the published sentence. `label` vs `isnadmatch` is now described as the whole isnad package.
- **Windows encoding.** The first item file held raw UTF-8, which a default Windows Python would have misread on 8 memory-only documents without any error. It is now ASCII-escaped, and every file read and write names UTF-8.
- **Run safety.** Stopping a run with Ctrl+C used to keep making queued calls and drop their answers. Workers now save each answer as it arrives, and queued calls are cancelled. A cut-off OpenAI reply is now saved as an unscored row, not retried and paid for again. The results folder now refuses a resume with a different model or effort setting, and `run.py` prints spend and projected cost for gpt-5.4-mini.
- **Grader and report.** A `label` answer with no label but a citation now reads as plain. The report adds the missing columns: quotes on conflict answers, answers naming both values, invalid-quote-only false grounding, one under-claiming rule, item counts per comparison, and an effort check. `regrade.py` now covers `results/matched/`.

Not changed: the reviewer's suggested fourth arm (plain plus the published sentence only), which would cost about 180 more calls per model; and the label format's definition of "inference", which the checker found doesn't bias the comparison.

## Deviations

No change to the design, items, prompts, grader or analysis. Results: `results/matched/RESULTS.md`. Notes added after the runs:

- **Runs.** Both runs completed every planned call with no errors, refusals or cut-off replies. gpt-5.4-mini was served as `gpt-5.4-mini-2026-03-17`. The note judges used the framing sentence stated above, and all 17 labels were unanimous.
- **"An earlier day" is wrong.** The "Comparisons" section above, and a comment in `matched.py`, say the published reference runs were made on an earlier day. They were made earlier the same day (the published gpt-5.4-mini rows are stamped 11:45 to 11:49 UTC on 2026-10-10). They are still single runs not made alongside the pilot, so R1 and R2 stay references. The text above is left as written.
- **Plan snapshot.** This file's final text was written before the first paid call (the Sonnet smoke test, 23:05:52 UTC) but was not hashed into the run manifests. The earliest copy outside this folder is the one sent to Nate's PC at 23:07:27 UTC, which matches this file except for this section; it was made after the Sonnet run started (23:06:15) and before the gpt-5.4-mini run (23:08:35). `matched.py` is byte-identical to its pre-run copy.
- **Power.** Rerunning the review's simulation (`analysis/matched_power_sim.py`) gives 0.94, not 0.95, for the interval criterion alone at a moderate effect. With the sign test also required, as the call rule does, power is 0.69 for a moderate effect and 0.23 for a small one.
- **Mixed notes.** The judges labeled near-identical mixed notes ("this is from general knowledge" after saying the document implies the answer) differently. Applying the precedence rule strictly gives 18 undisclosed in gpt-5.4-mini's plain format, and a lenient reading gives 14, against the judged 16. No pre-registered call changes.
