from django.urls import path

from . import views

urlpatterns = [
    path("test/", views.test),
    path("empty/", views.empty_test),
    path("redirect/", views.redirect_test),
    path("props/", views.props_test),
    path("template_data/", views.template_data_test),
    path("lazy/", views.lazy_test),
    path("optional/", views.optional_test),
    path("defer/", views.defer_test),
    path("defer-group/", views.defer_group_test),
    path("merge/", views.merge_test),
    path("complex-props/", views.complex_props_test),
    path("share/", views.share_test),  # type: ignore[arg-type]
    path("inertia-redirect/", views.inertia_redirect_test),
    path("external-redirect/", views.external_redirect_test),
    path("encrypt-history/", views.encrypt_history_test),
    path("no-encrypt-history/", views.encrypt_history_false_test),
    path("encrypt-history-type-error/", views.encrypt_history_type_error_test),
    path("clear-history/", views.clear_history_test),
    path("clear-history-redirect/", views.clear_history_redirect_test),
    path("clear-history-type-error/", views.clear_history_type_error_test),
    # Once props (Inertia v3)
    path("once/", views.once_test),
    path("once-shared/", views.once_shared_test),
    path("once-fresh/", views.once_fresh_test),
    # preserveFragment (Inertia v3)
    path("preserve-fragment/", views.preserve_fragment_page_test),
    path("preserve-fragment-redirect/", views.preserve_fragment_redirect_test),
    path("preserve-fragment-type-error/", views.preserve_fragment_type_error_test),
    # preserveErrors / shared errors (Inertia v3)
    path("preserve-errors/", views.preserve_errors_test),  # type: ignore[arg-type]
    # Infinite scroll merge intent (Inertia v3)
    path("infinite-scroll/", views.infinite_scroll_test),
]
