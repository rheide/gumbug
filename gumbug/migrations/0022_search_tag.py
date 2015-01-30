# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gumbug', '0021_auto_20150123_1449'),
    ]

    operations = [
        migrations.AddField(
            model_name='search',
            name='tag',
            field=models.CharField(db_index=True, max_length=80, null=True, blank=True),
            preserve_default=True,
        ),
    ]
