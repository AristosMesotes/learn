from __future__ import annotations

import asyncio
import json
import uuid
from typing import Any, Dict, Optional

from learn.thought.ithought import IThought


@IThought.thought_type("tool_request")
class ToolRequestThought(IThought):
    """
    Encapsulates one or more function calls that the model wants to execute.

    ❖ Design goals (per logging/bridge policy)
      • Silent data carrier — no logging/printing here (privacy + no duplication).
      • Keep outputs payload-safe (tool outputs are strings).
      • Preserve existing execution semantics, including parallel batching.

    Structure
    ---------
    self.content : list[dict]
        The tool call requests (OpenAI-style {"function":{...},"id":...} or
        Responses-style {"name":..., "arguments":..., "call_id":...}).

    self.tool_outputs : list[dict]
        A list of {"tool_call_id": str, "name": str, "content": str} accumulated
        by add_tool_output(), used later by the provider bridge.
    """

    def __init__(self, content: Optional[Dict[str, Any]] = None, **kwargs):
        kwargs["role"] = "assistant"
        super().__init__(content, **kwargs)

    @property
    def mime_type(self) -> str:
        return "application/json"

    @property
    def tool_outputs(self) -> list[dict]:
        """
        A list of dicts:
           {"tool_call_id": <id>, "name": <function_name>, "content": <str>}
        """
        if not isinstance(self.metadata.get("tool_outputs"), list):
            self.metadata["tool_outputs"] = []
        return self.metadata.get("tool_outputs")

    def add_tool_output(self, content, function_name, tool_call_id) -> None:
        """
        Store the output of a tool invocation, keyed by tool_call_id.
        'content' is coerced to a STRING to comply with provider bridge requirements.
        """
        if isinstance(content, (dict, list)):
            content_str = json.dumps(content)
        elif content is None:
            content_str = "null"
        else:
            content_str = str(content)

        self.tool_outputs.append(
            {
                "tool_call_id": tool_call_id,
                "name": function_name,   # kept for readability; bridge uses tool_call_id
                "content": content_str,  # always a string
            }
        )

    async def execute_tools(self, tools: "Tools") -> None:
        """
        Execute all requested tools and capture their outputs into self.tool_outputs.

        • Supports both OpenAI-style (function/name+arguments in "function") and
          raw Responses API-style (top-level name/arguments/call_id) entries.
        • Batches adjacent parallel tools (tools with .parallel=True) and runs them
          concurrently; executes sequential tools one-by-one in order.
        • Errors from execution are propagated into add_tool_output(content=error_str,...)
          while the centralized error logging happens in Tools.use_tool().
        """
        if not self.content or not isinstance(self.content, list):
            self.metadata["tool_outputs"] = []
            return

        self.metadata["tool_outputs"] = []
        task_entries = []

        # Build task list (do not log or print here)
        for req in self.content:
            fn_info = req.get("function", {}) if isinstance(req, dict) else {}
            function_name = fn_info.get("name")
            arguments_blob = fn_info.get("arguments", "{}")
            call_id = req.get("id", "call_" + str(uuid.uuid4())[:32])

            # Fallback for raw Responses-style format
            if function_name is None:
                function_name = req.get("name")
                arguments_blob = req.get("arguments", "{}")
                call_id = req.get("call_id", call_id)

            # Decode args
            try:
                arguments = (
                    json.loads(arguments_blob)
                    if isinstance(arguments_blob, str)
                    else (arguments_blob if isinstance(arguments_blob, dict) else {})
                )
            except json.JSONDecodeError:
                self.add_tool_output(
                    {"error": "Invalid JSON", "args": arguments_blob},
                    function_name or "<unknown>",
                    call_id,
                )
                continue

            # Invoke (async-aware, but do not await yet)
            try:
                result_or_task = tools.use_tool(function_name, arguments)
                task_entries.append((call_id, function_name, result_or_task))
            except Exception as e:
                # Unknown tool or immediate invocation setup error.
                self.add_tool_output(str(e), function_name or "<unknown>", call_id)

        # Execute with parallel batching
        i = 0
        while i < len(task_entries):
            call_id, fname, item = task_entries[i]

            # Determine parallelism (default True if tool not found)
            try:
                tool = tools.get_tool(fname)
                is_parallel = getattr(tool, "parallel", True)
            except Exception:
                is_parallel = True

            if not is_parallel:
                # Sequential tool — execute alone and wait
                if asyncio.iscoroutine(item) or isinstance(item, asyncio.Task):
                    try:
                        result = await item
                    except Exception as e:
                        result = e
                else:
                    result = item
                self.add_tool_output(result, fname, call_id)
                i += 1
            else:
                # Collect adjacent parallel tools for a single batch
                parallel_batch = [(call_id, fname, item)]
                j = i + 1
                while j < len(task_entries):
                    next_call_id, next_fname, next_item = task_entries[j]
                    try:
                        next_tool = tools.get_tool(next_fname)
                        next_is_parallel = getattr(next_tool, "parallel", True)
                    except Exception:
                        next_is_parallel = True
                    if next_is_parallel:
                        parallel_batch.append((next_call_id, next_fname, next_item))
                        j += 1
                    else:
                        break

                # Execute all async tasks in the batch concurrently; non-async immediately
                batch_coroutines = []
                batch_meta = []
                for b_call_id, b_fname, b_item in parallel_batch:
                    if asyncio.iscoroutine(b_item) or isinstance(b_item, asyncio.Task):
                        batch_coroutines.append(b_item)
                        batch_meta.append((b_call_id, b_fname, True))
                    else:
                        # Sync result already available
                        self.add_tool_output(b_item, b_fname, b_call_id)
                        batch_meta.append((b_call_id, b_fname, False))

                if batch_coroutines:
                    try:
                        batch_results = await asyncio.gather(*batch_coroutines, return_exceptions=True)
                        idx = 0
                        for b_call_id, b_fname, is_async in batch_meta:
                            if is_async:
                                self.add_tool_output(batch_results[idx], b_fname, b_call_id)
                                idx += 1
                    except Exception as e:
                        # Catastrophic batch failure — attribute the same error to each async item.
                        for b_call_id, b_fname, is_async in batch_meta:
                            if is_async:
                                self.add_tool_output(e, b_fname, b_call_id)

                i = j  # advance past this batch
