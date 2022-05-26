from django.contrib import admin

from .models import Follower, Like, NetworkPost

# Register your models here.
admin.site.register(Follower)
admin.site.register(Like)
admin.site.register(NetworkPost)