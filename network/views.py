import json
import operator
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator


from .models import Follower, Like, NetworkPost
from .forms import CreateUserForm, EditProfileForm

User = get_user_model()


def index(request):
    # pagination
    paginator = Paginator(NetworkPost.objects.all().order_by('-timestamp'), 10)
    page_number = request.GET.get('page', 1)
    posts = paginator.get_page(page_number)

    # determine if posts are liked by the user or not
    if request.user.is_authenticated:
        try:
            users_likes = Like.objects.get(user=request.user)
            liked_posts = users_likes.liked_posts.all()
        except:
            liked_posts = []
    else:
        liked_posts = []

    if request.method == "POST":
        post = NetworkPost()
        post.poster = request.user
        post.content = request.POST['post_content']
        post.save()

        return HttpResponseRedirect(reverse('network:index'))

    return render(request, "network/index.html", {
        'paginator': paginator,
        'page_number': int(page_number),
        'posts': posts,
        'liked_posts': liked_posts,
    })

@login_required
def edit(request):
    data = json.loads(request.body)
    original_post = data.get('original_post', '')
    edited_post = data.get('edited_post','')

    original_post_object = NetworkPost.objects.get(content=original_post)
    original_post_object.content = edited_post
    original_post_object.save()

    return HttpResponseRedirect(reverse('network:profile', kwargs={'username': request.user}))

@login_required
def edit_profile(request):
    profile = request.user.profile
    form = EditProfileForm(instance=profile)

    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
        return HttpResponseRedirect(reverse('network:profile', kwargs={'username': request.user}))
    return render(request, 'network/edit_profile.html', {
        'form': form
    })
        


def follow(request, followed_user):
    # Required objects
    current_user = User.objects.get(username=request.user)
    followed_user_id = User.objects.get(username=followed_user)
    try:
        followed_users = Follower.objects.get(user=current_user)
    except:
        followed_users = Follower.objects.create(user=current_user)

    # Follow a user
    if followed_user_id in followed_users.followed_users.all():
        followed_users.followed_users.remove(followed_user_id.id)
        followed_users.save()
        return JsonResponse(False, safe=False)
    # Unfollow a user
    else:
        followed_users.followed_users.add(followed_user_id.id)
        followed_users.save()
        return JsonResponse(True, safe=False)


def following(request):
    # required model objects
    current_user = User.objects.get(username=request.user)

    try:
        follower = Follower.objects.get(user=current_user)
        followed_users = follower.followed_users.all()
    except:
        followed_users = []

    # generate list of all posts by all followed users
    posts_list = []
    for followed_user in followed_users:
        for obj in NetworkPost.objects.filter(poster=followed_user):
            posts_list.append(obj)
    sorted_list = sorted(posts_list, key=operator.attrgetter('timestamp'), reverse=True)

    # pagination
    paginator = Paginator(sorted_list, 10)
    page_number = request.GET.get('page', 1)
    posts = paginator.get_page(page_number)

    # determine if posts are liked by the user or not
    if request.user.is_authenticated:
        try:
            users_likes = Like.objects.get(user=request.user)
            liked_posts = users_likes.liked_posts.all()
        except:
            liked_posts = []

    return render(request, "network/following.html", {
        'paginator': paginator,
        'page_number': int(page_number),
        'posts': posts,
        'followed_users': followed_users,
        'liked_posts': liked_posts
    })


def like(request, post):
    # Required objects
    current_user = User.objects.get(username=request.user)
    try:
        user_likes = Like.objects.get(user=current_user)
    except:
        user_likes = Like.objects.create(user=current_user)
    liked_post_id = NetworkPost.objects.get(id=post)

    # Like a post
    if liked_post_id in user_likes.liked_posts.all():
        user_likes.liked_posts.remove(liked_post_id)
        user_likes.save()
        liked_post_id.likes -= 1
        liked_post_id.save()
        return JsonResponse(False, safe=False)
    # Unlike a post
    else:
        user_likes.liked_posts.add(liked_post_id)
        user_likes.save()
        liked_post_id.likes += 1
        liked_post_id.save()
        return JsonResponse(True, safe=False)


def profile(request, username):
    # required model objects
    profile_user = User.objects.get(username=username)
    followers = Follower.objects.all()
    post_number = NetworkPost.objects.filter(poster=profile_user).count()

    # paginator
    paginator = Paginator(NetworkPost.objects.filter(poster=profile_user).order_by('-timestamp'), 10)
    page_number = request.GET.get('page', 1)
    posts = paginator.get_page(page_number)

    # get the number of users followed by profile_user
    try:
        follower = Follower.objects.get(user=profile_user)
        followed_users = follower.followed_users.count()
    except:
        followed_users = 0

    # get the number of users that follow profile_user
    followed_by_count = 0
    for follower in followers:
        for f in follower.followed_users.all():
            if f == profile_user:
                followed_by_count += 1

    # determine if request.user is following profile_user
    following = False
    if request.user.is_authenticated:
        try:
            request_user_following = Follower.objects.get(user=request.user)
            if profile_user in request_user_following.followed_users.all():
                following = True
        except:
            following = False

    # determine if posts are liked by the user or not
    if request.user.is_authenticated:
        try:
            users_likes = Like.objects.get(user=request.user)
            liked_posts = users_likes.liked_posts.all()
        except:
            liked_posts = []
    else:
        liked_posts = []
    

    return render(request, "network/profile.html", {
        'paginator': paginator,
        'page_number': int(page_number),
        'posts': posts,
        'profile_user': profile_user,
        'followed_users': followed_users,
        'followed_by_count': followed_by_count,
        'following': following,
        'liked_posts': liked_posts,
        'post_number': post_number
    })    


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("network:index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("network:index"))


def register_view(request):
    form = CreateUserForm(request.POST or None)
    if form.is_valid():
        user = form.save()

        if user != None:
            login(request, user)
            return redirect('network:index')
        else:
            return render(request, 'network/register.html', {
                'message': 'Could not register this account. Please try again.'
            })

    return render(request, 'network/register.html', {
        'form': form
    })