# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from mobilemarketer.items import MobileMarketerArticleItem


class McdSpider(CrawlSpider):
    name = "mcd"
    custom_settings = {
        'ITEM_PIPELINES' : {
            'mobilemarketer.pipelines.CommonItemProcessing': 300,
            'mobilemarketer.pipelines.MobilecommercedailyPipeline': 300,
        },
        # 'REDIRECT_ENABLED': False,  # they have a lot of offsite redirects
        'DIVE_URL_REDIRECT_PATTERN': '/ex/mobilecommercedaily/%s'
    }
    allowed_domains = ["www.mobilecommercedaily.com"]
    start_urls = ['http://www.mobilecommercedaily.com/']
    rules = [
        Rule(
            # content detail page
            LinkExtractor(
                restrict_css = ('h1', 'div.navigation'),
                deny=(
                    u'/category/',
                    u'/tag/',
                    u'/author/',
                    u'/page/',
                    u'/newsletter-archive/',
                    u'/rss-feeds/',
                    u'/wp-content/',
                    u'/newsletter/?$',
                    u'/print/?$',
                    u'/email/?$',
                    u'/jobs.php',
                    u'/advertise/?$',
                )
            ),
            callback='parse_detail_item',
            follow=True
        ),
    ]

    def parse_detail_item(self, response):
        """
            parses a news/opinion article

            @url http://www.mobilecommercedaily.com/how-mobile-point-of-sale-goes-beyond-checkout
            @scrapes title body pub_date authors main_topic topics
        """
        self.logger.info('Hi, this is an item page! %s', response.url)
        # item = scrapy.Item()
        item = MobileMarketerArticleItem()
        item['url'] = response.url
        item['title'] = response.css('h1::text').extract_first()
        item['body'] = ' '.join(response.css('div.entry > *').extract())
        item['page_title'] = response.xpath('//title/text()').extract()
        # FIXME: can't assume that good content won't have IDs or classes. Should blacklist and remove bad html content instead.
        #   see e.g. http://www.mobilemarketer.com/cms/sectors/travel/23565.html
        # FIXME: can't assume content is in a <div> or a <p>. See http://www.mobilemarketer.com/cms/news/advertising/24630.html

        item['pub_date'] = response.css('div#date::text').extract_first()
        item['authors'] = response.xpath('//span[@id="authorindex"]/a/text()').extract()
        item['topics'] = response.css('a[rel="tag"]::text').extract()
        return item