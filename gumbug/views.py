import logging
import json
import traceback

from django.http.response import Http404, HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator

from gumbug import tasks
from gumbug.models import Search, Listing, SearchListing, SearchUrl
from gumbug.forms import SearchForm, SearchUrlFormSet
from django.forms.models import model_to_dict

validate_url= URLValidator()

url_count = 10


def ignore_listing(request, search_slug, listing_id):
    """ Toggle the ignored flag of a listing. """
    if request.method != "POST":
        return HttpResponseForbidden()

    try:
        search = Search.objects.get(slug=search_slug)
        listing = SearchListing.objects.get(search=search, id=listing_id)
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
        listing = SearchListing.objects.get(search=search, id=listing_id)
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
    ignored_count = SearchListing.objects.filter(search=search, ignored=True).count()
    context['ignored_count'] = ignored_count
    context['previous_searches'] = previous_searches

    logging.info("Search status: %s" % search.status)
    if search.status != Search.STATUS_DONE:
        listings = SearchListing.objects.filter(search=search).order_by("-modified")
        context['result_count'] = listings.count()
        context['ignored_count'] = ignored_count
        if context['result_count']:
            context['last_updated'] = listings[:1][0].modified
        else:
            context['last_updated'] = search.modified
        return render(request, 'listings_in_progress.html', context)

    if request.method == "POST":
        form = SearchForm(request.POST)
        url_formset = SearchUrlFormSet(request.POST, queryset=SearchUrl.objects.none())
        if form.is_valid() and url_formset.is_valid():
            search = form.save()
            urls = url_formset.save(commit=False)
            for search_url in urls:
                search_url.search = search
                search_url.save()
            refetch_listings = form.cleaned_data['refetch_listings']
            tasks.start_search(search.id, refetch_listings)
            return redirect('listings', search.slug)
    else:
        initial_data = model_to_dict(search)
        initial_data['parent'] = search
        form = SearchForm(initial=initial_data)
        initial_urls = [{'url': s.url} for s in SearchUrl.objects.filter(search=search)]
        url_formset = SearchUrlFormSet(queryset=SearchUrl.objects.none(), initial=initial_urls)

    listings = SearchListing.objects.filter(search=search).order_by("-favorite",
                                                                    "ignored",
                                                                    "-listing__date_posted")

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
    context['form'] = form
    context['url_formset'] = url_formset

    return render(request, 'listings.html', context)


def index(request):
    context = {}

    if request.method == "POST":
        form = SearchForm(request.POST)
        url_formset = SearchUrlFormSet(request.POST, queryset=SearchUrl.objects.none())
        if form.is_valid() and url_formset.is_valid():
            search = form.save()
            urls = url_formset.save(commit=False)
            for search_url in urls:
                search_url.search = search
                search_url.save()
            refetch_listings = form.cleaned_data['refetch_listings']
            tasks.start_search(search.id, refetch_listings)
            return redirect('listings', search.slug)
    else:
        form = SearchForm()
        url_formset = SearchUrlFormSet(queryset=SearchUrl.objects.none())

    context['previous_searches'] = request.session.get('previous_searches', [])
    context['ignore_keywords'] = request.POST.get('ignore-keywords', "")
    context['require_keywords'] = request.POST.get('require-keywords', "")
    context['page_count'] = request.POST.get('page_count', 1)
    context['form'] = form
    context['url_formset'] = url_formset
    return render(request, 'index.html', context)
