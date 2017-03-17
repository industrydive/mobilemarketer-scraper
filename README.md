## How to scrape locally

$ scrapy crawl mm --set=FEED_URI=`pwd`/mm_data.jl --set=FEED_FORMAT=jsonlines

Press Ctrl-C twice to abort

Then you can convert it to a fixture for the legacy apps with this hacky script

$ python mm_jsonlines_to_fixture.py


## how to deploy to scrapinghub

$ shub deploy

First time you will need an api key from 