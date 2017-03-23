# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem
from bs4 import BeautifulSoup, Comment
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
    bad_html = soup.find_all(class_=["centerBanner", "tools", "breadcrumb", "articleAuthor", "articlePublished"])
    bad_html += soup.find_all(class_=["navigation","postmetadata","mr_social_sharing_wrapper", "banner", "authordesc"])  # MCD bad classes
    bad_html += soup.find_all('h1')  # we already extracted the title of the page
    bad_html += soup.find_all('a', {'name': 'top'})  # pointless anchor linking to top of page
    bad_html += soup.find_all('div', {"id" : re.compile('beacon_[0-9a-z]+')})  # beacon_* is for ad tracking
    bad_html += soup.find_all('a', {'target': '_new', 'href': 'http://www.mobilecommercedaily.com/newsletter/'})  # signup ad
        
    # actually remove the things we matched
    [x.decompose() for x in bad_html]

    # comment out hero images
    for img_wrapper in soup.find_all('div', {'class': ['articleImg', 'wp-caption']}):
        img_wrapper.replace_with(Comment(str(img_wrapper)))
    # comment out embedded images
    for img in soup.find_all('img', src=re.compile(r'http://www\.mobile(marketer|commercedaily)\.com/')):
        img_parent = img.parent
        if img_parent.name == 'a':
            img_parent = img_parent.parent
        # only proceed if there isn't much text in this tree
        if len(img_parent.get_text()) < 300:
            img_parent.replace_with(Comment(str(img_parent)))

    # make links relative by removing mobilemarketer.com hostname
    for link in soup.find_all('a', href=True):
        # make all absolute links to this site relative
        href = remove_hostname_from_url(link['href'], hostname)
        # only munge relative links, not links to other domains
        if not re.match(r'https?://', href):
            link['href'] = redirect_pattern % href

    # TODO: clean with bleach

    # hacky trick to remove <html><body> wrappers added automatically by lxml
    if soup.html is not None:
        soup.html.unwrap()
    if soup.body is not None:
        soup.body.unwrap()
    # convert to str
    html_str = unicode(soup).strip()
    # strip everything after tags for MCD
    html_str = re.sub(r'<p>Tags:.*$', '', html_str)
    # return what's left
    return html_str

class CommonItemProcessing(object):
    """ HTML munging and other cleanup tasks that are common to both MM and MCD """
    def process_item(self, item, spider):
        # Don't bother adding items to the output if they are missing critical fields
        # Likely means they aren't articles at all
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
        if 'body' in item and item['body']:
            item['body'] = process_mm_html(item['body'],
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
        if 'body' in item and item['body']:
            item['body'] = process_mm_html(item['body'],
                spider.settings.get('DIVE_URL_REDIRECT_PATTERN'),
                hostname)
    # make url just the relative path, with no leading slash
        item['url'] = remove_hostname_from_url(item['url'],hostname)  # make url just the relative path
        # convert pub_date text to a real python datetime
        return item