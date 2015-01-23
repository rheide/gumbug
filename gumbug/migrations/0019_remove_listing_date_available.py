# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gumbug', '0018_auto_20150123_1427'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='listing',
            name='date_available',
        ),
    ]
