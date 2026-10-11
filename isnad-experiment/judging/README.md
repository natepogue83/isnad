# Note judge scripts

These are the exact workflow scripts used to label caveat notes. They run in Claude Code's workflow runtime, not as standalone Node scripts.

## Current labels (after the outside review, 2026-10-10)

- `make_blind_batches.py OUT_DIR` rebuilds the exact blinded batches: the 139 false-grounded notes for disclosure (3 batches) and the 114 note-answer candidates plus 60 random controls (3 batches). Model names and conditions are removed, records are shuffled with fixed seeds, and the id-to-response maps are written next to the batches.
- `blind_note_judges.js` sends each batch to 3 Claude Opus 5.5 judges and returns every vote. Point `DIR` at `OUT_DIR` first.
- Import the majority labels with `python label_notes.py import ...` (disclosure) and `python label_notes.py import-answers ...` (note answers). Both refuse missing, duplicate or unexpected keys.

The instructions are written out in `../results/note_disclosure.md` and `../results/note_answers.md`.

## First-round disclosure labels (kept for comparison)

The scripts below produced `../results/note_disclosure_v1.jsonl`. The judges could see model names.

- `note_disclosure_judges.js` labeled the first 138 rows. It used 12 batches, with 3 judges per batch, each given one of three instructions.
- `note_disclosure_judges_extra_row.js` labeled the 139th row, which became false-grounded after the grader fix. It used the same instructions.

`DIR` points to where the batches lived during the run. To rerun:

1. Point `DIR` at your own copy.
2. Split `python label_notes.py export` into `batch_00.json`, `batch_01.json`, and so on. Each file is a JSON list of exported records, about 12 per file.
3. Save the majority labels the script returns as `labels.json`, then run `python label_notes.py import labels.json`. That command always writes `results/note_disclosure.jsonl`, which holds the current round-2 labels, so back that file up first and rename the output to `note_disclosure_v1.jsonl`.

