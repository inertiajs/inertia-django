from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from typing import Any


class CallableProp:
    """A lazily-resolved prop plus the protocol options it carries."""

    def __init__(
        self,
        prop: Any,
        *,
        once: bool = False,
        key: str | None = None,
        expires_at: datetime | timedelta | int | float | None = None,
        fresh: bool = False,
    ) -> None:
        self.prop = prop
        self._once = once
        self._once_key = key
        self._expires_at = expires_at
        self._fresh = fresh

    def __call__(self) -> Any:
        return self.prop() if callable(self.prop) else self.prop

    def should_resolve_once(self) -> bool:
        return self._once

    def once_key(self, path: str) -> str:
        return self._once_key or path

    def should_be_fresh(self) -> bool:
        return self._fresh

    def once_expires_at(self) -> int | None:
        value = self._expires_at
        if value is None:
            return None
        if isinstance(value, timedelta):
            value = datetime.now(timezone.utc) + value
        if isinstance(value, datetime):
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)
            return int(value.timestamp() * 1000)
        if isinstance(value, (int, float)):
            return int((datetime.now(timezone.utc).timestamp() + value) * 1000)
        raise TypeError(
            "expires_at must be a datetime, timedelta, or number of seconds"
        )


class MergeableProp(ABC):
    @abstractmethod
    def should_merge(self) -> bool:
        pass

    def should_deep_merge(self) -> bool:
        return False

    def merge_paths(self, root: str, prepend: bool = False) -> list[str]:
        return [] if prepend else [root]

    def match_on(self) -> list[str]:
        return []


class IgnoreOnFirstLoadProp:
    pass


class OptionalProp(CallableProp, IgnoreOnFirstLoadProp):
    pass


class AlwaysProp(CallableProp):
    """A prop that is included even when a partial reload excludes it."""


class OnceProp(CallableProp):
    def __init__(
        self,
        prop: Any,
        *,
        key: str | None = None,
        expires_at: datetime | timedelta | int | float | None = None,
        fresh: bool = False,
    ) -> None:
        super().__init__(prop, once=True, key=key, expires_at=expires_at, fresh=fresh)


class DeferredProp(CallableProp, MergeableProp, IgnoreOnFirstLoadProp):
    def __init__(
        self,
        prop: Any,
        group: str,
        merge: bool = False,
        *,
        deep_merge: bool = False,
        match_on: str | list[str] | None = None,
        once: bool = False,
        key: str | None = None,
        expires_at: datetime | timedelta | int | float | None = None,
        fresh: bool = False,
        rescue: bool = False,
    ) -> None:
        super().__init__(
            prop,
            once=once,
            key=key,
            expires_at=expires_at,
            fresh=fresh,
        )
        self.group = group
        self.merge = merge or deep_merge
        self.deep_merge = deep_merge
        self.rescue = rescue
        self._match_on = _as_list(match_on)

    def should_merge(self) -> bool:
        return self.merge

    def should_deep_merge(self) -> bool:
        return self.deep_merge

    def match_on(self) -> list[str]:
        return self._match_on


class MergeProp(CallableProp, MergeableProp):
    def __init__(
        self,
        prop: Any,
        *,
        append: bool | str | list[str] = True,
        prepend: bool | str | list[str] = False,
        deep_merge: bool = False,
        match_on: str | list[str] | None = None,
        once: bool = False,
        key: str | None = None,
        expires_at: datetime | timedelta | int | float | None = None,
        fresh: bool = False,
    ) -> None:
        super().__init__(
            prop,
            once=once,
            key=key,
            expires_at=expires_at,
            fresh=fresh,
        )
        if deep_merge and (append is not True or prepend is not False):
            raise ValueError("deep_merge cannot be combined with append or prepend")
        if append is not False and prepend is not False:
            raise ValueError("append and prepend cannot both be configured")
        self.append = append
        self.prepend = prepend
        self.deep_merge = deep_merge
        self._match_on = _as_list(match_on)

    def should_merge(self) -> bool:
        return True

    def should_deep_merge(self) -> bool:
        return self.deep_merge

    def merge_paths(self, root: str, prepend: bool = False) -> list[str]:
        configured = self.prepend if prepend else self.append
        if configured is True:
            return [root]
        if configured is False:
            return []
        return [f"{root}.{path}" for path in _as_list(configured)]

    def match_on(self) -> list[str]:
        return self._match_on


class ScrollProp(MergeProp):
    def __init__(
        self,
        prop: Any,
        metadata: dict[str, Any],
        *,
        wrapper: str | None = None,
        defer: bool = False,
        group: str = "default",
    ) -> None:
        super().__init__(prop, append=True)
        self.metadata = metadata
        self.wrapper = wrapper
        self.defer = defer
        self.group = group

    def merge_paths(self, root: str, prepend: bool = False) -> list[str]:
        if prepend:
            return []
        path = f"{root}.{self.wrapper}" if self.wrapper else root
        return [path]


def _as_list(value: str | list[str] | bool | None) -> list[str]:
    if value is None or isinstance(value, bool):
        return []
    return [value] if isinstance(value, str) else value
