from gumbug.models import Search, Listing
from django.http.response import Http404
from django.shortcuts import render, redirect


def listings(request, search_slug):
    try:
        search = Search.objects.get(slug=search_slug)
    except Search.DoesNotExist:
        raise Http404

    listings = Listing.objects.filter(search=search, ignored=False).order_by("-date_posted")
    ignored_listings = Listing.objects.filter(search=search, ignored=True).order_by("-date_posted")

    context = {
        'search': search,
        'listings': listings,
        'ignored_listings': ignored_listings,
    }

    return render(request, 'listings.html', context)


def index(request):
    context = {}
    return render(request, 'index.html', context)


def create_search(request):
    context = {}
    return redirect('listings', 'test')
