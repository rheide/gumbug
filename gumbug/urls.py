from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^$', 'gumbug.views.index', name='index'),

    url(r'^s/(?P<search_slug>[-\d\w_]+)$', 'gumbug.views.listings', name='listings'),
    url(r'^s/(?P<search_slug>[-\d\w_]+)/(?P<page_number>\d+)$', 'gumbug.views.listings', name='listings'),

    url(r'^s/(?P<search_slug>[-\d\w_]+)/ignore/(?P<listing_id>\d+)$', 'gumbug.views.ignore_listing', name='ignore_listing'),

    url(r'^admin/', include(admin.site.urls)),
)
