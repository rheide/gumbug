# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gumbug', '0011_auto_20140725_1423'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='url',
            field=models.URLField(max_length=511, db_index=True),
        ),
        migrations.AlterField(
            model_name='searchurl',
            name='url',
            field=models.URLField(max_length=511),
        ),
    ]
