# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gumbug', '0008_auto_20140725_1132'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='lat',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='listing',
            name='lon',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
