from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("review/", views.review, name="review"),
    path("stats/", views.stats, name="stats"),
    path("stat_user/", views.stat_user, name="stat_user"),
]