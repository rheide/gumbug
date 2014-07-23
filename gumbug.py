import scraper
from models import Search, SearchResult

def main():
    search = Search()
    search.url = "http://www.gumtree.com/flats-and-houses-for-rent/harrow/studio?distance=1.0&photos_filter=Y&price=up_to_200&seller_type=private"
    results = scraper.scrape(search)
    for r in results:
        print r.url
        print r
    print "Done!"

if __name__ == '__main__':
    main()
