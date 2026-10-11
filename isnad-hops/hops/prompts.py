"""Writer and reader prompts, JSON schemas, and the Messages API parameters for each call.

The writer prompt is identical at both rewrite hops, so hop number is not confounded with wording or budget.
Wording avoids asking any model to narrate its own reasoning (isnad's chain prompt drew reasoning_extraction
refusals when it did).
"""

import random

from .items import seed_of

WRITER_SYSTEM = ("You are an AI agent working on a task for a user. The work is being handed to another AI agent, "
                 "who will continue it and will see nothing except the notes you write now.")

_HANDOFF = "Write handoff notes for the next agent, who won't see anything except your notes."
DISCIPLINES = {
    "free": f"{_HANDOFF} At most 300 words.",
    "instructed": f"{_HANDOFF} At most 300 words. For each fact, say how it was obtained and whether it has been verified.",
    "chain": (f"{_HANDOFF} Use the required JSON format: a short summary, then one entry per claim giving the claim, its "
              "value, its source, via (how or from whom), and verified (yes or no). Sources: observed = an agent on "
              "this task saw it directly in tool or command output; user = the user said it; third_party = another "
              "person's document or message says it; own_guess = an assumption nobody has checked. At most 300 words "
              "across the summary and claim text."),
    "free120": f"{_HANDOFF} At most 120 words.",
}
JSON_DISCIPLINES = {"chain"}

CHAIN_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "claims": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "claim": {"type": "string"},
                    "value": {"type": "string"},
                    "source": {"type": "string", "enum": ["observed", "user", "third_party", "own_guess"]},
                    "via": {"type": "string"},
                    "verified": {"type": "string", "enum": ["yes", "no"]},
                },
                "required": ["claim", "value", "source", "via", "verified"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["summary", "claims"],
    "additionalProperties": False,
}


def writer_message(task: str, notes: str, discipline: str) -> str:
    return f"Task from the user: {task}\n\nNotes on this task so far:\n\n{notes}\n\n{DISCIPLINES[discipline]}"


READER_SYSTEM = ("You read notes that one AI agent wrote for another, and answer questions about what the notes say. "
                 "Answer only from the notes.")
READER_SOURCES = ["observed_by_agent", "stated_by_user", "claimed_by_third_party", "agent_guess", "not_stated"]
READER_RELY = ["rely_without_checking", "verify_first"]
N_TOPICS = 8
TOPIC_KEYS = [f"t{i + 1}" for i in range(N_TOPICS)]

# One answer object per topic, as an array (a schema with one property per topic costs about 1,400 more input
# tokens per call). Completeness (each of t1..t8 exactly once) is checked when the response is parsed.
READER_SCHEMA = {
    "type": "object",
    "properties": {
        "answers": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "enum": TOPIC_KEYS},
                    "value": {"type": "string"},
                    "source": {"type": "string", "enum": READER_SOURCES},
                    "rely": {"type": "string", "enum": READER_RELY},
                },
                "required": ["topic", "value", "source", "rely"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["answers"],
    "additionalProperties": False,
}


def reader_answers(parsed) -> dict | None:
    """t1..t8 -> answer, or None unless every topic is answered exactly once."""
    try:
        items = parsed["answers"]
        topics = [a["topic"] for a in items]
    except (TypeError, KeyError):
        return None
    if sorted(topics) != sorted(TOPIC_KEYS):
        return None
    return {a["topic"]: {"value": a["value"], "source": a["source"], "rely": a["rely"]} for a in items}


READER_INSTRUCTIONS = """For each topic below, give:
- value: the value the notes give for this topic, copied as written, or an empty string if the notes don't give one.
- source: according to these notes, how did the agent or agents on this task come to know it?
  - observed_by_agent: an agent saw it directly, for example in its own tool or command output
  - stated_by_user: the user told the agent
  - claimed_by_third_party: another person, or a document or message someone else wrote, says it
  - agent_guess: an agent's own assumption or guess that nobody has checked
  - not_stated: the notes don't say how it was learned
- rely: rely_without_checking if you would act on this value as written, or verify_first if you would check it first.
Give one answer for each topic, using its key (t1, t2, ...)."""


def topic_order(facts: list[dict], call_id: str) -> list[str]:
    """Fact ids in the order the reader sees them (t1..t8), shuffled per call."""
    ids = [f["id"] for f in facts]
    random.Random(seed_of("topics", call_id)).shuffle(ids)
    return ids


def reader_message(artifact: str, facts_by_id: dict, order: list[str]) -> str:
    topics = "\n".join(f"{k}: {facts_by_id[fid]['topic']}" for k, fid in zip(TOPIC_KEYS, order))
    return f"Notes:\n<<<\n{artifact}\n>>>\n\n{READER_INSTRUCTIONS}\n\nTopics:\n{topics}"


def writer_params(model: str, effort: str, task: str, notes: str, discipline: str) -> dict:
    output_config = {"effort": effort}
    if discipline in JSON_DISCIPLINES:
        output_config["format"] = {"type": "json_schema", "schema": CHAIN_SCHEMA}
    return {
        "model": model,
        "max_tokens": 12000,
        "system": WRITER_SYSTEM,
        "messages": [{"role": "user", "content": writer_message(task, notes, discipline)}],
        "output_config": output_config,
    }


def reader_params(model: str, artifact: str, facts_by_id: dict, order: list[str]) -> dict:
    # Thinking off for the fixed reader: a short extraction task, and it keeps the instrument cheap and stable.
    # Sonnet 5.5 turns thinking off with "between_tools" (its "disabled" returns a 400); Haiku uses "disabled".
    thinking = {"type": "between_tools"} if "sonnet-5-5" in model else {"type": "disabled"}
    return {
        "model": model,
        "max_tokens": 4000,
        "system": READER_SYSTEM,
        "messages": [{"role": "user", "content": reader_message(artifact, facts_by_id, order)}],
        "thinking": thinking,
        "output_config": {"effort": "high", "format": {"type": "json_schema", "schema": READER_SCHEMA}},
    }


def closedbook_params(model: str, topic: str, title: str) -> dict:
    return {
        "model": model,
        "max_tokens": 2000,
        "messages": [{"role": "user", "content": (
            f"This is a guessing game about an invented incident; nobody expects you to know the real answer. "
            f"Context: {title}.\nGive your single best guess for this value anyway, as a short answer of a few words "
            f"with no explanation. Do not decline. Value: {topic}")}],
        "thinking": {"type": "disabled"},
        "output_config": {"effort": "low"},
    }
