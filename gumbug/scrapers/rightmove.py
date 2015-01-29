#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import pytz
import re
import requests
import logging
from datetime import datetime, timedelta

from gumbug.models import Listing, ListingImage, SearchListing, Station,\
    StationDistance
from gumbug.utils import do_with_retry
from gumbug.scrapers import Scraper

"""
http://www.rightmove.co.uk/property-for-sale/Watford.html?maxPrice=290000&minBedrooms=2&retirement=false
"""


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
}


logger = logging.getLogger(__name__)
def log(search, msg):
    logger.info(u"[%s] %s", search.slug, msg)


price_regex = re.compile(r'.*[^\d]+([\d,]+) pcm.*', re.UNICODE | re.IGNORECASE | re.MULTILINE)
date_listed_regex = re.compile(r"added on (\d\d/\d\d/\d\d\d\d)", re.UNICODE | re.IGNORECASE)
latlon_regex = re.compile(r".*center=([-\d\.]+),([-\d\.]+).*")
distance_regex = re.compile(r'.*\(([\d\.]+) mi\).*', re.UNICODE | re.IGNORECASE | re.MULTILINE)

class RightmoveScraper(Scraper):

    def search(self, search_url):
        r = requests.get(search_url.url, headers=headers)
        soup = BeautifulSoup(r.text)

        listings = []
        for item in soup.findAll("li", {'class': 'summary-list-item'}):
            listing = self.load_listing(item)
            if listing:
                listings.append(listing)

        return listings

    def load_listing(self, html):
        listing = Listing()

        url_prefix = "http://www.rightmove.co.uk"
        title = html.find("h2", {'class': 'bedrooms'})
        title = title.find("a") if title else None
        title = title.find("span") if title else None
        listing.title = title.text.strip() if title and title.text else "-"

        relative_url = html.find("h2", {'class': 'bedrooms'})
        if not relative_url:
            return None  # rather fatal
        relative_url = relative_url.find("a")
        if not relative_url:
            return None  # still rather fatal
        relative_url = relative_url['href']
        relative_url = relative_url.split(".html")[0] + u".html"
        listing.url = url_prefix + relative_url
        logging.info("URL: %s" % listing.url)

        price = html.find("div", {'class': 'price-new'})
        price = price.find("a")
        price = price.text.strip()
        price = price.replace(u'£', '')
        price = price.replace(',', '')
        price = price.replace('\n', '').replace('\r', '')
        listing.price = int(price)

        listing.area = html.find("span", {'class': 'displayaddress'}).text.strip()

        listing.short_description = html.find("a", {'class': "description"}).span.text.strip()

        date_listed = html.find("p", {'class': 'branchblurb'}).text.strip().lower()
        if 'added today' in date_listed:
            listing.date_posted = datetime.now(pytz.utc)
        if 'added yesterday' in date_listed:
            listing.date_posted = datetime.now(pytz.utc) - timedelta(days=1)
        else:
            match = date_listed_regex.match(date_listed)
            if match:
                listing.date_posted =  pytz.utc.localize(datetime.strptime(match.group(1), "%d/%m/%Y"))

        return listing

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

        long_desc = u""
        desc_div = html.find("div", {'class': "agent-content"})
        features = desc_div.find("div", {'class': "key-features"})
        if features:
            for li in features.findAll("li"):
                long_desc += u"* %s\n" % li.text

        description_header = None
        for h3 in desc_div.findAll("h3"):
            if h3.text.lower() == "full description":
                description_header = h3
                break

        long_desc += "\n" + unicode(description_header.parent)

        long_desc = long_desc.replace("<br>", "")
        long_desc = long_desc.replace("<br/>", "")

        listing.long_description = long_desc

        latlon_html = html.find("a", {'class': 'js-ga-minimap'})
        if latlon_html:
            latlon_match = latlon_regex.match(latlon_html.img['src'])
            listing.lat = float(latlon_match.group(1))
            listing.lon = float(latlon_match.group(2))
            logging.info("Loc: %s %s", listing.lat, listing.lon)

        listing.save()

        # Load images
        matches = re.findall(r'thumbnailUrl":"([^"]*)","masterUrl":"([^"]*)"', r.text, re.IGNORECASE | re.UNICODE | re.MULTILINE)
        for i, (thumbnail_url, image_url) in enumerate(matches):
            image = ListingImage(listing=listing)
            image.url = image_url
            image.thumbnail_url = thumbnail_url
            image.position = i
            image.save()

        # Load distance from stations
        stations_list = html.find("ul", {'class': 'stations-list'})
        if stations_list:
            for li in stations_list.findAll("li"):
                station_name = li.find("span").text.strip()
                distance_text = li.find("small").text
                distance = float(distance_regex.match(distance_text).group(1))

                station, _ = Station.objects.get_or_create(name=station_name)
                StationDistance.objects.create(station=station,
                                               listing=listing,
                                               distance=distance)
