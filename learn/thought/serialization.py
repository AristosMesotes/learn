"""
serialization.py – pluggable converters that turn IThought objects into the
message dictionaries required by each backend.  Uses functools.singledispatch
so new Thought types or new backends register with *one* decorator instead of
editing core classes.
"""

from __future__ import annotations

import functools
import json
from typing import Any, Dict, List

from learn.thought.ithought import IThought
from learn.thought.text_thought import TextThought
from learn.thought.tool_request_thought import ToolRequestThought
from learn.thought.vision_thought import VisionThought


# ── local helpers (provider‑agnostic storage → provider payloads) ────────────
def _as_json_str(v: Any) -> str:
    """Ensure tool output is a string (OpenAI expects strings for tool content)."""
    if isinstance(v, str):
        return v
    try:
        return json.dumps(v)
    except Exception:
        return str(v)

def _as_json_obj(v: Any) -> Any:
    """Ensure tool output is an object for Gemini function_response."""
    if v is None:
        return None
    if isinstance(v, str):
        try:
            return json.loads(v)
        except Exception:
            return {"result": v}
    try:
        json.dumps(v)  # validate serialisable
        return v
    except Exception:
        return {"result": str(v)}

def _args_obj(v: Any) -> Any:
    """Arguments may be a JSON string (OpenAI-style) or already an object."""
    if isinstance(v, str):
        try:
            return json.loads(v)
        except Exception:
            return v  # leave as-is if it's not JSON; upstream may handle
    return v


# --------------------------- Registries ------------------------------------ #
@functools.singledispatch
def to_openai(th: IThought) -> List[Dict[str, Any]]:
    raise TypeError(f"No OpenAI serialiser registered for {type(th)}")


@functools.singledispatch
def to_gemini(th: IThought) -> List[Dict[str, Any]]:
    raise TypeError(f"No Gemini serialiser registered for {type(th)}")

# --------------------- Concrete registrations ------------------------------ #

@to_openai.register
def _(th: IThought) -> List[Dict[str, Any]]:
    """Default OpenAI serialization for base IThought."""
    content = th.content
    if content is None:
        content = ""
    elif not isinstance(content, str):
        content = _as_json_str(content)
    
    # Handle role mapping
    role = th.role
    if role not in {"system", "assistant", "user", "function", "tool", "developer"}:
        role = "user"  # Default to user role
    
    return [{"role": role, "content": content}]


@to_gemini.register  
def _(th: IThought) -> List[Dict[str, Any]]:
    """Default Gemini serialization for base IThought."""
    content = th.content
    if content is None:
        content = ""
    elif not isinstance(content, str):
        content = _as_json_str(content)
    
    return [{"role": th.role_gemini, "parts": [{"text": content}]}]


@to_openai.register
def _(th: TextThought) -> List[Dict[str, Any]]:
    return [{"role": th.role, "content": th.content}]


@to_gemini.register
def _(th: TextThought) -> List[Dict[str, Any]]:
    return [{"role": th.role_gemini, "parts": [{"text": th.content}]}]


@to_openai.register
def _(th: ToolRequestThought) -> List[Dict[str, Any]]:
    """Serialize a tool request and its results for OpenAI."""
    msg = {"role": "assistant", "tool_calls": th.content}

    # Map outputs by call id so we can preserve the request order.
    out_map = {o.get("tool_call_id"): _as_json_str(o.get("content", "")) for o in th.tool_outputs}
    tool_msgs = [
        {
            "role": "tool",
            "tool_call_id": call.get("id"),
            "content": out_map.get(call.get("id"), ""),
        }
        for call in th.content or []
    ]

    return [msg, *tool_msgs]


@to_gemini.register
def _(th: ToolRequestThought) -> List[Dict[str, Any]]:
    msgs: List[Dict[str, Any]] = []

    # 1) assistant/model function_call(s)
    for req in (th.content or []):
        fn = (req.get("function") or {})
        name = fn.get("name")
        if not name:
            continue
        args = _args_obj(fn.get("arguments", {}))
        msgs.append({
            "role": "model",
            "parts": [{"function_call": {"name": name, "args": args}}],
        })

    # 2) tool function_response(s)
    for out in th.tool_outputs:
        name = out.get("name")
        if name is None:
            continue
        msgs.append({
            "role": "tool",
            "parts": [{"function_response": {"name": name, "response": _as_json_obj(out.get("content"))}}],
        })
    return msgs


@to_openai.register
def _(th: VisionThought) -> List[Dict[str, Any]]:
    return [
        {
            "role": th.role,
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{th.mime_type};base64,{th.content}"},

                },
                {"type": "text", "text": th.query or ""},
            ],
        }
    ]
