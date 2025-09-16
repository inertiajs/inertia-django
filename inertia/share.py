from typing import Any

from django.http import HttpRequest

__all__ = ["share"]


class InertiaShare:
    def __init__(self) -> None:
        self.props: dict[str, Any] = {}

    def set(self, **kwargs: Any) -> None:
        self.props = {
            **self.props,
            **kwargs,
        }

    def all(self) -> dict[str, Any]:
        return self.props


def share(request: HttpRequest, **kwargs: Any) -> None:
    if not hasattr(request, "inertia"):
        request.inertia = InertiaShare()  # type: ignore[attr-defined]

    request.inertia.set(**kwargs)  # type: ignore[attr-defined]
