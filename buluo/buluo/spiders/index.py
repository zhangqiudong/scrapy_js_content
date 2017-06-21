# -*- coding: utf-8 -*-
import scrapy
import time
import base64
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from buluo.items import BuluoItem

class buluoSpider(scrapy.Spider):
   name = 'buluo_spider'
   def __init__(self, bid = None): #示例：bid = 12339
       """初始化起始页面和游戏bid
       """
       super(buluoSpider, self).__init__()
       self.bid = bid #参数bid由此传入
       self.start_urls = ['http://buluo.qq.com/p/barindex.html?bid=%s' % bid]
       self.allowed_domain = 'buluo.qq.com'
       self.driver = webdriver.Firefox()
       self.driver.set_page_load_timeout(5) #throw a TimeoutException when thepage load time is more than 5 seconds.

   def parse(self, response):
       """模拟浏览器实现翻页，并解析每一个话题列表页的url_list
       """
       url_set = set() #话题url的集合
       self.driver.get(response.url)
       while True:
           wait = WebDriverWait(self.driver, 2)
           wait.until(lambda driver:driver.find_element_by_xpath('//ul[@class="post-list"]/li[@class]/a'))#VIP，内容加载完成后爬取
           sel_list = self.driver.find_elements_by_xpath('//ul[@class="post-list"]/li[@class]/a')
           url_list = [sel.get_attribute("href") for sel in sel_list]
           url_set |= set(url_list)
           try:
                wait =WebDriverWait(self.driver, 2)
                wait.until(lambda driver:driver.find_element_by_xpath('//ul[@class="pg1"]/li[@class="pg_next"]'))#VIP，内容加载完成后爬取
                next_page =self.driver.find_element_by_xpath('//ul[@class="pg1"]/li[@class="pg_next"]')
                next_page.click() #模拟点击下一页
           except:
                print "#####Arrive thelast page.#####"
                break
       with open('url_set.txt', mode='w') as f:
           f.write(repr(url_set))
       for url in url_set:
           yield scrapy.Request(url, callback=self.parse_content)

   def parse_content(self, response):
       """提取话题页面内容，通过pipeline存入指定字段
       """
       item = BuluoItem()
       item['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
       item['bid'] = self.bid
       item['url'] = response.url
       #item['content'] = response.body.decode('utf-8')
       item['content'] = base64.b64encode(response.body) #编码为Base64的网页内容
       yield item