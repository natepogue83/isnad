# Isnad across hops: pilot findings

**Short answer:** when Claude models rewrote their own handoff notes twice, they did not turn a colleague's unverified claim, or their own guess, into something they had seen themselves. That happened 0 times in 2,688 chances. What wore away instead was the user's voice. At hop 3, Haiku 5.5 writing free-form notes had lost the "the user told me this" label on 53% of the user's statements: some were filed under headings like "Reported, not verified" with colleagues' claims, and some lost their attribution entirely. Opus 5.5 kept 99%. Asking the writer to say how each fact was obtained, or using the isnad JSON format, brought Haiku back to 99% or more.

Pilot only: 6 invented scenarios, 1,488 API calls, $6.75 for the pilot itself, and $7.42 including the checks run before it. The design and checks were fixed before any paid call ([PREREG-PILOT.md](PREREG-PILOT.md)). Full tables are in [results/pilot/RESULTS.md](results/pilot/RESULTS.md).

## What was tested

An agent's working notes on a task (an on-call incident, a revenue mismatch, a vendor choice, a flaky CI job, a double charge, a freezer failure) list 8 facts. Each fact carries a correct source:

- **observed:** seen in the agent's own tool output
- **user:** told by the user
- **third party:** a named colleague's document, not verified
- **guess:** the agent's own unchecked assumption

Half the facts also carry machine-like detail (a metric name, a file path, a job id). A Latin square moves every fact through every source and detail level, so the wording is held constant across conditions.

Claude Haiku 5.5 and Claude Opus 5.5 each rewrote the notes as a handoff for another agent (hop 2), then rewrote their own handoff again (hop 3). Claude Sonnet 5.5, which never wrote, read every version and said for each fact what the value is and where the notes say it came from. Writers used three formats:

- **free:** at most 300 words
- **instructed:** free, plus "say how each fact was obtained and whether it has been verified"
- **chain:** the isnad JSON, with a mandatory source field per claim

Haiku also ran a 120-word version of free, to add pressure.

## Results

**1. No upgrades to "I saw it".**
- Across all 672 rewrites, no third-party claim or guess was read as the agent's own observation (0 of 2,688).
- Three were read as coming from the user. One of the three was the reader's mistake: the line kept the colleague's name. The other two were Haiku filing a colleague's claim under a "from the user" heading.
- The reader never said it would act on a third-party claim or guess without checking.
- The pre-registered floor rule was reached: upgrades are rare under these conditions.

**2. Machine-like detail did not cause upgrades.**
- The pre-registered estimate is −1.0 percentage points (detail minus plain, third-party facts at hop 3). That is no effect.

**3. The user's voice is what gets lost, and the loss compounds.**

Each cell shows how many of 96 user statements were still read as "the user told me", at hop 2 / hop 3.

| writer | free | free, 120 words | instructed | chain |
|---|---|---|---|---|
| Haiku 5.5 | 62 / 45 | 52 / 40 | 95 / 95 | 96 / 96 |
| Opus 5.5 | 95 / 95 | not run | 96 / 96 | 96 / 96 |

- In free notes, Haiku sorts facts under headings such as "Observed directly" and "Reported, not verified" (or "Reported, not checked") (47 of 48 hop-3 notes had an unverified-style heading; only 20 had a heading naming the user), and often puts the user's statements in the unverified group with colleagues' claims.
- It also drops "user" from lines it compresses. At 120 words this got worse at each hop.
- Facts from other sources held up better in the same notes: at hop 3, 91 of 96 observed facts and 92 of 96 third-party claims were still read correctly.
- This error is cautious, not risky: it makes facts look weaker than they are. The cost is that the next agent can no longer tell what the user asked for from what a colleague said.

**4. The reader, not the writer, is where detail matters.**
- With every tag stripped from the planted notes, the reader called 6.2% of detailed bare claims "observed by the agent" (12 of 192), and none of the plain ones (0 of 192).
- An exploratory finding that was not pre-registered points the same way. In 6 of 672 detailed user statements, Haiku presented the statement without the user's name, or under a "Verified" heading, and the reader took it as the agent's own observation. That never happened to the 672 plain ones. All 6 were Haiku (5 of them at 120 words), and they come from about 4 note chains, so this is a lead, not a result.

**5. No sign of invented log detail.**
- The automatic counter flagged new identifiers in 134 of 672 rewrites. I read a random 30 of the 164 flagged items, and none was a new observation stated as fact:
  - 12 were names already in the notes joined into one dotted path (for example `analytics.fct_revenue_monthly.net_amount_usd`)
  - 9 were unit shorthand or arithmetic (`messages/month`, `$5.3k/year`)
  - 8 were word pairs (`api/cli`)
  - 1 was a command suggested as a next step (`git blame`)

## What this means in practice

For agents built on these models, the risk P15 worried about, an agent laundering a rumor into a first-hand claim by retelling it, did not appear in clean conditions.

The real risk is smaller models flattening provenance under length pressure. The fix is cheap: a one-sentence instruction ("say how each fact was obtained") or a source field in a structured handoff. With either one, both models kept 99% or more of the source labels on the facts they carried through two rewrites.

If tags are lost anyway, machine-like detail nudges a reader toward assuming the agent saw the fact itself. That makes keeping provenance in the handoff format worth more than relying on the reader to infer it.

## Limits

- Six scenarios, all invented by a Claude agent. Every interval in RESULTS.md is descriptive, not confirmatory.
- The notes started clean and correctly tagged. Real agents write their first notes from messy transcripts (Arm B in the full design), and that is where mislabelling is more likely to start.
- Only two hops, one model family, and default effort settings.
- The reader is one model (Sonnet 5.5). Its labels were checked only on the planted notes, where it was 100% correct.
- The "attribution kept" and "new identifier" measures are keyword heuristics, and are reported as such.

## What a full study would add

- Arm B: notes written from raw tool transcripts.
- More hops (5 or more).
- A writer from another vendor.
- A reader that has to act on the handoff, not just label it.
- New scenarios written to the same spec.

The pilot's cost data puts a 3x larger run at about $20 at batch prices.

## Provenance

The code, prompts and scenarios were written by Claude (Anthropic's model) under Nate's direction. Two independent review agents checked them, and 110 offline checks with fake models of known behaviour passed before the main run. A closed-book check and a smoke test ($0.67 together) ran before that, and PREREG-PILOT.md lists what changed after them. Nate picked the experiment, required it to be checked before spending, and set the budget.

Every raw response is in `results/pilot/calls.jsonl`. Rerun the analysis with `python analyze.py results/pilot`.
