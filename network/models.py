from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


User = settings.AUTH_USER_MODEL

class NetworkPost(models.Model):
    poster = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    content = models.CharField(max_length=280, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)
    likes = models.IntegerField(default=0, null=True)

    def __str__(self):
        return f"{self.poster} - post id {self.id}"

class Like(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    liked_posts = models.ManyToManyField(NetworkPost, blank=True)

    def __str__(self):
        return f"Posts that {self.user} likes"

class Follower(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    followed_users = models.ManyToManyField(User, related_name='followed_users', blank=True)

    def __str__(self):
        return f"Users that {self.user} follows"