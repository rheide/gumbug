# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gumbug', '0014_auto_20140727_2157'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='created',
            field=models.DateTimeField(editable=False, db_index=True),
        ),
        migrations.AlterField(
            model_name='listing',
            name='modified',
            field=models.DateTimeField(editable=False, db_index=True),
        ),
        migrations.AlterField(
            model_name='listingimage',
            name='created',
            field=models.DateTimeField(editable=False, db_index=True),
        ),
        migrations.AlterField(
            model_name='listingimage',
            name='modified',
            field=models.DateTimeField(editable=False, db_index=True),
        ),
        migrations.AlterField(
            model_name='search',
            name='created',
            field=models.DateTimeField(editable=False, db_index=True),
        ),
        migrations.AlterField(
            model_name='search',
            name='modified',
            field=models.DateTimeField(editable=False, db_index=True),
        ),
        migrations.AlterField(
            model_name='search',
            name='status',
            field=models.CharField(default=b'done', max_length=50, choices=[((b'new',), b'new'), ((b'done',), b'Done'), ((b'error',), b'Error')]),
        ),
        migrations.AlterField(
            model_name='searchurl',
            name='created',
            field=models.DateTimeField(editable=False, db_index=True),
        ),
        migrations.AlterField(
            model_name='searchurl',
            name='modified',
            field=models.DateTimeField(editable=False, db_index=True),
        ),
    ]
