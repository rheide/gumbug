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

def search(search):

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

    # Limit for now
    result_list = results.values()[:3]
    for result, search_url in result_list:
        result.save()  # Must be saved before saving related objects
        do_with_retry(_load_result, search, search_url, result, retry_count=1)

    if not result_list:
        raise Exception("No results found.")

    process_ignored_listings(search, result_list)


def process_ignored_listings(search, result_list):
    """ Mark listings that were previously marked as ignored, ignored. """
    # We'll want to find the first (least deep) entry for each result's url.
    # If an entry exists, copy that entry's ignored state and reason.
    search_query = search.get_ancestors(ascending=True)
    for result, _ in result_list:
        logging.info("Searching ancestor listings for %s", result.url)
        previous_results = Listing.objects.filter(search__in=search_query,
                                                  url=result.url).order_by("-search__level")[:1]

        if previous_results:
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
