import base64
import json
import time
import uuid
from importlib import import_module
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type
from pydantic import BaseModel

import requests

def jsonable(x: Any) -> Any:
    """Recursively convert objects to JSON-friendly representations."""
    if isinstance(x, BaseModel):
        return {
            "__pydantic__": f"{x.__class__.__module__}.{x.__class__.__name__}",
            "data": x.model_dump(mode="json"),
        }
    if isinstance(x, (list, tuple, set)):
        return [jsonable(i) for i in x]
    if isinstance(x, dict):
        return {k: jsonable(v) for k, v in x.items()}
    if isinstance(x, bytes):
        return x.decode("utf-8")
    return x

EMBED_DIM_DEFAULT = 3072

if TYPE_CHECKING:
    from learn.thought.serialization import (  # noqa: F401
        to_gemini,
        to_openai,
    )


def _restore_pydantic(obj: Any) -> Any:
    if isinstance(obj, dict) and "__pydantic__" in obj:
        mod, cls = obj["__pydantic__"].rsplit(".", 1)
        Model = getattr(import_module(mod), cls)
        return Model.model_validate(obj["data"])
    if isinstance(obj, list):
        return [_restore_pydantic(i) for i in obj]
    if isinstance(obj, dict):
        return {k: _restore_pydantic(v) for k, v in obj.items()}
    return obj


class IThought:
    """
    Fundamental message container used for all conversation pieces.
    Other thought classes inherit from it and register MIME types via register_message_type.
    This unified structure lets Node AI brains and tools pass messages consistently.
    """

    _registry: Dict[str, Type["IThought"]] = {}
    _instances: Dict[str, "IThought"] = {}

    def __init__(self, content: Optional[str] = None, role: str = "user", **kwargs):
        """
        :param content: The textual or raw content of this message.
        :param role: The role of the message (e.g., 'user', 'assistant', etc.).
        :param kwargs: Arbitrary metadata stored in self.metadata.
        """
        self.metadata: Dict[str, Any] = {}
        self.metadata["content"] = content
        self.metadata["role"] = role
        if self.metadata.get("id") is None:
            self.metadata["id"] = str(uuid.uuid4())
        if self.metadata.get("timestamp") is None:
            self.metadata["timestamp"] = time.time_ns()
        if "timestamp" not in kwargs:
            kwargs["timestamp"] = time.time_ns()
        if "message_type" not in kwargs:
            kwargs["message_type"] = next(
                (
                    key
                    for key, cls in IThought._registry.items()
                    if isinstance(self, cls)
                ),
                "base",
            )
        for k, v in kwargs.items():
            self.metadata[k] = v
        IThought._instances[self.id] = self

    @property
    def id(self) -> str:
        return self.metadata["id"]

    @property
    def content(self) -> str:
        return self.metadata["content"]

    @property
    def role(self) -> str:
        return self.metadata["role"]

    @property
    def timestamp(self) -> int:
        return self.metadata["timestamp"]

    @property
    def timestamp_iso(self) -> str:
        """
        Return a human-readable ISO-like timestamp string for convenience.
        """
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.timestamp / 1e9))

    @property
    def message_type(self) -> str:
        return self.metadata["message_type"]

    @property
    def file_type(self) -> str:
        """
        Attempt to parse the MIME type and return the subtype if possible.
        If parsing fails, return the entire MIME type.
        """
        try:
            return self.mime_type.split("/")[1]
        except:
            return self.mime_type

    @property
    def mime_type(self) -> str:
        """
        Return the message's MIME type, stored in metadata under 'message_type'.
        """
        return self.metadata["message_type"]

    @property
    def save_in_memory(self) -> bool:
        """
        A boolean that can indicate whether or not this message should be
        persisted in memory. Defaults to True if not set.
        """
        return self.metadata.get("save_in_memory", True)

    @property
    def role_gemini(self) -> str:
        """
        Convert the 'role' to something suitable for Gemini usage:
          - assistant => model
          - developer => user
          - else => same as self.role
        """
        r = self.role
        if r == "assistant":
            return "model"
        elif r == "developer":
            return "user"
        return r

    @staticmethod
    def get_thought_by_id(id: str) -> Optional["IThought"]:
        """
        Return a previously created IThought instance by its id, if it exists in memory.
        """
        return IThought._instances.get(id)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Helper for retrieving a metadata value by key, with an optional default.
        """
        return self.metadata.get(key, default)

    def _set(self, key: str, val: Any) -> None:
        """
        Internal method to set a key in metadata.
        """
        self.metadata[key] = val

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert metadata to a dict that can be stored or serialized.
        """
        meta = jsonable(self.metadata.copy())
        return meta

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IThought":
        """
        Create a IThought or subclass from the given dictionary data.
        Chooses the subclass based on 'message_type' if registered.
        """
        if isinstance(data, str):
            data = json.loads(data)
        mtype = data.get("message_type", "application/json")
        SubCls = cls._registry.get(mtype, cls)
        return SubCls._from_dict_impl(data)

    @classmethod
    def from_dicts(cls, data: List[Dict[str, Any]]) -> List["IThought"]:
        """
        Bulk conversion: create a list of messages from a list of dicts.
        Silently skip any dict that fails to parse.
        """
        out = []
        for d in data:
            try:
                msg = cls.from_dict(d)
                if msg:
                    out.append(msg)
            except:
                pass
        return out

    @staticmethod
    def thought_type(msg_type: str):
        """
        Decorator to register a subclass of IThought for a particular MIME type.

        Usage:
          @IThought.thought_type("mime/type")
          class MyMsg(IThought):
              ...
        """

        def decorator(subclass: Type["IThought"]):
            IThought._registry[msg_type] = subclass
            return subclass

        return decorator

    def to_openai_thought(self) -> List[Dict[str, Any]]:
        """Serialize this thought into one or more OpenAI chat messages."""
        from learn.thought.serialization import to_openai

        return to_openai(self)

    @classmethod
    def _from_dict_impl(cls, data: Dict[str, Any]) -> "IThought":
        """
        Subclasses can override for custom instantiation if needed.
        By default, pass all keys as kwargs to the constructor.
        """
        data = _restore_pydantic(data)
        return cls(**data)

    def __str__(self) -> str:
        return json.dumps(self.metadata, indent=2)

    def __repr__(self) -> str:
        return json.dumps(self.metadata, indent=2)

    def set_previous_thought(self, thought: "IThought") -> None:
        """
        Link this message's previous_message_id to the given message's id.
        """
        if thought:
            self._set("previous_message_id", thought.id)

    def set_next_thought(self, thought: "IThought") -> None:
        """
        Link this message's next_message_id to the given message's id.
        """
        if thought:
            self._set("next_message_id", thought.id)
