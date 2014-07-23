from bs4 import BeautifulSoup
from models import SearchResult
import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
}

def scrape(search):
    #r = requests.get(search.url, headers=headers)
    text = open("example.htm").read()
    soup = BeautifulSoup(text)
    results = []
    for ad in soup.find_all('li', {'class': 'hlisting'}):
        print "Ad found!"
        results.append(SearchResult.from_html(ad))
    return results
