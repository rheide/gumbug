# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import pytz
import csv
from datetime import datetime

from django.db import models, migrations


def load_stations(apps, schema_editor):
    Station = apps.get_model('gumbug', 'Station')
    path = os.path.abspath('data/stations.csv')
    print "Path: %s" % path
    with open(path, 'rb') as csvfile:
        reader = csv.reader(csvfile)
        reader.next()
        for row in reader:
            try:
                station = Station.objects.get(name=row[0])
            except Station.DoesNotExist:
                station = Station(name=row[0], created=datetime.now(pytz.utc))
            station.modified = datetime.now(pytz.utc)
            station.lat = float(row[3])
            station.lon = float(row[4])
            station.zone = row[5]
            station.save()

class Migration(migrations.Migration):

    dependencies = [
        ('gumbug', '0020_station_zone'),
    ]

    operations = [
        migrations.RunPython(load_stations),
    ]
