# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gumbug', '0015_auto_20140727_2220'),
    ]

    operations = [
        migrations.AlterField(
            model_name='search',
            name='status',
            field=models.CharField(default=b'new', max_length=50, choices=[(b'new', b'New'), (b'done', b'Done'), (b'error', b'Error')]),
        ),
    ]
