#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import pytz
from datetime import datetime
from django.db import models

price_regex = re.compile(r'[^\d]*(\d+)(pw)?.*', re.UNICODE | re.IGNORECASE)
date_listed_regex = re.compile("(\d+) (yesterday|seconds|days|hours|mins|month|months|year|years) ago", re.UNICODE | re.IGNORECASE)


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


class Search(BaseModel):

    name = models.CharField(max_length=80)
    slug = models.SlugField(max_length=80, unique=True)

    def __unicode__(self):
        return self.name


class SearchUrl(BaseModel):

    search = models.ForeignKey(Search)
    url = models.URLField()

    def __unicode__(self):
        return "%s - %s" % (self.search, self.url)


class Listing(BaseModel):

    source = models.CharField(max_length=50, db_index=True, choices=[('gumtree', 'gumtree')],
                              default='gumtree')

    search = models.ForeignKey(Search)

    url = models.URLField(db_index=True)

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

    @classmethod
    def from_gumtree(cls, html):
        result = cls()

        title = html.find("a", {'class': 'description'})
        result.title = title.text.strip()
        result.url = title["href"]

        price = html.find("span", {'class': 'price'}).text.strip()
        result.price_per_week = int(price_regex.match(price).group(1))
        result.price_per_month = int(float((result.price_per_week) * 52.0) / 12.0)
        result.area = html.find("span", {'class': 'location'}).text.strip()
        date_available =  html.find("span", {'class': 'displayed-date'}).text.strip()
        result.date_available = datetime.strptime(date_available, "%d/%m/%y")

        result.short_description = html.find("div", {'class': "ad-description"}).span.text.strip()

        result.photo_count = int(html.find("span", {'class': "ad-description-info-photo"}).text.strip())

        result.featured = bool(html.find("span", {"class": "featured"}))

        result.age = -1
        date_listed = html.find("span", {'class': 'post-date'})
        if date_listed:
            date_listed = date_listed.text.strip()
            print date_listed
            match = date_listed_regex.match(date_listed)
            if match:
                if match.group(2) == 'days':
                    result.age = int(match.group(1))
                elif 'month' in match.group(2):
                    # rough indication, most likely not interested in old ads anyway
                    result.age = 30 * int(match.group(1))
                elif 'year' in match.group(2):
                    result.age = 365 * int(match.group(1))
                else:  # seconds, minutes, hours
                    result.age = 0
            elif date_listed == 'yesterday':
                result.age = 1

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
