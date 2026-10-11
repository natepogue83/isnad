# Pilot run (not an API measurement)

20 items (4 per type) under all 4 conditions, answered by isolated Claude subagents inside an agent harness rather than through the API. It exists to check the dataset and grader end to end. Its numbers are not comparable to `run.py` results, because the subagents had a different system prompt and environment.

What it caught, all fixed before the real runs (see DESIGN.md, "Changes made after the pilot and smoke test"):
- conflict answers that named both the document's value and the real one;
- an accuracy rule that penalized correcting a false document under the open policy;
- one false-grounding case where the citation was real but did not contain the answer.

The pilot used the original response schema (no `note` field).
