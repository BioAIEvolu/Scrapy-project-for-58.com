
# from 信安17-2
import requests
import re
import base64
from fontTools.ttLib import TTFont
 
 
class five_eight:
    def __init__(self):
        self.dict = {}
        self.page = 0
        self.numbers = 0
        self.init_url = "https://bj.58.com/chaoyang/chuzu/"
        self.header = {
            "Accept": "text/html",
            "Referer": "",
            "Cookie": "f=n; commontopbar_new_city_info=1%7C%E5%8C%97%E4%BA%AC%7Cbj; f=n; commontopbar_new_city_info=1%7C%E5%8C%97%E4%BA%AC%7Cbj; userid360_xml=83BC9320CEEB5E8BFEE1ADEBF939971F; time_create=1565148056280; id58=e87rZl0itmsKJ9mAA8SKAg==; f=n; commontopbar_new_city_info=1%7C%E5%8C%97%E4%BA%AC%7Cbj; commontopbar_ipcity=bj%7C%E5%8C%97%E4%BA%AC%7C0; city=bj; 58home=bj; 58tj_uuid=363461fd-14a8-4cd6-bf26-6a279fb42b84; new_session=0; new_uv=1; utm_source=; spm=; init_refer=; als=0; xxzl_deviceid=oa5vl60lIZlrEFC8ZvN564VHOoNXCCj2q3UCBNLKrz8VaXJXMBPETx1FRHK7rEua",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0",
        }
 
    def convert_money(self, s):
        console = ''
        strs = {'&#x9476': 38006, '&#x958f': 38287, '&#x993c': 39228, '&#x9a4b': 39499, '&#x9e3a': 40506,
                '&#x9ea3': 40611, '&#x9f64': 40804, '&#x9f92': 40850, '&#x9fa4': 40868, '&#x9fa5': 40869}
        con_s = s.split(';')
        con_s = con_s[:-1]
        for i in con_s:
            temp = int(self.dict[strs[i]][-2:]) - 1
            console += str(temp)
        if console != '':
            return int(console)
        else:
            print("钱为空")
 
    def convert_title_room(self, s):
        strs = ['&#x9476;', '&#x958f;', '&#x993c;', '&#x9a4b;', '&#x9e3a;', '&#x9ea3;', '&#x9f64;', '&#x9f92;',
                '&#x9fa4;',
                '&#x9fa5;']
        nums = {'&#x9476;': 38006, '&#x958f;': 38287, '&#x993c;': 39228, '&#x9a4b;': 39499, '&#x9e3a;': 40506,
                '&#x9ea3;': 40611, '&#x9f64;': 40804, '&#x9f92;': 40850, '&#x9fa4;': 40868, '&#x9fa5;': 40869}
        for str_c in strs:
            beg = s.find(str_c)
            if beg != -1:
                temp = str(int(self.dict[nums[str_c]][-2:]) - 1)
                s = s.replace(str_c, temp)
            else:
                continue
        return s
 
    def onePage(self):
        param = 'pn' + str(self.page) + '/'
        self.header["Referer"] = self.init_url + param
        res = requests.get(self.init_url, headers=self.header)
        res_html = res.text
 
        title_pattern = r'target="_blank"  rel="nofollow" >(.*?)</a>'
        url_pattern = r'lazy_src="(.*?)"'
        room_pattern = r'<p class="room">(.*?)</p>'
        money_pattern = r'<b class="strongbox">(.*?)</b>'
        font_pattern = r"base64,(.*?)format"
 
        titles = re.findall(title_pattern, res_html, re.S | re.M)
        urls = re.findall(url_pattern, res_html, re.S | re.M)
        rooms = re.findall(room_pattern, res_html, re.S | re.M)
        moneys = re.findall(money_pattern, res_html, re.S | re.M)
        font_base64 = re.findall(font_pattern, res_html, re.S | re.M)
 
        titles = [c.replace('\n', '') for c in titles]
        titles = [c.replace(' ', '') for c in titles]
        urls = [c.replace('//', 'https://') for c in urls]
        rooms = [c.replace(' ', '') for c in rooms]
        rooms = [c.replace('&nbsp;', '') for c in rooms]
 
        # 解码数字
        str_base64 = font_base64[0][:-3]
        bin_data = base64.decodebytes(str_base64.encode())
        with open("font.woff", r"wb") as f:
            f.write(bin_data)
        onlineFonts = TTFont('font.woff')
        self.dict = onlineFonts.getBestCmap()
        # 数字解决
        for i in range(len(titles)):
            titles[i] = self.convert_title_room(titles[i])
        for i in range(len(rooms)):
            rooms[i] = self.convert_title_room(rooms[i])
        for i in range(len(moneys)):
            moneys[i] = self.convert_money(moneys[i])
        # 内容输出
        print("\033[31m[INFO]第{}页开始\033[0m".format(self.page + 1))
        for i in range(len(titles)):
            print("标题：{}\t图片链接：{}".format(titles[i], urls[i]))
            print("户型：{}\t价格：{}元/月\n".format(rooms[i], moneys[i]))
        print("\033[31m[INFO]第{}页结束\033[0m".format(self.page + 1))
 
    def manyPage(self):
        n = 3
        for i in range(n):
            self.page = i
            self.onePage()
 
    def __del__(self):
        print("\033[31m全部结束\033[0m")
 
 
if __name__ == "__main__":
    fe = five_eight()
    fe.manyPage()
