import datetime
import json
import re

from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt

from .forms import CreateUserForm, EditProfileForm, LoginForm, NewPostForm, NewTopicForm
from .models import Banner, Board, Category, Post, Topic

User = get_user_model()
try:
    banner = get_object_or_404(Banner, enabled=True)
except:
    banner = "ERROR: Add a banner in the admin panel."

# FORUM POST RELATED
def index(request):
    categories = Category.objects.all()
    today = datetime.datetime.today()

    if Topic.objects.all():
        topic_count = Topic.objects.all().count()
    else:
        topic_count = 0
    if Post.objects.all():
        post_count = Post.objects.all().count()
        most_recent_post = Post.objects.all().order_by('timestamp').last()
    else:
        post_count = 0
        most_recent_post = 'Nothing has been posted.'

    user_count = User.objects.all().count()
    most_recent_user = User.objects.all().order_by('date_joined').last()

    return render(request, 'forum/index.html', {
        'banner': banner,
        'categories': categories,
        'today': today.date(),
        'topic_count': topic_count,
        'post_count': post_count,
        'user_count': user_count,
        'most_recent_user': most_recent_user,
        'most_recent_post': most_recent_post
    })

def board(request, board):
    board = get_object_or_404(Board, board_slug=board)
    today = datetime.datetime.today()
    if request.method == 'POST':
        user = User.objects.get(username=request.user)
        form = NewTopicForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            new_topic_post = form.save(commit=False)
            new_topic = form.cleaned_data['new_topic']
            
            new_topic_obj = Topic()
            new_topic_obj.posts = 1
            new_topic_obj.started_by = request.user
            new_topic_obj.topic = new_topic
            new_topic_obj.board = board
            new_topic_obj.category = board.category
            new_topic_obj.topic_slug = slugify(new_topic)
            new_topic_obj.save()

            new_topic_post.poster = request.user
            new_topic_post.topic = new_topic_obj
            new_topic_post.board = board
            new_topic_post.category = board.category
            new_topic_post.topic_post = True
            new_topic_post.save()

            user.profile.post_count += 1
            user.save()

            return HttpResponseRedirect(reverse('forum:board', args=(board.board_slug,)))
    else:
        form = NewTopicForm()
    return render(request, 'forum/board.html', {
        'banner': banner,
        'board': board,
        'form': form,
        'today': today.date()
    })

def comment(request, post_pk):
    post = Post.objects.get(pk=post_pk)
    topic = post.topic
    user = request.user.profile

    form = NewPostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        new_comment = form.save(commit=False)

        new_comment.category = post.category
        new_comment.board = post.board
        new_comment.topic = post.topic
        new_comment.poster = request.user
        new_comment.parent = post
        new_comment.topic_post_number = topic.posts
        new_comment.save()

        topic.posts += 1
        topic.save()

        user.post_count += 1
        user.save()

        return HttpResponseRedirect(reverse('forum:topic', args=(topic.board.board_slug, topic.topic_slug,)))

    return render(request, 'forum/topic.html', {
        'form': form,
        'topic': topic
    })

def topic(request, board, topic):
    topic = Topic.objects.get(topic_slug=topic)
    paginator = Paginator(topic.post_set.all().order_by('timestamp'), 20)
    page_number = request.GET.get('page', 1)
    page_range = paginator.get_elided_page_range(number=page_number)
    posts = paginator.get_page(page_number)
    user = request.user

    topic.views += 1
    topic.save()

    form = NewPostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        new_post = form.save(commit=False)
        
        new_post.category = topic.category
        new_post.board = topic.board
        new_post.topic = topic
        new_post.poster = request.user
        new_post.topic_post_number = topic.posts
        new_post.save()

        topic.posts += 1
        topic.save()
        
        user.profile.post_count += 1
        user.save()

        return HttpResponseRedirect(reverse('forum:topic', args=(topic.board.board_slug, topic.topic_slug,)))

    return render(request, 'forum/topic.html', {
        'banner': banner,
        'form': form,
        'topic': topic,
        'paginator': paginator,
        'page_number': int(page_number),
        'page_range': page_range,
        'posts': posts
    })


# PROFILE RELATED
@login_required
def edit_profile(request):
    profile = request.user.profile
    form = EditProfileForm(instance=profile)

    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
        return HttpResponseRedirect(reverse('forum:profile', args=(profile.user,)))
    return render(request, 'forum/edit_profile.html', {
        'banner': banner,
        'form': form
    })

def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    return render(request, 'forum/profile.html', {
        'banner': banner,
        'profile_user': profile_user
    })

def user_posts(request, username):
    user = User.objects.get(username=username)
    paginator = Paginator(user.post_set.filter(topic_post=False).order_by('-timestamp'), 20)
    page_number = request.GET.get('page', 1)
    page_range = paginator.get_elided_page_range(number=page_number)
    posts = paginator.get_page(page_number)

    return render(request, 'forum/user_posts.html', {
        'banner': banner,
        'paginator': paginator,
        'page_number': int(page_number),
        'page_range': page_range,
        'posts': posts,
        'user': user
    })

def user_topics(request, username):
    user = User.objects.get(username=username)
    paginator = Paginator(user.topic_set.all().order_by('-date_created'), 20)
    page_number = request.GET.get('page', 1)
    page_range = paginator.get_elided_page_range(number=page_number)
    topics = paginator.get_page(page_number)
    topic_count = Topic.objects.filter(started_by=user.pk).count()

    return render(request, 'forum/user_topics.html', {
        'banner': banner,
        'paginator': paginator,
        'page_number': int(page_number),
        'page_range': page_range,
        'topic_count': topic_count,
        'topics': topics,
        'user': user
    })

# USER CREATION AND LOGIN
def login_view(request):
    form = LoginForm(request.POST or None)
    if form.is_valid():
        # Attempt to sign user in
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user != None:
            login(request, user)
            return redirect('forum:index')
        else:
            return render(request, 'forum/login.html', {
                'message': 'Invalid username and/or password.'
            })

    return render(request, 'forum/login.html', {
        'banner': banner,
        'form': form
    })

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('forum:index'))

def register_view(request):
    form = CreateUserForm(request.POST or None)
    if form.is_valid():
        user = form.save()

        if user != None:
            login(request, user)
            return redirect('forum:index')
        else:
            return render(request, 'forum/register.html', {
                'message': 'Could not register this account. Please try again.'
            })

    return render(request, 'forum/register.html', {
        'banner': banner,
        'form': form
    })