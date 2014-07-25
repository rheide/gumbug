import logging
import json
from uuid import uuid4

from django.http.response import Http404, HttpResponse, HttpResponseNotAllowed,\
    HttpResponseForbidden
from django.shortcuts import render, redirect
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.utils.text import slugify

from gumbug import scraper
from gumbug.models import Search, Listing, SearchUrl
from django.core.paginator import Paginator

validate_url= URLValidator()


def ignore_listing(request, search_slug, listing_id):
    """ Toggle the ignored flag of a listing. """
    if request.method != "POST":
        return HttpResponseForbidden()

    try:
        search = Search.objects.get(slug=search_slug)
        listing = Listing.objects.get(search=search, id=listing_id)
    except Search.DoesNotExist, Listing.DoesNotExist:
        raise Http404

    listing.ignored = request.POST.get("ignore", "True").lower() == 'true'
    if listing.ignored:
        listing.ignored_reason = "Flagged by user"
    else:
        listing.ignored_reason = ""
    listing.save()

    return HttpResponse(json.dumps({'result': 'OK'}), content_type="application/json")


def listings(request, search_slug, page_number=1):
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

    listings = Listing.objects.filter(search=search).order_by("ignored", "-date_posted")

    ignored_count = Listing.objects.filter(search=search, ignored=True).count()

    p = Paginator(listings, 10)
    page = p.page(page_number)

    context['search'] = search
    context['valid_count'] = p.count - ignored_count
    context['ignored_count'] = ignored_count
    context['listings'] = page.object_list
    context['page'] = page
    context['paginator'] = p

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
                search.ignore_keywords = request.POST.get('ignore-keywords', "")
                search.require_keywords = request.POST.get('require-keywords', "")
                search.save()
                scraper.search(search)
                return redirect('listings', search.slug)
            except Exception as e:
                logging.exception(e)
                context['error'] = u"Search failed: %s" % unicode(e)
    else:
        urls.append("http://www.gumtree.com/flats-and-houses-for-rent/harrow/studio?distance=1.0&photos_filter=Y&price=up_to_200&seller_type=private")

    while len(urls) < 5:
        urls.append("")

    context['ignore_keywords'] = request.POST.get('ignore-keywords', "")
    context['require_keywords'] = request.POST.get('require-keywords', "")
    context['page_count'] = request.POST.get('page_count', 1)
    context['urls'] = urls
    return render(request, 'index.html', context)
