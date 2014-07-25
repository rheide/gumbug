# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gumbug', '0007_auto_20140724_1514'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='lat',
            field=models.FloatField(default=0.0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='listing',
            name='lon',
            field=models.FloatField(default=0.0),
            preserve_default=True,
        ),
    ]
