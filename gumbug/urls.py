from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^$', 'gumbug.views.index', name='index'),

    url(r'^s/(?P<search_slug>[-\d\w_]+)$', 'gumbug.views.listings', name='listings'),
    url(r'^s/(?P<search_slug>[-\d\w_]+)/(?P<page_number>\d+)$', 'gumbug.views.listings', name='listings'),
    url(r'^s/(?P<search_slug>[-\d\w_]+)/(?P<status>[-\d\w_]+)$', 'gumbug.views.listings', name='listings'),
    url(r'^s/(?P<search_slug>[-\d\w_]+)/(?P<status>[-\d\w_]+)/(?P<page_number>\d+)$', 'gumbug.views.listings', name='listings'),

    url(r'^t/(?P<search_tag>[-\d\w_]+)$', 'gumbug.views.listings', name='tag_listings'),
    url(r'^t/(?P<search_tag>[-\d\w_]+)/(?P<page_number>\d+)$', 'gumbug.views.listings', name='tag_listings'),
    url(r'^t/(?P<search_tag>[-\d\w_]+)/(?P<status>[-\d\w_]+)$', 'gumbug.views.listings', name='tag_listings'),
    url(r'^t/(?P<search_tag>[-\d\w_]+)/(?P<status>[-\d\w_]+)/(?P<page_number>\d+)$', 'gumbug.views.listings', name='tag_listings'),

    url(r'^u/(?P<search_slug>[-\d\w_]+)/status/(?P<listing_id>\d+)$', 'gumbug.views.update_status', name='update_status'),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^ac/', include('autocomplete_light.urls')),
)
