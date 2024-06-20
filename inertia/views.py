from typing import Optional

from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic.list import MultipleObjectMixin
from inertia import render


class InertiaListView(MultipleObjectMixin, View):
    """
    Render some list of objects, set by `self.model` or `self.queryset`.
    `self.queryset` can actually be any iterable of items, not just a queryset.
    The Inertia.js component name to render to is set by `self.component_name`.
    """

    component_name: Optional[str] = None
    fields: Optional[list[str]] = None

    def get_object_dict(self, obj):
        if self.fields is None:
            raise ImproperlyConfigured(
                f"Using InertiaListView (base class of {self.__class__.__name__}) without "
                "the 'fields' attribute is prohibited."
            )

        return {field: getattr(obj, field) for field in self.fields}

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)

        queryset = object_list if object_list is not None else self.object_list
        context_object_name = self.get_context_object_name(queryset)

        # drop unserializable view object
        context.pop("view")

        object_list = [self.get_object_dict(obj) for obj in queryset]
        context["object_list"] = object_list

        if context_object_name is not None:
            context[context_object_name] = object_list

        return context

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()

        if not allow_empty:
            # When pagination is enabled and object_list is a queryset,
            # it's better to do a cheap query than to load the unpaginated
            # queryset in memory.
            if self.get_paginate_by(self.object_list) is not None and hasattr(
                self.object_list, "exists"
            ):
                is_empty = not self.object_list.exists()
            else:
                is_empty = not self.object_list
            if is_empty:
                raise Http404(
                    _("Empty list and “%(class_name)s.allow_empty” is False.")
                    % {
                        "class_name": self.__class__.__name__,
                    }
                )
        context = self.get_context_data()

        return render(
            request,
            self.component_name,
            props=context,
        )
