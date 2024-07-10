# -*- coding: utf-8 -*-
import datetime as dt
import logging
import scrapy
from github.items import GithubItem
from github.webapp.scrapy_model import app, GithubRecord

keywords = app.config['GITHUB_KEYWORDS']
last_index = {keyword: GithubRecord.get_indexed_at_by_keyword(keyword)
              for keyword in keywords}


def cookie():
    cookie = '''_octo=GH1.1.1649128655.1464322021; logged_in=yes; dotcom_user=luxiao; _gh_sess=eyJzZXNzaW9uX2lkIjoiNTBmYjI0NTIxY2E1MzVkNjY1NGRjZTUyNGYwNjgzMGYiLCJzcHlfcmVwbyI6ImJlbm9pdGMvZ3VuaWNvcm4iLCJzcHlfcmVwb19hdCI6MTQ3MzgyNTQzMSwiY29udGV4dCI6Ii8iLCJyZXR1cm5fdG8iOiIvSWFtQWxjaGVtaXN0L0g1Q2FjaGUifQ%3D%3D--2a12134bf16ca129f9c54f56def0264efd5df5c4; user_session=lx-dNfXrcevGhxaWzyo9dpmUz8kD2kpycy433KCMDVzDAzI2V9kYfTOXY41SwOz28BOPPtGs42po6rDN; _ga=GA1.2.1023446304.1464322021; tz=Asia%2FShanghai'''
    cookie_dict = {}
    for a in cookie.split('; '):
        k, v = a.split('=')
        cookie_dict[k] = v


class GithubSpiderSpider(scrapy.Spider):
    name = "github_spider"
    rotate_user_agent = True
    allowed_domains = ["github.com"]
    keywords = app.config['GITHUB_KEYWORDS']
    start_urls = (
        u'https://github.com/search?o=desc&ref=searchresults&s=indexed&type=Code&q=stars:<10+%s&utf8=✓' % keyword
        for keyword in keywords
    )

    def parse(self, response):
        indexed_already = False
        for repo in response.selector.xpath(
                '//*[@id="code_search_results"]/div[1]/div'):
            item = GithubItem()
            item['keyword'] = keyword = repo.xpath(
                '//em/text()').extract_first()
            item['full_name'] = repo.xpath('p/a[1]/@href').extract_first()
            item['avatar'] = repo.xpath('a').extract_first()
            item['owner'], item['name'] = tuple(
                item['full_name'].split('/')[1:])
            item['file_path'] = repo.xpath('p/a[2]/@href').extract_first()
            item['file_name'] = repo.xpath('p/a[2]/text()').extract_first()
            item['snippet'] = repo.xpath('div').extract_first()
            lang = repo.xpath('span[@class="language"]/text()').extract()
            if lang:
                item['lang'] = lang[0].strip()
            else:
                item['lang'] = ''
            indexed_at = repo.xpath(
                'p/span[2]/relative-time/@datetime').extract_first()

            item['indexed_at'] = dt.datetime.strptime(
                indexed_at, '%Y-%m-%dT%H:%M:%SZ')
            if last_index[keyword] and item['indexed_at'] < last_index[keyword]:
                indexed_already = True
                logging.info(u'crawl to last indexed keyword %s. last indexed %s' % (keyword, str(last_index[keyword])))
            yield item
            # yield scrapy.Request(url, self.parse_repo(url))

        next_page = response.xpath(
            '//*[@id="code_search_results"]/div/div/a[@rel="next"]/@href')
        if next_page and not indexed_already:
            url = response.urljoin(next_page[0].extract())
            yield scrapy.Request(url, self.parse, cookies=cookie())
        else:
            logging.info(u'next_page is %s.' % next_page)

