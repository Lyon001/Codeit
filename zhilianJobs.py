#!/usr/bin/python3
#_*_ coding:utf-8 _*_
#__author__='Flowingsun'
#__date__='2017.8.22'
"""
1.程序介绍：
此智联招聘查询工具，是用简单的爬虫调用智联招聘的api，可以用来爬取智联招聘上设定城市+职位关键字下所有的职位信息，信息存储到本地Mysql保存。
关键字City输入：全国，则遍历查询默认的全国30个城市下相应的工作职位链接，否则只查询指定城市下的职位链接。

2.使用方法：
使用前需要先配置Mysql,如：host='localhost',user='root',password='XXX',db='XXX'.
Mysql的建表SQL语句如下：
CREATE TABLE `Java_南京` (
  `ZL_Job_id` int(30) NOT NULL AUTO_INCREMENT,
  `职位名称` varchar(255) DEFAULT NULL,
  `公司名称` varchar(255) DEFAULT NULL,
  `公司链接` varchar(255) DEFAULT NULL,
  `职位链接` varchar(255) NOT NULL,
  `职位月薪` varchar(255) DEFAULT NULL,
  `工作地点` varchar(255) DEFAULT NULL,
  `发布日期` varchar(255) DEFAULT NULL,
  `工作性质` varchar(255) DEFAULT NULL,
  `工作经验` varchar(255) DEFAULT NULL,
  `最低学历` varchar(255) DEFAULT NULL,
  `招聘人数` varchar(255) DEFAULT NULL,
  `职位类别` varchar(255) DEFAULT NULL,
  `岗位职责描述` varchar(3000) DEFAULT NULL,
  `福利标签` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`职位链接`),
  UNIQUE KEY `ZL_Job_id` (`ZL_Job_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8

表新建好以后，程序运行时输入：
City=南京
Keyword=Java
CollectionName=南京_Java
即可
"""
import requests,pymysql
from pymysql import cursors
from bs4 import BeautifulSoup
from lxml import etree

class zhilianJobs():
    def __init__(self):
        self.HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36"
        }
        self.ALL_CITY = ['苏州','合肥','广州','深圳','天津','武汉','西安','成都','大连','长春','沈阳','南京','济南','青岛','杭州','北京','无锡','宁波','重庆','郑州','长沙','福州','厦门','哈尔滨','石家庄','上海','惠州','太原','昆明','烟台','佛山','南昌','贵阳','吉林','呼和浩特','泉州','海口','拉萨','西宁','兰州','银川','乌鲁木齐']
        self.City = input(f"{'Please input the city you want to search:'}")
        self.Keyword = input(f"{'The keyword of the job you want:'}")
        self.CollectionName = input(f"{'The collectionName of Mysql(or press Enter to use default name.):'}") or str(self.Keyword+'_'+self.City)
        self.CONNECTION = pymysql.connect(host='xxx',user='xxx',password='xxx',db='xxx',charset='utf8',cursorclass=pymysql.cursors.DictCursor)
        self.SQL = f"INSERT INTO {self.CollectionName}(职位名称,公司名称,公司链接,职位链接,职位月薪,工作地点,发布日期,工作性质,工作经验,最低学历,招聘人数,职位类别,岗位职责描述,福利标签)VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

    def city_start(self):
        #启动函数，主要用来判断搜索城市【关键词】，如果指定城市，则正常调用main()执行程序；
        #若指定关键词==‘全国’，则对ALL_CITY列表中的城市依次调用main()函数进行遍历！
        if self.City=='全国':
            for item in self.ALL_CITY:
                Originpage = 'http://sou.zhaopin.com/jobs/searchresult.ashx?jl=' + item + '&kw=' + self.Keyword + '&sm=0&p='
                self.mainfunction(Originpage)
                print('---------------------------------------------------------------\n')
                print(f"All Jobs in[{item}]has been saved in database!")
        else:
            Originpage = 'http://sou.zhaopin.com/jobs/searchresult.ashx?jl=' + self.City + '&kw=' + self.Keyword + '&sm=0&p='
            self.mainfunction(Originpage)

    def mainfunction(self,Originpage):
        #函数主体，首先计算当前关键词生成的目标职位的总页面数，通过homepage()进行获取页面上职位链接、翻页递归
        #homepage()通过调用jobpage()来对当前页面所有职位链接进行遍历，获取每一条职位链接页面中的详细信息，然后通过save_mysql()存储！
        pagenum = self.total_page_number(str(Originpage+'1'))#有的职位可能搜索出来有300多页，但是智联默认只能显示前90页，所以此处翻页最大数为90！
        max_pagelength = 90 if pagenum>=90 else pagenum
        for i in range(1,max_pagelength+1):
            pageurl = Originpage + str(i)
            print(f"------------------------------------------------------------\nNow,it's page【{i}】,the url is:\n",pageurl)
            joblink_list = self.homepage(pageurl)
            for j in range(1,61):
                try:
                    jobdata = self.jobpage(joblink_list[j-1])
                    self.save_mysql(jobdata,j)
                except Exception as e:
                    print(repr(e))
        print("Success!")


    def total_page_number(self,url):
        #获取页面职位总数，用于下一步判断翻页的页数和函数循环执行次数的确定（每页有60个职位，譬如职位总数3600，则需要翻页60页）
        req = requests.get(url=url, headers=self.HEADERS)
        totalnum = etree.HTML(req.text).xpath('/html/body/div[3]/div[3]/div[2]/span[1]/em')[0].text
        pagenum = int(int(totalnum)/60)
        print(f'There are: 【{totalnum}】 jobs of 【{self.Keyword}】 in 【{self.City}】，totally :【{pagenum}】 pages')
        return pagenum

    def homepage(self,homeurl):
        #homepagez即主页，每个页面一般情况下包括60条职位，在homepage上要进行的操作有以下2条：
        #1.获取页面上所有的职位链接，存在列表里，等待遍历具体职位页面的信息
        #2.获取完所有职位链接后，判断当前页码是否<总页码数（pagenum），是则停止，否跳转到下一页，继续遍历！
        joblink_list = []
        try:
            req = requests.get(homeurl, headers=self.HEADERS)
            soup = BeautifulSoup(req.text,"lxml")
        except Exception as e:
            print(repr(e))
            self.homepage(homeurl)
        for item in soup.find_all("td",{"zwmc"}):
            if item.a is not None:
                if item.a.attrs['href'] is not None:
                    joblink_list.append(item.a.attrs['href'])
        return joblink_list

    def jobpage(self,joburl):
        #根据传入的参数【joburl】网址链接，获取该链接下的所有职位信息，并以jobdata【列表】形式返回
        print('------------------------------------------------------------\n' + joburl)
        req = requests.get(joburl,headers=self.HEADERS)
        page_obj = BeautifulSoup(req.text,"lxml")
        string1 = string2 = ''
        details = []
        职位链接 = joburl.strip().strip('\n')
        职位名称=公司名称=公司链接=职位月薪=工作地点=发布日期=工作性质=工作经验=最低学历=招聘人数=职位类别=岗位职责描述=福利标签=''
        try:
            obj1 = page_obj.find("div",{"class":"inner-left fl"})
            obj2 = page_obj.find("ul",{"class":"terminal-ul clearfix"})
            obj3 = page_obj.find("div",{"class":"tab-inner-cont"})
            obj4 = page_obj.find("div",{"class":"welfare-tab-box"})
            职位名称 = obj1.find("h1").get_text().strip().strip('\n')
            公司名称 = obj1.find("h2").get_text().strip().strip('\n')
            公司链接 = obj1.find("h2").find("a")["href"].strip().strip('\n')
            for item in obj2.find_all("strong"):
                details.append(item.get_text().strip().strip('\n'))
            职位月薪,工作地点,发布日期,工作性质,工作经验,最低学历,招聘人数,职位类别=details[0],details[1],details[2],details[3],details[4],details[5],details[6],details[7]
            for item in obj3.find_all("p"):
                string1 += item.get_text().strip().strip('\n')
            岗位职责描述 = string1
            for item in obj4.find_all("span"):
                string2 += item.get_text().strip().strip('\n')
            福利标签 = string2
        except Exception as e:
            print(repr(e))
            职位名称=公司名称=公司链接='found no link'
            职位月薪=工作地点=发布日期=工作性质=工作经验=最低学历=招聘人数=职位类别=岗位职责描述=福利标签='found no element'
        finally:
            jobdata = [f'{职位名称}',f'{公司名称}',f'{公司链接}',f'{职位链接}',f'{职位月薪}',f'{工作地点}',f'{发布日期}',f'{工作性质}',f'{工作经验}',f'{最低学历}',f'{招聘人数}',f'{职位类别}',f'{岗位职责描述}',f'{福利标签}']
            return jobdata

    def save_mysql(self,j_list,count):
        #sql = "INSERT INTO ZLzhaopin6(字段名称1，字段名称2...) VALUES (%s，%s...)"
        #注意，sql语句中VALUE前括号中表字段不能加引号“”，直接写字段值就行
        #cursor.execute(sql,(item))中item只要是英文字符串就行，数组元素类型的str可以直接用，中文字符串则始终不行！
        #原因在于MySQL默认字符集是latin1，要想成功插入中文字符，我们必须将相应的表（或者数据库）默认字符集改为utf8！
        try:
            with self.CONNECTION.cursor() as cursor:
                cursor.execute(self.SQL,(j_list[0],j_list[1],j_list[2],j_list[3],j_list[4],j_list[5],j_list[6],j_list[7],j_list[8],j_list[9],j_list[10],j_list[11],j_list[12],j_list[13]))
            self.CONNECTION.commit()
            print(j_list)
            print(f"Page【{count}】 has been saved in Mysql!")
        except IntegrityError:
            pass

spider = zhilianJobs()
spider.city_start()
