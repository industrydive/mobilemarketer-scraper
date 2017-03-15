# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from bs4 import BeautifulSoup
import re

def process_mm_html(html):
    soup = BeautifulSoup(html, 'lxml')
    # throw away junk
    bad_html = soup.find_all(class_=["centerBanner", "tools", "breadcrumb", "articleAuthor", "articlePublished", "articleImg"])
    bad_html += soup.find_all('h1')
    bad_html += soup.find_all('a', {'name': 'top'})
    [x.extract() for x in bad_html]
    # make links relative by removing mobilemarketer.com hostname
    for link in soup.find_all('a', href=True):
        link['href'] = re.sub(r'^https?://(?:www\.)?mobilemarketer.com', '', link['href'])

    # remove <html><body> wrappers added by lxml
    soup.html.unwrap()
    soup.body.unwrap()
    # return what's left
    return unicode(soup).strip()  # colllapse to string and strip whitespace



class MobilemarketerPipeline(object):
    def process_item(self, item, spider):
        for html_key in ('body','content'):
            if html_key in item and item[html_key]:
                item[html_key] = process_mm_html(item[html_key])
        return item
