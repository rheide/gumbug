# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def set_status(apps, schema_editor):
    SearchListing = apps.get_model("gumbug", "SearchListing")
    for listing in SearchListing.objects.all().order_by('id'):
        print "Updating listing: %s" % listing.id
        if listing.favorite:
            listing.status = 'favorite'
        elif listing.ignored:
            listing.status = 'ignored'
        elif not listing.status:
            listing.status = 'new'
        listing.save()




class Migration(migrations.Migration):

    dependencies = [
        ('gumbug', '0024_searchlisting_status'),
    ]

    operations = [
        migrations.RunPython(set_status),
    ]
