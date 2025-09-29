from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from learn.thought.ithought import IThought


@IThought.thought_type("application/vnd.nodeai.buttons+json")
class ButtonThought(IThought):
    """
    Platform-agnostic representation of a message with clickable buttons.

    Vendor-neutral content schema (stored in .content):
    {
      "text": "Pick an option:",
      "buttons": [
        [
          {"label": "✅ Yes", "action": {"type": "postback", "data": "YES"}},
          {"label": "❌ No",  "action": {"type": "postback", "data": "NO"}}
        ],
        [
          {"label": "Open Docs", "action": {"type": "url", "url": "https://example.com/docs"}}
        ],
        [
          {"label": "Launch App", "action": {"type": "web_app",
                                             "url": "https://host/app.html",
                                             "params": {"h": "{\"USD\":100}"}}}
        ]
      ],
      "hints": { ... optional cross-platform UI hints ... }
    }

    Generic action types supported by the platform adapter(s):
      - "postback" (aka callback): opaque `data` is returned to the bot on click.
      - "url": opens a URL (`action.url`). Supports optional `action.params` to append query string.
      - "web_app": opens a web app (`action.url`). Supports optional `action.params` to append query string.
      - "login": login_url flow (`action.url`).
      - "pay": payment button (Telegram-specific semantics).
    """

    def __init__(
        self,
        text: str,
        buttons: List[List[Dict[str, Any]]],
        role: str = "assistant",
        **kwargs: Any,
    ) -> None:
        kwargs.setdefault("message_type", "application/vnd.nodeai.buttons+json")

        if not isinstance(buttons, list):
            raise TypeError("buttons must be a list of rows (list[list[dict]]).")
        for row in buttons:
            if not isinstance(row, list):
                raise TypeError("each buttons row must be a list.")
            for btn in row:
                if not isinstance(btn, dict):
                    raise TypeError("each button must be a dict.")
                if "label" not in btn:
                    raise ValueError("each button must include 'label'.")
                action = btn.get("action") or {}
                if not isinstance(action, dict):
                    raise TypeError("button 'action' must be a dict.")
                action.setdefault("type", "postback")
                # allow optional query params for url/web_app types (vendor-neutral)
                if "params" in action and not isinstance(action["params"], dict):
                    raise TypeError("action.params must be a dict if provided.")
                btn["action"] = action

        payload: Dict[str, Any] = {
            "text": text or "",
            "buttons": buttons,
        }

        hints = kwargs.pop("hints", None)
        if isinstance(hints, dict):
            payload["hints"] = hints

        super().__init__(content=payload, role=role, **kwargs)

    # Convenience accessors -------------------------------------------------
    @property
    def text(self) -> str:
        try:
            return (self.content or {}).get("text", "")  # type: ignore[union-attr]
        except Exception:
            return ""

    @property
    def buttons(self) -> List[List[Dict[str, Any]]]:
        try:
            return (self.content or {}).get("buttons", [])  # type: ignore[union-attr]
        except Exception:
            return []

    # Convenience constructors ---------------------------------------------
    @classmethod
    def web_app(
        cls,
        text: str,
        *,
        label: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        role: str = "assistant",
        **kwargs: Any,
    ) -> "ButtonThought":
        """
        Create a single-row, single-button WebApp launcher with optional query params.
        """
        btn = [[{"label": label, "action": {"type": "web_app", "url": url, **({"params": params} if params else {})}}]]
        return cls(text=text, buttons=btn, role=role, **kwargs)

    # ---------- Deserialization override ----------
    @classmethod
    def _from_dict_impl(cls, data: Dict[str, Any]) -> "ButtonThought":
        role: str = data.get("role", "assistant")

        payload = data.get("content")
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except Exception:
                payload = {"text": payload, "buttons": []}
        if not isinstance(payload, dict):
            payload = {}

        text: str = data.get("text", payload.get("text", ""))
        buttons: List[List[Dict[str, Any]]] = data.get("buttons", payload.get("buttons", []))
        hints: Optional[Dict[str, Any]] = data.get("hints", payload.get("hints"))

        meta: Dict[str, Any] = {
            k: v for k, v in data.items()
            if k not in ("content", "text", "buttons", "hints", "role")
        }
        if "id" in data:
            meta["id"] = data["id"]
        if "timestamp" in data:
            meta["timestamp"] = data["timestamp"]
        meta.setdefault("message_type", "application/vnd.nodeai.buttons+json")
        if hints is not None:
            meta["hints"] = hints

        return cls(text=text, buttons=buttons, role=role, **meta)
