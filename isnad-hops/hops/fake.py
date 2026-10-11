"""An offline stand-in for the Anthropic client, so the whole pipeline (jobs, both call modes, storage, grading,
analysis) can be tested with no API calls and known right answers.

Fake writers:
  identity  returns the notes it was given (expect: every source read correctly, no upgrades, full retention)
  stripper  deletes every prose source tag (expect: prose sources all read as not_stated; chain untouched)
  upgrader  turns a third-party tag into an "I saw this myself" tag with probability p_detail on detail facts and
            p_plain on plain facts, independently at each rewrite (expect at hop 3: 1-(1-p)^2)
The fake reader parses the planted tag wording (prose) or the source field (chain) on the value's line.
"""

import hashlib
import json
import re
import threading
import time
from pathlib import Path
from types import SimpleNamespace

from .grade import contains_value
from .items import load_scenarios
from .prompts import DISCIPLINES, TOPIC_KEYS

_THIRD_TAG = re.compile(r"\(([^()]*?)'s ([^()]*?) says this; I have not verified it\.\)")
_ANY_TAG = re.compile(r" \((I saw this myself in the [^()]*|The user told me this|[^()]*? says this; I have not verified it|"
                      r"My own assumption; I have not checked it)\.\)")
_CHAIN_TO_READER = {"observed": "observed_by_agent", "user": "stated_by_user", "third_party": "claimed_by_third_party",
                    "own_guess": "agent_guess"}


def _draw(*parts) -> float:
    return int(hashlib.sha256("|".join(parts).encode()).hexdigest()[:8], 16) / 0xFFFFFFFF


class FakeClient:
    def __init__(self, scenarios_path, writer="identity", p_detail=0.3, p_plain=0.1, error_every=0, state_path=None,
                 interrupt_after=0, lose_create=False, refuse_every=0, fail_create=False, usage_scale=1.0):
        self.scenarios = load_scenarios(scenarios_path)
        self.details = {f["detail"] for s in self.scenarios for f in s["facts"]}
        self.by_topic: dict[str, list] = {}
        for s in self.scenarios:
            for f in s["facts"]:
                self.by_topic.setdefault(f["topic"], []).append(f)
        self.writer, self.p_detail, self.p_plain, self.error_every = writer, p_detail, p_plain, error_every
        self.interrupt_after, self.lose_create, self.refuse_every = interrupt_after, lose_create, refuse_every
        self.fail_create, self.usage_scale = fail_create, usage_scale
        self.n_calls = 0
        self.attempts: dict[str, int] = {}
        self.lock = threading.Lock()
        # Batches persist on disk so a second process (a resume) sees what the first one submitted, as the real API does.
        self.state_path = Path(state_path) if state_path else None
        self.state = {"batches": {}, "interrupted": False, "lost": False, "failed": False}
        if self.state_path and self.state_path.exists():
            self.state = json.loads(self.state_path.read_text())
        self.messages = SimpleNamespace(create=self.create, batches=SimpleNamespace(
            create=self.batch_create, retrieve=self.batch_retrieve, results=self.batch_results, list=self.batch_list))

    def with_options(self, **_):
        return self

    def _save(self):
        if self.state_path:
            self.state_path.write_text(json.dumps(self.state))

    # --------------------------------------------------------------------------------------------- responses
    def _tick(self, params: dict) -> bool:
        """A transient error on about 1 in error_every attempts, drawn independently per request and attempt."""
        if not self.error_every:
            return False
        key = hashlib.sha256(json.dumps(params, sort_keys=True).encode()).hexdigest()
        with self.lock:
            self.n_calls += 1
            attempt = self.attempts[key] = self.attempts.get(key, 0) + 1
        return _draw(key, str(attempt)) < 1 / self.error_every

    def respond(self, params: dict):
        user = params["messages"][0]["content"]
        if user.startswith("Notes:\n<<<\n"):
            out = self.read(user)
        elif "Notes on this task so far:" in user:
            out = self.write(user)
        else:
            out = "unknown"
        usage = SimpleNamespace(input_tokens=int(len(user) // 4 * self.usage_scale),
                                output_tokens=int((len(out) // 4 + 50) * self.usage_scale))
        stop = "end_turn"
        if (self.refuse_every and "Notes on this task so far:" in user
                and _draw("refuse", user) < 1 / self.refuse_every):
            out, stop = "", "refusal"
        return SimpleNamespace(content=[SimpleNamespace(type="text", text=out)], model=params["model"],
                               stop_reason=stop, usage=usage, stop_details=None)

    def create(self, **params):
        if self._tick(params):
            raise RuntimeError("fake transient error")
        return self.respond(params)

    def write(self, user: str) -> str:
        instr = next(v for v in DISCIPLINES.values() if user.endswith(v))
        notes = user.split("Notes on this task so far:\n\n", 1)[1][: -len(instr) - 2]
        n = notes.count("(rewrite ") + 1
        if notes.lstrip().startswith("{"):
            data = json.loads(notes)
            if self.writer == "upgrader":
                for c in data["claims"]:
                    if c["source"] == "third_party":
                        p = self.p_detail if c["claim"] in self.details else self.p_plain
                        if _draw(c["claim"], notes) < p:
                            c["source"], c["verified"] = "observed", "yes"
            data["summary"] = data["summary"] + f" (rewrite {n})"
            return json.dumps(data, indent=1, ensure_ascii=False)
        lines = notes.splitlines()
        if self.writer == "stripper":
            lines = [_ANY_TAG.sub("", ln) for ln in lines]
        elif self.writer == "upgrader":
            out = []
            for ln in lines:
                if _THIRD_TAG.search(ln):
                    p = self.p_detail if any(d in ln for d in self.details) else self.p_plain
                    if _draw(ln, notes) < p:
                        ln = _THIRD_TAG.sub("(I saw this myself in the tool output.)", ln)
                out.append(ln)
            lines = out
        return "\n".join(lines + [f"(rewrite {n})"])

    def read(self, user: str) -> str:
        artifact = user.split("Notes:\n<<<\n", 1)[1].split("\n>>>", 1)[0]
        topics = dict(re.findall(r"^(t\d+): (.+)$", user, re.MULTILINE))
        claims = None
        if artifact.lstrip().startswith("{"):
            claims = json.loads(artifact)["claims"]
        answers = {}
        for k in TOPIC_KEYS:
            fact = next((f for f in self.by_topic.get(topics.get(k, ""), []) if contains_value(artifact, f)), None)
            if fact is None:
                answers[k] = {"value": "", "source": "not_stated", "rely": "verify_first"}
                continue
            if claims is not None:
                c = next(c for c in claims if contains_value(f"{c['value']} {c['claim']}", fact))
                src = _CHAIN_TO_READER[c["source"]]
            else:
                line = next(ln for ln in artifact.splitlines() if contains_value(ln, fact))
                if "(I saw this myself" in line:
                    src = "observed_by_agent"
                elif "(The user told me this" in line:
                    src = "stated_by_user"
                elif "says this; I have not verified it" in line:
                    src = "claimed_by_third_party"
                elif "(My own assumption" in line:
                    src = "agent_guess"
                else:
                    src = "not_stated"
            answers[k] = {"value": fact["value"], "source": src,
                          "rely": "rely_without_checking" if src == "observed_by_agent" else "verify_first"}
        items = [{"topic": k, **a} for k, a in answers.items()]
        return json.dumps({"answers": items[::-1]})  # reversed, so nothing relies on answer order

    # ----------------------------------------------------------------------------------------------- batches
    def batch_create(self, requests):
        if self.fail_create and not self.state.get("failed"):
            self.state["failed"] = True
            self._save()
            raise ConnectionError("fake: the create request never reached the API")
        bid = f"msgbatch_fake{len(self.state['batches']) + 1}"
        self.state["batches"][bid] = {"requests": list(requests), "polls": 0, "created_at": time.time()}
        self._save()
        if self.lose_create and not self.state["lost"]:
            self.state["lost"] = True
            self._save()
            raise ConnectionError("fake: batch created but the response was lost")
        return SimpleNamespace(id=bid, processing_status="in_progress")

    def _counts(self, b, ended):
        n = len(b["requests"])
        return SimpleNamespace(processing=0 if ended else n, succeeded=n if ended else 0, errored=0, canceled=0, expired=0)

    def batch_retrieve(self, bid):
        b = self.state["batches"][bid]
        b["polls"] += 1
        self._save()
        ended = b["polls"] >= 2
        return SimpleNamespace(id=bid, processing_status="ended" if ended else "in_progress",
                               request_counts=self._counts(b, ended))

    def batch_list(self, limit=20):
        items = sorted(self.state["batches"].items(), key=lambda kv: -kv[1]["created_at"])[:limit]
        return [SimpleNamespace(id=bid, created_at=b["created_at"], request_counts=self._counts(b, b["polls"] >= 2))
                for bid, b in items]

    def batch_results(self, bid):
        # Results are fixed per batch (like the real API): drawn once, stored, and replayed on a second collection.
        b = self.state["batches"][bid]
        if "results" not in b:
            out = []
            for req in b["requests"]:
                if self._tick(req["params"]):
                    out.append({"custom_id": req["custom_id"], "type": "errored"})
                else:
                    m = self.respond(req["params"])
                    out.append({"custom_id": req["custom_id"], "type": "succeeded", "text": m.content[0].text,
                                "model": m.model, "in": m.usage.input_tokens, "out": m.usage.output_tokens,
                                "stop": m.stop_reason})
            b["results"] = out
            self._save()
        for n, r in enumerate(b["results"]):
            if self.interrupt_after and n == self.interrupt_after and not self.state["interrupted"]:
                self.state["interrupted"] = True
                self._save()
                raise KeyboardInterrupt
            if r["type"] == "errored":
                yield SimpleNamespace(custom_id=r["custom_id"], result=SimpleNamespace(
                    type="errored", error=SimpleNamespace(type="api_error")))
            else:
                msg = SimpleNamespace(content=[SimpleNamespace(type="text", text=r["text"])], model=r["model"],
                                      stop_reason=r["stop"], stop_details=None,
                                      usage=SimpleNamespace(input_tokens=r["in"], output_tokens=r["out"]))
                yield SimpleNamespace(custom_id=r["custom_id"], result=SimpleNamespace(type="succeeded", message=msg))
