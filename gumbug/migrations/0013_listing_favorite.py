# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gumbug', '0012_auto_20140725_1606'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='favorite',
            field=models.BooleanField(default=False, db_index=True),
            preserve_default=True,
        ),
    ]
