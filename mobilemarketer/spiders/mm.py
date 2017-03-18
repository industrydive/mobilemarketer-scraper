# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from mobilemarketer.items import MobileMarketerArticleItem, MobileMarketerGenericItem


class MmSpider(CrawlSpider):
    name = "mm"
    allowed_domains = ["mobilemarketer.com"]
    start_urls = ['http://mobilemarketer.com/']
    custom_settings = {
        'ITEM_PIPELINES' : {
            'mobilemarketer.pipelines.CommonItemProcessing': 300,
            'mobilemarketer.pipelines.MobilemarketerPipeline': 300,
        },
        'DIVE_URL_REDIRECT_PATTERN': '/ex/mobilemarketer/%s'
    }    
    rules = [
        Rule(
            # content detail page
            LinkExtractor(
                allow=(u'mobilemarketer.com/cms/(news|opinion|resources|opinion|sectors)/([^/]+)/(\d+)\.html'),
                deny=(u'email_friend.php', u'/cms/general/')
            ),
            callback='parse_detail_item',
            follow=True
        ),
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
        item['body'] = ' '.join(response.css('div#content-area > *').extract())
        item['page_title'] = response.xpath('//title/text()').extract()
        # FIXME: can't assume that good content won't have IDs or classes. Should blacklist and remove bad html content instead.
        #   see e.g. http://www.mobilemarketer.com/cms/sectors/travel/23565.html
        # FIXME: can't assume content is in a <div> or a <p>. See http://www.mobilemarketer.com/cms/news/advertising/24630.html

        item['pub_date'] = response.css('.articlePublished::text').extract_first()
        item['authors'] = response.xpath('//p[@class="articleAuthor"]/a/text()').extract()
        item['topics'] = response.xpath('//div[@id="content"]/p/strong[contains(text(), "Related content:")]/../a/text()').extract()
        return item

    def parse_generic_item(self, response):
        """ Not currently used """
        self.logger.info('Hi, this is generic page! %s', response.url)
        item = MobileMarketerGenericItem()
        item['url'] = response.url
        item['title'] = response.css('h1::text').extract_first()
        item['content'] = ' '.join(response.css("#content > *").extract())
        return item