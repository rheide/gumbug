# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gumbug', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Listing',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.URLField()),
                ('title', models.CharField(max_length=255, null=True, blank=True)),
                ('price', models.DecimalField(null=True, max_digits=12, decimal_places=2, blank=True)),
                ('price_type', models.CharField(default=b'week', max_length=50, choices=[(b'week', b'week'), (b'month', b'month')])),
                ('short_description', models.TextField(null=True, blank=True)),
                ('long_description', models.TextField(null=True, blank=True)),
                ('date_available', models.DateTimeField(null=True, blank=True)),
                ('date_posted', models.DateTimeField(null=True, blank=True)),
                ('area', models.CharField(db_index=True, max_length=255, null=True, blank=True)),
                ('featured', models.BooleanField(default=False)),
                ('photo_count', models.PositiveSmallIntegerField(default=0)),
                ('search', models.ForeignKey(to='gumbug.Search')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
