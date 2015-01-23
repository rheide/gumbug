from django.contrib import admin
from gumbug.models import Search, SearchUrl, Listing, ListingImage, Station,\
    StationDistance, StationFilter

admin.site.register(Search)
admin.site.register(SearchUrl)
admin.site.register(Listing)
admin.site.register(ListingImage)
admin.site.register(Station)
admin.site.register(StationDistance)
admin.site.register(StationFilter)
