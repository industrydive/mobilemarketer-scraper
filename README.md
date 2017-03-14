## How to scrape locally

$ scrapy crawl mm --set=FEED_URI=`pwd`/mm_data.jl --set=FEED_FORMAT=jsonlines

Press Ctrl-C twice to abort


## how to deploy to scrapinghub

$ shub deploy