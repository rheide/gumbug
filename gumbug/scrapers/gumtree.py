#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import pytz
import re
import requests
import logging
from datetime import datetime, timedelta

from gumbug.models import Listing, ListingImage
from gumbug.scrapers import Scraper


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
}


price_regex = re.compile(r'[^\d]*(\d+)(pw)?.*', re.UNICODE | re.IGNORECASE)
date_listed_regex = re.compile(r"(\d+) (yesterday|seconds|days|hours|mins|month|months|year|years) ago", re.UNICODE | re.IGNORECASE)
latlon_regex = re.compile(r".*center=([-\d\.]+)%2C([-\d\.]+).*")


logger = logging.getLogger(__name__)
def log(search, msg):
    logger.info(u"[%s] %s", search.slug, msg)


class GumtreeScraper(Scraper):

    def search(self, search_url):
        """ Should return a list of Listings from a search page, with as much information
            as can be gathered. Returned Listings should not be saved.
        """
        results = []
        r = requests.get(search_url.url, headers=headers)
        soup = BeautifulSoup(r.text)

        listings = soup.find_all("ul", {"class": 'ad-listings'})
        for listing_section in listings:
            # Check if section was before or after the 'nearby' section, which is utterly useless.
            if listing_section.find_previous_sibling("div", {"class": "ad-group-nearby"}):
                log(search_url.search, "Skipping additional ads section")
                continue

            for ad in listing_section.find_all('li', {'class': 'hlisting'}):
                result = self.load_listing(ad)
                results.append(result)

        return results

    def fetch_details(self, search_url, listing):
        search = search_url.search
        log(search, "Fetching %s" % listing.url)
        detail_headers = {'referer': search_url.url}
        detail_headers.update(headers)
        r = requests.get(listing.url, headers=detail_headers)
        log(search, "Status: %s" % r.status_code)
        if r.status_code != 200:
            raise Exception("Invalid status code: %s" % r.status_code)

        html = BeautifulSoup(r.text)
        listing.long_description = html.find("div", {'id': "vip-description-text"}).text.strip()

        latlon_html = html.find("a", {'class': 'open_map'})
        if latlon_html:
            latlon_match = latlon_regex.match(latlon_html['data-target'])
            listing.lat = float(latlon_match.group(1))
            listing.lon = float(latlon_match.group(2))
            logging.info("Loc: %s %s", listing.lat, listing.lon)

        listing.save()

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

    def load_listing(self, html):
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
