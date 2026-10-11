# Results: smoke

Rates are shown as percent (k/n; Wilson 95% interval). Intervals marked 'scenario bootstrap' resample the 6 scenarios and are descriptive only.

## 1. Run health

| model | call type | calls | ok | refusal | truncated | invalid | errored | mean in | mean out |
|---|---|---|---|---|---|---|---|---|---|
| claude-haiku-5-5 | writer_chain | 4 | 4 | 0 | 0 | 0 | 0 | 1960 | 1779 |
| claude-haiku-5-5 | writer_prose | 12 | 12 | 0 | 0 | 0 | 0 | 867 | 1295 |
| claude-opus-5-5 | writer_chain | 4 | 4 | 0 | 0 | 0 | 0 | 1916 | 1144 |
| claude-opus-5-5 | writer_prose | 12 | 12 | 0 | 0 | 0 | 0 | 913 | 927 |
| claude-sonnet-5-5 | reader | 38 | 38 | 0 | 0 | 0 | 0 | 1757 | 340 |

Total spend in this folder: $0.66 (every call ever made, including retries).

## 2. Reader check on the planted notes (hop 1, reader alone)

- Tagged prose: source read correctly on plain facts 100.0% (8/8; 68-100); all facts 100.0% (16/16; 81-100); value returned 100.0% (16/16; 81-100).
- Tagged chain: source read correctly on plain facts 100.0% (8/8; 68-100); all facts 100.0% (16/16; 81-100); value returned 100.0% (16/16; 81-100).

Gate (pre-registered: at least 97% on plain planted facts, prose and chain pooled): PASS (100.0% (16/16; 81-100)).

## 3. Reader on tag-stripped planted notes (what a bare claim is read as)

| cue | n | observed | user | third party | guess | not stated |
|---|---|---|---|---|---|---|
| plain | 8 | 0.0% | 0.0% | 0.0% | 0.0% | 100.0% |
| detail | 8 | 0.0% | 0.0% | 0.0% | 0.0% | 100.0% |

Detail minus plain, share read as observed: +0.0 points.

## 4. Source fidelity across rewrites (fixed reader, Sonnet 5.5)

Content kept is a string match on the artifact; a failed writer call counts as not kept. U (upgrade) = third-party or guess facts read as observed or user-stated, out of all such facts the reader scored or whose writer failed (a lost value counts as no upgrade). D = observed or user facts read as third-party or guess. Source correct and loss (source read as not stated) are among facts whose value the reader returned. 'scored' = reader answers available / chain cells started.

| writer | discipline | hop | scored | content kept | source correct | loss | U third plain | U third detail | U guess plain | U guess detail | D | third read as observed | weak facts relied on unchecked |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| (planted) | chain JSON | planted | 100% (16/16) | 100% (16/16) | 100% (16/16) | 0% (0/16) | 0% (0/2) | 0% (0/2) | 0% (0/2) | 0% (0/2) | 0% (0/8) | 0% (0/4) | 0% (0/8) |
| haiku | chain | 2 | 100% (16/16) | 100% (16/16) | 100% (16/16) | 0% (0/16) | 0% (0/2) | 0% (0/2) | 0% (0/2) | 0% (0/2) | 0% (0/8) | 0% (0/4) | 0% (0/8) |
| haiku | chain | 3 | 100% (16/16) | 100% (16/16) | 100% (16/16) | 0% (0/16) | 0% (0/2) | 0% (0/2) | 0% (0/2) | 0% (0/2) | 0% (0/8) | 0% (0/4) | 0% (0/8) |
| opus | chain | 2 | 100% (16/16) | 100% (16/16) | 100% (16/16) | 0% (0/16) | 0% (0/2) | 0% (0/2) | 0% (0/2) | 0% (0/2) | 0% (0/8) | 0% (0/4) | 0% (0/8) |
| opus | chain | 3 | 100% (16/16) | 100% (16/16) | 100% (16/16) | 0% (0/16) | 0% (0/2) | 0% (0/2) | 0% (0/2) | 0% (0/2) | 0% (0/8) | 0% (0/4) | 0% (0/8) |
| (planted) | tagged prose | planted | 100% (16/16) | 100% (16/16) | 100% (16/16) | 0% (0/16) | 0% (0/2) | 0% (0/2) | 0% (0/2) | 0% (0/2) | 0% (0/8) | 0% (0/4) | 0% (0/8) |
| haiku | free | 2 | 100% (16/16) | 100% (16/16) | 100% (16/16) | 0% (0/16) | 0% (0/2) | 0% (0/2) | 0% (0/2) | 0% (0/2) | 0% (0/8) | 0% (0/4) | 0% (0/8) |
| haiku | free | 3 | 100% (16/16) | 100% (16/16) | 75% (12/16) | 19% (3/16) | 0% (0/2) | 0% (0/2) | 0% (0/2) | 0% (0/2) | 0% (0/8) | 0% (0/4) | 0% (0/8) |
| opus | free | 2 | 100% (16/16) | 100% (16/16) | 100% (16/16) | 0% (0/16) | 0% (0/2) | 0% (0/2) | 0% (0/2) | 0% (0/2) | 0% (0/8) | 0% (0/4) | 0% (0/8) |
| opus | free | 3 | 100% (16/16) | 88% (14/16) | 93% (13/14) | 0% (0/14) | 0% (0/2) | 0% (0/2) | 0% (0/2) | 0% (0/2) | 12% (1/8) | 0% (0/4) | 0% (0/6) |
| haiku | free120 | 2 | 100% (16/16) | 94% (15/16) | 87% (13/15) | 13% (2/15) | 0% (0/2) | 0% (0/2) | 0% (0/2) | 0% (0/2) | 0% (0/8) | 0% (0/4) | 0% (0/8) |
| haiku | free120 | 3 | 100% (16/16) | 94% (15/16) | 33% (5/15) | 67% (10/15) | 0% (0/2) | 0% (0/2) | 0% (0/2) | 0% (0/2) | 0% (0/8) | 0% (0/4) | 0% (0/8) |
| opus | free120 | 2 | 100% (16/16) | 100% (16/16) | 94% (15/16) | 6% (1/16) | 0% (0/2) | 0% (0/2) | 0% (0/2) | 0% (0/2) | 0% (0/8) | 0% (0/4) | 0% (0/8) |
| opus | free120 | 3 | 100% (16/16) | 100% (16/16) | 94% (15/16) | 6% (1/16) | 0% (0/2) | 0% (0/2) | 0% (0/2) | 0% (0/2) | 0% (0/8) | 0% (0/4) | 0% (0/8) |
| haiku | instructed | 2 | 100% (16/16) | 100% (16/16) | 100% (16/16) | 0% (0/16) | 0% (0/2) | 0% (0/2) | 0% (0/2) | 0% (0/2) | 0% (0/8) | 0% (0/4) | 0% (0/8) |
| haiku | instructed | 3 | 100% (16/16) | 100% (16/16) | 100% (16/16) | 0% (0/16) | 0% (0/2) | 0% (0/2) | 0% (0/2) | 0% (0/2) | 0% (0/8) | 0% (0/4) | 0% (0/8) |
| opus | instructed | 2 | 100% (16/16) | 100% (16/16) | 100% (16/16) | 0% (0/16) | 0% (0/2) | 0% (0/2) | 0% (0/2) | 0% (0/2) | 0% (0/8) | 0% (0/4) | 0% (0/8) |
| opus | instructed | 3 | 100% (16/16) | 100% (16/16) | 88% (14/16) | 12% (2/16) | 0% (0/2) | 0% (0/2) | 0% (0/2) | 0% (0/2) | 0% (0/8) | 0% (0/4) | 0% (0/8) |

## 5. Cue effect on third-party facts (H1, pilot estimate only) and where it comes from

Each line is detail minus plain on third-party facts, in percentage points. Read together: a cue effect that is already there when the reader sees the planted tagged notes, or on bare claims with the tags stripped, is the reader inferring a source from detail; a cue effect in the writer's own chain-format tags, or in whether the writer kept the colleague's name or a hedge, is the writer rebuilding the tag.

- Reader on rewrites, hop 3, free + instructed (primary population): U(detail) - U(plain) = +0.0 (scenario bootstrap [+0.0, +0.0]); among retained values +0.0; per writer haiku +0.0, opus +0.0.
- Reader on rewrites, hop 2, free + instructed: U(detail) - U(plain) = +0.0 (scenario bootstrap [+0.0, +0.0]); among retained values +0.0; per writer haiku +0.0, opus +0.0.
- Reader on rewrites, hop 3, chain: U(detail) - U(plain) = +0.0 (scenario bootstrap [+0.0, +0.0]); among retained values +0.0; per writer haiku +0.0, opus +0.0.
- Reader on rewrites, hop 3, free120: U(detail) - U(plain) = +0.0 (scenario bootstrap [+0.0, +0.0]); among retained values +0.0; per writer haiku +0.0, opus +0.0.
- Reader alone, planted tagged prose: read as observed or user: +0.0 (detail 0/2, plain 0/2)
- Reader alone, tag-stripped notes, all facts: read as observed or user: +0.0 (detail 0/8, plain 0/8)
- Writer, chain JSON at hop 3: tag raised to observed or user (no reader): +0.0 (detail 0/4, plain 0/4)
- Writer, prose at hop 3: colleague's name kept on the value's line: +0.0 (detail 8/8, plain 8/8)
- Writer, prose at hop 3: hedge kept on the value's line: +25.0 (detail 4/8, plain 2/8)
- Manipulation check, hop 3 free + instructed: content kept, all sources (pre-registered: within 3 points): +0.0 (detail 31/32, plain 31/32)

## 6. Chain format, read straight from the JSON (no reader)

| writer | hop | claim found | tag correct | weak tag raised to observed/user | strong tag lowered | marked verified though not observed |
|---|---|---|---|---|---|---|
| haiku | 2 | 100.0% (16/16; 81-100) | 100.0% (16/16; 81-100) | 0.0% (0/8; 0-32) | 0.0% (0/8; 0-32) | 0.0% (0/12; 0-24) |
| haiku | 3 | 100.0% (16/16; 81-100) | 100.0% (16/16; 81-100) | 0.0% (0/8; 0-32) | 0.0% (0/8; 0-32) | 0.0% (0/12; 0-24) |
| opus | 2 | 100.0% (16/16; 81-100) | 100.0% (16/16; 81-100) | 0.0% (0/8; 0-32) | 0.0% (0/8; 0-32) | 0.0% (0/12; 0-24) |
| opus | 3 | 100.0% (16/16; 81-100) | 100.0% (16/16; 81-100) | 0.0% (0/8; 0-32) | 0.0% (0/8; 0-32) | 0.0% (0/12; 0-24) |

## 7. What attribution survives on the value's line (prose disciplines; keyword heuristic)

| writer | discipline | hop | cue | colleague's name kept (third) | hedge kept (third) | hedge kept (guess) | 'user' kept (user) |
|---|---|---|---|---|---|---|---|
| haiku | free | 2 | plain | 100.0% (2/2; 34-100) | 50.0% (1/2; 9-91) | 50.0% (1/2; 9-91) | 50.0% (1/2; 9-91) |
| haiku | free | 2 | detail | 100.0% (2/2; 34-100) | 50.0% (1/2; 9-91) | 50.0% (1/2; 9-91) | 50.0% (1/2; 9-91) |
| haiku | free | 3 | plain | 100.0% (2/2; 34-100) | 50.0% (1/2; 9-91) | 50.0% (1/2; 9-91) | 0.0% (0/2; 0-66) |
| haiku | free | 3 | detail | 100.0% (2/2; 34-100) | 50.0% (1/2; 9-91) | 50.0% (1/2; 9-91) | 50.0% (1/2; 9-91) |
| opus | free | 2 | plain | 100.0% (2/2; 34-100) | 50.0% (1/2; 9-91) | 50.0% (1/2; 9-91) | 0.0% (0/2; 0-66) |
| opus | free | 2 | detail | 100.0% (2/2; 34-100) | 50.0% (1/2; 9-91) | 50.0% (1/2; 9-91) | 0.0% (0/2; 0-66) |
| opus | free | 3 | plain | 100.0% (2/2; 34-100) | 0.0% (0/2; 0-66) | 0.0% (0/1; 0-79) | 0.0% (0/2; 0-66) |
| opus | free | 3 | detail | 100.0% (2/2; 34-100) | 50.0% (1/2; 9-91) | 0.0% (0/1; 0-79) | 0.0% (0/2; 0-66) |
| haiku | free120 | 2 | plain | 0.0% (0/2; 0-66) | 100.0% (2/2; 34-100) | 100.0% (2/2; 34-100) | 100.0% (1/1; 21-100) |
| haiku | free120 | 2 | detail | 0.0% (0/2; 0-66) | 100.0% (2/2; 34-100) | 100.0% (2/2; 34-100) | 100.0% (2/2; 34-100) |
| haiku | free120 | 3 | plain | 0.0% (0/2; 0-66) | 100.0% (2/2; 34-100) | 100.0% (2/2; 34-100) | 0.0% (0/1; 0-79) |
| haiku | free120 | 3 | detail | 0.0% (0/2; 0-66) | 100.0% (2/2; 34-100) | 100.0% (2/2; 34-100) | 50.0% (1/2; 9-91) |
| opus | free120 | 2 | plain | 100.0% (2/2; 34-100) | 0.0% (0/2; 0-66) | 0.0% (0/2; 0-66) | 50.0% (1/2; 9-91) |
| opus | free120 | 2 | detail | 100.0% (2/2; 34-100) | 0.0% (0/2; 0-66) | 0.0% (0/2; 0-66) | 50.0% (1/2; 9-91) |
| opus | free120 | 3 | plain | 100.0% (2/2; 34-100) | 0.0% (0/2; 0-66) | 50.0% (1/2; 9-91) | 50.0% (1/2; 9-91) |
| opus | free120 | 3 | detail | 100.0% (2/2; 34-100) | 0.0% (0/2; 0-66) | 50.0% (1/2; 9-91) | 50.0% (1/2; 9-91) |
| haiku | instructed | 2 | plain | 100.0% (2/2; 34-100) | 50.0% (1/2; 9-91) | 50.0% (1/2; 9-91) | 50.0% (1/2; 9-91) |
| haiku | instructed | 2 | detail | 100.0% (2/2; 34-100) | 50.0% (1/2; 9-91) | 50.0% (1/2; 9-91) | 50.0% (1/2; 9-91) |
| haiku | instructed | 3 | plain | 100.0% (2/2; 34-100) | 50.0% (1/2; 9-91) | 50.0% (1/2; 9-91) | 50.0% (1/2; 9-91) |
| haiku | instructed | 3 | detail | 100.0% (2/2; 34-100) | 50.0% (1/2; 9-91) | 50.0% (1/2; 9-91) | 50.0% (1/2; 9-91) |
| opus | instructed | 2 | plain | 100.0% (2/2; 34-100) | 0.0% (0/2; 0-66) | 50.0% (1/2; 9-91) | 50.0% (1/2; 9-91) |
| opus | instructed | 2 | detail | 100.0% (2/2; 34-100) | 50.0% (1/2; 9-91) | 50.0% (1/2; 9-91) | 50.0% (1/2; 9-91) |
| opus | instructed | 3 | plain | 100.0% (2/2; 34-100) | 0.0% (0/2; 0-66) | 50.0% (1/2; 9-91) | 50.0% (1/2; 9-91) |
| opus | instructed | 3 | detail | 100.0% (2/2; 34-100) | 50.0% (1/2; 9-91) | 50.0% (1/2; 9-91) | 50.0% (1/2; 9-91) |

## 8. Machine-like specifics the writer added that it was never shown (H6)

Counted: backticked names, paths, 'line N', file:line, and tokens mixing letters and digits that appear nowhere in the writer's input and are not a rewriting of a planted value. An upper bound: read the examples before relying on it.

| writer | discipline | hop | artifacts | with any new specific | mean new per artifact | mean words |
|---|---|---|---|---|---|---|
| haiku | chain | 2 | 2 | 0.0% (0/2; 0-66) | 0.00 | 236 |
| haiku | chain | 3 | 2 | 0.0% (0/2; 0-66) | 0.00 | 226 |
| opus | chain | 2 | 2 | 0.0% (0/2; 0-66) | 0.00 | 212 |
| opus | chain | 3 | 2 | 0.0% (0/2; 0-66) | 0.00 | 225 |
| haiku | free | 2 | 2 | 0.0% (0/2; 0-66) | 0.00 | 272 |
| haiku | free | 3 | 2 | 0.0% (0/2; 0-66) | 0.00 | 266 |
| opus | free | 2 | 2 | 100.0% (2/2; 34-100) | 1.00 | 352 |
| opus | free | 3 | 2 | 100.0% (2/2; 34-100) | 1.00 | 347 |
| haiku | free120 | 2 | 2 | 0.0% (0/2; 0-66) | 0.00 | 106 |
| haiku | free120 | 3 | 2 | 0.0% (0/2; 0-66) | 0.00 | 98 |
| opus | free120 | 2 | 2 | 0.0% (0/2; 0-66) | 0.00 | 138 |
| opus | free120 | 3 | 2 | 0.0% (0/2; 0-66) | 0.00 | 118 |
| haiku | instructed | 2 | 2 | 0.0% (0/2; 0-66) | 0.00 | 306 |
| haiku | instructed | 3 | 2 | 0.0% (0/2; 0-66) | 0.00 | 313 |
| opus | instructed | 2 | 2 | 50.0% (1/2; 9-91) | 0.50 | 308 |
| opus | instructed | 3 | 2 | 50.0% (1/2; 9-91) | 1.00 | 315 |

Plain facts whose own line or claim gained a new specific, by true source: OBS 0.0% (0/32; 0-11), USER 3.1% (1/32; 1-16), THIRD 0.0% (0/32; 0-11), GUESS 0.0% (0/32; 0-11)

Most common new specifics: `kubectl rollout history` (2), `i/o` (1), `orders-config/kafka/fulfil-svc.yaml` (1), `gh run list --workflow payments-int.yml --branch main --status failure` (1), `git blame` (1), `concurrency` (1)

## 9. Pre-registered pilot checks

- pass: Reader gate at least 97% on plain planted facts
- pass: claude-haiku-5-5 writer_chain: refusals, schema failures and truncations at most 5% (0/4)
- pass: claude-haiku-5-5 writer_prose: refusals, schema failures and truncations at most 5% (0/12)
- pass: claude-opus-5-5 writer_chain: refusals, schema failures and truncations at most 5% (0/4)
- pass: claude-opus-5-5 writer_prose: refusals, schema failures and truncations at most 5% (0/12)
- pass: claude-sonnet-5-5 reader: refusals, schema failures and truncations at most 5% (0/38)
- pass: haiku chain: hop-3 content kept at least 70% (100.0% (16/16; 81-100))
- pass: opus chain: hop-3 content kept at least 70% (100.0% (16/16; 81-100))
- pass: haiku free: hop-3 content kept at least 70% (100.0% (16/16; 81-100))
- pass: opus free: hop-3 content kept at least 70% (87.5% (14/16; 64-97))
- pass: haiku free120: hop-3 content kept at least 70% (93.8% (15/16; 72-99))
- pass: opus free120: hop-3 content kept at least 70% (100.0% (16/16; 81-100))
- pass: haiku instructed: hop-3 content kept at least 70% (100.0% (16/16; 81-100))
- pass: opus instructed: hop-3 content kept at least 70% (100.0% (16/16; 81-100))
- pass: Content kept differs by cue by at most 3 points at hop 3 (+0.0)
- Floor rule, haiku free hop 3 (third-party upgrades under 3% at both cues): reached: report upgrades as rare under these conditions
- Floor rule, opus free hop 3 (third-party upgrades under 3% at both cues): reached: report upgrades as rare under these conditions

Inputs check: the items and prompts match the ones this folder was run with.
