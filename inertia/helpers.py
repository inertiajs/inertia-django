from typing import Any


def deep_transform_callables(prop: Any) -> Any:
    if not isinstance(prop, dict):
        return prop() if callable(prop) else prop

    for key in list(prop.keys()):
        prop[key] = deep_transform_callables(prop[key])

    return prop
