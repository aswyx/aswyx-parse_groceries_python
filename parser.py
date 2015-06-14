import http.cookiejar
import urllib.request as request
import re

from bs4 import BeautifulSoup


class Opener(object):
    def __init__(self, url):
        self.url = url
        self.cj = http.cookiejar.CookieJar()
        self.opener = request.build_opener(request.HTTPCookieProcessor(self.cj))

    def open(self):
        return self.opener.open(self.url)


class BaseParser(object):
    def __init__(self, response):
        self.document = BeautifulSoup(response)


class ProductDescriptionParser(BaseParser):
    def get_description(self):
        return ' '.join(
            [' '.join(p.text.strip().replace('\n', ' ').split()) for p in
             self.document.find('div', class_='productText').find_all('p')]
        )


class ProductListParser(BaseParser):
    @classmethod
    def format_file_size(cls, num):
        # not proper SI but works for now
        for unit in ['b', 'kb', 'mb', 'gb', 'tb', 'pb', 'eb']:
            if abs(num) < 1024.0:
                return "%3.1f%s" % (num, unit)
            num /= 1024.0
        return "%.1f%s" % (num, 'eb')

    @classmethod
    def get_product_title(cls, product):
        return product.find('h3').text.strip()

    @classmethod
    def get_product_link(cls, product):
        return product.find('h3').find('a')['href'].strip()

    @classmethod
    def get_product_price(cls, product):
        return float(re.search(r'\d+.\d+', product.find('p', class_='pricePerUnit').find(text=True)).group())

    @classmethod
    def get_description_info(cls, product_url):
        opener = Opener(product_url)
        description_response = opener.open()
        description_content = description_response.read()
        size = int(description_response.headers.get('content-length', len(description_content)))
        return description_content, size

    @classmethod
    def parse_product(cls, product):
        description_response, page_size = cls.get_description_info(cls.get_product_link(product))
        return {
            'title': cls.get_product_title(product),
            'size': cls.format_file_size(page_size),
            'unit_price': cls.get_product_price(product),
            'description': ProductDescriptionParser(description_response).get_description(),
        }

    def get_products(self):
        return self.document.find_all('div', class_='product')

    def parse(self):
        products = [self.parse_product(product) for product in self.get_products()]
        return {
            'results': products,
            'total': sum([product['unit_price'] for product in products])
        }
