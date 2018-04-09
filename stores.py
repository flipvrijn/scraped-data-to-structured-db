import re
from io import StringIO

import lxml.html as lh


def query_if_exists(root, query):
	node = root.xpath(query)
	return node[0].strip() if node else ''

class Store():
	'''Base class for parsing a store website'''
	def __init__(self):
		self.product_pages = {}
		self.overview_pages = []
		
	def parse(self, json_obj):
		"""Calls the correct parsing function for the type of json object"""
		if json_obj['page_type'] == 'product_detail':
			product_info = self.parse_detail_page(json_obj)
			self.product_pages[product_info['product_page']] = product_info
		elif json_obj['page_type'] == 'product_listing':
			overview_info = self.parse_overview_page(json_obj)
			self.overview_pages.append(overview_info)
		else:
			raise Exception('Unknown page type at line {}!'.format(i))

	def parse_detail_page(self, json_obj):
		"""Parses a product detail page and returns a dictionary of product information"""
		raise Exception('Parsing detail page not implemented yet!')

	def parse_overview_page(self, json_obj):
		"""Parses an overview page and returns a dictionary of information"""
		raise Exception('Parsing overview page not implemented yet!')

class Omoda(Store):
	name = 'Omoda'

	def parse_detail_page(self, json_obj):
		info = {}

		root = lh.parse(StringIO(unicode(json_obj['body'])))

		info['brand'] 		 = query_if_exists(root, '//h2[@itemprop="brand"]/text()')
		info['product_name'] = query_if_exists(root, '//h1[@itemprop="name"]/text()')
		info['product_type'] = ''
		info['price'] 		 = query_if_exists(root, '//div[@id="artikel-prijs"]/meta[@itemprop="price"]/@content').replace(',', '.')
		info['product_page'] = json_obj['page_url']

		return info

	def parse_overview_page(self, json_obj):
		info = {}
		
		root = lh.parse(StringIO(unicode(json_obj['body'])))
		
		info['product_category'] = json_obj['product_category']
		info['page_number']      = json_obj['page_number']
		info['product_urls'] 	 = root.xpath('//a[contains(@class, "artikel-link")]/@href')

		return info

class Ziengs(Store):
	name = 'Ziengs'

	def parse_detail_page(self, json_obj):
		info = {}

		root = lh.parse(StringIO(unicode(json_obj['body'])))

		info['brand'] = query_if_exists(root, '//meta[@itemprop="brand"]/@content')
		info['product_name'] = query_if_exists(root, '//h1[@itemprop="name"]/text()')
		info['product_type'] = ''
		info['price'] = query_if_exists(root, '//meta[@itemprop="price"]/@content')
		info['product_page'] = json_obj['page_url']

		return info

	def parse_overview_page(self, json_obj):
		info = {}

		root = lh.parse(StringIO(unicode(json_obj['body'])))

		info['product_category'] = json_obj['product_category']
		info['page_number']      = json_obj['page_number']
		links = root.xpath('//div[contains(@class, "thumb")]/a/@href')
		info['product_urls'] 	 = ['http://www.ziengs.nl/{}'.format(link.replace('../', '')) for link in links]

		return info

class Zalando(Store):
	name = 'Zalando'

	def parse_detail_page(self, json_obj):
		info = {}

		root = lh.parse(StringIO(unicode(json_obj['body'])))

		info['brand'] = query_if_exists(root, '//span[@itemprop="brand"]/text()')
		info['product_name'] = query_if_exists(root, '//span[@itemprop="name"]/text()')
		info['product_type'] = ''
		price = query_if_exists(root, '//span[@itemprop="price"]/text()')
		if not price:
			price = query_if_exists(root, '//span[@id="articlePrice"]/text()')
		m = re.search('(\d+),(\d+)', price)
		if m:
			price = '{}.{}'.format(m.group(1), m.group(2))
		info['price'] = price
		info['product_page'] = json_obj['page_url']

		return info

	def parse_overview_page(self, json_obj):
		info = {}

		root = lh.parse(StringIO(unicode(json_obj['body'])))

		info['product_category'] = json_obj['product_category']
		info['page_number']      = json_obj['page_number']
		links = root.xpath('//a[@class="catalogArticlesList_productBox"]/@href')
		info['product_urls'] 	 = ['https://www.zalando.nl/{}'.format(link.replace('/', '')) for link in links]

		return info
