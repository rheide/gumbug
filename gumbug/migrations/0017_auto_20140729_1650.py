# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gumbug', '0016_auto_20140727_2236'),
    ]

    operations = [
        migrations.CreateModel(
            name='SearchListing',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(editable=False, db_index=True)),
                ('modified', models.DateTimeField(editable=False, db_index=True)),
                ('favorite', models.BooleanField(default=False, db_index=True)),
                ('ignored', models.BooleanField(default=False, db_index=True)),
                ('ignored_reason', models.CharField(max_length=255, null=True, blank=True)),
                ('listing', models.ForeignKey(to='gumbug.Listing')),
                ('search', models.ForeignKey(to='gumbug.Search')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='search',
            name='preserve_favorites',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='search',
            name='preserve_ignored',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.RemoveField(
            model_name='listing',
            name='favorite',
        ),
        migrations.RemoveField(
            model_name='listing',
            name='ignored',
        ),
        migrations.RemoveField(
            model_name='listing',
            name='ignored_reason',
        ),
        migrations.RemoveField(
            model_name='listing',
            name='search',
        ),
    ]
