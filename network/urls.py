
from django.urls import path

from . import views

app_name='network'
urlpatterns = [
    path("", views.index, name="index"),
    path("edit_profile", views.edit_profile, name="edit_profile"),
    path("following", views.following, name="following"),
    path("profile/<str:username>", views.profile, name="profile"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register_view, name="register"),

    #API route
    path("edit", views.edit, name="edit"),
    path("follow/<str:followed_user>", views.follow, name="follow"),
    path("like/<int:post>", views.like, name="like")
]
