import datetime

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

User = settings.AUTH_USER_MODEL

# Create your models here.
class Banner(models.Model):
    text = models.CharField(max_length=64, null=True)
    banner_image = models.ImageField(upload_to='forum/banner_pictures', null=True, blank=True)
    enabled = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class Category(models.Model):
    category = models.CharField(max_length=64, blank=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.category

class Board(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    board = models.CharField(max_length=64, blank=False)
    info = models.CharField(max_length=264, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    board_slug = models.SlugField(unique=True, null=True)

    def __str__(self):
        return f"{self.category} -- {self.board}"

    def last_post(self):
        last_post = self.post_set.all().last()
        return last_post

class Topic(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    topic = models.CharField(max_length=64)
    started_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=False)
    date_created = models.DateTimeField(auto_now_add=True)
    posts = models.IntegerField(default=0)
    views = models.IntegerField(default=0)
    topic_slug = models.SlugField(unique=True, null=True)

    def __str__(self):
        return f"{self.category} -- {self.board.board} -- {self.topic}"

    def short_topic(self):
        if len(self.topic) < 20:
            return self.topic
        else:
            return f"{self.topic[:20]}..."

class Post(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    board = models.ForeignKey(Board, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    poster = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    image_upload = models.ImageField(upload_to='forum/post_pictures', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)
    topic_post = models.BooleanField(default=False, null=True)
    topic_post_number = models.IntegerField(default=0)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='+', null=True, blank=True)

    def __str__(self):
        return f"{self.poster} -- post pk: {self.id}"

    def children(self):
        return Post.objects.filter(parent=self).all()

    def modify_timestamp(self):
        now = timezone.now()
        minute_ahead = now + datetime.timedelta(minutes = 1)
        post_time = self.timestamp
        if now - post_time < minute_ahead - now:
            return 'Just now.'
        else:
            return self.timestamp

    def short_content(self):
        return f"{self.content[:20]}..."

    @property
    def is_parent(self):
        if self.parent is None:
            return True
        else:
            return False

    def serialize(self):
        return {
            'poster': self.poster.username,
            'poster_pk': self.poster.pk,
            'poster_tagline': self.poster.profile.tagline,
            'image': self.poster.profile.image.url,
            'post_count': self.poster.profile.post_count,
            'post_pk': self.pk,
            'original_post': self.parent.pk,
            'original_poster': self.parent.poster.username,
            'quote': self.parent.content,
            'board_slug': self.topic.board.board_slug,
            'topic': self.topic.topic,
            'content': self.content,
            'timestamp': self.timestamp
        }

