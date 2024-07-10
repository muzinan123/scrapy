# -*- coding: utf-8 -*-
import scrapy


class HidemyassSpiderSpider(scrapy.Spider):
    name = "hidemyass_spider"
    allowed_domains = ["hidemyass.com"]
    start_urls = (
        'http://www.github/',
    )

    def parse(self, response):
        pass
