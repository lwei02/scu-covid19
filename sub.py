'''
！！！必看！！！
进入https://wfw.scu.edu.cn/ncov/wap/default/index即打卡网页，登录后在“所在地点”中获取当前位置信息，
然后F12，在element里面用ctrl+f搜索geo_api_info，把对应位置的geo_api_info的内容复制到https://www.sojson.com/yasuo.html
先"去除转义"再"unicode转中文"，把获取的结果复制到下面对应的geo_api_info的位置，此脚本中地址默认为四川大学望江校区，江安校区的地址在注释中，可以自行添加/取消注释。
'''

# -*- coding: utf-8 -*-
'''
Modified on 20221218
By: lwei02

Changelog:
2022-12-22:
 - 修复因系统升级造成所在地点空信息问题
2022-12-18: 
 - 修复了因为学校打卡系统升级导致的打卡失败问题
2022-07-03: 
 - 修复了因为学校打卡系统升级导致的打卡第三针疫苗空信息问题
 - 增加简单的QQ推送功能
'''

"""
Modified on 20210930
@author: HyperMn
"""

"""
author: Les1ie
mail: me@les1ie.com
license: CC BY-NC-SA 3.0
"""

import pytz
import requests
from time import sleep,time
from random import randint
from datetime import datetime


s = requests.Session()
header = {"User-Agent": "Mozilla/5.0 (Linux; Android 10;  AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/045136 Mobile Safari/537.36 wxwork/3.0.16 MicroMessenger/7.0.1 NetType/WIFI Language/zh",}
s.headers.update(header)

user = ""    # 账号
passwd = ""   # 川大统一认证密码

# 微信推送
wechat_api_key = ""  # server酱的api，填了可以微信通知打卡结果，不填没影响

# QQ推送，下方均需填写方可生效（需要mirai-api-http，且配置为单账号模式，无authKey；若有authKey需求请自行fork修改）
mirai_addr = ""  # mirai-api-http的地址
qq_target = ""  # qq号，要推送到的qq号

def login(s: requests.Session, username, password):
    payload = {
        "username": username,
        "password": password
    }
    r = s.post("https://wfw.scu.edu.cn/a_scu/api/sso/check", data=payload, timeout=3)
    if r.json().get('m') != "操作成功":
        print(r.text)
        print("登录失败")
        exit(1)


def get_daily(s: requests.Session):
    daily = s.get("https://wfw.scu.edu.cn/ncov/api/default/daily?xgh=0&app_id=scu", timeout=3)
    j = daily.json()
    d = j.get('d', None)
    if d:

        return daily.json()['d']
    else:
        print("获取昨日信息失败")
        exit(1)


def submit(s: requests.Session, old: dict):
    new_daily = {
        "address": old["address"],
        "area": old["area"],
        "bztcyy": old["bztcyy"],
        "bzxyy": old["bzxyy"],
        "city": old["city"],
        "created": str(int(time())),
        "created_uid": old["created_uid"],
        "csmjry": old["csmjry"],
        "date": datetime.now(tz=pytz.timezone("Asia/Shanghai")).strftime("%Y%m%d"),
        "dqglzt": old["dqglzt"],
        "dqjczts": old["dqjczts"],
        'fjsj': old['fjsj'],
        'fxyy': old['fxyy'],
        'geo_api_info': '{"type":"complete","position":{"Q":30.552839084202,"R":103.99331054687502,"lng":103.993311,"lat":30.552839},"location_type":"html5","message":"Get sdkLocation failed.Get geolocation success.Convert Success.Get address success.","accuracy":315,"isConverted":true,"status":1,"addressComponent":{"citycode":"028","adcode":"510116","businessAreas":[{"name":"白家","id":"510116","location":{"Q":30.562482,"R":104.006821,"lng":104.006821,"lat":30.562482}}],"neighborhoodType":"","neighborhood":"","building":"","buildingType":"","street":"川大路三段","streetNumber":"365号","country":"中国","province":"四川省","city":"成都市","district":"双流区","township":"西航港街道"},"formattedAddress":"四川省成都市双流区西航港街道四川大学江安校区学生西园8舍围合","roads":[],"crosses":[],"pois":[],"info":"SUCCESS"}', # 10
        # 'geo_api_info': '{"type":"complete","position":{"Q":30.62923529731,"R":104.09010172526098,"lng":104.090102,"lat":30.629235},"location_type":"html5","message":"Get sdkLocation failed.Get geolocation success.Convert Success.Get address success.","accuracy":40,"isConverted":true,"status":1,"addressComponent":{"citycode":"028","adcode":"510107","businessAreas":[],"neighborhoodType":"科教文化服务;学校;高等院校","neighborhood":"四川大学","building":"","buildingType":"","street":"望江路","streetNumber":"71号","country":"中国","province":"四川省","city":"成都市","district":"武侯区","township":"望江路街道"},"formattedAddress":"四川省成都市武侯区望江路街道四川大学四川大学望江校区","roads":[],"crosses":[],"pois":[],"info":"SUCCESS"}',
        'glksrq': old['glksrq'], 
        'gllx': old['gllx'],
        'gtjzzfjsj': old['gtjzzfjsj'],
        'gwszdd':'', 
        'hsjcdd':old['hsjcdd'], 
        'hsjcjg':old['hsjcjg'],
        'hsjcrq': old['hsjcrq'],
        'id': old['id'],
        'ismoved': old['ismoved'],
        'jcbhlx': old['jcbhlx'],
        'jcbhrq': old['jcbhrq'],
        'jcjg': old['jcjg'],
        'jcjgqr': old['jcjgqr'],
        'jcqzrq': old['jcqzrq'],
        'jcwhryfs': old['jcwhryfs'],
        'jchbryfs': old['jchbryfs'],
        'jrsfqzfy': '',
        'jrsfqzys': '',
        'jzdezxgymrq': old['jzdezxgymrq'],
        "jzdszxgymrq": old["jzdszxgymrq"],
        "jzxgymrq": old["jzxgymrq"],
        "mjry": old["mjry"],
        "province": old["province"],
        "qksm": old["qksm"],
        "remark": old["remark"],
        "sfcxtz": old["sfcxtz"],
        "sfcxzysx": old["sfcxzysx"],
        "sfcyglq": old["sfcyglq"],
        "sfjcbh": old["sfjcbh"],
        "sfjchbry": old["sfjchbry"],
        "sfjcqz": old["sfjcqz"],
        "sfjcwhry": old["sfjcwhry"],
        'sfjxhsjc': old['sfjxhsjc'],
        "sfjzdezxgym": old["sfjzdezxgym"],
        "sfjzdszxgym": old["sfjzdszxgym"],
        "sfjzxgym": old["sfjzxgym"],
        "sfmjry": old["sfmjry"],
        'sfsfbh': old['sfsfbh'],
        "sfsqhzjkk": old["sfsqhzjkk"],
        "sftjhb": old["sftjhb"],
        "sftjwh": old["sftjwh"],
        "sfygtjzzfj": old["sfygtjzzfj"],
        "sfyqjzgc": "",
        "sfyyjc": old["sfyyjc"],
        "sfzx": old["sfzx"],
        'old_sfzx': old['old_sfzx'],
        "sqhzjkkys": old["sqhzjkkys"],
        "szcs": old["szcs"],
        'szdd': old['szdd'],
        'old_szdd': old['old_szdd'],
        "szgj": old["szgj"],
        'old_szgj': old['old_szgj'],
        "szsqsfybl": old["szsqsfybl"],
        "szxqmc": old["szxqmc"],
        "tw": old["tw"],
        "uid": old["uid"],
        'xjzd': old['xjzd'],
        "zgfxdq": old["zgfxdq"],
        'app_id': 'scu'
        }

    r = s.post("https://wfw.scu.edu.cn/ncov/wap/default/save", data=new_daily, timeout=3)
    print("提交信息:", new_daily)
    # print(r.text)
    result = r.json()
    if result.get('m') == "操作成功":
        print("打卡成功")
        message(result.get('m'))
    else:
        print("打卡失败，错误信息: ", r.json().get("m"))
        message(result.get('m'))


def message(title):
    """
    微信/QQ通知打卡结果
    """
    if wechat_api_key != '' and wechat_api_key != None:
        msg_url = "https://sc.ftqq.com/{}.send?text={}&desp={}".format(wechat_api_key, "疫情防控通自动填报结果通知 (SCU)", "打卡结果：{}\n\n\n\n学号：{}\n\n时间：{}\n\n\n\n".format(title, user, datetime.now(tz=pytz.timezone("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S")))
        requests.get(msg_url)
    if mirai_addr != '' and mirai_addr != None and qq_target != '' and qq_target != None:
        r=requests.post("http://%s/sendFriendMessage" % mirai_addr, json={"qq":qq_target,"messageChain":[{"type":"Plain","text":"疫情防控通自动填报结果通知 (SCU)\n打卡结果：{}\n\n学号：{}\n时间：{}".format(title, user, datetime.now(tz=pytz.timezone("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])}]})
        print(r.text)

if __name__ == "__main__":
    print(datetime.now(tz=pytz.timezone("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S %Z"))
    for i in range(randint(10,600),0,-1):
        print("\r等待{}秒后填报".format(i),end='')
        sleep(1)

    login(s, user, passwd)
    yesterday = get_daily(s)
    submit(s, yesterday)
