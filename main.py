"""AutoGen Multi-Agent Chain: Automated Code Testing & Debugging

This script demonstrates an AutoGen (AG2) multi-agent workflow where three
specialised agents — CodeGen, Tester, and Debugger — collaborate to generate,
test, and iteratively fix a Python function (is_palindrome).

Workflow:
    1. CodeGen generates a solution.py with the target function.
    2. Tester produces test_solution.py with assertion-based tests.
    3. Tests are executed in a sandboxed subprocess.
    4. If tests fail, the Debugger agent rewrites the solution (up to
       MAX_DEBUG_ROUNDS attempts).
    5. Final artefacts (solution, tests, logs) are saved to a timestamped
       runs/ directory.

Requirements:
    - Python 3.12+
    - A valid GROQ_API_KEY in a .env file
    - Dependencies managed via uv (see pyproject.toml)
"""

import os
from dotenv import load_dotenv
import re
import time
import tempfile
import subprocess
import textwrap
import json
import datetime
import pathlib
import sys
import asyncio
from typing import Tuple

# Load environment variables from .env file (must contain GROQ_API_KEY)
load_dotenv()

# AutoGen (AG2) imports
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from langchain_openai import ChatOpenAI
 
# ── LLM Configuration ─────────────────────────────────────────────────────────
# Uses Llama 3.3 70B hosted on Groq (OpenAI-compatible API).
groq_key = os.getenv("GROQ_API_KEY")
if not groq_key:
    raise ValueError("GROQ_API_KEY not found in environment variables. Add it to your .env file.")

# LangChain ChatOpenAI client (used for any direct LangChain-style calls)
llm = ChatOpenAI(
    model="llama-3.3-70b-versatile",
    api_key=groq_key,
    base_url="https://api.groq.com/openai/v1",
    temperature=0.5,
)
MODEL = "groq-llama-3.3-70b-versatile"

# AutoGen-style config list (kept for reference / potential multi-provider use)
llm_cfg = {
    "config_list": [
        {
            "api_type": "groq",
            "model": "llama-3.3-70b-versatile",
            "api_key": groq_key,
            "base_url": "https://api.groq.com/openai/v1",
            "api_version": "2025-01-01-preview",
        }
    ]
}

groq_cfg = llm_cfg["config_list"][0]

# AutoGen model client — wraps the Groq endpoint as an OpenAI-compatible client.
# model_info is required because Llama 3.3 is not a built-in OpenAI model name.
model_client = OpenAIChatCompletionClient(
    model=groq_cfg["model"],
    api_key=groq_cfg["api_key"],
    base_url=groq_cfg["base_url"],
    model_info={
        "vision": False,
        "function_calling": True,
        "json_output": True,
        "structured_output": False,
        "family": "unknown",
    },
)

# ── Rate-Limiting & Retry Settings ────────────────────────────────────────────
# Delay (seconds) between consecutive LLM calls to respect API rate limits.
SLEEP_BETWEEN_CALLS_SEC = float(os.environ.get("RATE_SLEEP_SEC", "1.0"))
# Maximum number of Debugger retry rounds before giving up.
MAX_DEBUG_ROUNDS = int(os.environ.get("MAX_DEBUG_ROUNDS", "2"))

# ── Logging & Run Artefacts ───────────────────────────────────────────────────
# Each run is saved in a timestamped directory under runs/.
RUN_DIR = pathlib.Path("runs") / datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
RUN_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = RUN_DIR / "log.jsonl"


def log_event(kind: str, payload: dict):
    """Append a JSON-lines log entry with a UTC timestamp."""
    rec = {"ts": datetime.datetime.now(datetime.timezone.utc).isoformat(), "kind":kind, **payload}
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n") 
 
# ── Helpers ────────────────────────────────────────────────────────────────────
# Regex to capture content inside a Markdown fenced code block (```python ... ```).
CODE_BLOCK_RE = re.compile(r"```(?:python)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)


def extract_code_block(text: str) -> str:
    """Extract and dedent Python code from a Markdown fenced code block."""
    m = CODE_BLOCK_RE.search(text or "")
    return textwrap.dedent(m.group(1).strip()) if m else textwrap.dedent(text or "").strip() 
 
def run_py_tests(solution_code: str, test_code: str, timeout_sec: int = 10) -> Tuple[bool, str]:
    """Execute test_solution.py against solution.py in an isolated temp directory.
    Returns a (passed, output) tuple where *passed* is True when all assertions
    succeed and the subprocess exits with code 0.
    """
    with tempfile.TemporaryDirectory() as tmp:
        sol = pathlib.Path(tmp) / "solution.py"
        tst = pathlib.Path(tmp) / "test_solution.py"
        sol.write_text(solution_code, encoding="utf-8")
        tst.write_text(test_code, encoding="utf-8")

        cmd = [sys.executable, str(tst)]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_sec, cwd=tmp)
            out = (proc.stdout or "") + (proc.stderr or "")
            passed = proc.returncode == 0
            return passed, out.strip()
        except subprocess.TimeoutExpired as e:
            return False, f"TIMEOUT after {timeout_sec}s\n{e}"
        except Exception as e:
            return False, f"EXEC_ERROR: {e}" 

async def _ask_async(agent: AssistantAgent, message: str, label: str) -> str:
    """Send a message to an AutoGen agent, wait for the reply, and log it.
    A short sleep is inserted before each call to respect API rate limits.
    The response content is extracted from whichever result attribute the
    agent populates (chat_message, messages list, or raw string fallback).
    """
    await asyncio.sleep(SLEEP_BETWEEN_CALLS_SEC)
    result = await agent.on_messages(
        messages=[TextMessage(content=message, source="user")],
        cancellation_token=None,
    )

    content = ""
    if hasattr(result, "chat_message") and getattr(result.chat_message, "content", None) is not None:
        content = result.chat_message.content
    elif hasattr(result, "messages") and result.messages:
        content = getattr(result.messages[-1], "content", "") or ""
    else:
        content = str(result)

    log_event("llm_reply", {"agent": getattr(agent, "name", "assistant"), "label": label, "content": content})
    return content


def ask(agent: AssistantAgent, message: str, label: str) -> str:
    """Synchronous wrapper around _ask_async for convenience."""
    return asyncio.run(_ask_async(agent, message, label))

# ── Agent Definitions ─────────────────────────────────────────────────────────
# Three specialised agents collaborate in a sequential pipeline:
#   CodeGen  → generates the initial solution.py
#   Tester   → writes assertion-based tests (test_solution.py)
#   Debugger → fixes the solution when tests fail

codegen = AssistantAgent( 
    name="CodeGen", 
    system_message=( 
        "You are CodeGen. Write Python code for solution.py with a SINGLE function:\n" 
        "def is_palindrome(text: str) -> bool\n" 
        "- Return True if text is a palindrome.\n" 
        "- Ignore non-alphanumeric characters and case.\n" 
        "- Do not print; no comments; no extra text.\n" 
        "Reply with ONLY a Python fenced code block for solution.py." 
    ), 
    model_client=model_client, 
)

tester = AssistantAgent( 
    name="Tester", 
    system_message=( 
        "You are Tester. Write tests in test_solution.py using Python asserts.\n" 
        "Import from solution import is_palindrome.\n" 
        "Cover typical and edge cases (empty, punctuation, mixed case, long string).\n" 
        "Reply with ONLY a Python fenced code block for test_solution.py." 
    ), 
    model_client=model_client, 
) 
 
debugger = AssistantAgent( 
    name="Debugger", 
    system_message=( 
        "You are Debugger. Given failing test output and the current solution.py, " 
        "produce a FIXED solution.py that passes tests. Keep the same signature:\n" 
        "def is_palindrome(text: str) -> bool\n" 
        "Reply with ONLY a Python fenced code block for solution.py." 
    ), 
    model_client=model_client, 
)

# ── Main Orchestration ────────────────────────────────────────────────────────

async def main():
    """Run the full CodeGen → Tester → Debugger pipeline."""
    print("== AutoGen Code Testing and Debugging Chain (Groq / Llama 3.3 70B) ==")
    print(f"Model: {MODEL}")
    log_event("start", {"deployment": MODEL})

    # Step 1 — CodeGen produces solution.py
    cg_out = await _ask_async(codegen, "Write solution.py as specified. Return ONLY the code block.", "codegen")
    solution = extract_code_block(cg_out)
    # Quick sanity check: retry once if the expected function signature is missing.
    if "def is_palindrome" not in solution:
        cg_out = await _ask_async(codegen, "Please include def is_palindrome(text: str) -> bool", "codegen_retry")
        solution = extract_code_block(cg_out)
    log_event("solution", {"code": solution})
    print("\n[CodeGen] Generated solution.py")

    # Step 2 — Tester produces test_solution.py
    tt_out = await _ask_async(tester, "Create test_solution.py for is_palindrome; ONLY code block.", "tester")
    tests = extract_code_block(tt_out)
    log_event("tests", {"code": tests})
    print("[Tester] Generated test_solution.py") 
 
    # Step 3 — Execute tests in a sandboxed subprocess
    passed, output = run_py_tests(solution, tests, timeout_sec=10)
    print("\n[Test Runner] First run passed? ", passed)
    print(output)
    log_event("test_run", {"passed": passed, "output": output})

    # Step 4 — Debugger retry loop (up to MAX_DEBUG_ROUNDS attempts)
    rounds = 0
    while not passed and rounds < MAX_DEBUG_ROUNDS:
        rounds += 1
        print(f"\n[Debugger] Fix attempt #{rounds}")
        dbg_prompt = (
            "Tests failed with output below. Current solution.py is also provided.\n\n"
            f"=== FAIL LOG ===\n{output}\n\n=== CURRENT solution.py ===\n```python\n{solution}\n```"
        )
        dbg_out = await _ask_async(debugger, dbg_prompt, f"debugger_round_{rounds}")
        fixed = extract_code_block(dbg_out)
        if fixed and fixed != solution:
            solution = fixed
        log_event("debug_fix", {"round": rounds, "code": solution})

        passed, output = run_py_tests(solution, tests, timeout_sec=10)
        print("[Test Runner] Passed after fix? ", passed)
        print(output)
        log_event("test_rerun", {"round": rounds, "passed": passed, "output": output})

    # Step 5 — Persist artefacts and print final status
    (RUN_DIR / "solution.py").write_text(solution, encoding="utf-8")
    (RUN_DIR / "test_solution.py").write_text(tests, encoding="utf-8")
    status = "ALL TESTS PASSED" if passed else "STOPPED WITH FAILURES (see logs)"
    print("\n== RESULT:", status)
    print("Artefacts saved to:", RUN_DIR)
    log_event("end", {"status": status, "artifacts_dir": str(RUN_DIR)}) 
 
if __name__ == "__main__":
    asyncio.run(main())