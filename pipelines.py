# -*- coding: utf-8 -*-
import logging
from spiders import GithubSpiderSpider, KuaidailiSpider


# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class GithubPipeline(object):
    def process_item(self, item, spider):
        if isinstance(spider, GithubSpiderSpider):
            from github.webapp.scrapy_model import GithubRecord
            record = GithubRecord.get_by_uk(
                item['full_name'], item['file_path'], item['keyword'])
            if not record:
                record = GithubRecord.create(
                    item['full_name'], item['name'], item['keyword'],
                    item['owner'], item['file_path'], item['lang'],
                    item['snippet'], item['indexed_at'], item['avatar'],
                    item['file_name'])
            else:
                logging.info('Duplicate github file')
        elif spider.type == 'proxy':
            from github.webapp.scrapy_model import Proxy
            try:
                if Proxy.verify(item['ip'], int(item['port']), item['protocal']):
                    Proxy(item['protocal'], item['ip'], item['port'],
                          location=item['location'], anon=item['anon'],
                          speed=item['speed'], clast_check=item['last_check'],
                          src=spider.name).save()
                else:
                    logging.info('proxy time out')
            except Exception as e:
                logging.warning(str(e))
