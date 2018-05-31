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


#scrape_restaurants_pages()

def parse_price(s):
    return float(s.replace('₪','').strip())

def scrape_rest_menu(content):
    import re
    the_re = re.compile("(^\s*\d+\s*₪\s*$|^\s*₪\s*\d+\s*$)")

    def price_pred(e):
        return e.contents and bool(the_re.search(str(e.contents[0])))

    def find_dish_name(e):
        price_string = e.string
        while True:
#            print("checking: ", e)
            for child in e.find_all():
                s = child.string
                if s and len(s) > 2 and s != price_string:
#                    print("found: ", child.string)
                    return s
            e = e.parent

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(content, 'html.parser')
    price_elements = soup.find_all(price_pred)
    dishes = []
    for e in price_elements:
        if not e.string:
            continue
        dishes.append(dict(price=parse_price(e.string),
                           name=find_dish_name(e)))
    return dishes

def scrape_mishlohim_menu(content):
    tree = html.fromstring(content)
    dishes = []
    for e in tree.xpath('//*[@class="row-item"]'):
        maybe_price = e.xpath('.//p[@class="price"]/text()')
        if (len(maybe_price) == 0):
            continue
        dishes.append(dict(price=parse_price(maybe_price[0]),
                           name=e.xpath('.//*[@class="title"]/text()')[0]))
    return dishes

def scrape_menu(url):
    if url.startswith("/"):
        url = "http://rest.co.il" + url
    print("Fetching menu page %s..." % (url, ))
    try:
        page = requests.get(url)
    except:
        print("failed fetching from %s" % (url, ))
        return dict(url=url, dishes=[])
    print("Fetched")
    try:
        content = page.content.decode(page.apparent_encoding)
    except:
        print("failed decoding content of %s" % (url, ))
        return dict(url=url, dishes=[])
    if "mishlohim" in url:
        dishes = scrape_mishlohim_menu(content)
    else:
        dishes = scrape_rest_menu(content)
    return dict(url=url, dishes=dishes)

def scrape_all_menues():
    for restaurant_file in glob.glob("scraps/restaurants/*"):
        menu_file = restaurant_file.replace("restaurants", "menus")
        if os.path.isfile(menu_file):
            print ("%s already exists" % (menu_file, ))
            continue
        info = json.load(open(restaurant_file))
        if "menu_url" not in info:
            print ("%s does not have a menu url" % (restaurant_file, ))
            continue
        url = info["menu_url"]
        if url.endswith("pdf"):
            print ("%s has a pdf menu: %s" % (restaurant_file, url))
            continue
        menu = scrape_menu(url)
        for dish in menu["dishes"]:
            print("%5s %60s" % (dish["price"], dish["name"]))
        print()
        json.dump(menu, open(menu_file, "w"))

#print(scrape_mishlohim_menu())
#print(scrape_rest_menu())
scrape_all_menues()
