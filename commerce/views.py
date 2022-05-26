from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib import messages

from .forms import CreateUserForm
from .models import AuctionListing, Bid, Comment, Watchlist
from main.models import Profile

User = get_user_model()
CATEGORIES = AuctionListing.Categories
CONDITIONS = AuctionListing.Conditions

def index(request):
    listings = AuctionListing.objects.all().order_by('-timestamp')
    return render(request, "commerce/index.html", {
        "listings": listings
    })


def category(request, category_name):
    listings_by_category = AuctionListing.objects.filter(category=category_name)

    # Get category label
    for cat in CATEGORIES:
        if cat == category_name:
            category = cat.label

    return render(request, "commerce/category.html", {
        "listings_by_category": listings_by_category,
        "category": category
    })


def categories(request):
    return render(request, "commerce/categories.html", {
        "categories": CATEGORIES
    })


@login_required(login_url="commerce:login")
def create_listing(request):
    if request.method == "POST":
        listing = AuctionListing()
        listing.active = True
        listing.user = User.objects.get(username=request.user)
        listing.title = request.POST["title"]
        listing.category = request.POST["category"]
        listing.condition = request.POST["condition"]
        listing.description = request.POST["description"]
        listing.starting_price = request.POST["starting_price"]
        listing.current_price = request.POST["starting_price"]
        listing.image = request.POST["image_url"]
        listing.number_of_bids = 0
        listing.save()
        return HttpResponseRedirect(reverse("commerce:listing", kwargs={"listing_id": listing.pk}))
    else:
        return render(request, "commerce/create_listing.html", {
            "categories": CATEGORIES,
            "conditions": CONDITIONS
        })


def listing(request, listing_id):
    listing = AuctionListing.objects.get(pk=listing_id)
    bids = Bid.objects.filter(auction_listing=listing)
    comments = Comment.objects.filter(auction_listing=listing).order_by('-timestamp')
    watched = False

    if request.method == "POST":
        # BIDDING ON A LISTING
        if "bid_value" in request.POST:
            # ERROR CASE: no value was submitted as a bid:
            if request.POST["bid_value"] == "":
                messages.add_message(request, messages.ERROR, "Please input a bid.")
            # ERROR CASE: the value of the bid is less than the current price of the listing:
            elif float(request.POST["bid_value"]) <= float(listing.current_price):
                messages.add_message(request, messages.ERROR, "Your bid must be greater than the current price.")
            # SUCCESS CASE: the bid is valid    
            else:
                make_bid(listing_id, request.user, float(request.POST["bid_value"]))
                messages.add_message(request, messages.SUCCESS, f"You have successfully placed a bid!")
        
        # CLOSING A LISTING
        if "end" in request.POST:
            listing.active = False
            listing.save()

        # COMMENTING ON A LISTING
        if "add_comment" in request.POST:
            make_comment(listing_id, request.user, request.POST["comment"])
            listing.has_comments = True
            listing.save()

        # ADDING A LISTING TO WATCHLIST
        if "watchlist" in request.POST:
            toggle_watchlist(listing, request.user)

        return HttpResponseRedirect(reverse("commerce:listing", kwargs={"listing_id": listing.pk}))

    else:
        if request.user.is_authenticated:
            if Watchlist.objects.filter(user=request.user, auction_listing=listing):
                watched = True
        if watched == False:
                watch_button = 'Add to Watchlist'
        else:
            watch_button = 'Remove from Watchlist'
        if comments:
            listing.has_comments = True
        if comments.count() == 0:
            comment_placeholder = 'Be the first to comment!'
        else:
            comment_placeholder = 'Leave a comment'
        if bids:
            bidder = bids.last()
        else:
            bidder = 'asdf'
        return render(request, "commerce/listing.html", {
            "listing": listing,
            "comments": comments,
            "bidder": bidder,
            "comment_placeholder": comment_placeholder,
            "watched": watched,
            "watch_button": watch_button
        })


def make_bid(listing_id, user, price):
    listing = AuctionListing.objects.get(pk=listing_id)
    bids = Bid.objects.filter(auction_listing=listing)

    bid = Bid()
    bid.auction_listing = listing
    bid.user = user
    bid.bid_value = price
    bid.save()

    count = bids.count()

    listing.current_price = price
    listing.number_of_bids = count
    listing.save()


def make_comment(listing_id, user, comment_content):
    listing = AuctionListing.objects.get(pk=listing_id)

    comment = Comment()
    comment.auction_listing = listing
    comment.user = user
    comment.comment = comment_content
    comment.save()


def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return redirect('commerce:index')
        else:
            return render(request, "commerce/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "commerce/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("commerce:index"))

def register_view(request):
    form = CreateUserForm(request.POST or None)
    if form.is_valid():
        user = form.save()

        if user != None:
            login(request, user)
            return redirect('commerce:index')
        else:
            return render(request, 'commerce/register.html', {
                'message': 'Could not register this account. Please try again.'
            })

    return render(request, 'commerce/register.html', {
        'form': form
    })


@login_required(login_url="commerce:login")
def watchlist(request):
    watchlist = Watchlist.objects.filter(user=request.user)

    if watchlist:
        pop = True
    else:
        pop = False

    return render(request, "commerce/watchlist.html", {
        "watchlist": watchlist,
        "pop": pop
    })


def toggle_watchlist(listing, user):
    watchlist = Watchlist.objects.filter(user=user, auction_listing=listing)
    
    if watchlist.exists():
        watchlist.delete()
    else:
        watchlist.create(user=user, auction_listing=listing)