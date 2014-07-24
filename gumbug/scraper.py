from bs4 import BeautifulSoup
from .models import Listing
import requests
import logging

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
}

logger = logging.getLogger(__name__)
def log(search, msg):
    logger.info(u"[%s] %s", search.slug, msg)

def search(search):

    results = {}

    search_urls = search.searchurl_set.all()
    log(search, "Searching %s urls" % len(search_urls))
    for search_url in search_urls:
        log(search, "Fetching url: %s" % search_url.url)
        r = requests.get(search_url.url, headers=headers)
        soup = BeautifulSoup(r.text)

        for ad in soup.find_all('li', {'class': 'hlisting'}):
            result = Listing.from_gumtree(ad)
            if result.url in results:
                log(search, "Duplicate results for url %s. Skipping" % result.url)
            else:
                result.search = search
                result.save()
                results[result.url] = result

    if not results:
        raise Exception("No results found.")
