import datetime

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from forum.models import Post, Topic

class Profile(models.Model):
    class Gender(models.TextChoices):
        MALE = 'M', _('Male')
        FEMALE = 'F', _('Female')

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', null=True)
    banner = models.ImageField(default='banner-default.jpg', upload_to='network/banner_pictures', null=True, blank=True)
    display_name = models.CharField(max_length=64, null=True, blank=True)
    image = models.ImageField(default='default.jpg', upload_to='profile_pictures', null=True, blank=True)
    gender = models.CharField(max_length=3, choices=Gender.choices, default='M/F', blank=True)
    tagline = models.CharField(max_length=124, blank=True)
    birthday = models.DateField(_("Birthday"), default=datetime.date.today, null=True, blank=True)
    location = models.CharField(max_length=64, blank=True)
    post_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user}'s Profile"

    def get_age(self):
        today = datetime.date.today()
        return today.year - self.birthday.year - ((today.month, today.day) < (self.birthday.month, self.birthday.day))

    def get_gender(self):
        if self.gender == 'M':
            return 'Male'
        elif self.gender == 'F':
            return 'Female'
        else:
            return False

    def short_date_joined(self):
        return self.user.date_joined.strftime('%B %d, %Y')

    def get_modified_post_count(self):
        """
        A Topic can only be created if there is a first post. This first post does not count toward a user's post_count.
        The aggregate post_count can be found by calling Profile.post_count.
        This function gets the modified post_count.
        """
        topic_post_count = Post.objects.filter(poster=self.user.pk, topic_post=True).count()
        return self.post_count - topic_post_count

    def get_topic_count(self):
        return Topic.objects.filter(started_by=self.user.pk).count()

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, display_name=instance.username)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()