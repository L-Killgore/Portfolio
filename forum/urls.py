from django.urls import path

from . import views

app_name = 'forum'
urlpatterns = [
    path('', views.index, name='index'),
    path('comment/<int:post_pk>', views.comment, name='comment'),
    path('edit_profile>', views.edit_profile, name='edit_profile'),
    path('board/<str:board>', views.board, name='board'),
    path('topic/<str:board>/<str:topic>', views.topic, name='topic'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('profile/<str:username>', views.profile, name='profile'),
    path('register', views.register_view, name='register'),
    path('user_posts/<str:username>', views.user_posts, name='user_posts'),
    path('user_topics/<str:username>', views.user_topics, name='user_topics')
]