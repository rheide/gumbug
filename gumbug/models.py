#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import re
import pytz
from datetime import datetime, timedelta
from django.db import models
from django.utils.text import slugify
from uuid import uuid4
from bs4 import BeautifulSoup
from mptt.models import MPTTModel

price_regex = re.compile(r'[^\d]*(\d+)(pw)?.*', re.UNICODE | re.IGNORECASE)
date_listed_regex = re.compile(r"(\d+) (yesterday|seconds|days|hours|mins|month|months|year|years) ago", re.UNICODE | re.IGNORECASE)
latlon_regex = re.compile(r".*center=([-\d\.]+)%2C([-\d\.]+).*")

class BaseModel(models.Model):

    class Meta:
        abstract = True

    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField(editable=False)

    def save(self, *args, **kwargs):
        if not self.id or not self.created:
            self.created = datetime.now(pytz.utc)
        self.modified = datetime.now(pytz.utc)
        super(BaseModel, self).save(*args, **kwargs)


class Search(MPTTModel, BaseModel):

    name = models.CharField(max_length=80)
    slug = models.SlugField(max_length=80, unique=True)

    parent = models.ForeignKey("self", null=True, blank=True, related_name="children")

    ignore_keywords = models.TextField(null=True, blank=True)
    require_keywords = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return self.name

    @property
    def ignore_keywords_list(self):
        return [s for s in map(lambda s: s.strip(), self.ignore_keywords.split(",")) if s]

    @property
    def require_keywords_list(self):
        return [s for s in map(lambda s: s.strip(), self.require_keywords.split(",")) if s]

    def __init__(self, *args, **kwargs):
        super(Search, self).__init__(*args, **kwargs)
        if not self.id and not self.slug:
            search_id = slugify(unicode(uuid4().bytes.encode('base64').rstrip('=\n')[:10]))
            self.name = search_id
            self.slug = search_id

    @classmethod
    def create(cls, urls=[]):
        search_id = slugify(unicode(uuid4().bytes.encode('base64').rstrip('=\n')[:10]))
        search = cls()
        search.name = search_id
        search.slug = search_id
        search.save()

        for url in urls:
            SearchUrl.objects.create(search=search, url=url)

        return search

    def clone(self):
        new_search = Search()
        new_search.parent = self
        new_search.ignore_keywords = self.ignore_keywords
        new_search.require_keywords = self.require_keywords
        new_search.save()

        for search_url in self.searchurl_set.all():
            search_url.clone(new_search)

        return new_search


class SearchUrl(BaseModel):

    search = models.ForeignKey(Search)
    url = models.URLField(max_length=511)

    def __unicode__(self):
        return "%s - %s" % (self.search, self.url)

    def clone(self, search):
        new_search_url = SearchUrl(search=search, url=self.url)
        new_search_url.save()
        return new_search_url


class Listing(BaseModel):

    source = models.CharField(max_length=50, db_index=True, choices=[('gumtree', 'gumtree')],
                              default='gumtree')

    search = models.ForeignKey(Search)

    url = models.URLField(max_length=511, db_index=True)

    title = models.CharField(max_length=255, null=True, blank=True)
    price = models.DecimalField(decimal_places=2, max_digits=12, blank=True, null=True)
    price_type = models.CharField(max_length=50, choices=[("week", "week"), ("month", "month")], default="week")
    short_description = models.TextField(blank=True, null=True)
    long_description = models.TextField(blank=True, null=True)

    date_available = models.DateTimeField(blank=True, null=True)
    date_posted = models.DateTimeField(blank=True, null=True, db_index=True)

    area = models.CharField(max_length=255, blank=True, null=True, db_index=True)

    featured = models.BooleanField(default=False)

    ignored = models.BooleanField(default=False, db_index=True)
    ignored_reason = models.CharField(max_length=255, null=True, blank=True)

    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)

    @property
    def description(self):
        """ Will default to the long description unless only the short one is available. """
        return self.long_description or self.short_description

    @property
    def price_per_month(self):
        if self.price_type == "month":
            return int(self.price)
        elif self.price_type == "week":
            return int((float(self.price) * 52.0) / 12.0)
        else:
            return "N/A"

    @property
    def price_per_week(self):
        if self.price_type == "month":
            return int((float(self.price) * 12.0) / 52.0)
        elif self.price_type == "week":
            return int(self.price)
        else:
            return "N/A"

    def load_details_from_listing(self, listing):
        self.lat = listing.lat
        self.lon = listing.lon
        self.long_description = listing.long_description
        for img in listing.listingimage_set.all():
            ListingImage.objects.create(listing=self,
                                        url=img.url,
                                        thumbnail_url=img.thumbnail_url,
                                        position=img.position)
        self.save()

    def load_details_from_gumtree(self, raw_html):
        html = BeautifulSoup(raw_html)
        self.long_description = html.find("div", {'id': "vip-description-text"}).text.strip()

        latlon_html = html.find("a", {'class': 'open_map'})
        if latlon_html:
            latlon_match = latlon_regex.match(latlon_html['data-target'])
            self.lat = float(latlon_match.group(1))
            self.lon = float(latlon_match.group(2))
            logging.info("Loc: %s %s", self.lat, self.lon)

        # Load images
        for i in range(20):
            image_html = html.find("ul", {'class': "gallery-main"}).find("li", {'id': "gallery-item-mid-%s" % i})
            if not image_html:
                continue
            image = ListingImage(listing=self)
            image.url = image_html.find("img")['src']
            thumbnail_html = html.find("ul", {'class': 'gallery-thumbs'}).find("a", {'href': "#gallery-item-mid-%s" % i})
            image.thumbnail_url = thumbnail_html.find("img")['src']
            image.position = i
            image.save()

        self.save()

    @classmethod
    def from_gumtree(cls, html):
        result = cls()

        title = html.find("a", {'class': 'description'})
        result.title = title.text.strip()
        result.url = title["href"]

        price = html.find("span", {'class': 'price'}).text.strip()

        result.price = float(price_regex.match(price).group(1))
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

    def __str__(self):
        return self.__unicode__().encode("ascii", "ignore")

    def __unicode__(self):
        return "\t".join(map(unicode, [
            datetime.strftime(self.date_available, "%Y-%m-%d"),
            "%s PCM" % self.price_per_month,
            self.area,
        ]))


class ListingImage(BaseModel):

    listing = models.ForeignKey(Listing)
    url = models.URLField()
    thumbnail_url = models.URLField(blank=True, null=True)
    position = models.PositiveSmallIntegerField(default=0)
