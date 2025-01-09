def deep_transform_callables(prop):
    if not isinstance(prop, dict):
        return prop() if callable(prop) else prop

    for key in list(prop.keys()):
        prop[key] = deep_transform_callables(prop[key])

    return prop


def validate_type(value, name, expected_type):
    if not isinstance(value, expected_type):
        raise TypeError(
            f"Expected {expected_type.__name__} for {name}, got {type(value).__name__}"
        )

    return value
