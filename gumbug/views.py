from gumbug.models import Search, Listing, SearchUrl
from django.http.response import Http404
from django.shortcuts import render, redirect
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from uuid import uuid4
from gumbug import scraper
import logging
from django.utils.text import slugify

validate_url= URLValidator()


def listings(request, search_slug):
    context = {}

    try:
        search = Search.objects.get(slug=search_slug)
    except Search.DoesNotExist:
        raise Http404

    if request.method == "POST":
        try:
            new_search = search.clone()
            scraper.search(new_search)
            return redirect('listings', new_search.slug)
        except Exception as e:
            logging.exception(e)
            context['error'] = u"Search failed: %s" % unicode(e)

    listings = Listing.objects.filter(search=search, ignored=False).order_by("-date_posted")
    ignored_listings = Listing.objects.filter(search=search, ignored=True).order_by("-date_posted")

    context['search'] = search
    context['listings'] = listings
    context['ignored_listings'] = ignored_listings

    return render(request, 'listings.html', context)


def index(request):
    context = {}
    urls = []

    if request.method == "POST":
        for i in range(10):
            url = request.POST.get("url%s" % i, "").strip()
            if url:
                try:
                    validate_url(url)
                except ValidationError:
                    context['error'] = u"Invalid url: %s" % url
                urls.append(url)

        if not urls:
            context['error'] = "Please specify at least one url"

        if not 'error' in context:
            # Construct a search object, perform search and redirect to the listings page if successful
            try:
                search = Search.create(urls)
                scraper.search(search)
                return redirect('listings', search.slug)
            except Exception as e:
                logging.exception(e)
                context['error'] = u"Search failed: %s" % unicode(e)
    else:
        urls.append("http://www.gumtree.com/flats-and-houses-for-rent/harrow/studio?distance=1.0&photos_filter=Y&price=up_to_200&seller_type=private")

    while len(urls) < 5:
        urls.append("")

    context['page_count'] = request.POST.get('page_count', 1)
    context['urls'] = urls
    return render(request, 'index.html', context)
