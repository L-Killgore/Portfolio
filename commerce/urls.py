from django.contrib.auth import views as auth_views
from django.urls import include, path

from .views import *

app_name='commerce'
urlpatterns = [
    path("", index, name="index"),
    # path("accounts", include('django.contrib.auth.urls')),
    # path("accounts/login", auth_views.LoginView.as_view(template_name="commerce/login.html")),
    path("categories", categories, name="categories"),
    path("category/<str:category_name>", category, name="category"),
    path("create_listing", create_listing, name="create_listing"),
    path("listing/<int:listing_id>", listing, name="listing"),
    path("login", login_view, name="login"),
    path("logout", logout_view, name="logout"),
    path("register", register_view, name="register"),
    path("watchlist", watchlist, name="watchlist")
]
