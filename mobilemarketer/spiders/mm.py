# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from mobilemarketer.items import MobileMarketerArticleItem, MobileMarketerGenericItem


class MmSpider(CrawlSpider):
    name = "mm"
    allowed_domains = ["mobilemarketer.com"]
    start_urls = ['http://mobilemarketer.com/']
    rules = [
        Rule(
            # content detail page
            LinkExtractor(
                allow=(u'/cms/(news|opinion|resources|opinion|sectors)/([^/]+)/(\d+)\.html'),
                deny=()
            ),
            callback='parse_detail_item',
            follow=True
        ),
        Rule(
            # Tag page
            LinkExtractor(
                allow=(u'/tag/', u'^/cms/[^/]+\.html', u'^/cms/[^/]+/[^/]+\.html'),
                deny=()
            ),
            # callback='parse_generic_item',
            # follow=True
        )
    ]      

    def parse_detail_item(self, response):
        """
            parses a news/opinion article

            @url http://www.mobilemarketer.com/cms/news/video/24617.html
            @scrapes title body pub_date authors main_topic topics
        """
        self.logger.info('Hi, this is an item page! %s', response.url)
        # item = scrapy.Item()
        item = MobileMarketerArticleItem()
        item['url'] = response.url
        item['title'] = response.css('h1::text').extract_first()
        item['body'] = ' '.join(response.css('div#content-area > div:not([id]):not([class]), div#content-area > p:not([id]):not([class])').extract())
        item['pub_date'] = response.css('.articlePublished::text').extract_first()
        item['authors'] = response.xpath('//p[@class="articleAuthor"]/a/text()').extract()
        item['topics'] = response.xpath('//div[@id="content"]/p/strong[contains(text(), "Related content:")]/../a/text()').extract()
        return item

    def parse_generic_item(self, response):
        self.logger.info('Hi, this is generic page! %s', response.url)
        item = MobileMarketerGenericItem()
        item['url'] = response.url
        item['title'] = response.css('h1::text').extract_first()
        item['content'] = response.css("#content").extract()