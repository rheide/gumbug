from __future__ import absolute_import
import logging
from celery import shared_task
from gumbug.models import Search
from gumbug import scraper
import traceback

@shared_task
def search(search_id, refetch_listings=False):
    logging.info("Celery searching stuff %s" % search_id)
    search = Search.objects.get(id=search_id)
    try:
        scraper.search(search, refetch_listings)
        search.status = Search.STATUS_DONE
        search.save()
    except Exception as e:
        traceback.print_exc()
        search.status = Search.STATUS_ERROR
        search.search_result = u"Error: %s" % unicode(e)
        search.save()
