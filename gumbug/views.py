import logging
import json
import traceback

from django.core.cache import cache
from django.http.response import Http404, HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Q

from gumbug import tasks
from gumbug.models import Search, Listing, SearchListing, SearchUrl,\
    StationFilter
from gumbug.forms import SearchForm, SearchUrlFormSet, StationFormSet
from django.forms.models import model_to_dict

validate_url= URLValidator()

url_count = 10


def update_status(request, search_slug, listing_id):
    """ Toggle the ignored flag of a listing. """
    if request.method != "POST":
        return HttpResponseForbidden()

    status = request.POST.get('status')
    try:
        search = Search.objects.get(slug=search_slug)
        listing = SearchListing.objects.get(search=search, id=listing_id)
    except Search.DoesNotExist, Listing.DoesNotExist:
        raise Http404

    listing.status = status
    if status == 'ignored':
        listing.ignored_reason = "Flagged by user"

    listing.save()

    return HttpResponse(json.dumps({'result': 'OK'}), content_type="application/json")


def listings(request, search_slug=None, search_tag=None, status=None, page_number=1):
    context = {}
    context['listing_name'] = search_slug or search_tag

    if request.GET.get('nocache', False):
        logging.info("Clearing cache")
        cache.clear()

    if search_slug:
        context['search_type'] = 'slug'
        context['listings_url'] = 'listings'
        try:
            search = Search.objects.get(slug=search_slug)
        except Search.DoesNotExist:
            raise Http404
    else:
        context['search_type'] = 'tag'
        context['listings_url'] = 'tag_listings'
        searches = Search.objects.filter(tag=search_tag).order_by("-created")[:1]
        if not searches:
            raise Http404
        search = searches[0]

    previous_searches = request.session.get('previous_searches', [])
    context['search'] = search
    context['previous_searches'] = previous_searches

    logging.info("Search status: %s" % search.status)
    if search.status not in [Search.STATUS_DONE, Search.STATUS_ERROR]:
        listings = SearchListing.objects.filter(search=search).order_by("-modified")
        context['result_count'] = listings.count()

        status_counts = {}
        for s, _ in SearchListing.STATUSES:
            status_counts[s] = listings.filter(status=s).count()
        context['status_counts'] = status_counts

        if context['result_count']:
            context['last_updated'] = listings[:1][0].modified
        else:
            context['last_updated'] = search.modified
        
        return render(request, 'listings_in_progress.html', context)

    if request.method == "POST":
        form = SearchForm(request.POST)
        url_formset = SearchUrlFormSet(request.POST, queryset=SearchUrl.objects.none())
        station_formset = StationFormSet(request.POST, queryset=StationFilter.objects.none())

        if form.is_valid() and url_formset.is_valid() and station_formset.is_valid():
            new_search = form.save(commit=False)
            new_search.tag = search.tag
            new_search.save()

            urls = url_formset.save(commit=False)
            for search_url in urls:
                search_url.search = new_search
                search_url.save()
            station_filters = station_formset.save(commit=False)
            for sf in station_filters:
                sf.search = new_search
                sf.save()
            refetch_listings = form.cleaned_data['refetch_listings']
            tasks.start_search(new_search.id, refetch_listings)
            if new_search.tag:
                return redirect('tag_listings', new_search.tag)
            else:
                return redirect('listings', new_search.slug)
    else:
        initial_data = model_to_dict(search)
        initial_data['parent'] = search
        form = SearchForm(initial=initial_data)
        initial_urls = [{'url': s.url} for s in SearchUrl.objects.filter(search=search)]
        url_formset = SearchUrlFormSet(queryset=SearchUrl.objects.none(), initial=initial_urls)

        initial_stations = [{'station': s.station.id,
                             'min_dist': s.min_dist,
                             'max_dist': s.max_dist} for s in StationFilter.objects.filter(search=search)]
        station_formset = StationFormSet(queryset=StationFilter.objects.none(), initial=initial_stations)

    listings = SearchListing.objects.filter(search=search).order_by("-listing__date_posted")

    total_count = listings.count()

    status_counts = {}
    for s, _ in SearchListing.STATUSES:
        status_counts[s] = listings.filter(status=s).count()

    context['total_listing_count'] = total_count
    context['status_counts'] = status_counts
    context['json_statuses'] = json.dumps([s for s, _ in SearchListing.STATUSES])

    if status:
        context['status'] = status
        listings = listings.filter(status=status)
    else:
        context['status'] = 'all'

    search_query = request.GET.get('q', '')
    context['search_query'] = search_query
    if search_query:
        listings = listings.filter(
            Q(listing__title__icontains=search_query) | \
            Q(listing__long_description__icontains=search_query) | \
            Q(listing__area__icontains=search_query)
        )

    p = Paginator(listings, 10)
    page = p.page(page_number)

    if not search.slug in previous_searches:
        previous_searches.insert(0, search.slug)
        if len(previous_searches) > 8:
            previous_searches.pop()
        request.session['previous_searches'] = previous_searches

    context['listings'] = page.object_list
    context['page'] = page
    context['paginator'] = p
    context['form'] = form
    context['url_formset'] = url_formset
    context['station_formset'] = station_formset

    return render(request, 'listings.html', context)


def index(request):
    context = {}

    if request.method == "POST":
        form = SearchForm(request.POST)
        url_formset = SearchUrlFormSet(request.POST, queryset=SearchUrl.objects.none())
        station_formset = StationFormSet(request.POST, queryset=StationFilter.objects.none())
        if form.is_valid() and url_formset.is_valid() and station_formset.is_valid():
            search = form.save()
            urls = url_formset.save(commit=False)
            for search_url in urls:
                search_url.search = search
                search_url.save()
            station_filters = station_formset.save(commit=False)
            for sf in station_filters:
                sf.search = search
                sf.save()
            refetch_listings = form.cleaned_data['refetch_listings']
            tasks.start_search(search.id, refetch_listings)
            return redirect('listings', search.slug)
    else:
        form = SearchForm()
        url_formset = SearchUrlFormSet(queryset=SearchUrl.objects.none())
        station_formset = StationFormSet(queryset=StationFilter.objects.none())

    context['previous_searches'] = request.session.get('previous_searches', [])
    context['ignore_keywords'] = request.POST.get('ignore-keywords', "")
    context['require_keywords'] = request.POST.get('require-keywords', "")
    context['page_count'] = request.POST.get('page_count', 1)
    context['form'] = form
    context['url_formset'] = url_formset
    context['station_formset'] = station_formset

    return render(request, 'index.html', context)
