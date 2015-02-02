# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gumbug', '0022_search_tag'),
    ]

    operations = [
        migrations.AddField(
            model_name='listingimage',
            name='image_type',
            field=models.CharField(default=b'image', max_length=32, db_index=True, choices=[(b'image', b'Image'), (b'floorplan', b'Floorplan')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='listingimage',
            name='position',
            field=models.PositiveSmallIntegerField(default=0, db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='search',
            name='parent',
            field=models.ForeignKey(related_name='children', blank=True, to='gumbug.Search', null=True),
            preserve_default=True,
        ),
    ]
