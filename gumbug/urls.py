from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^$', 'gumbug.views.index', name='index'),
    url(r'^create$', 'gumbug.views.create_search', name='create_search'),
    url(r'^s/(?P<search_slug>[-\d\w_]+)$', 'gumbug.views.listings', name='listings'),
    url(r'^admin/', include(admin.site.urls)),
)
