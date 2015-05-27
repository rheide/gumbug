from __future__ import absolute_import
import logging
import traceback
from celery import shared_task
from django.conf import settings
from gumbug.models import Search, SearchListing, Listing
from gumbug.scrapers.gumtree import GumtreeScraper
from gumbug.utils import do_with_retry
from gumbug.scrapers.rightmove import RightmoveScraper
from django.core.cache import cache


logger = logging.getLogger(__name__)
def log(search, msg):
    logger.info(u"[%s] %s", search.slug, msg)


gumtree = GumtreeScraper()
rightmove = RightmoveScraper()


def start_search(search_id, refetch_listings=False):
    if settings.USE_CELERY:
        search.delay(search_id, refetch_listings=refetch_listings)
    else:
        search(search_id, refetch_listings=refetch_listings)


def get_scraper(url):
    if 'gumtree.com' in url:
        return gumtree
    elif 'rightmove.co.uk' in url:
        return rightmove
    else:
        raise Exception(u"Invalid url: %s" % url)


@shared_task
def search(search_id, refetch_listings=False):
    logger.info("Celery searching stuff %s" % search_id)
    search = Search.objects.get(id=search_id)
    try:
        do_search(search, refetch_listings)
        search.status = Search.STATUS_DONE
        search.save()
    except Exception as e:
        traceback.print_exc()
        logger.exception(unicode(e))
        search.status = Search.STATUS_ERROR
        search.search_result = u"Error: %s" % unicode(e)
        search.save()
    finally:
        logging.info("Clearing cache")
        cache.clear()


def do_search(search, refetch_listings):
    search_results = {}

    # Get initial search results
    search_urls = search.searchurl_set.all()
    log(search, "Searching %s urls" % len(search_urls))
    for search_url in search_urls:
        scraper = get_scraper(search_url.url)
        listings = scraper.search(search_url)
        for l in listings:
            search_results[l.url] = (l, search_url)

    # Fetch listing details or load existing details
    search_listings = []
    for listing, search_url in search_results.values():
        previous_versions = Listing.objects.filter(url=listing.url,
                                                   long_description__isnull=False).order_by('-created')[:1]
        if previous_versions:
            listing = previous_versions[0]
        if not listing.id or refetch_listings:
            try:
                do_with_retry(load_result_details, search_url, listing, retry_count=3)
            except Exception as e:
                traceback.print_exc()
                log(search, u"Could not fetch details: %s" % e)
                listing.long_description= u"Could not fetch details: %s" % e
                listing.save()

        search_listing = SearchListing(search=search, listing=listing)
        search_listing.save()
        search_listings.append(search_listing)

    process_past_search_listings(search, search_listings)
    process_ignore_keywords(search, search_listings)
    process_require_keywords(search, search_listings)
    process_station_filters(search, search_listings)

    for res in search_listings:
        res.save()


def load_result_details(search_url, listing):
    scraper = get_scraper(search_url.url)
    scraper.fetch_details(search_url, listing)


def process_ignore_keywords(search, search_listings):
    ignore_keywords = search.ignore_keywords_list
    if not ignore_keywords:
        return
    for search_listing in search_listings:
        if search_listing.ignored:
            continue  # Skip already ignored results
        text = search_listing.listing.filter_text
        if any(word in text for word in ignore_keywords):
            search_listing.ignored = True
            search_listing.ignored_reason = "Contains ignored keywords"


def process_station_filters(search, search_listings):
    station_filters = search.station_filters
    if not station_filters:
        return
    for search_listing in search_listings:
        if search_listing.ignored:
            continue  # Skip already ignored results

        if not any([sf.matches(search_listing.listing) for sf in station_filters]):
            search_listing.ignored = True
            search_listing.ignored_reason = "Does not match transport filters"


def process_require_keywords(search, search_listings):
    require_keywords = search.require_keywords_list
    if not require_keywords:
        return
    for search_listing in search_listings:
        if search_listing.ignored:
            continue  # Skip already ignored results
        text = search_listing.listing.filter_text
        if not any(word in text for word in require_keywords):
            search_listing.ignored = True
            search_listing.ignored_reason = "Did not contain a required keyword"


def process_past_search_listings(search, result_list):
    """ Mark listings that were previously marked as ignored or favorited. """
    # We'll want to find the first (least deep) entry for each result's url.
    # If an entry exists, copy that entry's ignored state and reason.
    search_query = search.get_ancestors(ascending=True)
    for result in result_list:
        logging.info("Searching ancestor listings for %s", result.listing.url)
        previous_results = SearchListing.objects.filter(search__in=search_query,
                                                        listing__url=result.listing.url).order_by("-search__level")[:1]

        if not previous_results:
            continue

        previous = previous_results[0]

        if previous.status != 'new' and previous.status != result.status:
            result.status = previous.status
