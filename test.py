# code:utf-8
from scrapy import Selector
from pyquery import PyQuery

with open('test.html', encoding='utf-8') as f:
    text = f.read()
#print(text)
#sel = Selector(text=text)
jpy = PyQuery(text)
items = jpy('li')
for item in items.items():
    print(item.attr('class'))