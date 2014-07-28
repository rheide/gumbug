#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import pytz
import re
import requests
import logging
from datetime import datetime, timedelta

from gumbug.models import Listing, ListingImage
from gumbug.utils import do_with_retry

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
}


price_regex = re.compile(r'[^\d]*(\d+)(pw)?.*', re.UNICODE | re.IGNORECASE)
date_listed_regex = re.compile(r"(\d+) (yesterday|seconds|days|hours|mins|month|months|year|years) ago", re.UNICODE | re.IGNORECASE)
latlon_regex = re.compile(r".*center=([-\d\.]+)%2C([-\d\.]+).*")


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

        listings = soup.find_all("ul", {"class": 'ad-listings'})
        for listing_section in listings:
            # Check if section was before or after the 'nearby' section, which is utterly useless.
            if listing_section.find_previous_sibling("div", {"class": "ad-group-nearby"}):
                log(search, "Skipping additional ads section")
                continue

            for ad in listing_section.find_all('li', {'class': 'hlisting'}):
                result = listing_from_gumtree(ad)
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
            do_with_retry(load_result_details, search, search_url, result, retry_count=3)

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
        title_and_desc = u"%s %s" % (result.title, result.description)
        title_and_desc = title_and_desc.lower()
        if any(word in title_and_desc for word in ignore_keywords):
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
        title_and_desc = u"%s %s" % (result.title, result.description)
        title_and_desc = title_and_desc.lower()
        if not any(word in title_and_desc for word in require_keywords):
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


def load_result_details(search, search_url, result):
    log(search, "Fetching %s" % result.url)
    detail_headers = {'referer': search_url.url}
    detail_headers.update(headers)
    r = requests.get(result.url, headers=detail_headers)
    log(search, "Status: %s" % r.status_code)
    if r.status_code != 200:
        raise Exception("Invalid status code: %s" % r.status_code)
    result.load_details_from_gumtree(r.text)


def listing_from_gumtree(html):
    result = Listing()

    title = html.find("a", {'class': 'description'})
    result.title = title.text.strip()
    result.url = title["href"]

    price = html.find("span", {'class': 'price'}).text.strip()

    price_match = price_regex.match(price)
    if price_match:
        result.price = float(price_match.group(1))
        result.price_type = 'week'

    result.area = html.find("span", {'class': 'location'}).text.strip()
    date_available =  html.find("span", {'class': 'displayed-date'}).text.strip()
    result.date_available = pytz.utc.localize(datetime.strptime(date_available, "%d/%m/%y"))

    result.short_description = html.find("div", {'class': "ad-description"}).span.text.strip()

    result.featured = bool(html.find("span", {"class": "featured"}))

    age_days = -1
    date_listed = html.find("span", {'class': 'post-date'})
    if date_listed:
        date_listed = date_listed.text.strip()
        match = date_listed_regex.match(date_listed)
        if match:
            if match.group(2) == 'days':
                age_days = int(match.group(1))
            elif 'month' in match.group(2):
                # rough indication, most likely not interested in old ads anyway
                age_days = 30 * int(match.group(1))
            elif 'year' in match.group(2):
                age_days = 365 * int(match.group(1))
            else:  # seconds, minutes, hours
                age_days = 0
        elif date_listed == 'yesterday':
            age_days = 1

    if age_days >= 0:
        result.date_posted = datetime.now(pytz.utc) - timedelta(days=age_days)
    else:
        result.date_posted = None

    return result


def load_listing_details_from_gumtree(listing, raw_html):
    html = BeautifulSoup(raw_html)
    listing.long_description = html.find("div", {'id': "vip-description-text"}).text.strip()

    latlon_html = html.find("a", {'class': 'open_map'})
    if latlon_html:
        latlon_match = latlon_regex.match(latlon_html['data-target'])
        listing.lat = float(latlon_match.group(1))
        listing.lon = float(latlon_match.group(2))
        logging.info("Loc: %s %s", listing.lat, listing.lon)

    # Load images
    for i in range(20):
        image_html = html.find("ul", {'class': "gallery-main"})
        if not image_html:
            continue
        image_html = image_html.find("li", {'id': "gallery-item-mid-%s" % i})
        if not image_html:
            continue
        image_html = image_html.find("img")
        if not image_html:
            continue

        image = ListingImage(listing=listing)
        image.url = image_html['src']

        thumbnail_html = html.find("ul", {'class': 'gallery-thumbs'})
        if thumbnail_html:
            thumbnail_html = thumbnail_html.find("a", {'href': "#gallery-item-mid-%s" % i})
            if thumbnail_html:
                image.thumbnail_url = thumbnail_html.find("img")['src']

        image.position = i
        image.save()

    listing.save()
