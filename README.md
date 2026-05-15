Start by installing UV

- uv init
- uv add autogen-agentchat
-uv add autogen-ext[openai]
- uv run main.py

---

# AutoGen Multi-Agent Chain: Automated Code Testing & Debugging

A demonstration of an **AutoGen (AG2) multi-agent workflow** where three specialised agents collaborate to generate, test, and iteratively debug a Python function.

## Overview

| Agent | Role |
|---|---|
| **CodeGen** | Generates `solution.py` containing an `is_palindrome` function |
| **Tester** | Writes `test_solution.py` with assertion-based tests |
| **Debugger** | Analyses failures and rewrites the solution (up to N retries) |

### Workflow

```
CodeGen ──▶ Tester ──▶ Test Runner ──▶ (pass?) ──▶ Done
                           │
                        (fail)
                           │
                       Debugger ──▶ Test Runner ──▶ ... (retry loop)
```

1. **CodeGen** produces `solution.py` with the target function.
2. **Tester** generates `test_solution.py` covering typical and edge cases.
3. Tests are executed in an **isolated subprocess** (sandboxed temp directory).
4. If tests fail, the **Debugger** agent rewrites the solution — up to `MAX_DEBUG_ROUNDS` attempts (default: 2).
5. Final artefacts (solution, tests, JSON logs) are saved to a timestamped `runs/` directory.

## Tech Stack

- **Python 3.12+**
- **AutoGen (AG2)** — `autogen-agentchat`, `autogen-ext[openai]`
- **LangChain OpenAI** — `langchain-openai`
- **Groq API** — Llama 3.3 70B (OpenAI-compatible endpoint)
- **python-dotenv** — loads secrets from `.env`
- **uv** — fast Python package manager

## Prerequisites

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/).
2. Create a `.env` file in the project root:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```
3. (Optional) Set environment variables to tune behaviour:
   - `RATE_SLEEP_SEC` — delay between LLM calls (default `1.0`).
   - `MAX_DEBUG_ROUNDS` — max debugger retries (default `2`).

## Quick Start

```bash
uv init
uv add autogen-agentchat autogen-ext[openai] langchain-openai python-dotenv
uv run main.py
```

## Project Structure

```
├── main.py               # Orchestration script (agents + pipeline)
├── pyproject.toml        # Project metadata & dependencies
├── .env                  # API keys (git-ignored)
├── .gitignore
├── runs/                 # Timestamped output directories
│   └── YYYYMMDD_HHMMSS/
│       ├── solution.py
│       ├── test_solution.py
│       └── log.jsonl
└── README.md
```

## Output

Each run creates a timestamped directory under `runs/` containing:
- **solution.py** — the final (possibly debugger-fixed) solution
- **test_solution.py** — the generated test file
- **log.jsonl** — full JSON-lines log of every agent interaction and test result
