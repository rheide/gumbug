import logging
import json
from uuid import uuid4

from django.http.response import Http404, HttpResponse, HttpResponseNotAllowed,\
    HttpResponseForbidden
from django.shortcuts import render, redirect
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.utils.text import slugify

from gumbug import scraper, tasks
from gumbug.models import Search, Listing, SearchUrl
from django.core.paginator import Paginator
import traceback

validate_url= URLValidator()

url_count = 10


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
        listing.favorite = False
        listing.ignored_reason = "Flagged by user"
    else:
        listing.ignored_reason = ""
    listing.save()

    return HttpResponse(json.dumps({'result': 'OK'}), content_type="application/json")


def favorite_listing(request, search_slug, listing_id):
    """ Toggle the favorite flag of a listing. """
    if request.method != "POST":
        return HttpResponseForbidden()

    try:
        search = Search.objects.get(slug=search_slug)
        listing = Listing.objects.get(search=search, id=listing_id)
    except Search.DoesNotExist, Listing.DoesNotExist:
        raise Http404

    listing.favorite = request.POST.get("favorite", "True").lower() == 'true'
    listing.save()

    return HttpResponse(json.dumps({'result': 'OK'}), content_type="application/json")


def listings(request, search_slug, page_number=1):
    context = {}

    try:
        search = Search.objects.get(slug=search_slug)
    except Search.DoesNotExist:
        raise Http404

    previous_searches = request.session.get('previous_searches', [])
    context['search'] = search
    ignored_count = Listing.objects.filter(search=search, ignored=True).count()
    context['ignored_count'] = ignored_count
    context['previous_searches'] = previous_searches

    logging.info("Search status: %s" % search.status)
    if search.status != Search.STATUS_DONE:
        listings = Listing.objects.filter(search=search).order_by("-modified")
        context['result_count'] = listings.count()
        context['ignored_count'] = ignored_count
        if context['result_count']:
            context['last_updated'] = listings[:1][0].modified
        else:
            context['last_updated'] = search.modified
        return render(request, 'listings_in_progress.html', context)

    if request.method == "POST":
        try:
            new_search = search.clone()
            tasks.search.delay(new_search.id, refetch_listings=False)
            return redirect('listings', new_search.slug)
        except Exception as e:
            logging.exception(e)
            context['error'] = u"Search failed: %s" % unicode(e)

    listings = Listing.objects.filter(search=search).order_by("-favorite",
                                                              "ignored",
                                                              "-date_posted")

    p = Paginator(listings, 10)
    page = p.page(page_number)

    if not search.slug in previous_searches:
        previous_searches.insert(0, search.slug)
        if len(previous_searches) > 8:
            previous_searches.pop()
        request.session['previous_searches'] = previous_searches

    context['valid_count'] = p.count - ignored_count
    context['listings'] = page.object_list
    context['page'] = page
    context['paginator'] = p

    return render(request, 'listings.html', context)


def index(request):
    context = {}
    urls = []

    previous_searches = request.session.get('previous_searches', [])

    if request.method == "POST":
        for i in range(url_count):
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
                search.status = Search.STATUS_NEW
                search.save()
                refetch_listings=bool(request.POST and request.POST.get('refetch', ''))
                if settings.USE_CELERY:
                    tasks.search.delay(search.id, refetch_listings)
                else:
                    scraper.search(search, refetch_listings)
                return redirect('listings', search.slug)
            except Exception as e:
                logging.exception(e)
                traceback.print_exc()
                context['error'] = u"Search failed: %s" % unicode(e)
    else:
        urls.append("http://www.gumtree.com/flats-and-houses-for-rent/harrow/studio?distance=1.0&photos_filter=Y&price=up_to_200&seller_type=private")

    while len(urls) < url_count:
        urls.append("")

    context['previous_searches'] = previous_searches
    context['ignore_keywords'] = request.POST.get('ignore-keywords', "")
    context['require_keywords'] = request.POST.get('require-keywords', "")
    context['page_count'] = request.POST.get('page_count', 1)
    context['urls'] = urls
    return render(request, 'index.html', context)
