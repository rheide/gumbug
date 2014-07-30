#!/usr/bin/python
# -*- coding: utf-8 -*-

import pytz
from datetime import datetime
from django.db import models
from django.utils.text import slugify
from uuid import uuid4
from mptt.models import MPTTModel


class BaseModel(models.Model):

    class Meta:
        abstract = True

    created = models.DateTimeField(editable=False, db_index=True)
    modified = models.DateTimeField(editable=False, db_index=True)

    def save(self, *args, **kwargs):
        if not self.id or not self.created:
            self.created = datetime.now(pytz.utc)
        self.modified = datetime.now(pytz.utc)
        super(BaseModel, self).save(*args, **kwargs)


class Search(MPTTModel, BaseModel):

    STATUS_NEW = 'new'
    STATUS_DONE = 'done'
    STATUS_ERROR = 'error'

    name = models.CharField(max_length=80)
    slug = models.SlugField(max_length=80, unique=True)

    parent = models.ForeignKey("self", null=True, blank=True, related_name="children")

    preserve_ignored = models.BooleanField(default=True)
    preserve_favorites = models.BooleanField(default=True)

    ignore_keywords = models.TextField(null=True, blank=True)
    require_keywords = models.TextField(null=True, blank=True)

    status = models.CharField(max_length=50, default='new', choices=[
        (STATUS_NEW, 'New'),
        (STATUS_DONE, 'Done'),
        (STATUS_ERROR, 'Error'),
    ])
    search_result = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return self.name

    @property
    def title(self):
        stamp = datetime.strftime(self.modified, "%d %b %H:%M")
        return u"%s %s" % (stamp, self.slug)

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

    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)

    @property
    def description(self):
        """ Will default to the long description unless only the short one is available. """
        return self.long_description or self.short_description

    @property
    def filter_text(self):
        return u" ".join([self.title, self.area, self.description]).lower()

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

    def __str__(self):
        return self.__unicode__().encode("ascii", "ignore")

    def __unicode__(self):
        return "\t".join(map(unicode, [
            datetime.strftime(self.date_available, "%Y-%m-%d"),
            "%s PCM" % self.price_per_month,
            self.area,
        ]))


class SearchListing(BaseModel):

    search = models.ForeignKey(Search)
    listing = models.ForeignKey(Listing)

    favorite = models.BooleanField(default=False, db_index=True)
    ignored = models.BooleanField(default=False, db_index=True)
    ignored_reason = models.CharField(max_length=255, null=True, blank=True)


class ListingImage(BaseModel):

    listing = models.ForeignKey(Listing)
    url = models.URLField()
    thumbnail_url = models.URLField(blank=True, null=True)
    position = models.PositiveSmallIntegerField(default=0)
