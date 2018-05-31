from lxml import html
import requests
import json
from bunch import Bunch
import string
from slugify import slugify
import itertools, glob, os.path

def scrape_index_page(page_num):
    url = "https://www.rest.co.il/restaurants/israel/page-%s/" % (page_num, )
    print("Fetching index page %s - %s" % (page_num, url))
    page = requests.get(url)
    tree = html.fromstring(page.content)
    restaurants_urls = tree.xpath('//div[@class="RestInfo"]//a[@data-name="aRestName"]/@href')
    assert len(restaurants_urls) > 0, "failed getting results from %s" % (url, )
    json.dump(restaurants_urls, open("scraps/index-page-%s" % (page_num, ), "w"))
    print("Saved %s results from index page %s" % (len(restaurants_urls), page_num,))

# for i in range(94,95):
#     scrape_index_page(i)

def get_hours(row_element):
    return ", ".join([x.text.strip() for x in row_element.findall("div") if x.text is not None])

def xstrip(s):
    return s.strip("," + string.whitespace)

def scrape_restaurant_page(url):
    if url.startswith("/"):
        url = "http://rest.co.il" + url
    print("Fetching restaurant page %s..." % (url, ))
    page = requests.get(url)
    print("Fetched")
    tree = html.fromstring(page.content.decode(page.apparent_encoding))
    info = Bunch(url=url)
    stripped = [xstrip(t) for t in tree.xpath('//*[@class="RestaurantName"]//*/text()')]
    info.name = " ".join(t for t in stripped if t)
    info.address = ", ".join(xstrip(x) for x in tree.xpath('//*[@class="Address"]//span/text()'))
    maybe_phone = tree.xpath('//*[@class="OrginalPhone"]//span/text()')
    if len(maybe_phone) > 0:
        info.phone = maybe_phone[0].strip()
    info.hours = [get_hours(row) for row in tree.xpath('//*[@class="HoursRow"]')]
    maybe_menu = [e for e in tree.xpath('//*[@class="LinksRow"]//a[@href]') if e.text and u'תפריט' in e.text]
    if len(maybe_menu) > 0:
        info.menu_url = maybe_menu[0].attrib['href']
    return info

def scrape_restaurants_pages():
    all=list(itertools.chain.from_iterable([json.load(open(f)) for f in glob.glob("scraps/index-pages/*")]))
    standard = [x for x in all if x.startswith('/')]
    for url in standard:
        filename = "scraps/restaurants/%s" % (slugify(url), )
        if os.path.isfile(filename):
            print ("%s already exists" % (filename, ))
            continue
        info = scrape_restaurant_page(url)
        for k, v in info.items():
            print(k, ": ", v)
        print()
        json.dump(info, open(filename, "w"))


scrape_restaurants_pages()
