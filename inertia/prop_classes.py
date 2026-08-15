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


class OnceProp(CallableProp):
    """
    A prop that is resolved on the first visit and remembered by the client.

    On subsequent visits the server skips resolving it when the client lists
    its key in the X-Inertia-Except-Once-Props request header, unless the
    prop was created with fresh=True, which forces re-resolution on every
    request.
    """

    def __init__(self, prop: Any, fresh: bool = False) -> None:
        super().__init__(prop)
        self._fresh = fresh

    def should_be_fresh(self) -> bool:
        return self._fresh


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
