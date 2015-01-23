# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gumbug', '0017_auto_20140729_1650'),
    ]

    operations = [
        migrations.CreateModel(
            name='Station',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(editable=False, db_index=True)),
                ('modified', models.DateTimeField(editable=False, db_index=True)),
                ('name', models.CharField(max_length=200)),
                ('lat', models.FloatField(null=True, blank=True)),
                ('lon', models.FloatField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StationDistance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(editable=False, db_index=True)),
                ('modified', models.DateTimeField(editable=False, db_index=True)),
                ('distance', models.FloatField(default=0.0)),
                ('listing', models.ForeignKey(to='gumbug.Listing')),
                ('station', models.ForeignKey(to='gumbug.Station')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StationFilter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(editable=False, db_index=True)),
                ('modified', models.DateTimeField(editable=False, db_index=True)),
                ('min_dist', models.FloatField(default=0.0)),
                ('max_dist', models.FloatField(default=0.0)),
                ('search', models.ForeignKey(to='gumbug.Search')),
                ('station', models.ForeignKey(to='gumbug.Station')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='listing',
            name='ground_rental',
            field=models.DecimalField(null=True, max_digits=12, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='listing',
            name='lease_duration',
            field=models.PositiveIntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='listing',
            name='service_charges',
            field=models.DecimalField(null=True, max_digits=12, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='listing',
            name='stations',
            field=models.ManyToManyField(to=b'gumbug.Station', null=True, through='gumbug.StationDistance', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='search',
            name='start_date',
            field=models.DateField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='search',
            name='stations',
            field=models.ManyToManyField(to=b'gumbug.Station', null=True, through='gumbug.StationFilter', blank=True),
            preserve_default=True,
        ),
        migrations.RemoveField(
            model_name='listing',
            name='price_type',
        ),
        migrations.AlterField(
            model_name='listing',
            name='source',
            field=models.CharField(default=b'rightmove', max_length=50, db_index=True, choices=[(b'rightmove', b'rightmove')]),
        ),
        migrations.AlterField(
            model_name='search',
            name='ignore_keywords',
            field=models.TextField(help_text=b'Ads with any of these keywords will be automatically ignored.', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='search',
            name='preserve_favorites',
            field=models.BooleanField(default=True, help_text=b'Favorite already favorited items in future searches.'),
        ),
        migrations.AlterField(
            model_name='search',
            name='preserve_ignored',
            field=models.BooleanField(default=True, help_text=b'Ignore already ignored items in future searches.'),
        ),
        migrations.AlterField(
            model_name='search',
            name='require_keywords',
            field=models.TextField(help_text=b"Ads that don't contain at least one of these keywords will be automatically ignored.", null=True, blank=True),
        ),
    ]
