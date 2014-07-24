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
                results[result.url] = result

    # Limit for now
    result_list = results.values()[:10]
    for result in result_list:
        result.save()  # Must be saved before saving related objects
        do_with_retry(_load_result, search, result, retry_count=3)

    if not result_list:
        raise Exception("No results found.")


def _load_result(search, result):
    log(search, "Fetching %s" % result.url)
    r = requests.get(result.url, headers=headers)
    log(search, "Status: %s" % r.status_code)
    if r.status_code != 200:
        raise Exception("Invalid status code: %s" % r.status_code)
    soup = BeautifulSoup(r.text)
    result.load_details_from_gumtree(soup)
