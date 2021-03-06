# Generated by Django 3.2.9 on 2021-11-08 04:11

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('banner', models.ImageField(blank=True, default='banner-default.jpg', null=True, upload_to='network/banner_pictures')),
                ('display_name', models.CharField(blank=True, max_length=64, null=True)),
                ('image', models.ImageField(blank=True, default='default.jpg', null=True, upload_to='profile_pictures')),
                ('gender', models.CharField(blank=True, choices=[('M', 'Male'), ('F', 'Female')], default='M/F', max_length=3)),
                ('tagline', models.CharField(blank=True, max_length=124)),
                ('birthday', models.DateField(blank=True, default=datetime.date.today, null=True, verbose_name='Birthday')),
                ('location', models.CharField(blank=True, max_length=64)),
                ('post_count', models.IntegerField(default=0)),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
