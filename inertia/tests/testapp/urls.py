from django.urls import path
from . import views

urlpatterns = [
  path('test/', views.test),
  path('empty/', views.empty_test),
  path('redirect/', views.redirect_test),
  path('props/', views.props_test),
  path('template_data/', views.template_data_test),
  path('lazy/', views.lazy_test),
  path('complex-props/', views.complex_props_test),
  path('share/', views.share_test),
  path('inertia-redirect/', views.inertia_redirect_test),
]