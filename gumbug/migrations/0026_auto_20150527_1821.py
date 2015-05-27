# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gumbug', '0025_auto_20150527_1804'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='search',
            name='preserve_favorites',
        ),
        migrations.RemoveField(
            model_name='search',
            name='preserve_ignored',
        ),
        migrations.AlterField(
            model_name='searchlisting',
            name='ignored_reason',
            field=models.CharField(db_index=True, max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='searchlisting',
            name='status',
            field=models.CharField(default=b'new', max_length=50, db_index=True, choices=[(b'new', b'New'), (b'favorite', b'Favorite'), (b'ignored', b'Ignored'), (b'maybe', b'Maybe'), (b'offer', b'Under Offer')]),
            preserve_default=True,
        ),
    ]
