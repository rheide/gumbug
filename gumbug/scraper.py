#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from .models import Listing
import requests
import logging
from gumbug.utils import do_with_retry

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
}

logger = logging.getLogger(__name__)
def log(search, msg):
    logger.info(u"[%s] %s", search.slug, msg)

def search(search, refetch_listings=False):
    """ Searches urls for listings and loads their information.
        If refetch_listings is false then the most recent version of the
        listing (based on url) will be used rather than fetching the listing again.
    """

    results = {}

    search_urls = search.searchurl_set.all()
    log(search, "Searching %s urls" % len(search_urls))
    for search_url in search_urls:
        log(search, "Fetching url: %s" % search_url.url)
        r = requests.get(search_url.url, headers=headers)
        soup = BeautifulSoup(r.text)

        for ad in soup.find_all('li', {'class': 'hlisting'}):
            result = Listing.from_gumtree(ad)
            if result.url in results:
                log(search, "Duplicate results for url %s. Skipping" % result.url)
            else:
                result.search = search
                results[result.url] = (result, search_url)

    result_list = results.values()
    for result, search_url in result_list:
        result.save()  # Must be saved before saving related objects

        refetch_details = True
        if not refetch_listings:
            # See if we have a previous record for this url
            previous_versions = Listing.objects.filter(url=result.url,
                                                       long_description__isnull=False).order_by('-created')[:1]
            if previous_versions:
                log(search, "Loading listing %s from previous version %s" % (result.id, previous_versions[0].id))
                result.load_details_from_listing(previous_versions[0])
                refetch_details = False

        if refetch_details:
            do_with_retry(_load_result, search, search_url, result, retry_count=1)

    if not result_list:
        raise Exception("No results found.")

    process_ignored_listings(search, result_list)
    process_ignore_keywords(search, result_list)
    process_require_keywords(search, result_list)


def process_ignore_keywords(search, result_list):
    ignore_keywords = search.ignore_keywords_list
    if not ignore_keywords:
        return
    for result, _ in result_list:
        if result.ignored:
            continue  # Skip already ignored results
        if any(word in result.description for word in ignore_keywords):
            result.ignored = True
            result.ignored_reason = "Contains ignored keywords"
            result.save()


def process_require_keywords(search, result_list):
    require_keywords = search.require_keywords_list
    if not require_keywords:
        return
    for result, _ in result_list:
        if result.ignored:
            continue  # Skip already ignored results
        if not any(word in result.description for word in require_keywords):
            result.ignored = True
            result.ignored_reason = "Did not contain a required keyword"
            result.save()


def process_ignored_listings(search, result_list):
    """ Mark listings that were previously marked as ignored, ignored. """
    # We'll want to find the first (least deep) entry for each result's url.
    # If an entry exists, copy that entry's ignored state and reason.
    search_query = search.get_ancestors(ascending=True)
    for result, _ in result_list:
        logging.info("Searching ancestor listings for %s", result.url)
        previous_results = Listing.objects.filter(search__in=search_query,
                                                  url=result.url).order_by("-search__level")[:1]

        if previous_results and previous_results[0].ignored != result.ignored:
            result.ignored = previous_results[0].ignored
            result.ignored_reason = previous_results[0].ignored_reason
            result.save()


def _load_result(search, search_url, result):
    log(search, "Fetching %s" % result.url)
    detail_headers = {'referer': search_url.url}
    detail_headers.update(headers)
    r = requests.get(result.url, headers=detail_headers)
    log(search, "Status: %s" % r.status_code)
    if r.status_code != 200:
        raise Exception("Invalid status code: %s" % r.status_code)
    result.load_details_from_gumtree(r.text)
