# -*- coding: utf-8 -*-
import scrapy
from pyquery import PyQuery
from ..items import City58Item
from scrapy.http import Request

def convert(strange):
    cov_dict = {'驋':0, '龒':1, '麣':2, '龤':3, '閏':4, 
                '餼':5, '鑶':6, '龥':7, '鑶':8, '齤':9}
    normal = ''
    for i in strange:
        num = cov_dict.get(i, '')
        num = str(num)
        normal = normal + num
        
    price = normal
    try:
        price = int(price)
    except:
        price = strange
    return price

class City58TestSpider(scrapy.Spider):
    name = 'city58_test'    #必不可少的爬虫名字，启动的关键
    allowed_domains = ['58.com']
    start_urls = ['http://fs.58.com/chuzu/']    #开始爬取的链接

    def parse(self, response):
        jpy = PyQuery(response.text)
        li_list = jpy('body > div.list-wrap > div.list-box > ul > li').items()  #记得带上.items()
        for it in li_list:
            a_tag = it('div.des > h2 > a')
            item = City58Item()
            item['name'] = a_tag.text() #a_tag取出文本
            item['url'] = a_tag.attr('href')    #取出href参数
            strange = it('div.list-li-right > div.money > b').text() #转换成数字
            item['price'] = convert(strange)
            yield item   #把Item返回给引擎

        test_request = response.follow('/chuzu/pn2/', callback=self.parse)   #使用response.follow方法把“/chuzu/pn2/”这个相对路径转换为绝对路径，并回调parse()函数
         
        
        test_request1 = Request('https://fs.58.com/chuzu/pn3', 
                                callback=self.parse,
                                errback=self.error_back,  #调用异常函数
                                headers={},
                                cookies={},  #cookie设为空
                                priority=10,     #headers设为空
                                )

        test_request2 = Request('https://58.com',
                                callback=self.parse,
                                errback=self.error_back,     #调用异常函数
                                priority=10,    #优先级设为10   
                                meta={'dont_redirect': True}    #不用重定向
                                )

        test_request3 = Request('https://58.com',
                                callback=self.parse,
                                errback=self.error_back,
                                priority=10,
                                dont_filter=True,
                                # meta={'dont_redirect': True}
                                )                                

        yield test_request   
        yield test_request1
        yield test_request2
        yield test_request3

    def error_back(self, e):
        _ = self
        print(e)
        print('我报错了')