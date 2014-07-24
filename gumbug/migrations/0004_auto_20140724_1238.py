# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gumbug', '0003_auto_20140724_1102'),
    ]

    operations = [
        migrations.CreateModel(
            name='ListingImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(editable=False)),
                ('modified', models.DateTimeField(editable=False)),
                ('url', models.URLField()),
                ('listing', models.ForeignKey(to='gumbug.Listing')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='listing',
            name='ignored',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='listing',
            name='ignored_reason',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='listing',
            name='source',
            field=models.CharField(default=b'gumtree', max_length=50, db_index=True, choices=[(b'gumtree', b'gumtree')]),
            preserve_default=True,
        ),
        migrations.RemoveField(
            model_name='listing',
            name='photo_count',
        ),
    ]
