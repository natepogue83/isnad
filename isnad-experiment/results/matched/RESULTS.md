# Matched-instruction pilot: results

Run 2026-10-10, after the design and analysis plan in `MATCHED.md` were fixed. Every number below comes from `report.md` in this folder (`python matched.py report`) or from the saved responses next to it.

**Runs.** Claude Sonnet 5.5 made 540 calls plus a 24-call smoke test, for $2.40. gpt-5.4-mini made 540 plus 24, using 423,642 input and 84,906 output tokens; that is about $0.70 at a third-party list price of $0.75 and $4.50 per million tokens, not checked against OpenAI's own page. It was served as `gpt-5.4-mini-2026-03-17` and run on Nate's PC. There were no errors, refusals or cut-off replies. 17 caveat notes on false-grounded answers were judged blind by 3 Claude Opus 5.5 judges each. All 17 were unanimous, but the judges labeled near-identical notes differently (see Limits).

## The answer depends on the model

The question was whether the published isnad drop came from the chain format or from its instruction about memory. Every format here got the same instruction, stronger than the published one. The two models gave opposite answers. The headings below use the readings fixed in `MATCHED.md`.

**Claude Sonnet 5.5: the instruction does the work.** With the shared instruction, Sonnet's plain citations presented a remembered answer as coming from the document on 2 of 108 memory-only calls (2%). In the published plain run, without the instruction, it was 13 of 54 (24%); that run was made earlier the same day, so this is a reference, not a test. The isnad package was at 0 of 108, a difference of 1.9 points (95% interval 0.0 to 4.6), so no clear difference. Both of those notes said the name came from general knowledge, so no format left a reader uninformed. The pre-registered guards held: Sonnet answered every memory-only question from memory in every format, and cited all 48 of its correct document answers.

**gpt-5.4-mini: the instruction does little, and the isnad package changes what the reader is told.** The instruction did little for mini's plain citations: 27 of 108 (25%), against 14 of 54 (26%) in the published run. That is a reference comparison, and a small effect can't be ruled out (interval -4.6 to +6.5 points). All 14 items it false-grounded in the published run did so again in at least one of the pilot's two runs. One source label cut false grounding to 10 of 108 (9%), and the isnad package cut it to 3 of 108 (3%).

- Isnad package vs plain, same instruction: 22.2 points lower (interval 13.0 to 31.5; 17 items lower, 0 higher; sign test p = 0.00002).
- What the reader is told: undisclosed false grounding fell from 16 of 108 to 3 of 108. That is 12.0 points (interval 5.6 to 19.4; p = 0.002), so the isnad package changed what a reader learns, not just where it's recorded. In the plain format, 14 of mini's 27 false-grounded answers had an empty note, although the prompt asked it to say so in the note. Reading the mixed notes strictly or leniently (see Limits) gives 14 to 18 instead of 16, and the call is the same.
- One label vs plain (exploratory): false grounding fell clearly (15.7 points, p = 0.001), which is about 70% of the isnad package's drop. But undisclosed false grounding fell only from 16 to 10, which is not a clear difference (p = 0.11), and all 10 remaining label failures were undisclosed. Half of them were labeled `document` and half `inference`.
- Isnad package vs one label (exploratory): 6.5 points lower, not a clear difference (p = 0.07).

## Quoting and the source labels

**Quoting.** The formats changed quoting in different ways for the two models. For Sonnet, the isnad package brought it back: with the instruction, its plain and label answers quoted the document for 2 of 108 memory answers, but its chains quoted a related passage for 80 of 108, each next to a memory link (a clear difference). For mini, no format changed it: 23 to 27 of 108 memory answers carried a quote in every format. In the label format, 13 of its 23 quoted answers were labeled `memory`, so the label told the truth while the citation field still held a passage. A product that shows quotes as "sources" would display passages that don't contain the answer, from Sonnet's chains and from mini in every format.

**The remaining failures.** In the label format, 5 of mini's 10 failures were labeled `inference` and 5 `document`, so checking only the `inference` label would catch half. All 3 isnad failures were chains of document quotes ending in an inference (Mendeleev twice, Chadwick once).

## Other results

- **Conflict questions.** When Sonnet corrected a false document, its plain citation of the sentence it was correcting fell from 9 of 10 in the published run to 1 of 18, and that one note said the document was wrong. Sonnet followed the false document on 3 to 7 of 24 calls per format, against 2 of 12 published, and named the real answer in the note every time. mini followed the false document on 22 or 23 of 24 calls in every format, as before.
- **No sign of a cost on these items.** Every format answered all 24 document questions correctly in both runs and cited every answer (48 of 48). Those answers are about invented entities, so this can't show whether the instruction makes models call a document-stated fact they also know "memory".
- **Tokens.** Compared with plain plus the instruction, the label format used about 13% more input and 11% more output tokens on both models. The isnad package used about 30% more input, plus 43% (mini) to 130% (Sonnet) more output.
- **Run-to-run spread.** mini's plain format false-grounded 13 and 14 times in its two runs, but only 9 of its 18 items did so in both. A single run, like the published one, gives a stable rate, but not a stable list of which items fail.

## What this means for the published finding

The published run couldn't say whether the chain or the memory instruction cut false grounding. For Sonnet, an instruction was enough. That instruction was stronger than the published one: it added "a passage that is only related to the answer does not support it" and "if your answer came from memory, say so in the note". Whether the published sentence alone would have been enough is not tested. For gpt-5.4-mini, this instruction didn't change how often a remembered answer came with a related passage as its citation. A source label or chain stated the source correctly far more often. Only the isnad package clearly reduced the cases where nothing told the reader. It had the fewest failures (3 of 108), but it was not clearly lower than one label (10 of 108; p = 0.07).

For a product: with this instruction, Sonnet needed nothing more. For mini, one answer-level label cut false grounding from 27 to 10 of 108, for about 13% more input tokens. But that comparison is exploratory. The label didn't clearly reduce undisclosed cases, and half of its remaining failures were labeled `document`, so a check on the `inference` label alone would miss them. The related-passage rule was in every prompt, so this pilot can't say whether it helps on its own.

## Limits

- Two models, 54 memory-only items, 2 runs each, on built documents, in one day.
- The comparisons with the published runs (the "instruction alone" effects above) use runs made earlier the same day, not alongside the pilot, so they are references rather than tests.
- The pre-registered calls need the 95% item-bootstrap interval to exclude zero and an exact sign test p < 0.05. With no correction for multiple comparisons, everything except the primary comparison is exploratory.
- The note judges labeled near-identical mixed notes differently. mini's "The document implies a river but does not name it; this is from general knowledge" (two runs) was labeled disclosed, while "The document implies this border mountain chain; the specific name comes from general knowledge" and a similar vitamin note were labeled not disclosed under the rubric's precedence rule. Applying the rule strictly gives 18 undisclosed in mini's plain format, and treating "from general knowledge" as enough gives 14. The judged count is 16. No pre-registered call changes.
- The plan's final text was written before the first paid call but not hashed into the run manifests; see `MATCHED.md`, Deviations.

## Next

1. A fourth arm for Sonnet with only the published sentence, to see whether the added clauses matter (about 108 calls, about $0.50).
2. For mini, whether an explicit rule in the citation instruction ("set citation to null if the answer came from memory") reaches the field when the general rule doesn't.
3. Real documents with obscure facts, where the answer may appear in the document in another role.
