# -*- coding: utf-8 -*-

import requests
import scrapy

from scrapy.loader import ItemLoader

from ..items import BsicbankItem
from itemloaders.processors import TakeFirst


class BsicbankSpider(scrapy.Spider):
	name = 'bsicbank'
	start_urls = ['http://www.bsicbank.com/']

	def parse(self, response):
		data = requests.request("GET", 'http://www.bsicbank.com//category/%D8%A3%D8%AE%D8%A8%D8%A7%D8%B1')
		data = scrapy.Selector(text=data.text)
		post_links = data.xpath('//ul[@class="category-list"]/li/a/@href').getall()
		for foo in post_links:
			url = foo.encode('Latin-1').decode('UTF-8')
			yield response.follow(url, self.parse_post)

		next_page = data.xpath('//a[@class="pagearrow"]/@href').getall()
		yield from response.follow_all(next_page, self.parse)

	def parse_post(self, response):
		title = response.xpath('//h2/text()').get()
		print(response)
		description = response.xpath('//div[@class="blog-post-description"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description if '{' not in p]
		description = ' '.join(description).strip()
		date = response.xpath('//div[@class="blog-post-time ml-0"]/a/i/text()[normalize-space()]').get()

		item = ItemLoader(item=BsicbankItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
