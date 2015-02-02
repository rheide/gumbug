from django.contrib import admin
from gumbug.models import Search, SearchUrl, Listing, ListingImage, Station,\
    StationDistance, StationFilter

class BaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'created', '__unicode__')
    list_display_links = ('id', '__unicode__',)

class ListingAdmin(BaseAdmin):
    list_display = ('id', 'created', 'date_posted', 'title', 'area', 'price', )
    list_display_links = ('id', 'title')
    list_filter = ('created', 'date_posted')


admin.site.register(Search, BaseAdmin)
admin.site.register(SearchUrl, BaseAdmin)
admin.site.register(Listing, ListingAdmin)
admin.site.register(ListingImage, BaseAdmin)
admin.site.register(Station, BaseAdmin)
admin.site.register(StationDistance, BaseAdmin)
admin.site.register(StationFilter, BaseAdmin)
