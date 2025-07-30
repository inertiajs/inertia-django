from abc import ABC, abstractmethod
from typing import Any


class CallableProp:
    def __init__(self, prop: Any) -> None:
        self.prop = prop

    def __call__(self) -> Any:
        return self.prop() if callable(self.prop) else self.prop


class MergeableProp(ABC):
    @abstractmethod
    def should_merge(self) -> bool:
        pass


class IgnoreOnFirstLoadProp:
    pass


class OptionalProp(CallableProp, IgnoreOnFirstLoadProp):
    pass


class DeferredProp(CallableProp, MergeableProp, IgnoreOnFirstLoadProp):
    def __init__(self, prop: Any, group: str, merge: bool = False) -> None:
        super().__init__(prop)
        self.group = group
        self.merge = merge

    def should_merge(self) -> bool:
        return self.merge


class MergeProp(CallableProp, MergeableProp):
    def should_merge(self) -> bool:
        return True
