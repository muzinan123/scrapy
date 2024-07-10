# -*- coding: utf-8 -*-
import datetime as dt
import scrapy
from github.items import ProxyItem


class KuaidailiSpider(scrapy.Spider):
    type = 'proxy'
    name = "kuaidaili"
    allowed_domains = ["kuaidaili.com"]
    rotate_user_agent = True
    start_urls = (
        'http://www.kuaidaili.com/free/inha',
        'http://www.kuaidaili.com/free/intr',
        'http://www.kuaidaili.com/free/outha',
        'http://www.kuaidaili.com/free/outtr',
    )

    def parse(self, response):
        for tr in response.selector.xpath('//*[@id="list"]/table/tbody/tr'):
            item = ProxyItem()
            item['ip'] = tr.xpath('td[1]/text()').extract_first()
            item['port'] = tr.xpath('td[2]/text()').extract_first()
            anon = tr.xpath('td[3]/text()').extract_first()
            item['anon'] = 2 if anon == u'高匿名' else 1 if anon == u'匿名' else 0
            item['protocal'] = tr.xpath('td[4]/text()').extract_first()
            item['location'] = tr.xpath('td[5]/text()').extract_first()
            speed = tr.xpath('td[6]/text()').extract_first()
            try:
                speed = float(speed[:speed.index(u'秒')])
            except:
                speed = None
            item['speed'] = speed
            last_check = tr.xpath('td[7]/text()').extract_first()
            item['last_check'] = dt.datetime.strptime(
                last_check, '%Y-%m-%d %H:%M:%S')
            yield item
        active = response.xpath(
            '//*[@id="listnav"]/ul/li/a[@class="active"]/@href').extract_first()
        all = response.xpath(
            '//*[@id="listnav"]/ul/li/a/@href').extract()
        index = all.index(active)
        if index < len(all) - 1 and index < 20:
            url = response.urljoin(all[index+1])
            yield scrapy.Request(url, self.parse)
