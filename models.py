#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from datetime import datetime

price_regex = re.compile(r'[^\d]*(\d+)(pw)?.*', re.UNICODE | re.IGNORECASE)
date_listed_regex = re.compile("(\d+) (yesterday|seconds|days|hours|mins|month|months|year|years) ago", re.UNICODE | re.IGNORECASE)

class Search(object):

    def __init__(self, *args, **kwargs):
        super(Search, self).__init__(*args, **kwargs)
        self.url = None


class SearchResult(object):

    def __init__(self, *args, **kwargs):
        super(SearchResult, self).__init__(*args, **kwargs)
        self.title = None
        self.price_per_week = None  # per week
        self.price_per_month = None
        self.short_description = None
        self.date_available = None
        self.area = None
        self.age = None  # x days ago
        self.url = None
        self.featured = False
        self.photo_count = 0

    @classmethod
    def from_html(cls, html):
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
            "%s days ago" % self.age,
            "%s photos%s" % (self.photo_count, " (F)" if self.featured else ""),
            self.area,
        ]))
