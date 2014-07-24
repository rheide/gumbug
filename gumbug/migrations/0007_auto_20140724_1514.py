# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gumbug', '0006_listingimage_position'),
    ]

    operations = [
        migrations.AddField(
            model_name='search',
            name='cloned_from',
            field=models.ForeignKey(blank=True, to='gumbug.Search', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='listing',
            name='date_posted',
            field=models.DateTimeField(db_index=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='listing',
            name='ignored',
            field=models.BooleanField(default=False, db_index=True),
        ),
        migrations.AlterField(
            model_name='listing',
            name='url',
            field=models.URLField(db_index=True),
        ),
    ]
