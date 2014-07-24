# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('gumbug', '0002_listing'),
    ]

    operations = [
        migrations.CreateModel(
            name='SearchUrl',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(editable=False)),
                ('modified', models.DateTimeField(editable=False)),
                ('url', models.URLField()),
                ('search', models.ForeignKey(to='gumbug.Search')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='listing',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2014, 7, 24, 11, 2, 28, 989000), editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='listing',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2014, 7, 24, 11, 2, 34, 77000), editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='search',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2014, 7, 24, 11, 2, 40, 62000), editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='search',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2014, 7, 24, 11, 2, 45, 981000), editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='search',
            name='name',
            field=models.CharField(default='', max_length=80),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='search',
            name='slug',
            field=models.SlugField(default='', unique=True, max_length=80),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name='search',
            name='source_url',
        ),
    ]
