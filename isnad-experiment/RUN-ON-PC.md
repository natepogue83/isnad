# Running the gpt-5.4-mini half of the matched-instruction pilot

This folder is a copy of the experiment code for one job: the OpenAI half of the pilot described in MATCHED.md. The Claude half already ran in the cloud.

All commands run from a local copy of this folder. Use `python -X utf8` for every command.

1. Install: `python -X utf8 -m pip install -r requirements.txt`
2. Check the grader: `python -X utf8 tests\test_grade.py` (must end with "all probes pass").
3. The OpenAI key is the OPENAI_API_KEY line of a local key file outside the repository. Load it into the environment of the run commands only. Never print it, log it, or copy it to another file.
4. Smoke test (24 calls):
   `python -X utf8 run.py --models gpt-5.4-mini --openai-reasoning medium --items data/matched_items.jsonl --conditions plainmatch-open label-open isnadmatch-open --limit 8 --out runs/matched-smoke`
   Check: 24 rows in runs\matched-smoke\gpt-5.4-mini\results.jsonl with status "ok", no errors.jsonl, and runs\matched-smoke\gpt-5.4-mini\manifest.json shows "items_sha": "c95f2749e0c9fa95". Note the printed cost.
5. Full run (540 calls; stop if the printed projection passes $1.00):
   `python -X utf8 run.py --models gpt-5.4-mini --openai-reasoning medium --items data/matched_items.jsonl --conditions plainmatch-open label-open isnadmatch-open --reps 2 --out results/matched`
   If it stops part-way, run the same command again: it resumes without repeating finished calls.
