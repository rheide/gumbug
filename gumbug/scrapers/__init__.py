

class Scraper(object):

    def search(self, search_url):
        """ Should return a list of Listings from a search page, with as much information
            as can be gathered. Returned Listings should not be saved.
        """
        return []

    def fetch_details(self, search_url, listing):
        """ Should populate and fetch details for the given Listing.
            The Listing is guaranteed to be saved before this function is called.
        """
        pass
