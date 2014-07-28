from __future__ import absolute_import
import logging
import traceback
from celery import shared_task
from django.conf import settings
from gumbug.models import Search
from gumbug.scrapers import gumtree


def start_search(search_id, refresh_listings=False):
    if settings.USE_CELERY:
        search.delay(search_id, refetch_listings=refresh_listings)
    else:
        search(search_id, refetch_listings=refresh_listings)

@shared_task
def search(search_id, refetch_listings=False):
    logging.info("Celery searching stuff %s" % search_id)
    search = Search.objects.get(id=search_id)
    try:
        gumtree.search(search, refetch_listings)
        search.status = Search.STATUS_DONE
        search.save()
    except Exception as e:
        traceback.print_exc()
        search.status = Search.STATUS_ERROR
        search.search_result = u"Error: %s" % unicode(e)
        search.save()
