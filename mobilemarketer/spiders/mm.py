# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from mobilemarketer.items import MobileMarketerArticleItem, MobileMarketerGenericItem


class MmSpider(CrawlSpider):
    name = "mm"
    allowed_domains = ["mobilemarketer.com"]
    start_urls = ['http://mobilemarketer.com/cms/news/email.html']
    rules = [
        Rule(
            # content detail page
            LinkExtractor(
                allow=(
                    u'mobilemarketer.com/cms/news/email/(\d+)\.html'
                    u'mobilemarketer.com/authors/(\d+)\.html'
                ),
                deny=(
                    u'email_friend.php',
                    u'/cms/general/',
                    u'mobilemarketer.com/tag/',  # tag page
                )
            ),
            callback='parse_detail_item',
            follow=True
        ),
        Rule(
            LinkExtractor(
                allow=(
                    u'mobilemarketer.com/cms/[^/]+\.html',  # uber topic page
                    u'mobilemarketer.com/cms/[^/]+/[^/]+\.html'  # topic page
                ),

                deny=(
                    u'mobilemarketer.com/tag/',  # tag page
                    u'email_friend.php',
                    u'/cms/general',
                    u'/cms/newsletter/'
                )
            ),
            callback='parse_generic_item',
            follow=True
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
        item['body'] = ' '.join(response.css('div#content-area > *').extract())
        # FIXME: can't assume that good content won't have IDs or classes. Should blacklist and remove bad html content instead.
        #   see e.g. http://www.mobilemarketer.com/cms/sectors/travel/23565.html
        # FIXME: can't assume content is in a <div> or a <p>. See http://www.mobilemarketer.com/cms/news/advertising/24630.html

        item['pub_date'] = response.css('.articlePublished::text').extract_first()
        item['authors'] = response.xpath('//p[@class="articleAuthor"]/a/text()').extract()
        item['topics'] = response.xpath('//div[@id="content"]/p/strong[contains(text(), "Related content:")]/../a/text()').extract()
        return item

    def parse_generic_item(self, response):
        self.logger.info('Hi, this is generic page! %s', response.url)
        item = MobileMarketerGenericItem()
        item['url'] = response.url
        item['title'] = response.css('h1::text').extract_first()
        item['content'] = ' '.join(response.css("#content > *").extract())
        return item
