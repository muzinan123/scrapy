# -*- coding: utf-8 -*-
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


def run_process():
    process = CrawlerProcess(get_project_settings())

    # 'github' is the name of one of the spiders of the project.
    process.crawl('github', domain='github.com')
    process.start()
    # the script will block here until the crawling is finished

if __name__ == '__main__':
   print 'start crawl'
   run_process()
   print 'end crawl'
