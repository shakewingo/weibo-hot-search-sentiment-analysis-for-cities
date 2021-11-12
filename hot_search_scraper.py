import pandas as pd
import numpy as np
import csv
import time
import selenium.webdriver as webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from googletrans import Translator

translator = Translator()
oversee_city_trans = translator.translate('Mexico City', src='en', dest='zh-cn').text

def get_results(search_item):
    url = 'https://weibo.zhaoyizhe.com/'  # the earliest is recorded back to 2019-10-26
    # automatically download latest version of Chrome
    browser = webdriver.Chrome(ChromeDriverManager().install())
    browser.get(url)
    # search key word
    search_place = browser.find_element_by_xpath('//input[@placeholder="输入你想搜索的热搜关键字"]')
    search_place.send_keys(search_item)
    browser.find_element_by_xpath('//div[@class="ivu-input-group-append ivu-input-search"]').click()
    # wait until several seconds until the ad pops up
    time.sleep(20)
    try:
        # close pop-up window
        browser.find_element_by_xpath('//button[@class="el-button el-button--default el-button--small el-button--primary "]').click()
    except Exception as e:
        pass
    # extract attribute value
    topics = BeautifulSoup(browser.page_source, 'html.parser').find_all('span', {'style': 'font-weight: bold;'})
    durations = BeautifulSoup(browser.page_source, 'html.parser').find_all('td', {'class': 'el-table_1_column_2 is-center'})
    index = BeautifulSoup(browser.page_source, 'html.parser').find_all('td', {'class': 'el-table_1_column_3 is-center'})
    event_time = BeautifulSoup(browser.page_source, 'html.parser').find_all('td', {'class': 'el-table_1_column_4'})
    # check no missing data per event
    assert len(topics) == len(durations) == len(index) == len(event_time), 'Received mismatched length of attribute!'

    for i, j, k, v in zip(topics, durations, index, event_time):
        # print(i.text.strip('#'), j.text, k.text, v.text)
        new_result = {'city': search_item, 'hot_search': i.text.strip('#'), 'hot_duration': j.text, 'hot_index': k.text,
                           'event_time': v.text}
        # filter out irrelevant info
        if search_item in new_result['hot_search']:
            with open('./hot_search_result.csv', 'a', encoding='utf-8-sig') as f: # the key of it is encoding!
                w = csv.DictWriter(f, new_result.keys())
                if f.tell() == 0:
                    w.writeheader()
                w.writerow(new_result)
    browser.close()
    # browser.find_element_by_xpath('//div[@class="ivu-input-group-append ivu-input-search"]').click()
    # after click in, <p class='txt'  </p>

def get_city_list():
    f = pd.read_excel('./城市等级划分.xlsx', index_col = 0)
    cities = f['city'].tolist()[:30]
    return cities

for c in get_city_list():
    get_results(c)