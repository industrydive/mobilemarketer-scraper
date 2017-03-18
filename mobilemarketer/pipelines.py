# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem
from bs4 import BeautifulSoup
import re
import dateparser

def remove_hostname_from_url(url,hostname):
    """ turn MM aboslute URLS into relative ones, with no leading slash """
    rel_url = re.sub(r'^https?://(?:www\.)?'+hostname, '', url)
    if rel_url.startswith('/'):
        rel_url = rel_url[1:]  # remove leading slash
    return rel_url


def process_mm_html(html, redirect_pattern, hostname):
    soup = BeautifulSoup(html, 'lxml')
    # throw away junk
    bad_html = soup.find_all(class_=["centerBanner", "tools", "breadcrumb", "articleAuthor", "articlePublished", "articleImg"])
    bad_html += soup.find_all(class_=["navigation","postmetadata","mr_social_sharing_wrapper", "banner", "authordesc"])  # MCD bad classes
    bad_html += soup.find_all('h1')  # we already extracted the title of the page
    bad_html += soup.find_all('a', {'name': 'top'})  # pointless anchor linking to top of page
    bad_html += soup.find_all('div', {"id" : re.compile('beacon_[0-9a-z]+')})  # beacon_* is for ad tracking
    [x.extract() for x in bad_html]
    # make links relative by removing mobilemarketer.com hostname
    for link in soup.find_all('a', href=True):
        # make all mobilemarketer links relative
        href = remove_hostname_from_url(link['href'], hostname)
        # only munge relative links, not links to other domains
        if not re.match(r'https?://', href):
            link['href'] = redirect_pattern % href

    # TODO: clean with bleach

    # hacky trick to remove <html><body> wrappers added automatically by lxml
    soup.html.unwrap()
    soup.body.unwrap()
    # return what's left
    return unicode(soup).strip()  # colllapse to string and strip whitespace

class CommonItemProcessing(object):
    """ HTML munging and other cleanup tasks that are common to both MM and MCD """
    def process_item(self, item, spider):
        if not item['title']:
            raise DropItem("Missing title")
        if not item['pub_date']:
            raise DropItem("Missing pub_date")
        if item['pub_date']:
            item['pub_date'] = dateparser.parse(item['pub_date'])
        return item


class MobilemarketerPipeline(object):
    """ Item cleanup tasks specific to MM """
    def process_item(self, item, spider):
        hostname = "mobilemarketer.com"
        for html_key in ('body','content'):
            if html_key in item and item[html_key]:
                item[html_key] = process_mm_html(item[html_key],
                    spider.settings.get('DIVE_URL_REDIRECT_PATTERN'), 
                    hostname)
        # make url just the relative path, with no leading slash
        item['url'] = remove_hostname_from_url(item['url'],hostname)  # make url just the relative path
        # convert pub_date text to a real python datetime
        return item

class MobilecommercedailyPipeline(object):
    """ Item cleanup tasks specific to MCD """
    def process_item(self, item, spider):
        hostname = "mobilecommercedaily.com"
        for html_key in ('body','content'):
            if html_key in item and item[html_key]:
                item[html_key] = process_mm_html(item[html_key],
                    spider.settings.get('DIVE_URL_REDIRECT_PATTERN'),
                    hostname)
        # make url just the relative path, with no leading slash
        item['url'] = remove_hostname_from_url(item['url'],hostname)  # make url just the relative path
        # convert pub_date text to a real python datetime
        return item