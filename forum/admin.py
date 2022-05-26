from django.contrib import admin

from .models import Banner, Board, Category, Post, Topic

# Register your models here.
admin.site.register(Banner)
admin.site.register(Board)
admin.site.register(Category)
admin.site.register(Post)
admin.site.register(Topic)