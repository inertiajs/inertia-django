from abc import ABC, abstractmethod


class CallableProp:
    def __init__(self, prop):
        self.prop = prop

    def __call__(self):
        return self.prop() if callable(self.prop) else self.prop


class MergeableProp(ABC):
    @abstractmethod
    def should_merge(self):
        pass


class IgnoreOnFirstLoadProp:
    pass


class OptionalProp(CallableProp, IgnoreOnFirstLoadProp):
    pass


class DeferredProp(CallableProp, MergeableProp, IgnoreOnFirstLoadProp):
    def __init__(self, prop, group, merge=False):
        super().__init__(prop)
        self.group = group
        self.merge = merge

    def should_merge(self):
        return self.merge


class MergeProp(CallableProp, MergeableProp):
    def should_merge(self):
        return True
