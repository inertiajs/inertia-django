from __future__ import annotations

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any, TypeVar

    T = TypeVar("T", bound=Any)


def deep_transform_callables(prop: T | Callable[[], T]) -> T:
    if not isinstance(prop, dict):
        return cast("T", prop() if callable(prop) else prop)

    for key in list(prop.keys()):
        prop[key] = deep_transform_callables(prop[key])

    return prop
