# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gumbug', '0005_listingimage_thumbnail_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='listingimage',
            name='position',
            field=models.PositiveSmallIntegerField(default=0),
            preserve_default=True,
        ),
    ]
