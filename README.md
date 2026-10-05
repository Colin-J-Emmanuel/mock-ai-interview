# Mock AI Interviewer

A voice-based mock interviewer for behavioral and verbal technical/system-design interviews. An LLM interviewer asks questions from a question bank and probes with follow-ups; after the session, a separate evaluator grades the transcript against per-question rubrics.

> **Status:** early build. Phase 0a (question schema) is complete. See the [build log](#build-log).

## How it works (target design)

```
question bank ──► interviewer (state machine + LLM) ──► transcript ──► evaluator (LLM + rubric) ──► report
                         ▲                │
                         └── you (voice) ─┘
```

1. **Question bank:** each question carries its type, time budget, follow-up probes, and an anchored scoring rubric.
2. **Interviewer:** a state machine (intro → ask → probe → next → wrap-up) decides *when* to move on; the LLM only phrases what to say.
3. **Transcript:** every turn is stored, so evaluation can be re-run independently of the interview.
4. **Evaluator:** a separate agent scores the finished transcript, citing quotes from your answers for each score.

## Design decisions

- **Interviewer and evaluator are separate agents.** An interviewer that also grades tends to leak hints or go easy. The evaluator only sees the finished transcript, so it judges what was actually said (maker ≠ checker).
- **Code controls the flow; the LLM only phrases it.** Probe limits and time budgets are enforced by the state machine, so the model can't wander off or turn into a tutor.
- **Anchored rubrics.** Each criterion defines what a 1, 3, and 5 look like. Without anchors, LLM scores drift between runs.
- **Probes with triggers.** Follow-ups are chosen from a list based on stated conditions, not invented freely.
- **Strict validation at load time.** Invalid questions (missing anchors, duplicate criteria, unknown fields) are rejected when loaded, not discovered as confusing scores later.
- **Rubric versioning.** Each evaluation records the rubric version it used, so scores stay comparable as rubrics evolve.
- **Provider-agnostic LLM layer.** Model calls go through one interface, so switching providers is a config change.
- **One session, one device.** A session starts and finishes on the same device; state lives on the server so a refresh or dropped connection doesn't lose progress.

## Stack

- **Backend:** Python, pydantic
- **Planned:** FastAPI, Postgres, React PWA, Groq (LLM + Whisper speech-to-text), browser speech synthesis

## Running the tests

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -v
```

## Build log

| Phase | Description | Status |
| --- | --- | --- |
| 0a | Question schema models (pydantic) with happy- and failure-path tests | ✅ Done |
| 0b | Postgres `questions` table and idempotent YAML seed script | Next |
| 1 | Interviewer state machine behind API endpoints, minimal web chat, first deploy | Planned |
| 2 | Transcript persistence | Planned |
| 3 | Rubric-driven evaluator, tested on strong vs. weak answer fixtures | Planned |
| 4 | Voice: push-to-talk speech-to-text and text-to-speech | Planned |
| 5 | Reports and score history across sessions | Planned |