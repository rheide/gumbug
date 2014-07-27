# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gumbug', '0013_listing_favorite'),
    ]

    operations = [
        migrations.AddField(
            model_name='search',
            name='search_result',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='search',
            name='status',
            field=models.CharField(default=b'done', max_length=50, choices=[(b'new', b'new'), (b'done', b'Done'), (b'error', b'Error')]),
            preserve_default=True,
        ),
    ]
