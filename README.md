## What's this then?

This Django app + celery worker scrapes Rightmove search listings to give you a better (and combined) view of the results. It also allows you to filter down more deeply, automatically ignore ads that you've previously ignored in the same search and set favorites. Furthermore, it's got some neat map advantages over the origin sites, such as a deprivation index overlay and ability to display a route to the nearest transport.


## Setup

- Install the requirements
- Initialize your database (Django 1.7: syncdb and migrate)
- celery -A gumbug worker -l info
