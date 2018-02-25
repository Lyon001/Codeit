import re
import json
import requests


def searchTrain(querystring):
    headers = {
        "Cookie":"__NRF=74C05F8DA4A54BAD8FE8C1858576401F; JSESSIONID=7F000001F6317B0C83A920B23A62A0D64E27924D83; route=495c805987d0f5c8c84b14f60212447d; BIGipServerotn=602931722.64545.0000; BIGipServerpool_passport=200081930.50215.0000; _jc_save_fromStation=%u4E0A%u6D77%2CSHH; _jc_save_toStation=%u5357%u4EAC%2CNJH; _jc_save_fromDate=2017-07-20; _jc_save_toDate=2017-07-18; _jc_save_wfdc_flag=dc",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
        }
    url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9018'
    requests.packages.urllib3.disable_warnings()
    html_stations= requests.get(url,verify=False)
    station = re.findall(u'([\u4e00-\u9fa5]+)\|([A-Z]+)', html_stations.text)
    stations = dict(station)
    infolist = querystring.split('+')
    arguments = {'option':infolist[0],'from':infolist[1],'to':infolist[2],'date':infolist[3]}
    fromStation = stations[arguments['from']]
    toStation = stations[arguments['to']]
    tripDate = arguments['date']
    options = ''.join([item for item in arguments['option']])

    url2 = ('https://kyfw.12306.cn/otn/leftTicket/queryZ?leftTicketDTO.train_date={}&leftTicketDTO.from_station={}&leftTicketDTO.to_station={}&purpose_codes=ADULT').format(tripDate,fromStation,toStation)
    requests.packages.urllib3.disable_warnings()#在语句前加上此句即可不会被报错urllib3/connectionpool.py:843: InsecureRequestWarning: Unverified HTTPS request
    r2 = requests.get(url2,headers = headers,verify=False)
    available_trains = r2.json()['data']['result']
    details = '【车次|车站|发到时间(历时)|商务座|特等座|一等|二等|高级软卧|软卧|硬卧|软座|硬座(票价)|无座|其他】\n'
    for item in available_trains:
        cm = item.split('|')
        train_no = cm[2]
        train_name = cm[3]
        initial = train_name[0].lower()
        if not options or initial in options:
            try:
                url3 = "https://kyfw.12306.cn/otn/czxx/queryByTrainNo?train_no={}&from_station_telecode={}&to_station_telecode={}&depart_date={}".format(train_no,cm[6],cm[7],tripDate)
                requests.packages.urllib3.disable_warnings()
                r3 = requests.get(url3,headers = headers,verify=False)
                fromstationNo = tostationNo = ""
                for item in r3.json()['data']['data']:
                    if arguments['from'] in item['station_name']:
                        fromstationNo = item['station_no']
                    if arguments['to'] in item['station_name']:
                        tostationNo = item['station_no']
                url4 = ('https://kyfw.12306.cn/otn/leftTicket/queryTicketPrice?train_no={}&from_station_no={}&to_station_no={}&seat_types=1413&train_date={}'.format(train_no,fromstationNo,tostationNo,tripDate))
                requests.packages.urllib3.disable_warnings()
                r4 = requests.get(url4,headers = headers,verify=False)
                regularseatPrice = r4.json()['data']['WZ']
            except Exception as e:
                print(repr(e))
            train = [
            '【'+train_name,'-'.join([cm[6],cm[7]]),'-'.join([cm[8],cm[9]])+'('+cm[10]+')',cm[32],cm[25],
            cm[31],cm[30],cm[21],cm[23],cm[28],cm[24],cm[29]+'('+regularseatPrice+')',cm[26],cm[22]+'】\n']
            details += ' | '.join(train)
    return details

if __name__ == '__main__':
    searchTrain(querystring = 'dgz+南京+太原+2018-02-25')
