# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gumbug', '0004_auto_20140724_1238'),
    ]

    operations = [
        migrations.AddField(
            model_name='listingimage',
            name='thumbnail_url',
            field=models.URLField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
