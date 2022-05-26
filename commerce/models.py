from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

User = settings.AUTH_USER_MODEL

class AuctionListing(models.Model):
    class Categories(models.TextChoices):
        ANTIQUES = 'AN', _('Antiques')
        BOOKS = 'BO', _('Books')
        CLOTHING = 'CL', _('Clothing and Accessories')
        COLLECTIBLES = 'CO', _('Collectibles')
        ELECTRONICS = 'EL', _('Electronics')
        FOOD = 'FO', _('Food')
        FURNITURE = 'FU', _('Furniture')
        HOME_AND_GARDEN = 'HG', _('Home and Garden')
        MUSIC = 'MU', _('Music')
        PETS = 'PE', _('Pet Supplies')
        TOYS_HOBBIES = 'TH', _('Toys and Hobbies')
        EVERYTHING = 'EV', _('Everything Else')

    class Conditions(models.TextChoices):
        BRAND_NEW = 'BN', _('Brand New')
        LIKE_NEW = 'LN', _('Like New')
        VERY_GOOD = 'VG', _('Very Good')
        GOOD = 'GO', _('Good')
        ACCEPTABLE = 'AC', _('Acceptable')

    active = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=100)
    category = models.CharField(max_length=2, choices=Categories.choices, null=True)
    condition = models.CharField(max_length=2, choices=Conditions.choices, null=True)
    description = models.CharField(max_length=1000)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    starting_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    image = models.URLField(max_length=256, null=True)
    number_of_bids = models.IntegerField(null=True)
    has_comments = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)
    
    def __str__(self):
        return f"{self.title}: ${self.starting_price} - posted by {self.user}"


class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    auction_listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    bid_value = models.DecimalField(max_digits=6, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.auction_listing} - Bid: ${self.bid_value} - {self.user} at {self.timestamp}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    auction_listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    comment = models.CharField(max_length=300)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.auction_listing} - {self.user} at {self.timestamp}"

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    auction_listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.user} - {self.auction_listing}"
