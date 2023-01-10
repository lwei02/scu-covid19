# -*- coding: utf-8 -*-
'''
Modified on 20221228
By: lwei02

Changelog:
2023-01-11:
 - 新加入另一个旧数据来源以应对API接口中'szdd'属性值错误的问题（使用填报前端页面内预渲染的内容作为数据来源）
 - 替换geo_api_info内容来源
2022-12-28:
 - 重写表单内容，修复打卡失败问题（表单变化频繁，建议有能力者自行F12查看提交数据调整表单内容）
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
import json, re


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
        message("登录失败")
        exit(1)


def get_daily(s: requests.Session):
    daily = s.get("https://wfw.scu.edu.cn/ncov/api/default/daily?xgh=0&app_id=scu", timeout=3)
    j = daily.json()
    d = j.get('d', None)
    if d:
        return daily.json()['d']
    else:
        message("获取昨日信息失败")
        exit(1)
       
def get_inpage_info(s: requests.Session):
    try:
        x = s.get('https://wfw.scu.edu.cn/ncov/wap/default/index', timeout=3)
        y = re.search(r'var def = (.*?);\n', x.text).group(1)
        z = json.loads(y)
        if 'szdd' in z:
            return z
        else:
            raise "'szdd' attribute missing"
    except Exception as e:
        message("获取旧所在地点信息失败：" + str(e))
        exit(1)


def submit(s: requests.Session, old: dict, old2: dict):
    new_daily = {
        'zgfxdq': old['zgfxdq'], #走过风险地区（？
        'mjry': old['mjry'], #密接人员（？
        'csmjry': old['csmjry'], #??密接人员（？
        'szxqmc': old['szxqmc'], #所在校区名称
        'sfjzxgym': old['sfjzxgym'], #是否接种新冠疫苗
        'jzxgymrq': old['jzxgymrq'], #接种新冠疫苗日期
        'sfjzdezxgym': old['sfjzdezxgym'], #是否接种第二针新冠疫苗
        'jzdezxgymrq': old['jzdezxgymrq'], #接种第二针新冠疫苗日期
        'sfjzdszxgym': old['sfjzdszxgym'], #是否接种第三针新冠疫苗
        'jzdszxgymrq': old['jzdszxgymrq'], #接种第三针新冠疫苗日期
        'dqjczts': old['dqjczts'], #当前????（未知时间弃用）
        'dqglzt': old['dqglzt'], #当前隔离状态（未知时间弃用）
        'sfmjry': old['sfmjry'], #是否密接人员
        'szdd': old2['szdd'], #所在地点（2022-12，新）
        'sfwzzgrz': old['sfwzzgrz'], #是否????
        'sfwwzzgrz': old['sfwwzzgrz'], #是否????
        'address': old['address'], #地址（2022-12弃用）
        'area': old['area'], #地区（2022-12弃用）
        'bztcyy': old['bztcyy'], #不在同城原因（2022-12弃用）
        'bzxyy': old['bzxyy'], #不在校原因（2022-12弃用）
        'city': old['city'], #城市（2022-12弃用）
        'created': str(int(time())), #表单创建时间戳
        "date": datetime.now(tz=pytz.timezone("Asia/Shanghai")).strftime("%Y%m%d"), #日期
        'geo_api_info': old2['geo_api_info'], #高德API返回信息（2022-12弃用，但仍出现于打卡信息中）
        'glksrq': old['glksrq'], #隔离开始日期（未知时间弃用）
        'gllx': old['gllx'], #隔离类型（未知时间弃用）
        'gtjzzfjsj': old['gtjzzfjsj'], #共同居住???时间（未知时间弃用）
        'hsjcdd': old['hsjcdd'], #核酸检测地点（未知时间弃用）
        'hsjcjg': old['hsjcjg'], #核酸检测结果（未知时间弃用）
        'hsjcrq': old['hsjcrq'], #核酸检测日期（未知时间弃用）
        'jcbhlx': old['jcbhlx'], #接触病号类型（？，未知时间弃用）
        'jcbhrq': old['jcbhrq'], #接触病号日期（？，未知时间弃用）
        'province': old['province'], #省份（2022-12弃用）
        'qksm': old['qksm'], #情况说明（2022-12弃用）
        'remark': old['remark'], #备注（2022-12弃用）
        'sfcxtz': old['sfcxtz'], #是否???（未知时间弃用，但仍有数据0）
        'sfcxzysx': old['sfcxzysx'], #是否???（未知时间弃用，但仍有数据0）
        'sfcyglq': old['sfcyglq'], #是否处于隔离期（未知时间弃用，但仍有数据0）
        'sfjcbh': old['sfjcbh'], #是否接触病号（？，未知时间弃用，但仍有数据0）
        'sfjchbry': old['sfjchbry'], #是否接触湖北人员（未知时间弃用，但仍有数据0）
        'sfjcqz': old['sfjcqz'], #是否接触确诊（未知时间弃用）
        'sfjcwhry': old['sfjcwhry'], #是否接触武汉人员（未知时间弃用，但仍有数据0）
        'sfsqhzjkk': old['sfsqhzjkk'], #是否???（未知时间弃用，但仍有数据0）
        'sftjhb': old['sftjhb'], #是否???（未知时间弃用，但仍有数据0）
        'sftjwh': old['sftjwh'], #是否???（未知时间弃用，但仍有数据0）
        'sfygtjzzfj': old['sfygtjzzfj'], #是否有共同居住???（未知时间弃用，但仍有数据0）
        'sfyyjc': old['sfyyjc'], #是否????（未知时间弃用，但仍有数据0）
        'sfzx': old['sfzx'], #是否在校（未知时间弃用，但仍有数据1）
        'sqhzjkkys': old['sqhzjkkys'], #未知（未知时间弃用）
        'szcs': old['szcs'], #所在城市（2022-12弃用）
        'szgj': old['szgj'], #所在国家（2022-12弃用）
        'szsqsfybl': old['szsqsfybl'], #所在社区是否有病例（未知时间弃用，但仍有数据0）
        'tw': old['tw'], #体温（2022-12弃用）
        'uid': old['uid'], #用户id
        'jcjgqr': old['jcjgqr'], #检测结果确认（？，未知时间弃用）
        'jcqzrq': old['jcqzrq'], #接触确诊日期（？，未知时间弃用）
        'jcjg': old['jcjg'], #检测结果（？，未知时间弃用）
        'id': old['id'], #id
        # 此行下默认为空，旧资料中亦无此5项，直接置空
        'gwszdd': '', #未知
        'sfyqjzgc': '', #是否有?????
        'jrsfqzys': '', #未知
        'jrsfqzfy': '', #未知
        'szgjcs': '' #未知
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

if __name__ == "__main__":
    print(datetime.now(tz=pytz.timezone("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S %Z"))
    for i in range(randint(10,600),0,-1):
        print("\r等待{}秒后填报".format(i),end='')
        sleep(1)
    login(s, user, passwd)
    yesterday_api_info = get_daily(s)
    yesterday_inpage_info = get_inpage_info(s)
    submit(s, yesterday_api_info, yesterday_inpage_info)
