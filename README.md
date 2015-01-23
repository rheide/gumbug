## What's this then?

This Django app + celery worker scrapes Gumtree and Rightmove search listings to give you a better (and combined) view of the results. It also allows you to filter down more deeply, automatically ignore ads that you've previously ignored in the same search and set favorites. Furthermore, it's got some neat map advantages over the origin sites, such as a deprivation index overlay.


## Setup

- celery -A gumbug worker -l info


## TODO

- email notifications
- always store price as pcm
- analyze text similarity to ignore ads instead of relying on url
- Find nearest station, then other stations within ~0.3 miles, calculate distance to each of them.
- Filter for min. x minutes from station
- Run Celery worker somewhere stable but preferrably free


## Things required for public release:

- a better database
- periodic removal of old search results, listings and sessions
- ads
- donation option via paypal + bitcoin
- saved searches + ad-free login notice
- analytics
- email notifications + unsubscribe
