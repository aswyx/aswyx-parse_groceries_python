from unittest.case import TestCase
from unittest.mock import patch
import urllib.parse as parse
import urllib.request as request
import os

from parser import Opener, ProductListParser, ProductDescriptionParser


def path2url(filename):
    path = os.path.abspath(filename)
    return parse.urljoin('file:', request.pathname2url(path))


class TestParsingGroceries(TestCase):
    start_page_file = 'test_data/sains1.html'
    description_page_path = 'test_data/sains2.html'

    @classmethod
    def setUpClass(cls):
        cls.list_parser = ProductListParser(Opener(url=path2url(cls.start_page_file)).open())
        cls.products = cls.list_parser.get_products()

    def test_opener(self):
        with open(self.start_page_file, 'rb') as start_page:
            self.assertEqual(start_page.read(), Opener(url=path2url(self.start_page_file)).open().read())

    def test_parser_finds_all_products(self):
        self.assertEqual(12, len(self.products))

    def test_get_product_titles(self):
        expected_titles = [
            "Sainsbury's Apricot Ripe & Ready 320g",
            "Sainsbury's Avocado Ripe & Ready XL Loose 300g",
            "Sainsbury's Avocado, Ripe & Ready x2",
            "Sainsbury's Avocados, Ripe & Ready x4",
            "Sainsbury's Conference Pears, Ripe & Ready x4 (minimum)",
            "Sainsbury's Kiwi Fruit, Ripe & Ready x4",
            "Sainsbury's Mango, Ripe & Ready x2",
            "Sainsbury's Nectarines, Ripe & Ready x4",
            "Sainsbury's Peaches Ripe & Ready x4",
            "Sainsbury's Pears, Ripe & Ready x4 (minimum)",
            "Sainsbury's Plums Ripe & Ready x5",
            "Sainsbury's White Flesh Nectarines, Ripe & Ready x4"
        ]
        parsed_titles = [self.list_parser.get_product_title(product) for product in self.products]
        self.assertEqual(expected_titles, parsed_titles)

    def test_get_product_links(self):
        expected_links = [
            "http://www.sainsburys.co.uk/shop/gb/groceries/ripe---ready/sainsburys-apricot-ripe---ready-320g",
            "http://www.sainsburys.co.uk/shop/gb/groceries/ripe---ready/sainsburys-avocado-xl-pinkerton-loose-300g",
            "http://www.sainsburys.co.uk/shop/gb/groceries/ripe---ready/sainsburys-avocado--ripe---ready-x2",
            "http://www.sainsburys.co.uk/shop/gb/groceries/ripe---ready/sainsburys-avocados--ripe---ready-x4",
            "http://www.sainsburys.co.uk/shop/gb/groceries/ripe---ready/sainsburys-conference-pears--ripe---ready-x4-%28minimum%29",  # noqa
            "http://www.sainsburys.co.uk/shop/gb/groceries/ripe---ready/sainsburys-kiwi-fruit--ripe---ready-x4",
            "http://www.sainsburys.co.uk/shop/gb/groceries/ripe---ready/sainsburys-mango--ripe---ready-x2",
            "http://www.sainsburys.co.uk/shop/gb/groceries/ripe---ready/sainsburys-nectarines--ripe---ready-x4",
            "http://www.sainsburys.co.uk/shop/gb/groceries/ripe---ready/sainsburys-peaches-ripe---ready-x4",
            "http://www.sainsburys.co.uk/shop/gb/groceries/ripe---ready/sainsburys-pears--ripe---ready-x4-%28minimum%29",  # noqa
            "http://www.sainsburys.co.uk/shop/gb/groceries/ripe---ready/sainsburys-plums--firm---sweet-x4-%28minimum%29",  # noqa
            "http://www.sainsburys.co.uk/shop/gb/groceries/ripe---ready/sainsburys-white-flesh-nectarines--ripe---ready-x4"  # noqa
        ]

        parsed_links = [self.list_parser.get_product_link(product) for product in self.products]
        self.assertEqual(expected_links, parsed_links)

    def test_get_product_prices(self):
        expected_prices = [3.0, 1.5, 1.8, 3.2, 2.0, 1.8, 2.0, 2.0, 2.0, 2.0, 2.5, 2.0]
        parsed_prices = [self.list_parser.get_product_price(product) for product in self.products]
        self.assertEqual(expected_prices, parsed_prices)

    def test_get_description_info(self):
        description_content, page_size = self.list_parser.get_description_info(
            product_url=path2url(self.description_page_path))
        with open(self.description_page_path, 'rb') as description_page:
            page_content = description_page.read()
            self.assertEqual(page_content, description_content)
            self.assertEqual(len(page_content), page_size)

    def test_get_product_description(self):
        description_content, page_size = self.list_parser.get_description_info(
            product_url=path2url(self.description_page_path))
        description_parser = ProductDescriptionParser(description_content)
        description = description_parser.get_description()
        self.assertEqual('Ripe & ready', description)

    @patch('parser.ProductListParser.get_product_link', return_value=path2url(description_page_path))
    def test_parse_product(self, mock_get_product_link):
        expected_products = [
            {
                'unit_price': 3.0,
                'title': "Sainsbury's Apricot Ripe & Ready 320g",
                'description': 'Ripe & ready',
                'size': '52.9kb'
            },
            {
                'unit_price': 1.5,
                'title': "Sainsbury's Avocado Ripe & Ready XL Loose 300g",
                'description': 'Ripe & ready',
                'size': '52.9kb'
            },
            {
                'unit_price': 1.8,
                'title': "Sainsbury's Avocado, Ripe & Ready x2",
                'description': 'Ripe & ready',
                'size': '52.9kb'
            },
            {
                'unit_price': 3.2,
                'title': "Sainsbury's Avocados, Ripe & Ready x4",
                'description': 'Ripe & ready',
                'size': '52.9kb'},
            {
                'unit_price': 2.0,
                'title': "Sainsbury's Conference Pears, Ripe & Ready x4 (minimum)",
                'description': 'Ripe & ready',
                'size': '52.9kb'
            },
            {
                'unit_price': 1.8,
                'title': "Sainsbury's Kiwi Fruit, Ripe & Ready x4",
                'description': 'Ripe & ready',
                'size': '52.9kb'
            },
            {
                'unit_price': 2.0,
                'title': "Sainsbury's Mango, Ripe & Ready x2",
                'description': 'Ripe & ready',
                'size': '52.9kb'},
            {
                'unit_price': 2.0,
                'title': "Sainsbury's Nectarines, Ripe & Ready x4",
                'description': 'Ripe & ready',
                'size': '52.9kb'},
            {
                'unit_price': 2.0,
                'title': "Sainsbury's Peaches Ripe & Ready x4",
                'description': 'Ripe & ready',
                'size': '52.9kb'},
            {
                'unit_price': 2.0,
                'title': "Sainsbury's Pears, Ripe & Ready x4 (minimum)",
                'description': 'Ripe & ready',
                'size': '52.9kb'
            },
            {
                'unit_price': 2.5,
                'title': "Sainsbury's Plums Ripe & Ready x5",
                'description': 'Ripe & ready',
                'size': '52.9kb'
            },
            {'unit_price': 2.0,
             'title': "Sainsbury's White Flesh Nectarines, Ripe & Ready x4",
             'description': 'Ripe & ready',
             'size': '52.9kb'
             }
        ]

        parsed_products = [self.list_parser.parse_product(product) for product in self.products]
        self.assertEqual(expected_products, parsed_products)
        self.assertEqual(12, len(mock_get_product_link.mock_calls))

    @patch('parser.ProductListParser.get_product_link', return_value=path2url(description_page_path))
    def test_full_parse(self, mock_get_product_link):
        expected_response = {
            'total': 25.8,
            'results': [
                {
                    'unit_price': 3.0,
                    'title': "Sainsbury's Apricot Ripe & Ready 320g",
                    'description': 'Ripe & ready',
                    'size': '52.9kb'
                },
                {
                    'unit_price': 1.5,
                    'title': "Sainsbury's Avocado Ripe & Ready XL Loose 300g",
                    'description': 'Ripe & ready',
                    'size': '52.9kb'
                },
                {
                    'unit_price': 1.8,
                    'title': "Sainsbury's Avocado, Ripe & Ready x2",
                    'description': 'Ripe & ready',
                    'size': '52.9kb'
                },
                {
                    'unit_price': 3.2,
                    'title': "Sainsbury's Avocados, Ripe & Ready x4",
                    'description': 'Ripe & ready',
                    'size': '52.9kb'},
                {
                    'unit_price': 2.0,
                    'title': "Sainsbury's Conference Pears, Ripe & Ready x4 (minimum)",
                    'description': 'Ripe & ready',
                    'size': '52.9kb'
                },
                {
                    'unit_price': 1.8,
                    'title': "Sainsbury's Kiwi Fruit, Ripe & Ready x4",
                    'description': 'Ripe & ready',
                    'size': '52.9kb'
                },
                {
                    'unit_price': 2.0,
                    'title': "Sainsbury's Mango, Ripe & Ready x2",
                    'description': 'Ripe & ready',
                    'size': '52.9kb'},
                {
                    'unit_price': 2.0,
                    'title': "Sainsbury's Nectarines, Ripe & Ready x4",
                    'description': 'Ripe & ready',
                    'size': '52.9kb'},
                {
                    'unit_price': 2.0,
                    'title': "Sainsbury's Peaches Ripe & Ready x4",
                    'description': 'Ripe & ready',
                    'size': '52.9kb'},
                {
                    'unit_price': 2.0,
                    'title': "Sainsbury's Pears, Ripe & Ready x4 (minimum)",
                    'description': 'Ripe & ready',
                    'size': '52.9kb'
                },
                {
                    'unit_price': 2.5,
                    'title': "Sainsbury's Plums Ripe & Ready x5",
                    'description': 'Ripe & ready',
                    'size': '52.9kb'
                },
                {'unit_price': 2.0,
                 'title': "Sainsbury's White Flesh Nectarines, Ripe & Ready x4",
                 'description': 'Ripe & ready',
                 'size': '52.9kb'
                 }
            ]
        }

        self.assertEqual(expected_response, self.list_parser.parse())
        self.assertEqual(12, len(mock_get_product_link.mock_calls))

    def test_file_size_formatter(self):
        test_values = []
        p = 1
        for _ in range(1, 7):
            test_values.append(p)
            test_values.append(p * 1.5)
            p *= 1024
        expected_values = [
            '1.0b', '1.5b', '1.0kb', '1.5kb', '1.0mb', '1.5mb', '1.0gb', '1.5gb', '1.0tb', '1.5tb', '1.0pb', '1.5pb'
        ]
        self.assertEqual(expected_values, [self.list_parser.format_file_size(number) for number in test_values])
