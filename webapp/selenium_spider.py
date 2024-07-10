# -*- coding: utf-8 -*-
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from lxml import etree
import logging
import datetime as dt

from scrapy_model import GithubRecord, send_mail, today_alarmed

keyword = 'zhongan'
last_index = {keyword: GithubRecord.get_indexed_at_by_keyword(keyword)}
now = dt.datetime.now
# last_index = {keyword: now() - dt.timedelta(hours=1)}

def test():
    try:
        # driver = webdriver.PhantomJS()
        #driver = webdriver.Chrome()
        driver = webdriver.Firefox()
        github = 'https://github.com/login'
        driver.get(github)

        # login
        login = driver.find_element_by_name("login")
        login.send_keys('app_xx01@163.com')
        passwd = driver.find_element_by_name("password")
        passwd.send_keys('luxiao1223')
        passwd.send_keys(Keys.RETURN)

        # query
        elem = driver.find_element_by_name("q")
        elem.send_keys(keyword)
        elem.send_keys(Keys.RETURN)

        # code
        code_path = '//*[@id="js-pjax-container"]/div/div[2]/nav[1]/a[2]'
        elem = driver.find_element_by_xpath(code_path)
        elem.click()

        # wait
        time.sleep(3)
        path = '//*[@id="js-pjax-container"]/div/div[3]/div/div[1]/details/summary'
        sort = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, path))
        )
        sort.click()
        time.sleep(3)
        last = '//*[@id="js-pjax-container"]/div/div[3]/div/div[1]/details/details-menu/div[2]/a[2]'
        recently = driver.find_element_by_xpath(last)
        recently.click()
        time.sleep(3)
        parse(driver)
        send_mail('zasrc@zhongan.io, zasrc@zhongan.com',
                  u'Github代码爬虫成功结束',
                  u'Github代码爬虫成功结束，%d' % len(today_alarmed))
    except Exception as e:
        print str(e)
        send_mail('zasrc@zhongan.io, zasrc@zhongan.com',
                  u'Github代码爬虫执行失败',
                  u'Github代码爬虫执行失败: \n%s' % str(e))
    finally:
        driver.quit()


def parse(driver):
    html = etree.HTML(driver.page_source.encode('utf-8'))
    indexed_already = False
    for repo in html.xpath('//*[@id="code_search_results"]/div[1]/div'):
        item = {}
        item['keyword'] = keyword
        item['full_name'] = repo.xpath('div/div[1]/a/@href')[0]
        # item['avatar'] = etree.tostring(repo.xpath('div/a')[0])
        item['avatar'] = 'avatar'
        item['owner'], item['name'] = tuple(
            item['full_name'].split('/')[1:])
        item['file_path'] = repo.xpath('div/div[2]/a/@href')[0]

        item['file_name'] = repo.xpath('div/div[2]/a/text()')[0]
        item['snippet'] = etree.tostring(repo.xpath('div/div[3]')[0])
        # code_search_results > div.code-list > div:nth-child(1) > div.file-box.blob-wrapper
        lang = repo.xpath('div/div[4]/div/span/span[2]/text()')
        if lang:
            item['lang'] = lang[0].strip()
        else:
            item['lang'] = ''
        lang_white_list = ['SCSS', 'GPERF', 'TEXT', 'PUG', 'MARKDOWN', 'CSV',
                           'VUE', 'JAVASCRIPT', 'HTML', 'JSON', 'TEX', 'JSX']

        if item['lang'].upper() in lang_white_list:
            continue

        indexed_at = repo.xpath(
            'div/div[4]/span[2]/relative-time/@datetime')[0]

        item['indexed_at'] = dt.datetime.strptime(
            indexed_at, '%Y-%m-%dT%H:%M:%SZ')
        write2db(item)
        # print item

        if last_index[keyword] and item['indexed_at'] < last_index[keyword]:
            indexed_already = True
            print(u'crawl to last indexed keyword %s. last indexed %s' % (keyword, str(last_index[keyword])))
            break
        else:
            print item['indexed_at'], last_index[keyword]

    next_page = driver.find_element_by_xpath(
        '//*[@id="code_search_results"]/div[2]/div/a[@rel="next"]')
    if next_page and not indexed_already:
        next_page.click()
        parse(driver)
    else:
        logging.info(u'next_page is %s.' % next_page)


def write2db(item):
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


if __name__ == '__main__':
    import time
    import random
    seconds = random.randint(1, 60)
    time.sleep(seconds)
    test()
