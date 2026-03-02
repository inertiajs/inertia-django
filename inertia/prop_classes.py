from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Generic, TypeVar, cast

if TYPE_CHECKING:
    from collections.abc import Callable


T = TypeVar("T", bound=Any)


class CallableProp(Generic[T]):
    def __init__(self, prop: T | Callable[[], T]) -> None:
        self.prop = prop

    def __call__(self) -> T:
        return cast(T, self.prop() if callable(self.prop) else self.prop)


class MergeableProp(ABC):
    @abstractmethod
    def should_merge(self) -> bool:
        pass


class IgnoreOnFirstLoadProp:
    pass


class OptionalProp(CallableProp[T], IgnoreOnFirstLoadProp):
    pass


class DeferredProp(CallableProp[T], MergeableProp, IgnoreOnFirstLoadProp):
    def __init__(self, prop: T | Callable[[], T], group: str, merge: bool = False) -> None:
        super().__init__(prop)
        self.group = group
        self.merge = merge

    def should_merge(self) -> bool:
        return self.merge


class MergeProp(CallableProp[T], MergeableProp):
    def should_merge(self) -> bool:
        return True
