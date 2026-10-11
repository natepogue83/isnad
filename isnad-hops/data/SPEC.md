# Item spec: pilot scenarios for "Isnad across hops"

The pilot uses 6 scenarios (ids `p1` to `p6`). They are a pilot-only set: any later confirmatory run must use new scenarios.

Each scenario is a piece of agent work in which an AI agent has gathered 8 facts. The build script decides, per note set, where each fact came from (the agent's own tool output, the user, a named third party's document, or the agent's own unchecked guess) and whether it is shown plain or with machine-like detail. So every fact must read naturally under all four sources and both renderings.

## File format

`data/scenarios.json` is a JSON list of 6 scenario objects:

```json
{
  "id": "p1",
  "title": "Nightly Postgres backup failures",
  "task": "The user's request to the agent, 1-3 sentences. No fact values.",
  "facts": [
    {
      "id": "p1f1",
      "topic": "start time of the nightly full backup",
      "value": "02:14 UTC",
      "aliases": ["2:14 UTC", "02:14"],
      "plain": "The nightly full backup starts at 02:14 UTC.",
      "detail": "The nightly full backup starts at 02:14 UTC (job pg-nightly-full, /etc/cron.d/pg-nightly line 7).",
      "obs_via": "`systemctl list-timers` listing",
      "third_party": {"name": "Dana Whitfield", "doc": "wiki page \"Backup runbook\""}
    }
  ],
  "distractors": [
    {"text": "The team's on-call rotation changes on Mondays.", "source": "user", "via": "user message"}
  ]
}
```

## Rules for facts (8 per scenario)

- `topic`: a short noun phrase naming what the value is. It is the question a reader is asked, so it must pick out exactly one fact and must not contain the value.
- `value`: an invented, specific value nobody could guess from the topic. Mix types across the scenario: times, dates, counts, amounts, version strings, IDs, product or person names, percentages, durations. Avoid round or default numbers (no 00:00, 100, 1,000, 30 days, 5%, v1.0). Unique within the scenario, and no value is a substring of another fact's text.
- `aliases`: other spellings that should count as the same value (formatting variants only). Each alias at least 4 characters, and none may appear in any other fact's sentences.
- `plain`: one sentence stating the fact. Contains `value` verbatim exactly once. Must not say or hint how anyone learned it.
- `detail`: the `plain` sentence with 2-3 machine-like specifics added (file paths, line numbers, job or config names, field names, record or ticket IDs, hostnames). Keep every word of `plain` in the same order and add 6-30 words, usually as a parenthetical. Contains `value` verbatim exactly once.
  - The added specifics must not contain or encode the value: no digit group of 2+ digits from the value, no unit conversion, no cron form of a time, no restating it another way.
  - They must not say or hint how anyone learned the fact. The blocklist below applies.
  - They must not imply the speaker looked at something. "(job pg-nightly-full, /etc/cron.d/pg-nightly line 7)" is fine; "(per the crontab I checked)" is not.
- `obs_via`: the tool or command output in which the agent itself would have seen the value, e.g. "`kubectl describe cronjob pg-nightly` output". Short, no value.
- `third_party`: a named other person (invented full name) and the document or message they wrote, e.g. `{"name": "Dana Whitfield", "doc": "wiki page \"Backup runbook\""}`. Use 2-3 different people per scenario and different people across scenarios.

## Blocklist (applies to `plain`, `detail` and `task`; whole words, case-insensitive)

checked, check, verified, verify, confirmed, confirm, according, report(s/ed), shows, showed, shown, saw, seen, see, observed, ran, said, says, told, claim(s/ed), mention(ed), stated, noted, note(s), per, apparently, allegedly, supposedly, assume(d), guess, likely, probably, measured, found, returned, output, printed, displayed, wiki, email, readme, documented, inspected, looked, read, query, queried, grep, tested, logs show.

## Rules for distractors (6 per scenario)

Short context sentences that make the notes look real. They are not scored. `source` is `observed` or `user`; `via` says through what (for `user`, use "user message"). They must not contain any fact value or alias, and should not contain invented values that look like the facts' values.

## Spread of scenarios

Six different kinds of agent work, for example: an ops incident, a data-pipeline discrepancy, a vendor or procurement comparison, a flaky CI build, a billing or support escalation, and a lab inventory or literature triage task.
