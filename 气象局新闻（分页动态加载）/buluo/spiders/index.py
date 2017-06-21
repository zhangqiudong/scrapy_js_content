# -*- coding: utf-8 -*-
import scrapy
import time
import base64
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from buluo.items import BuluoItem
from bs4 import BeautifulSoup

class buluoSpider(scrapy.Spider):
   name = 'buluo_spider'
   def __init__(self,bid = None): #示例：bid = 12339
       """初始化起始页面和游戏bid
       """
       super(buluoSpider, self).__init__()
       self.bid = bid
       self.start_urls = ['http://www.cma.gov.cn/2011xzt/2017zt/20170502/2017050201/index.html',
                          'http://www.cma.gov.cn/2011xzt/2017zt/20170502/2017050201/index_%s.html'%bid]
       self.allowed_domain = 'cma.gov.cn'
       self.driver = webdriver.Firefox()
       self.driver.set_page_load_timeout(5) #throw a TimeoutException when thepage load time is more than 5 seconds.

   def parse(self, response):
       """模拟浏览器实现翻页，并解析每一个话题列表页的url_list
       """
       url_set = set() #话题url的集合
       self.driver.get(response.url)
       while True:
           wait = WebDriverWait(self.driver, 2)
           wait.until(lambda driver:driver.find_element_by_xpath('//td[@class="nblue"]/a'))#VIP，内容加载完成后爬取
           sel_list = self.driver.find_elements_by_xpath('//td[@class="nblue"]/a')
           url_list = [sel.get_attribute("href") for sel in sel_list]
           url_set |= set(url_list)
           try:
                wait =WebDriverWait(self.driver, 2)
                wait.until(lambda driver:driver.find_element_by_xpath('//span[@class="currentt"]/following-sibling::a[1]'))#VIP，内容加载完成后爬取
                next_page =self.driver.find_element_by_xpath('//span[@class="currentt"]/following-sibling::a[1]')
                next_page.click() #模拟点击下一页
           except:
                print "#####Arrive thelast page.#####"
                break
       for url in url_set:
           print(url)

   def parse_detail(self, response):
        item = response.meta["item"]
        item['date'] = response.xpath('//div[@class="news_textspan"]/div/span[2]/text()').extract()
        yield item