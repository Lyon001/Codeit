import re
import pymysql
import requests
from bs4 import BeautifulSoup


class SearchWeather():
    def __init__(self):
        self.URL = 'http://www.weather.com.cn/weather/101190101.shtml'
        self.HEADERS ={
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 ''(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        self.CONNECTION = pymysql.connect(host='localhost',user='root',password='admin',db='IP_POOL',charset='utf8',cursorclass=pymysql.cursors.DictCursor)

    def getcityCode(self,cityName):
        SQL = "SELECT cityCode FROM cityWeather WHERE cityName='%s'" % cityName
        try:
            with self.CONNECTION.cursor() as cursor:
                cursor.execute(SQL)
                self.CONNECTION.commit()
                result = cursor.fetchone()
                return result['cityCode']
        except Exception as e:
            print(repr(e))

    def getWeather(self,cityCode,cityname):
        url = 'http://www.weather.com.cn/weather/%s.shtml' % cityCode
        html = requests.get(url,headers = self.HEADERS)
        html.encoding='utf-8'
        soup=BeautifulSoup(html.text,'lxml')
        weather = "日期|天气|最高温|最低温|风向|风力\n"
        for day in soup.find("div", {'id': '7d'}).find('ul').find_all('li'):
            date,detail = day.find('h1').string, day.find_all('p')
            title = detail[0].string
            templow = detail[1].find("i").string
            temphigh = detail[1].find('span').string if detail[1].find('span')  else ''
            wind,direction = detail[2].find('span')['title'], detail[2].find('i').string
            if temphigh=='':
                weather += '你好，【%s】今天白天：【%s】，温度：【%s】，%s：【%s】\n' % (cityname,title,templow,wind,direction)
            else:
                weather += (date + title + "【" + templow +  "~"+temphigh +'°C】' + wind + direction + "\n")
        return weather

    def main(self,city='南京'):
        cityCode = self.getcityCode(city)
        detail = self.getWeather(cityCode,city)
        return detail

if __name__ == "__main__":
    weather = SearchWeather()
    weather.main()
