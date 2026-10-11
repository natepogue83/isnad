# Isnad: do AI models stay honest about where their information came from?

Two small experiments on source honesty in language models, with all code, test items, prompts, raw model responses and analysis scripts.

The name comes from the *isnad*, the chain of narrators that hadith scholars attached to every report so it could be judged by its weakest link. Both studies test a version of that idea: make the model label where each piece of its answer came from, then check the label against a source that was planted, so the right answer is known.

| Folder | Question | Start with |
|---|---|---|
| [`isnad-experiment/`](isnad-experiment/) | When a model answers a question about a document from its own memory, does it still cite the document? | [FINDINGS.md](isnad-experiment/FINDINGS.md) |
| [`isnad-hops/`](isnad-hops/) | When an agent rewrites its own handoff notes, does each fact keep its source, or does an unverified claim turn into "I saw this myself"? | [FINDINGS.md](isnad-hops/FINDINGS.md) |

## Results in brief

**Citations (5 models, 5,880 scored responses, plus a 1,080-call follow-up).** Given a plain citation field, every model sometimes answered from memory while citing a real quote from the document: from 9% (GPT-5.5) to 33% (Claude Opus 5.5) of the questions the document never answers. A prompt that has the model label each piece of its answer as document, memory or inference, and says plainly that recalled facts are memory, cut this to zero for four of the five models and from 26% to 7% for gpt-5.4-mini. A pre-registered follow-up found that the instruction alone did the work for Claude Sonnet 5.5, while for gpt-5.4-mini the instruction did little and the labeled chain made the clearest difference.

**Handoff notes (pre-registered pilot, 1,488 calls).** Across two rewrites, Claude Haiku 5.5 and Claude Opus 5.5 never turned a colleague's claim or their own guess into something they had observed (0 of 2,688 chances). What wore away was the user's voice: Haiku's free-form notes lost "the user told me this" on 53% of user statements by the second rewrite, against 1% for Opus. Asking for sources, or using the labeled format, fixed it.

Each FINDINGS.md lists its limits and how to regenerate its numbers from the saved responses.

## How this was made

I chose the questions and set the budgets. The designs were worked out with AI agents, the code was written by Claude (Anthropic's model) under my direction, and every result was checked against the saved data by tests and separate review agents before it was written up. The citation study was revised after an outside review found real grader problems; the changes are listed in its FINDINGS.md.

## Running it

Each folder has its own README with setup and commands. The offline checks need no API key:

```
cd isnad-experiment && python tests/test_grade.py    # grader regression probes
cd isnad-hops && python tests/test_all.py            # item, grading and resume checks with fake models
```

Paid runs need your own Anthropic (and, for the GPT models, OpenAI) API key. No keys are stored in this repository.

## License

MIT, for the code and the data. See [LICENSE](LICENSE).

Nathan Pogue · [natepogue83.github.io](https://natepogue83.github.io)
