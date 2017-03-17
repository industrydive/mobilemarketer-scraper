# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from bs4 import BeautifulSoup
import re

def remove_mm_hostname_from_url(url):
    """ turn MM aboslute URLS into relative ones, with no leading slash """
    rel_url = re.sub(r'^https?://(?:www\.)?mobilemarketer.com', '', url)
    if rel_url.startswith('/'):
        rel_url = rel_url[1:]  # remove leading slash
    return rel_url

def process_mm_html(html, redirect_pattern):
    soup = BeautifulSoup(html, 'lxml')
    # throw away junk
    bad_html = soup.find_all(class_=["centerBanner", "tools", "breadcrumb", "articleAuthor", "articlePublished", "articleImg"])
    bad_html += soup.find_all('h1')  # we already extracted the title of the page
    bad_html += soup.find_all('a', {'name': 'top'})  # pointless anchor linking to top of page
    bad_html += soup.find_all('div', {"id" : re.compile('beacon_[0-9a-z]+')})  # beacon_* is for ad tracking
    [x.extract() for x in bad_html]
    # make links relative by removing mobilemarketer.com hostname
    for link in soup.find_all('a', href=True):
        # make all mobilemarketer links relative
        href = remove_mm_hostname_from_url(link['href'])
        # only munge relative links, not links to other domains
        if not re.match(r'https?://', href):
            link['href'] = redirect_pattern % href

    # TODO: clean with bleach

    # hacky trick to remove <html><body> wrappers added automatically by lxml
    soup.html.unwrap()
    soup.body.unwrap()
    # return what's left
    return unicode(soup).strip()  # colllapse to string and strip whitespace



class MobilemarketerPipeline(object):
    def process_item(self, item, spider):
        for html_key in ('body','content'):
            if html_key in item and item[html_key]:
                item[html_key] = process_mm_html(item[html_key], spider.settings.get('DIVE_URL_REDIRECT_PATTERN'))
        # make url just the relative path, with no leading slash
        item['url'] = remove_mm_hostname_from_url(item['url'])  # make url just the relative path
        return item
