# -*- coding: utf-8 -*-
import scrapy
import urllib
import os

image_dir = '/Users/lux/projects/ocr/img_samples'


class MayidailiSpider(scrapy.Spider):
    name = "mayidaili"
    rotate_user_agent = True
    allowed_domains = ["mayidaili.com"]
    start_urls = (
        'http://www.mayidaili.com/free',
    )

    def start_requests(self):
        cookies = {'Hm_lvt_dad083bfc015b67e98395a37701615ca': '1474532817,1474533118',
                  'Hm_lpvt_dad083bfc015b67e98395a37701615ca': '1474625282',
                  'proxy_token': 'icUdOeHm'}
        for url in MayidailiSpider.start_urls:
            yield scrapy.Request(
                url=url, callback=self.parse,
                headers={'referer': 'http://www.mayidaili.com/free'},
                cookies=cookies)

    def parse(self, response):
        for tr in response.selector.xpath('/html/body/div[4]/div/div[2]/table/tbody/tr'):
            print response.request.headers
            image_src = tr.xpath('td[2]/img/@data-uri').extract_first()
            print image_src
            image_name = image_src.rsplit('/', 1)[1]
            with open(os.path.join(image_dir, image_name), 'w') as img:
                img.write(urllib.urlopen(image_src).read())
