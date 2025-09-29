"""DeferredThought – lazily-resolved IThought."""

from __future__ import annotations

import asyncio
import inspect
import threading
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Callable, Coroutine, Optional, TypeAlias, Dict, Any

from learn.thought.ithought import IThought

Resolver: TypeAlias = (
    Callable[[], IThought] | Callable[[], Coroutine[None, None, IThought]]
)


@IThought.thought_type("deferred/base")
class DeferredThought(IThought):
    """Placeholder that resolves to another IThought on first access."""

    _executor: ThreadPoolExecutor = ThreadPoolExecutor(
        max_workers=8, thread_name_prefix="deferred"
    )

    def __init__(
        self,
        resolver: Resolver,
        *,
        expected_mime: str = "plain/txt",
        role: str = "assistant",
        **meta,
    ) -> None:
        super().__init__(
            content=None,
            role=role,
            save_in_memory=False,
            message_type=f"deferred/{expected_mime}",
            **meta,
        )
        self._resolver: Resolver = resolver
        self._expected_mime: str = expected_mime
        self._result: Optional[IThought] = None
        self._lock = threading.Lock()
        self._future: Future = self._schedule_eager()

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------
    @property
    def is_resolved(self) -> bool:
        return self._result is not None

    def resolve_now(self) -> IThought:
        if not self.is_resolved:
            self._run_resolver()
        return self._result  # type: ignore[return-value]

    # ------------------------------------------------------------------
    # IThought overrides
    # ------------------------------------------------------------------
    @property
    def content(self):
        return self.resolve_now().content

    @property
    def mime_type(self):
        return self.resolve_now().mime_type if self.is_resolved else self._expected_mime

    @property
    def save_in_memory(self) -> bool:  # noqa: D401
        return self.is_resolved

    # ------------------------------------------------------------------
    # internals
    # ------------------------------------------------------------------
    def _run_resolver(self) -> None:
        with self._lock:
            if self._result is not None:
                return

            res = self._future.result()
            if not isinstance(res, IThought):
                if isinstance(res, list):
                    raise TypeError(
                        "DeferredThought expected a single IThought but the resolver "
                        f"returned a list of length {len(res)}. "
                        "Mark this brain with __defer_think__ = False."
                    )
                raise TypeError("Resolver must return an IThought")

            res._set("previous_message_id", self.get("previous_message_id"))
            res._set("next_message_id", self.get("next_message_id"))

            self._result = res
            IThought._instances[self.id] = res

    # ------------------------------------------------------------------
    # scheduling helpers
    # ------------------------------------------------------------------
    def _schedule_eager(self) -> Future:
        ex = self.__class__._executor

        def _wrapper():
            func = self._resolver
            if inspect.iscoroutinefunction(func):
                return asyncio.run(func())
            return func()

        return ex.submit(_wrapper)

    def done(self):
        return self._future.done()

    def cancel(self):
        return self._future.cancel()

    def to_dict(self) -> Dict[str, Any]:
        """
        Resolve‑then‑serialise.

        Storage.save_new_thoughts() ultimately calls thought.to_dict(); if this
        object is still deferred we first run the resolver, then delegate the
        actual serialisation to the resolved IThought.  We still keep our own
        ID/timestamp so linkage is preserved.
        """
        resolved = self.resolve_now()      # forces resolver once
        meta = resolved.to_dict()          # serialise the *real* thought
        # Re‑stamp with our original identifiers so any chains stay intact.
        meta["id"]        = self.id
        meta["timestamp"] = self.timestamp
        meta["message_type"] = resolved.message_type
        return meta

    def __getstate__(self):
        # Ensure the resolver has run so _result is populated
        self.resolve_now()

        state = self.__dict__.copy()
        state.pop("_lock",    None)      # remove un‑pickleable lock
        state.pop("_future",  None)      # remove Future (contains RLock)
        state.pop("_resolver", None)     # no longer needed after resolve
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

        # recreate lock
        import threading
        self._lock = threading.Lock()

        # recreate a dummy future that is already done
        fut: Future = Future()
        fut.set_result(self._result)          # _result was saved in state
        self._future = fut
