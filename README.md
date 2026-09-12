# Code Smith

An AI coding mentor that runs in your terminal. Ask it about any programming
topic and it explains the concept at the difficulty level you pick.

It talks to any **OpenAI-compatible** provider — OpenAI, Google Gemini, Groq or
NVIDIA — so you can run it on a free tier while you learn.

```
$ uv run code-smith
==================================================
Code Smith AI Agent
Ask about any topic. Type exit / q / quit to leave.
==================================================

Topic: decorators
Difficulty: beginner

Assistant:

A decorator is a function that wraps another function...
```

## Requirements

- [uv](https://docs.astral.sh/uv/) — handles Python and dependencies for you
- An API key from one of the supported providers

You do **not** need to install Python yourself. `uv` reads `.python-version`
and fetches the right one (3.13).

## Setup

```bash
git clone https://github.com/rahulCoder9417/Code-Smith.git
cd Code-Smith

uv sync                  # creates .venv/ and installs everything
cp .env.example .env     # then open .env and add your API key
```

## Configuration

All configuration comes from `.env`. `.env.example` lists every variable.

| Variable | Required | Default | What it does |
|---|---|---|---|
| `LLM_PROVIDER` | yes | — | `openai`, `gemini`, `groq` or `nvidia` |
| `LLM_MODEL` | yes | — | Model id, as your provider names it |
| `LLM_API_KEY` | yes | — | Your key for that provider |
| `SYSTEM_PROMPT` | no | `teacher` | A file in `app/prompts/system/`, without `.txt` |
| `LOG_LEVEL` | no | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |

`.env` is gitignored. **Never commit an API key.**

Switching providers is one line — no code change:

```bash
LLM_PROVIDER=groq
LLM_MODEL=llama-3.3-70b-versatile
```

## Running it

```bash
uv run code-smith                 # or: uv run python -m app.main
LOG_LEVEL=DEBUG uv run code-smith # see which model and prompts are used
```

Logs go to **stderr** and answers go to **stdout**, so you can redirect the
answer on its own:

```bash
uv run code-smith > answers.txt
```

## Tests

```bash
uv run pytest
uv run pytest -v          # one line per test
uv run pytest tests/test_settings.py
```

**Tests never call a real LLM.** They run offline, cost nothing, and need no
API key — `tests/fakes.py` provides a `FakeChatClient` that answers from a
script and a `FakeOpenAI` that imitates the SDK. How good the real model's
answers are is a separate question, measured later with evals.

## How it fits together

```
                 .env
                  │
                  ▼
      ┌───────────────────────┐
      │ Settings              │  pydantic-settings validates the config
      │ (app/config)          │  when you ask for it, not at import time
      └───────────┬───────────┘
                  │ injected
      ┌───────────▼───────────┐         ┌──────────────────────┐
      │ main.run_cli          │────────▶│ PromptManager        │
      │ (the loop)            │         │ system/*.txt         │
      │                       │         │ user/*.txt           │
      └───────────┬───────────┘         └──────────────────────┘
                  │ depends on the LLMClient protocol,
                  │ not on any concrete class
      ┌───────────▼───────────┐
      │ LLMClient (Protocol)  │
      └───────┬───────────┬───┘
              │           │
      ┌───────▼─────┐ ┌───▼──────────────┐
      │ ChatClient  │ │ FakeChatClient   │
      │ real API    │ │ tests, no network│
      └─────────────┘ └──────────────────┘
```

`run_cli()` receives its client, prompts and even its input/output functions
as arguments. That is **dependency injection**: the real app passes the real
client, the tests pass a fake, and neither knows about the other.

## Layout

```
app/
  config/
    settings.py      validated configuration (pydantic-settings)
    providers.py     base URLs for each OpenAI-compatible provider
  llm/
    base.py          the LLMClient protocol every client implements
    chat_client.py   the real client
  prompts/
    manager.py       loads and renders prompt files
    system/          who the model is  (teacher, debugger, interviewer, ...)
    user/            what to ask it    (explanation, quiz, summarize)
  models/            (Pydantic schemas — coming in Chapter 2)
  parsers/           (output validation — coming in Chapter 2)
  logging_config.py  one place that configures logging
  main.py            entry point and the CLI loop
tests/
  fakes.py           FakeChatClient + FakeOpenAI
  conftest.py        shared fixtures
```

## Adding a provider

Add an entry to `PROVIDER_CONFIG` in `app/config/providers.py`:

```python
"together": {"base_url": "https://api.together.xyz/v1/"},
```

Then set `LLM_PROVIDER=together` in `.env`. Anything that speaks the
OpenAI chat-completions format will work.

## Status

Code Smith is being grown into a full agentic AI mentor — tool calling, RAG,
memory, and multiple specialist agents. Current stage: **Chapter 1, LLM
foundations.**
