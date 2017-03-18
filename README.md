## How to set up this project

There's a docker-compose file that defines a service cleverly named "scrapy" and has an entrypoint that looks at incoming arguments sees if they look like arguments to the scrapy script in the container of if they're other commands. It just kinda works. The container volume mounts the project directory so all the data and caching happens in the project directory. You should only need to manually rebuild the container if the requirements.txt changes.

Basically you can just run `docker-compose run scrapy argument-to-scrapy` and it works or `docker-compose run python something_else.py` and that works too.


(You can also skip docker and run it the old fashioned way by creating a virtualenv and running `pip install -r requirements.txt`. )

## Running it

To stop a running spider, press Ctrl-C twice.

### Scrape mobilemarketer.com 
```
docker-compose run scrapy crawl mm --set=FEED_URI=`pwd`/mm_data.jl --set=FEED_FORMAT=jsonlines
```

And then there's a super hacky script to convery jsonlines to a fixture you can run like:
```
docker-compose run scrapy python mm_jsonlines_to_fixture.py
```

it assumes input is mm_data.jl and output is mm_fixture.json


### Scrape mobilecommercedaily.com

Same as above but the spider is "mcd" instead of "mm"

```
docker-compose run scrapy crawl mcd --set=FEED_URI=`pwd`/mcm_data.jl --set=FEED_FORMAT=jsonlines
```


## Scrapinghub

I don't think we're going to end up using scrapinghub, but FYI it has deployment script you can run like

```
docker-compose run scrapy shub deploy
```

I believe you'll need an API key from the project page in order to be able to push the first time.