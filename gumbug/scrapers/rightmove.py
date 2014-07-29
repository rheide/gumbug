#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import pytz
import re
import requests
import logging
from datetime import datetime, timedelta

from gumbug.models import Listing, ListingImage, SearchListing
from gumbug.utils import do_with_retry
from gumbug.scrapers import Scraper


"""
http://www.rightmove.co.uk/property-to-rent/find.html
?searchType=RENT&locationIdentifier=POSTCODE%5E936383&insId=1&radius=1.0
&displayPropertyType=&minBedrooms=&maxBedrooms=&minPrice=700&maxPrice=1000
&maxDaysSinceAdded=&retirement=&sortByPriceDescending=&_includeLetAgreed=on
&primaryDisplayPropertyType=&secondaryDisplayPropertyType=&oldDisplayPropertyType=
&oldPrimaryDisplayPropertyType=&letType=&letFurnishType=&houseFlatShare=false
"""

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
}


logger = logging.getLogger(__name__)
def log(search, msg):
    logger.info(u"[%s] %s", search.slug, msg)


price_regex = re.compile(r'.*[^\d]+([\d,]+) pcm.*', re.UNICODE | re.IGNORECASE | re.MULTILINE)
date_listed_regex = re.compile(r"Listed on (\d\d/\d\d/\d\d\d\d)", re.UNICODE | re.IGNORECASE)
latlon_regex = re.compile(r".*center=([-\d\.]+)%2C([-\d\.]+).*")


class RightmoveScraper(Scraper):

    def search(self, search_url):
        r = requests.get(search_url.url, headers=headers)
        soup = BeautifulSoup(r.text)

        listings = []
        for item in soup.findAll("li", {'class': 'summary-list-item'}):
            listings.append(self.load_listing(item))

        return listings

    def load_listing(self, html):
        listing = Listing()

        url_prefix = "http://www.rightmove.co.uk"
        title = html.find("h2", {'class': 'bedrooms'})
        title = title.find("a")
        title = title.find("span")
        listing.title = title.text.strip()
        listing.url = url_prefix + html.find("h2", {'class': 'bedrooms'}).find("a")['href']

        price = html.find("p", {'class': 'price-new'}).text.strip().replace('\n', '').replace('\r', '')
        price_match = price_regex.match(price)
        if price_match:
            listing.price = int(price_match.group(1).replace(',', ''))
            listing.price_type = 'month'

        listing.area = html.find("span", {'class': 'displayaddress'}).text.strip()

        listing.short_description = html.find("p", {'class': "description"}).span.text.strip()

        date_listed = html.find("p", {'class': 'branchblurb'}).text.strip()
        if 'Listed today' in date_listed:
            listing.date_posted = datetime.now(pytz.utc)
        if 'Listed yesterday' in date_listed:
            listing.date_posted = datetime.now(pytz.utc) - timedelta(days=1)
        else:
            match = date_listed_regex.match(date_listed)
            if match:
                listing.date_posted =  pytz.utc.localize(datetime.strptime(match.group(1), "%d/%m/%Y"))

        return listing

    def fetch_details(self, search_url, listing):
        listing.save()
