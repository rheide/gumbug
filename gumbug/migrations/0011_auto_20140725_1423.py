# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gumbug', '0010_auto_20140725_1246'),
    ]

    operations = [
        migrations.AddField(
            model_name='search',
            name='ignore_keywords',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='search',
            name='require_keywords',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
