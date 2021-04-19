# -*- coding: utf-8 -*-

import requests
import scrapy

from scrapy.loader import ItemLoader

from ..items import BsicbankItem
from itemloaders.processors import TakeFirst


class BsicbankSpider(scrapy.Spider):
	name = 'bsicbank'
	start_urls = ['http://www.bsicbank.com/']
	page_link = 'http://www.bsicbank.com//category/%D8%A3%D8%AE%D8%A8%D8%A7%D8%B1'
	next_page = []

	def parse(self, response):
		print(self.page_link)
		data = requests.request("GET", self.page_link)
		data = scrapy.Selector(text=data.text)
		post_links = data.xpath('//ul[@class="category-list"]/li/a/@href').getall()
		for foo in post_links:
			url = foo.encode('Latin-1').decode('UTF-8')
			yield response.follow(url, self.parse_post)

		try:
			self.page_link = data.xpath('//a[@class="pagearrow"][img[@alt="Next"]]/@href').get().encode('Latin-1')
		except:
			return
		if self.page_link in self.next_page:
			return
		else:
			self.next_page.append(self.page_link)
		yield response.follow(response.url, self.parse, dont_filter=True)

	def parse_post(self, response):
		title = response.xpath('//h2/text()').get()
		description = response.xpath('//div[@class="blog-post-description"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description if '{' not in p]
		description = ' '.join(description).strip()
		date = response.xpath('//div[@class="blog-post-time ml-0"]/a//text()[normalize-space()]').get()

		item = ItemLoader(item=BsicbankItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
