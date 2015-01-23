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


class Station(BaseModel):

    name = models.CharField(max_length=200)
    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)
    zone = models.CharField(max_length=50, null=True, blank=True)

    def __unicode__(self):
        return "%s %s %s" % (self.name, self.lat, self.lon)


class Search(MPTTModel, BaseModel):

    STATUS_NEW = 'new'
    STATUS_DONE = 'done'
    STATUS_ERROR = 'error'

    name = models.CharField(max_length=80)
    slug = models.SlugField(max_length=80, unique=True)

    parent = models.ForeignKey("self", null=True, blank=True, related_name="children")

    preserve_ignored = models.BooleanField(default=True,
                                           help_text="Ignore already ignored items in future searches.")
    preserve_favorites = models.BooleanField(default=True,
                                             help_text="Favorite already favorited items in future searches.")

    ignore_keywords = models.TextField(null=True, blank=True,
                                       help_text="Ads with any of these keywords will be automatically ignored.")
    require_keywords = models.TextField(null=True, blank=True,
                                        help_text="Ads that don't contain at least one of these keywords will be automatically ignored.")

    start_date = models.DateField(null=True, blank=True)

    status = models.CharField(max_length=50, default='new', choices=[
        (STATUS_NEW, 'New'),
        (STATUS_DONE, 'Done'),
        (STATUS_ERROR, 'Error'),
    ])
    search_result = models.TextField(null=True, blank=True)

    stations = models.ManyToManyField(Station, through='StationFilter', null=True, blank=True)

    def __unicode__(self):
        return self.name

    @property
    def station_filters(self):
        return StationFilter.objects.filter(search=self).order_by('station__name')

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


class StationFilter(BaseModel):

    search = models.ForeignKey(Search)
    station = models.ForeignKey(Station)
    min_dist = models.FloatField(default=0.0)
    max_dist = models.FloatField(default=0.0)

    def __unicode__(self):
        return "%s %s - %s" % (self.station.name, self.min_dist, self.max_dist)

    def matches(self, listing):
        """ Returns true if the listing is within the range of this filter. """
        for dist in listing.station_distances:
            if dist.station.name != self.station.name:
                continue  # station name doesn't match, so this can't be a match 
            if self.min_dist and dist.distance < self.min_dist:
                continue  # distance less than min dist required for this filter to match
            if self.max_dist and dist.distance > self.max_dist:
                continue  # distance more than max dist required for this filter to match
            return True  # yay
        return False


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

    source = models.CharField(max_length=50, db_index=True, choices=[('rightmove', 'rightmove')],
                              default='rightmove')

    url = models.URLField(max_length=511, db_index=True)

    title = models.CharField(max_length=255, null=True, blank=True)
    price = models.DecimalField(decimal_places=2, max_digits=12, blank=True, null=True)

    short_description = models.TextField(blank=True, null=True)
    long_description = models.TextField(blank=True, null=True)

    date_posted = models.DateTimeField(blank=True, null=True, db_index=True)

    area = models.CharField(max_length=255, blank=True, null=True, db_index=True)

    featured = models.BooleanField(default=False)

    lease_duration = models.PositiveIntegerField(blank=True, null=True)  # years
    property_type = models.CharField(max_length=50, db_index=True, choices=[('apartment', 'house')]),
    service_charges = models.DecimalField(decimal_places=2, max_digits=12, blank=True, null=True)
    ground_rental= models.DecimalField(decimal_places=2, max_digits=12, blank=True, null=True)

    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)

    stations = models.ManyToManyField(Station, through='StationDistance', null=True, blank=True)

    @property
    def station_distances(self):
        return StationDistance.objects.filter(listing=self).order_by('distance')

    @property
    def description(self):
        """ Will default to the long description unless only the short one is available. """
        return self.long_description or self.short_description

    @property
    def filter_text(self):
        return u" ".join([self.title, self.area, self.description]).lower()

    def __str__(self):
        return self.__unicode__().encode("ascii", "ignore")

    def __unicode__(self):
        return "\t".join(map(unicode, [
            datetime.strftime(self.date_posted, "%Y-%m-%d") if self.date_posted else '',
            "%s" % self.price,
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


class StationDistance(BaseModel):

    listing = models.ForeignKey(Listing)
    station = models.ForeignKey(Station)
    distance = models.FloatField(default=0.0)

    def __unicode__(self):
        return "%s %s" % (self.station, self.distance)
