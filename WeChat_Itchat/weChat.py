import re
import time
import itchat
from itchat.content import *
from weather import SearchWeather
from package import getPackage
from airlineTicket import getAirline
from trainTicket import searchTrain
@itchat.msg_register([TEXT, PICTURE, MAP, CARD, NOTE, SHARING, RECORDING, ATTACHMENT, VIDEO])
def text_reply(msg):
    if msg['Type'] == 'Text':
        words = "【今天是大年初八，祝福我生命中遇到的每个人！🎀🎀新年快乐🎀🎀 开开心心,身体健康旺旺旺🐶🐶🐶！[耶][耶][耶][耶]】"
        try:
            print("【%s】收到一条消息："%time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()),msg['Content'])
            print(msg)
            if re.search(r"快乐",msg['Content']) or re.search(r"恭喜",msg['Content']) or re.search(r"发财",msg['Content']):
                reply_content = "衷心感谢您的祝福，在此，【小赵】祝您：[發][發][發][發]  " + words
                print(reply_content)
                itchat.send('@img@%s' % '/Users/zhaoluyang/PycharmProjects/WeChat_Itchat/qqq.jpg',toUserName=msg['FromUserName'])
                #itchat.send('@vid@%s' % '/Users/zhaoluyang/PycharmProjects/WeChat_Itchat/demo.mp4',toUserName=msg['FromUserName'])
            elif re.search(r"天气",msg['Content']) or re.search(r"气温",msg['Content']):
                try:
                    cityname = re.search(r"(天气)(\+)(.*)",msg['Content']).group(3)
                    reply_content = SearchWeather().main(city = cityname)
                except:
                    reply_content ="查询天气请输入：天气+城市名"
                finally:
                    print(reply_content)
            elif re.search(r"快递",msg['Content']):
                try:
                    packNum = re.search(r"(快递)(\+)([0-9]+)",msg['Content']).group(3)
                    reply_content = getPackage(package = packNum)
                except:
                    reply_content ="查询快递请输入：快递+运单号"
                finally:
                    print(reply_content)
            elif re.search(r"航班",msg['Content']) or re.search(r"飞机",msg['Content']):
                try:
                    info = re.search(r"(航班)(\+)(.*)",msg['Content']).group(3)
                    reply_content = getAirline(string = info)
                except:
                    reply_content ="查询航班请输入：航班+出发地+目的地+时间（如：航班+南京+北京+2018-02-20）"
                finally:
                    print(reply_content)

            elif re.search(r"火车",msg['Content']) or re.search(r"余票",msg['Content']):
                try:
                    info2 = re.search(r"(余票)(\+)(.*)",msg['Content']).group(3)
                    reply_content = searchTrain(querystring = info2)
                except:
                    reply_content ="查询火车余票请输入：余票+车型+出发地+目的地+时间，其中可选车型d动车、g高铁、k快速、t特快、z直达（例如：余票+dgz+南京+太原+2018-02-25）"
                finally:
                    print(reply_content)
            elif re.search(r"知乎",msg['Content']):
                reply_content ="https://www.zhihu.com/question/62024734/answer/324957818"
                print(reply_content)
            else:
                reply_content = words + msg['Text']
                print(reply_content)
        except Exception as e:
            print(repr(e))

    elif msg['Type'] == 'Picture':
        print(msg)
        reply_content = r"图片: " + msg['FileName']
    elif msg['Type'] == 'Card':
        reply_content = r" " + msg['RecommendInfo']['NickName'] + r" 的名片"
    elif msg['Type'] == 'Map':
        print(msg)
        x, y, location = re.search("<location x=\"(.*?)\" y=\"(.*?)\".*label=\"(.*?)\".*", msg['OriContent']).group(1,2,3)
        if location is None:
            reply_content = r"位置: 纬度->" + x.__str__() + " 经度->" + y.__str__()
        else:
            reply_content = r"位置: " + location
    elif msg['Type'] == 'Note':
        reply_content = r"通知"
    elif msg['Type'] == 'Sharing':
        reply_content = r"分享"
    elif msg['Type'] == 'Recording':
        print(msg)
        reply_content = r"语音"
    elif msg['Type'] == 'Attachment':
        print(msg)
        reply_content = r"文件: " + msg['FileName']
    elif msg['Type'] == 'Video':
        print(msg)
        reply_content = r"视频: " + msg['FileName']
    else:
        reply_content = r"消息"

    friend = itchat.search_friends(userName=msg['FromUserName'])
    itchat.send(r"Friend:%s -- %sTime:%sMessage:%s" % (friend['NickName'], friend['RemarkName'], time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()), reply_content),toUserName='filehelper')
    if friend['RemarkName']=='建丽':
        pass
    else:
        itchat.send(r"收到您于%s发送的消息,更多玩法，请回复：快递、火车、航班/飞机、天气/气温【Python-itchat】%s" % (time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()), reply_content),toUserName=msg['FromUserName'])
itchat.auto_login(hotReload=True)
itchat.run()
