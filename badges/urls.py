from django.urls import re_path

from badges import views

urlpatterns = [
    re_path(r'^$', views.overview, name="badges_overview"),
    re_path(r'^(?P<slug>[A-Za-z0-9_-]+)/$', views.detail, name="badge_detail"),
]