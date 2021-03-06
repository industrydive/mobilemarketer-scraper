# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import Join, MapCompose, Identity

class MobilemarketerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class NewsArticleItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    page_title = scrapy.Field()
    body = scrapy.Field()
    pub_date = scrapy.Field()
    topics = scrapy.Field()
    authors = scrapy.Field()


class MobileMarketerGenericItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    body = scrapy.Field()