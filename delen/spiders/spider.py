import scrapy

from scrapy.loader import ItemLoader
from ..items import DelenItem
from itemloaders.processors import TakeFirst


class DelenSpider(scrapy.Spider):
	name = 'delen'
	start_urls = ['https://www.delen.lu/nl/nieuws?sc_lang=nl-be']

	def parse(self, response):
		post_links = response.xpath('//div[@class="o-media-block o-filters__target"]')
		for post in post_links:
			url = post.xpath('.//a[@class="o-media-block__image-wrapper"]/@href').get()
			date = post.xpath('.//div[@class="o-media-block__label"]//text()').get()
			yield response.follow(url, self.parse_post, cb_kwargs=dict(date=date))

	def parse_post(self, response, date):
		title = response.xpath('//div[@class="o-editable"]/h1/text()').get()
		description = response.xpath('//div[@class="o-editable"]//text()[normalize-space() and not(ancestor::h1 | ancestor::p[@class="c-metabox"])]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()
		date = date.split('|')[0]

		item = ItemLoader(item=DelenItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
