# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

class Migration(migrations.Migration):

    dependencies = [
        ('gumbug', '0023_auto_20150202_2207'),
    ]

    operations = [
        migrations.AddField(
            model_name='searchlisting',
            name='status',
            field=models.CharField(default=b'new', max_length=50, choices=[(b'new', b'New'), (b'favorite', b'Favorite'), (b'ignored', b'Ignored'), (b'maybe', b'Maybe'), (b'offer', b'Under Offer')]),
            preserve_default=True,
        ),
    ]
