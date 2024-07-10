# -*- coding: utf-8 -*-
import datetime as dt
import scrapy
from github.items import ProxyItem


class XicidailiSpider(scrapy.Spider):
    type = 'proxy'
    name = "xicidaili"
    allowed_domains = ["xicidaili.com"]
    rotate_user_agent = True
    start_urls = (
        'http://www.xicidaili.com/nn',
        'http://www.xicidaili.com/nt',
        'http://www.xicidaili.com/wn',
        'http://www.xicidaili.com/wt',
    )

    def parse(self, response):
        for tr in response.selector.xpath('//*[@id="ip_list"]/tr'):
            item = ProxyItem()
            item['ip'] = tr.xpath('td[2]/text()').extract_first()
            item['port'] = tr.xpath('td[3]/text()').extract_first()
            anon = tr.xpath('td[5]/text()').extract_first()
            item['anon'] = 2 if anon == u'高匿' else 1 if anon == u'匿名' else 0
            item['protocal'] = tr.xpath('td[6]/text()').extract_first()
            item['location'] = tr.xpath('td[4]/text()').extract_first()
            speed = tr.xpath('td[7]/div/@title').extract_first()
            try:
                speed = float(speed[:speed.index(u'秒')])
            except:
                speed = None
            item['speed'] = speed
            last_check = tr.xpath('td[10]/text()').extract_first()
            if last_check:
                item['last_check'] = dt.datetime.strptime(
                    last_check, '%y-%m-%d %H:%M')
            yield item
        next = response.xpath('//*[@id="body"]/div[2]/a[@rel="next"]/@href').extract_first()
        page_number = response.xpath('//*[@id="body"]/div[2]/a[@rel="next"]/text()').extract_first()
        if next and int(page_number) < 20:
            url = response.urljoin(next)
            yield scrapy.Request(url, self.parse)
