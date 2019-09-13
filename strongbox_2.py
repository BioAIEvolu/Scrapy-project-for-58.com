#!/bin/env/python
# coding=utf-8
import requests
import re
import os
import time

# 存储爬取信息的列表
g_info = list()
# 58同城用G#x编码的一些奇异字符表示数字，这些时我个人整理的，网站随时会变动
g_dict = {'龒': '0', '驋': '1', '鸺': '2', '餼': '3', '龤': '4', '麣': '5', '閏': '6', '龥': '7', '鑶': '8', '齤': '9'}


def get_session():
    """获取一个设置了头部的session,自动保持cookie"""
    s = requests.Session()
    s.headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'accept-language': 'zh-CN,zh;q=0.9',
        'referer': 'https://jj.58.com/chuzu/?PGTID=0d100000-008c-78a5-ac77-a44cc3330ee8&ClickID=2',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    }
    s.get(url='https://jj.58.com/chuzu/')
    return s


def convert(s):
    """把&#x转换为ｕtf8最后转换为数字"""
    s = s.strip('&#x;')  # 例如把'&#x957f;'变成'957f'
    s = bytes(r'\u' + s, 'ascii')  # 把'xxxx'转换成b'\uxxxx'
    s = s.decode('unicode_escape')  # 把bytes转换为字符串,为奇异汉字
    s = g_dict.get(s, '')  # 将奇异汉字转换为数字
    return s


def get_content(html, info=g_info):
    """解析具体的网页，存入列表中"""
    # 诊断参数
    assert isinstance(html, str)
    if not info or not isinstance(info, list):
        info = g_info
    # 替换换行和&#x
    html = html.replace('\n', '')
    html = re.sub(r'&#x[a-f0-9]{4};', lambda match: convert(match.group()), html)
    # 获取li块列表
    ul = re.search(r'<ul class="listUl">(.*?)</ul>', html).group(1)
    lis = re.findall(r'<li logr=".*?"\s+sortid=".*?">(.*?)</li>', ul)
    # 遍历li块列表,取具体的内容,存入列表中, 解析出错会打印错误并继续执行
    for li in lis:
        try:
            temp = dict()
            temp['img'] = "https:" + re.search(r'<img\s+lazy_src="(.*?)"\s+src=".*?">', li).group(1)
            temp['name'] = re.search(r'<a href=".*?"\s+class="strongbox"\s+tongji_label="listclick".*?>\s*(.*?)\s*</a>', li).group(1)
            temp['money'] = re.search(r'<div class="money">\s*?<b class="strongbox">(.*?)</b>元/月\s*?</div>', li).group(1)
            ret = re.search(r'<p class="room strongbox">(.*?)\s+(&nbsp;)+(.*?)</p>', li)
            temp['house'] = ret.group(1) + ret.group(3)
            info.append(temp)
        except Exception as err:
            print(err)


def save_content(info=g_info):
    """把列表里面的信息存入文件"""
    # 检测info列表
    if not info or not isinstance(info, list):
        info = g_info
    # 写入txt文件
    # with open('info.txt', 'a', encoding='utf-8') as f:
    #     temp = "标题:{}\n\t价位:{:<8}户型:{}\n"
    #     for i in info:
    #         temp2 = temp.format(i['name'], i['money'], i['house'])
    #         f.write(temp2)
    import json
    with open('info.json', 'w', encoding='utf-8') as f:
        # 写入json文件,中文字符串编码问题为\uxxxx这样显示
        # json.dump(info, f)
        # 可行的写入json文件方式
        f.write(json.dumps(info, ensure_ascii=False))


def get_img(session, imgdir=None, info=g_info):
    """通过爬取的图片链接，下载并保存图片"""
    # 诊断参数
    assert isinstance(session, requests.Session)
    if not info or not isinstance(info, list):
        info = g_info
    if not imgdir or not isinstance(imgdir, str) or (
            not os.path.isdir(imgdir) and not os.path.isdir(os.path.join('.', imgdir))):
        if not os.path.exists('./图片'):
            os.mkdir('./图片')
        imgdir = './图片'
    # 遍历下载图片
    for item in info:
        try:
            img = session.get(item['img']).content
            # 部分标题名称最后面为标点或者标题中含义/，不能成功存储,替换/,在后面放时间,使之成为有效路径
            filename = item['name'].replace('/', '-')
            filename += str(time.time()) + '.jpg'
            with open(os.path.join(imgdir, filename), 'wb') as f:
                f.write(img)
        except Exception as err:
            print(err)


def get_link(session, pindex=1):
    """爬取九江租房信息,pindex为页码"""
    assert isinstance(session, requests.Session)
    url = 'https://jj.58.com/chuzu/pn{}/?PGTID=0d3090a7-008c-73bb-6037-bfeefa80b85e&ClickID=2'.format(int(pindex))
    try:
        res = session.get(url=url)
        if res.status_code != 200:
            raise Exception('状态码非200')
        get_content(res.text)
    except Exception as err:
        print(err)


def main():
    try:
        pindex = int(input("请输入爬取的页码(无效输入均默认为１):"))
    except:
        pindex = 1
    s = get_session()
    get_link(session=s, pindex=pindex)
    get_img(session=s)
    save_content()


if __name__ == '__main__':
    main()
