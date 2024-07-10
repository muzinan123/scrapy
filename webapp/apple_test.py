from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from lxml import etree
import logging
import datetime as dt
import time

from scrapy_model import GithubRecord

keyword = 'zhongan'
last_index = {keyword: GithubRecord.get_indexed_at_by_keyword(keyword)}
now = dt.datetime.now
# last_index = {keyword: now() - dt.timedelta(hours=1)}

def test():
    # driver = webdriver.PhantomJS()
    driver = webdriver.Chrome()
    #driver = webdriver.Firefox()
    github = 'https://www.tmall.com/'
    driver.get(github)
    '''
    
    # cart click
    elem = driver.find_element_by_id("mc-menu-hd")
    elem.click()

    # login
    login = driver.find_element_by_name("TPL_username")
    login.send_keys('damncaste')
    passwd = driver.find_element_by_name("TPL_password")
    passwd.send_keys('#')
    passwd.send_keys(Keys.RETURN)

    
    # cart 
    elem = driver.find_element_by_id("J_SelectAll2")
    elem.click()

    # code
    elem = driver.find_element_by_xpath('//*[@id="js-pjax-container"]/div[2]/div/div[1]/nav/a[2]')
    elem.click()
    '''
    # wait

    try:
        #time 
        #while(now() < now()+delta):
        static = '//*[@id="mc-menu-hd"]'
        sort = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, static))
        )
        sort.click()

        # cart 
        elem = driver.find_element_by_id("J_Quick2Static")
        elem.click()
        
        login = driver.find_element_by_name("TPL_username")
        login.send_keys('damncaste')
        passwd = driver.find_element_by_name("TPL_password")
        passwd.send_keys('#')
        passwd.send_keys(Keys.RETURN)

        # cart click
        elem = driver.find_element_by_id("mc-menu-hd")
        elem.send_keys(keyword)
        elem.send_keys(Keys.RETURN)

        # cart 
        elem = driver.find_element_by_id("J_SelectAll2")
        elem.send_keys(keyword)
        elem.send_keys(Keys.RETURN)
        elem = driver.find_element_by_class("go-btn")
        elem.send_keys(keyword)
        elem.send_keys(Keys.RETURN)
    finally:
        driver.quit()


def parse(driver):
    html = etree.HTML(driver.page_source.encode('utf-8'))
    indexed_already = False
    for repo in html.xpath('//*[@id="code_search_results"]/div[1]/div'):
        item = {}
        item['keyword'] = keyword = repo.xpath('//em/text()')[0].lower()
        item['full_name'] = repo.xpath('p/a[1]/@href')[0]
        item['avatar'] = etree.tostring(repo.xpath('a')[0])
        item['owner'], item['name'] = tuple(
            item['full_name'].split('/')[1:])
        item['file_path'] = repo.xpath('p/a[2]/@href')[0]
        item['file_name'] = repo.xpath('p/a[2]/text()')[0]
        item['snippet'] = etree.tostring(repo.xpath('div')[0])
        lang = repo.xpath('span[@class="language"]/text()')
        if lang:
            item['lang'] = lang[0].strip()
        else:
            item['lang'] = ''
        lang_white_list = [
            'TEXT', 'INI', 'MARKDOWN', 'CSV', 'VUE', 'JAVASCRIPT', 'HTML', 'JSON']
        if item['lang'].upper() in lang_white_list:
            continue
        indexed_at = repo.xpath(
            'p/span[2]/relative-time/@datetime')[0]

        item['indexed_at'] = dt.datetime.strptime(
            indexed_at, '%Y-%m-%dT%H:%M:%SZ')
        write2db(item)
        # print item

        if last_index[keyword] and item['indexed_at'] < last_index[keyword]:
            indexed_already = True
            logging.info(u'crawl to last indexed keyword %s. last indexed %s' % (keyword, str(last_index[keyword])))
            break
        else:
            print item['indexed_at'], last_index[keyword]


    next_page = driver.find_element_by_xpath(
        '//*[@id="code_search_results"]/div/div/a[@rel="next"]')
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
