# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GithubItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    keyword = scrapy.Field()
    full_name = scrapy.Field()
    name = scrapy.Field()
    owner = scrapy.Field()
    file_path = scrapy.Field()
    file_name = scrapy.Field()
    lang = scrapy.Field()
    snippet = scrapy.Field()
    indexed_at = scrapy.Field()
    avatar = scrapy.Field()


class ProxyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    ip = scrapy.Field()
    port = scrapy.Field()
    anon = scrapy.Field()
    protocal = scrapy.Field()
    location = scrapy.Field()
    speed = scrapy.Field()
    last_check = scrapy.Field()
