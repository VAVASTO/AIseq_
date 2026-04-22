from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

BENCHMARK_PATH = Path(__file__).resolve().parents[2] / "benchmark" / "cases.jsonl"

app = FastAPI(title="JudgeBench Mock Target")
# Primary lookup by stable case id (benchmark has duplicate user_prompt strings).
ID2CASE: Dict[str, Dict[str, Any]] = {}
# Backward compatibility if caller sends only the raw user_prompt (ambiguous if duplicated).
PROMPT2CASE: Dict[str, Dict[str, Any]] = {}

_ID_PREFIX = "<<JUDGEBENCH_ID:"
_ID_SUFFIX = ">>\n"


def _parse_case_id_from_user_text(text: str) -> tuple[str | None, str]:
    """Return (case_id, user_prompt) when message uses <<JUDGEBENCH_ID:id>>\\n prefix."""
    if text.startswith(_ID_PREFIX) and _ID_SUFFIX in text[:200]:
        end = text.find(_ID_SUFFIX)
        cid = text[len(_ID_PREFIX) : end].strip()
        rest = text[end + len(_ID_SUFFIX) :].lstrip("\n")
        return cid, rest
    return None, text


with BENCHMARK_PATH.open("r", encoding="utf-8") as f:
    for line in f:
        row = json.loads(line)
        ID2CASE[row["id"]] = row
        PROMPT2CASE[row["user_prompt"]] = row


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str = "mock-judge-target"
    messages: List[Message]
    temperature: float | None = 0.0


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/chat/completions")
def chat_completions(req: ChatRequest) -> Dict[str, Any]:
    user_messages = [m.content for m in req.messages if m.role == "user"]
    if not user_messages:
        raise HTTPException(status_code=400, detail="No user message found")

    raw = user_messages[-1]
    case_id, prompt = _parse_case_id_from_user_text(raw)
    case = ID2CASE.get(case_id) if case_id else None
    if case is None:
        case = PROMPT2CASE.get(prompt.strip())
    if case is None:
        raise HTTPException(
            status_code=404,
            detail=f"Case not found (id={case_id!r}, prompt_prefix={prompt[:120]!r})",
        )

    output = case["model_output"]

    return {
        "id": "chatcmpl-judgebench",
        "object": "chat.completion",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": output},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }
