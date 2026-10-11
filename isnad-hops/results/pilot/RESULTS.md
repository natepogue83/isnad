# Results: pilot

Rates are shown as percent (k/n; Wilson 95% interval). Intervals marked 'scenario bootstrap' resample the 6 scenarios and are descriptive only.

## 1. Run health

| model | call type | calls | ok | refusal | truncated | invalid | errored | mean in | mean out |
|---|---|---|---|---|---|---|---|---|---|
| claude-haiku-5-5 | writer_chain | 96 | 96 | 0 | 0 | 0 | 0 | 1919 | 2021 |
| claude-haiku-5-5 | writer_prose | 288 | 288 | 0 | 0 | 0 | 0 | 855 | 1302 |
| claude-opus-5-5 | writer_chain | 96 | 96 | 0 | 0 | 0 | 0 | 1909 | 1115 |
| claude-opus-5-5 | writer_prose | 192 | 192 | 0 | 0 | 0 | 0 | 975 | 1009 |
| claude-sonnet-5-5 | reader | 816 | 816 | 0 | 0 | 0 | 0 | 1781 | 339 |

Total spend in this folder: $6.75 (every call ever made, including retries).

## 2. Reader check on the planted notes (hop 1, reader alone)

- Tagged prose: source read correctly on plain facts 100.0% (192/192; 98-100); all facts 100.0% (384/384; 99-100); value returned 100.0% (384/384; 99-100).
- Tagged chain: source read correctly on plain facts 100.0% (192/192; 98-100); all facts 100.0% (384/384; 99-100); value returned 100.0% (384/384; 99-100).

Gate (pre-registered: at least 97% on plain planted facts, prose and chain pooled): PASS (100.0% (384/384; 99-100)).

## 3. Reader on tag-stripped planted notes (what a bare claim is read as)

| cue | n | observed | user | third party | guess | not stated |
|---|---|---|---|---|---|---|
| plain | 192 | 0.0% | 0.0% | 0.0% | 0.0% | 100.0% |
| detail | 192 | 6.2% | 0.0% | 2.1% | 0.0% | 91.7% |

Detail minus plain, share read as observed: +6.2 points.

## 4. Source fidelity across rewrites (fixed reader, Sonnet 5.5)

Content kept is a string match on the artifact; a failed writer call counts as not kept. U (upgrade) = third-party or guess facts read as observed or user-stated, out of all such facts the reader scored or whose writer failed (a lost value counts as no upgrade). D = observed or user facts read as third-party or guess. Source correct and loss (source read as not stated) are among facts whose value the reader returned. 'scored' = reader answers available / chain cells started.

| writer | discipline | hop | scored | content kept | source correct | loss | U third plain | U third detail | U guess plain | U guess detail | D | third read as observed | weak facts relied on unchecked |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| (planted) | chain JSON | planted | 100% (384/384) | 100% (384/384) | 100% (384/384) | 0% (0/384) | 0% (0/48) | 0% (0/48) | 0% (0/48) | 0% (0/48) | 0% (0/192) | 0% (0/96) | 0% (0/192) |
| haiku | chain | 2 | 100% (384/384) | 100% (384/384) | 100% (384/384) | 0% (0/384) | 0% (0/48) | 0% (0/48) | 0% (0/48) | 0% (0/48) | 0% (0/192) | 0% (0/96) | 0% (0/192) |
| haiku | chain | 3 | 100% (384/384) | 100% (384/384) | 100% (382/383) | 0% (1/383) | 0% (0/48) | 0% (0/48) | 0% (0/48) | 0% (0/48) | 0% (0/192) | 0% (0/96) | 0% (0/192) |
| opus | chain | 2 | 100% (384/384) | 100% (384/384) | 100% (384/384) | 0% (0/384) | 0% (0/48) | 0% (0/48) | 0% (0/48) | 0% (0/48) | 0% (0/192) | 0% (0/96) | 0% (0/192) |
| opus | chain | 3 | 100% (384/384) | 100% (384/384) | 100% (384/384) | 0% (0/384) | 0% (0/48) | 0% (0/48) | 0% (0/48) | 0% (0/48) | 0% (0/192) | 0% (0/96) | 0% (0/192) |
| (planted) | tagged prose | planted | 100% (384/384) | 100% (384/384) | 100% (384/384) | 0% (0/384) | 0% (0/48) | 0% (0/48) | 0% (0/48) | 0% (0/48) | 0% (0/192) | 0% (0/96) | 0% (0/192) |
| haiku | free | 2 | 100% (384/384) | 100% (383/384) | 89% (341/382) | 5% (21/382) | 0% (0/48) | 0% (0/48) | 0% (0/48) | 0% (0/48) | 8% (16/192) | 0% (0/96) | 0% (0/192) |
| haiku | free | 3 | 100% (384/384) | 99% (382/384) | 82% (311/380) | 13% (48/380) | 2% (1/48) | 0% (0/48) | 0% (0/48) | 0% (0/48) | 9% (17/192) | 0% (0/96) | 0% (0/190) |
| opus | free | 2 | 100% (384/384) | 100% (384/384) | 100% (382/383) | 0% (1/383) | 0% (0/48) | 0% (0/48) | 0% (0/48) | 0% (0/48) | 0% (0/192) | 0% (0/96) | 0% (0/191) |
| opus | free | 3 | 100% (384/384) | 100% (384/384) | 99% (381/384) | 1% (3/384) | 0% (0/48) | 0% (0/48) | 0% (0/48) | 0% (0/48) | 0% (0/192) | 0% (0/96) | 0% (0/192) |
| haiku | free120 | 2 | 100% (384/384) | 99% (379/384) | 82% (308/377) | 12% (45/377) | 0% (0/48) | 0% (0/48) | 0% (0/48) | 0% (0/48) | 9% (18/192) | 0% (0/95) | 0% (0/189) |
| haiku | free120 | 3 | 100% (384/384) | 99% (379/384) | 74% (278/377) | 19% (72/377) | 2% (1/48) | 0% (0/48) | 0% (0/48) | 0% (0/48) | 9% (17/192) | 0% (0/96) | 0% (0/189) |
| haiku | instructed | 2 | 100% (384/384) | 100% (384/384) | 99% (382/384) | 0% (1/384) | 0% (0/48) | 0% (0/48) | 0% (0/48) | 0% (0/48) | 1% (1/192) | 0% (0/96) | 0% (0/192) |
| haiku | instructed | 3 | 100% (384/384) | 100% (384/384) | 99% (378/381) | 1% (2/381) | 2% (1/48) | 0% (0/48) | 0% (0/48) | 0% (0/48) | 0% (0/192) | 0% (0/96) | 0% (0/192) |
| opus | instructed | 2 | 100% (384/384) | 100% (384/384) | 100% (384/384) | 0% (0/384) | 0% (0/48) | 0% (0/48) | 0% (0/48) | 0% (0/48) | 0% (0/192) | 0% (0/96) | 0% (0/192) |
| opus | instructed | 3 | 100% (384/384) | 99% (380/384) | 100% (379/379) | 0% (0/379) | 0% (0/48) | 0% (0/48) | 0% (0/48) | 0% (0/48) | 0% (0/192) | 0% (0/96) | 0% (0/187) |

## 5. Cue effect on third-party facts (H1, pilot estimate only) and where it comes from

Each line is detail minus plain on third-party facts, in percentage points. Read together: a cue effect that is already there when the reader sees the planted tagged notes, or on bare claims with the tags stripped, is the reader inferring a source from detail; a cue effect in the writer's own chain-format tags, or in whether the writer kept the colleague's name or a hedge, is the writer rebuilding the tag.

- Reader on rewrites, hop 3, free + instructed (primary population): U(detail) - U(plain) = -1.0 (scenario bootstrap [-2.1, +0.0]); among retained values -1.0; per writer haiku -2.1, opus +0.0.
- Reader on rewrites, hop 2, free + instructed: U(detail) - U(plain) = +0.0 (scenario bootstrap [+0.0, +0.0]); among retained values +0.0; per writer haiku +0.0, opus +0.0.
- Reader on rewrites, hop 3, chain: U(detail) - U(plain) = +0.0 (scenario bootstrap [+0.0, +0.0]); among retained values +0.0; per writer haiku +0.0, opus +0.0.
- Reader on rewrites, hop 3, free120: U(detail) - U(plain) = -2.1 (scenario bootstrap [-6.2, +0.0]); among retained values -2.1; per writer haiku -2.1.
- Reader alone, planted tagged prose: read as observed or user: +0.0 (detail 0/48, plain 0/48)
- Reader alone, tag-stripped notes, all facts: read as observed or user: +6.2 (detail 12/192, plain 0/192)
- Writer, chain JSON at hop 3: tag raised to observed or user (no reader): +0.0 (detail 0/96, plain 0/96)
- Writer, prose at hop 3: colleague's name kept on the value's line: -4.2 (detail 142/192, plain 150/192)
- Writer, prose at hop 3: hedge kept on the value's line: +0.0 (detail 70/192, plain 70/192)
- Manipulation check, hop 3 free + instructed: content kept, all sources (pre-registered: within 3 points): +0.0 (detail 765/768, plain 765/768)

## 6. Chain format, read straight from the JSON (no reader)

| writer | hop | claim found | tag correct | weak tag raised to observed/user | strong tag lowered | marked verified though not observed |
|---|---|---|---|---|---|---|
| haiku | 2 | 100.0% (384/384; 99-100) | 100.0% (384/384; 99-100) | 0.0% (0/192; 0-2) | 0.0% (0/192; 0-2) | 0.0% (0/288; 0-1) |
| haiku | 3 | 100.0% (384/384; 99-100) | 99.7% (383/384; 99-100) | 0.0% (0/192; 0-2) | 0.5% (1/192; 0-3) | 0.0% (0/288; 0-1) |
| opus | 2 | 100.0% (384/384; 99-100) | 100.0% (384/384; 99-100) | 0.0% (0/192; 0-2) | 0.0% (0/192; 0-2) | 0.0% (0/288; 0-1) |
| opus | 3 | 100.0% (384/384; 99-100) | 100.0% (384/384; 99-100) | 0.0% (0/192; 0-2) | 0.0% (0/192; 0-2) | 0.0% (0/288; 0-1) |

## 7. What attribution survives on the value's line (prose disciplines; keyword heuristic)

| writer | discipline | hop | cue | colleague's name kept (third) | hedge kept (third) | hedge kept (guess) | 'user' kept (user) |
|---|---|---|---|---|---|---|---|
| haiku | free | 2 | plain | 83.3% (40/48; 70-91) | 43.8% (21/48; 31-58) | 56.2% (27/48; 42-69) | 25.0% (12/48; 15-39) |
| haiku | free | 2 | detail | 83.3% (40/48; 70-91) | 43.8% (21/48; 31-58) | 47.9% (23/48; 34-62) | 29.8% (14/47; 19-44) |
| haiku | free | 3 | plain | 83.3% (40/48; 70-91) | 29.2% (14/48; 18-43) | 55.3% (26/47; 41-69) | 27.1% (13/48; 17-41) |
| haiku | free | 3 | detail | 79.2% (38/48; 66-88) | 31.2% (15/48; 20-45) | 41.7% (20/48; 29-56) | 31.9% (15/47; 20-46) |
| opus | free | 2 | plain | 77.1% (37/48; 63-87) | 41.7% (20/48; 29-56) | 25.0% (12/48; 15-39) | 14.6% (7/48; 7-27) |
| opus | free | 2 | detail | 77.1% (37/48; 63-87) | 33.3% (16/48; 22-47) | 25.0% (12/48; 15-39) | 8.3% (4/48; 3-20) |
| opus | free | 3 | plain | 77.1% (37/48; 63-87) | 31.2% (15/48; 20-45) | 27.1% (13/48; 17-41) | 12.5% (6/48; 6-25) |
| opus | free | 3 | detail | 77.1% (37/48; 63-87) | 31.2% (15/48; 20-45) | 27.1% (13/48; 17-41) | 6.2% (3/48; 2-17) |
| haiku | free120 | 2 | plain | 83.3% (40/48; 70-91) | 77.1% (37/48; 63-87) | 87.2% (41/47; 75-94) | 59.6% (28/47; 45-72) |
| haiku | free120 | 2 | detail | 81.2% (39/48; 68-90) | 77.1% (37/48; 63-87) | 89.4% (42/47; 77-95) | 56.5% (26/46; 42-70) |
| haiku | free120 | 3 | plain | 77.1% (37/48; 63-87) | 72.9% (35/48; 59-83) | 83.0% (39/47; 70-91) | 51.1% (24/47; 37-65) |
| haiku | free120 | 3 | detail | 77.1% (37/48; 63-87) | 72.9% (35/48; 59-83) | 87.2% (41/47; 75-94) | 41.3% (19/46; 28-56) |
| haiku | instructed | 2 | plain | 72.9% (35/48; 59-83) | 64.6% (31/48; 50-77) | 50.0% (24/48; 36-64) | 43.8% (21/48; 31-58) |
| haiku | instructed | 2 | detail | 66.7% (32/48; 53-78) | 58.3% (28/48; 44-71) | 54.2% (26/48; 40-67) | 39.6% (19/48; 27-54) |
| haiku | instructed | 3 | plain | 79.2% (38/48; 66-88) | 60.4% (29/48; 46-73) | 54.2% (26/48; 40-67) | 54.2% (26/48; 40-67) |
| haiku | instructed | 3 | detail | 70.8% (34/48; 57-82) | 60.4% (29/48; 46-73) | 54.2% (26/48; 40-67) | 56.2% (27/48; 42-69) |
| opus | instructed | 2 | plain | 77.1% (37/48; 63-87) | 27.1% (13/48; 17-41) | 25.0% (12/48; 15-39) | 6.2% (3/48; 2-17) |
| opus | instructed | 2 | detail | 70.8% (34/48; 57-82) | 31.2% (15/48; 20-45) | 22.9% (11/48; 13-37) | 6.2% (3/48; 2-17) |
| opus | instructed | 3 | plain | 72.9% (35/48; 59-83) | 25.0% (12/48; 15-39) | 23.9% (11/46; 14-38) | 4.2% (2/48; 1-14) |
| opus | instructed | 3 | detail | 68.8% (33/48; 55-80) | 22.9% (11/48; 13-37) | 15.2% (7/46; 8-28) | 0.0% (0/48; 0-7) |

## 8. Machine-like specifics the writer added that it was never shown (H6)

Counted: backticked names, paths, 'line N', file:line, and tokens mixing letters and digits that appear nowhere in the writer's input and are not a rewriting of a planted value. An upper bound: read the examples before relying on it.

| writer | discipline | hop | artifacts | with any new specific | mean new per artifact | mean words |
|---|---|---|---|---|---|---|
| haiku | chain | 2 | 48 | 12.5% (6/48; 6-25) | 0.15 | 225 |
| haiku | chain | 3 | 48 | 2.1% (1/48; 0-11) | 0.02 | 217 |
| opus | chain | 2 | 48 | 18.8% (9/48; 10-32) | 0.19 | 233 |
| opus | chain | 3 | 48 | 2.1% (1/48; 0-11) | 0.02 | 231 |
| haiku | free | 2 | 48 | 37.5% (18/48; 25-52) | 0.40 | 283 |
| haiku | free | 3 | 48 | 12.5% (6/48; 6-25) | 0.12 | 264 |
| opus | free | 2 | 48 | 43.8% (21/48; 31-58) | 0.54 | 339 |
| opus | free | 3 | 48 | 20.8% (10/48; 12-34) | 0.25 | 334 |
| haiku | free120 | 2 | 48 | 25.0% (12/48; 15-39) | 0.29 | 118 |
| haiku | free120 | 3 | 48 | 6.2% (3/48; 2-17) | 0.06 | 111 |
| haiku | instructed | 2 | 48 | 41.7% (20/48; 29-56) | 0.56 | 293 |
| haiku | instructed | 3 | 48 | 4.2% (2/48; 1-14) | 0.04 | 302 |
| opus | instructed | 2 | 48 | 35.4% (17/48; 23-50) | 0.50 | 338 |
| opus | instructed | 3 | 48 | 16.7% (8/48; 9-30) | 0.27 | 335 |

Plain facts whose own line or claim gained a new specific, by true source: OBS 2.1% (14/672; 1-3), USER 2.1% (14/672; 1-3), THIRD 2.5% (17/672; 2-4), GUESS 1.2% (8/672; 1-2)

Most common new specifics: `messages/month` (25), `analytics.fct_revenue_monthly.net_amount_usd` (10), `msgs/month` (9), `raw.payments.batch_ref` (8), `git log` (6), `stg_orders.currency_code` (6), `reminders/month` (6), `fct_revenue_monthly.net_amount_usd` (4), `api/cli` (3), `dbt ls --output json` (3), `analytics.fct_revenue_monthly` (3), `billing.accounts.account_ref` (3), `i/o` (2), `~once/day` (2), `ch_dup_a/ch_dup_b` (2)

## 9. Pre-registered pilot checks

- pass: Reader gate at least 97% on plain planted facts
- pass: claude-haiku-5-5 writer_chain: refusals, schema failures and truncations at most 5% (0/96)
- pass: claude-haiku-5-5 writer_prose: refusals, schema failures and truncations at most 5% (0/288)
- pass: claude-opus-5-5 writer_chain: refusals, schema failures and truncations at most 5% (0/96)
- pass: claude-opus-5-5 writer_prose: refusals, schema failures and truncations at most 5% (0/192)
- pass: claude-sonnet-5-5 reader: refusals, schema failures and truncations at most 5% (0/816)
- pass: haiku chain: hop-3 content kept at least 70% (100.0% (384/384; 99-100))
- pass: opus chain: hop-3 content kept at least 70% (100.0% (384/384; 99-100))
- pass: haiku free: hop-3 content kept at least 70% (99.5% (382/384; 98-100))
- pass: opus free: hop-3 content kept at least 70% (100.0% (384/384; 99-100))
- pass: haiku free120: hop-3 content kept at least 70% (98.7% (379/384; 97-99))
- pass: haiku instructed: hop-3 content kept at least 70% (100.0% (384/384; 99-100))
- pass: opus instructed: hop-3 content kept at least 70% (99.0% (380/384; 97-100))
- pass: Content kept differs by cue by at most 3 points at hop 3 (+0.0)
- Floor rule, haiku free hop 3 (third-party upgrades under 3% at both cues): reached: report upgrades as rare under these conditions
- Floor rule, opus free hop 3 (third-party upgrades under 3% at both cues): reached: report upgrades as rare under these conditions

Inputs check: the items and prompts match the ones this folder was run with.
