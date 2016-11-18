# coding: utf-8

import time
from datetime import datetime, timedelta
import base64
import urllib
import urllib2
#import os
import random
from bs4 import BeautifulSoup
import json

#CMD_URL="http://10.80.60.25:8080"
CMD_URL="http://hanxin.applinzi.com"

tms_headers={
'Accept':'image/gif, image/jpeg, image/pjpeg, image/pjpeg, application/x-shockwave-flash, application/x-ms-application, application/x-ms-xbap, application/vnd.ms-xpsdocument, application/xaml+xml, application/vnd.ms-excel, application/vnd.ms-powerpoint, application/msword, */*',
'Referer':'http://tms.zte.com.cn/tms/Login.aspx',
'Accept-Language':'zh-cn',
'User-Agent':'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; InfoPath.2; .NET4.0C; TCO_20160823182603)',
'Content-Type':'application/x-www-form-urlencoded',
#'Accept-Encoding':'gzip, deflate',
'Host':'tms.zte.com.cn',
#'Content-Length':'918',
'Connection': 'Keep-Alive',
'Pragma':'no-cache',
}

tms_login_data={
    '__EVENTTARGET':'',
    '__EVENTARGUMENT':'',
    '__LASTFOCUS':'',
    '__VIEWSTATE':'',
    '__EVENTVALIDATION':'',
    'hidPostback':0,
    'btnLogin.x':25,
    'btnLogin.y':8,
    'rdoList':'zh-CN'
}


def post_png_code_to_master(name):

    with open('vcode.png', 'rb') as f:
        ct = f.read()
        cts = base64.urlsafe_b64encode(ct)

        #print(type(cts))

    url= CMD_URL+"/article/verify?name=%s&query=%s" % (name, cts)
    #print(url)
    response = urllib2.urlopen(url).read()

    url= CMD_URL+"/article/status?name=%s&status=%s" % (name,"plz_fill_the_code")
    print url
    urllib2.urlopen(url).read()

def get_trigger(name):

    ret = False
    with open('vcode.png', 'rb') as f:
        ct = f.read()
        cts = base64.urlsafe_b64encode(ct)
        #cts = base64.encodebytes(ct)

        print(type(cts))

        #with open('out.png', 'wb') as ff:
        #    ff.write(base64.decodebytes(cts))

        #print(type(cts))
    url= CMD_URL+"/article/status?name=%s" % name
    print url
    response = urllib2.urlopen(url).read()

    res=json.loads(response)
    if res['status'] == "server_hello":
        url= CMD_URL+"/article/status?name=%s&status=%s" % (name,"client_hello")
        urllib2.urlopen(url)
        ret = True
    else:
        ret = False

    return ret

def get_status(name):

    url= CMD_URL+"/article/status?name=%s" % name
    response = urllib2.urlopen(url).read()

    res=json.loads(response)
    return res['status']

def set_status(name,status):
    url= CMD_URL+"/article/status?name=%s&status=%s" % (name,status)
    response = urllib2.urlopen(url).read()

    res=json.loads(response)
    return res['status']

def get_submit_code(name):

    url= CMD_URL+"/article/status?name=%s" % name
    print "get submit code try..."
    print url
    response = urllib2.urlopen(url).read()

    res=json.loads(response)
    if res['status'] == "plz_submit":
        url= CMD_URL+"/article/verify?name=%s" % name
        response = urllib2.urlopen(url).read()
        set_status(name,"got_sumit_code")
        res=json.loads(response)
        return res['code']
    else:
        return None

def wait_for_submit_code(name):
    start_time = datetime.now()
    wait_time = [(1,2),(1,2),(2,3),(2,3),(2,3),(3,5),(3,5),(3,5),(5,10),(10,15),(30,35),(30,35)]
    wait_flag = 0
    while True:
        #delta_time = datetime.now()- start_time
        #if delta_time.total_seconds()> 50* 60:
        #    return None
        if wait_flag < len(wait_time):
            random_s, random_e = wait_time[wait_flag]
            t_sleep_time = random.randint(random_s, random_e)
            print "get submit code timer will sleep %s" % t_sleep_time
            time.sleep(t_sleep_time * 60)
            code = get_submit_code(name)
            if code is not None:
                return code
        else:
            return None

def is_touch_door_ok(content):
    import re
    re_match = re.compile(ur'\u7f51\u4e0a\u5237\u5361\u6210\u529f')

    match = re_match.findall(content.decode('utf-8'))

    #print match
    if match != []:
        return True
    else:
        return False

def is_need_relogin(content):
    import re
    re_match = re.compile(ur'logoutPortal')

    match = re_match.findall(content.decode('utf-8'))

    #print match
    if match != []:
        return True
    else:
        return False

def get_sleep_seconds(hour, minute):
    curTime = datetime.now()
    desTime = curTime.replace(hour=hour, minute=minute, second=0)

    delta = desTime - curTime
    if desTime< curTime:
        delta = delta + timedelta(days=1)
    print delta
    return delta.total_seconds()

def login_atm(name, user_id, user_passwd):
    opener=urllib2.build_opener(urllib2.HTTPCookieProcessor())

    opener.addheaders=[]
    for k,v in tms_headers.items():
        opener.addheaders.append((k,v))

    urllib2.install_opener(opener)

    while True:
        url = "http://tms.zte.com.cn/tms/login.aspx"
        print(url)
        response = urllib2.urlopen(url).read()
        with open("login_ui.html", 'wb') as f:
            f.write(response)
        time.sleep(5)

        soup=BeautifulSoup(response, "html.parser")
        event_validation=soup.find(attrs={"name":"__EVENTVALIDATION"})['value']
        #print(event_validation)
        view_state=soup.find(attrs={"name":"__VIEWSTATE"})['value']
        #print(view_state)
        tms_login_data.update({'__VIEWSTATE':view_state})
        tms_login_data.update({'__EVENTVALIDATION':event_validation})
        tms_login_data.update({'txtUserName':user_id})
        tms_login_data.update({'PassWord':user_passwd})

        tms_login_data_en=urllib.urlencode(tms_login_data)
        tms_login_data_en = tms_login_data_en.encode(encoding='utf-8')

        #real login
        full_url =urllib2.Request(url, tms_login_data_en)
        response = urllib2.urlopen(full_url).read()
        with open("login_result.html", "wb") as f:
            f.write(response)
        time.sleep(5)

        #进入刷卡界面
        url = "http://atm.zte.com.cn/atm/Application/AboutMy/netchkinout.aspx?menuId=ssb.atm.menu.item.onlinecheck"
        print(url)
        response = urllib2.urlopen(url).read()
        with open("onlinecheck.html", "wb") as f:
            f.write(response)

        #准备填充提交表单及验证码
        submit_soup=BeautifulSoup(response, "html.parser")
        submit_event_validation=submit_soup.find(attrs={"name":"__EVENTVALIDATION"})['value']
        #print(submit_event_validation)

        submit_view_state=submit_soup.find(attrs={"name":"__VIEWSTATE"})['value']
        #print(submit_view_state)
        tms_submit_data={
            '__VIEWSTATE':submit_view_state,
            '__EVENTVALIDATION':submit_event_validation,
            'btnSubmit':"提交",
            'hidLanguage':'zh-CN'
        }
        tms_submit_data.update({'hidEmpInfo':user_id})

        touch_door_ok=False

        while touch_door_ok == False:
            #获取验证码
            random_num = random.randint(0,1000)
            url= "http://atm.zte.com.cn/atm/Application/AboutMy/CheckCode.aspx?x=%s" % random_num
            #print(url)
            response = urllib2.urlopen(url).read()
            vcode_file = "vcode.png"
            with open(vcode_file, "wb") as f:
                f.write(response)
            #yzm = input("Plz input the verify code:")

            post_png_code_to_master(name)
            print("send code to web ok.")
            yzm = wait_for_submit_code(name)

            print(yzm)
            if yzm is None:
                set_status(name,"touch_door_faield")
                return

            tms_submit_data.update({'txtpas':yzm})
            time.sleep(5)

            #准备提交刷卡
            url = "http://atm.zte.com.cn/atm/Application/AboutMy/netchkinout.aspx?menuId=ssb.atm.menu.item.onlinecheck"
            print(url)
            tms_submit_data_en=urllib.urlencode(tms_submit_data)
            tms_submit_data_en = tms_submit_data_en.encode(encoding='utf-8')
            full_url =urllib2.Request(url, tms_submit_data_en)

            #real login
            response = urllib2.urlopen(full_url).read()
            with open("%s_submit_result.html" % datetime.now().strftime("%y-%m-%d_%H_%M"), "wb") as f:
                f.write(response)

            if is_touch_door_ok(response):
                print("touch door ok.")
                set_status(name,"touch_door_ok")
                touch_door_ok= True
                return
            else:
                print("touch door faield.")
                if is_need_relogin(response):
                    print("need relogin.")
                    break
                # set_status(name,"touch_door_faield")
                touch_door_ok= False

def parse_time(time):
    tt = time.split(":")
    m_hour = 0
    m_minute = 0
    if len(tt) == 1:
        m_hour = int(tt[0])
        m_minute = 0
    if len(tt) == 2:
        m_hour = int(tt[0])
        m_minute =int(tt[1])
    else:
        return None
    return m_hour, m_minute


def auto_touch_door(user_name, user_id, user_passwd, m_time, n_time):

    m_hour, m_minute = parse_time(m_time)
    n_hour, n_minute = parse_time(n_time)
    while True:
        hour=0
        minute=0
        try:
            if datetime.now()< datetime.now().replace(hour=m_hour, minute=m_minute):
                hour = m_hour
                minute = m_minute
            #elif datetime.now()< datetime.now().replace(hour=m_hour + 1, minute=m_minute):
            #    hour = m_hour + 1
            #    minute = m_minute
            elif datetime.now()< datetime.now().replace(hour=n_hour, minute=n_minute):
                hour = n_hour
                minute = n_minute
            #elif datetime.now()< datetime.now().replace(hour=n_hour + 1, minute=minute):
            #    hour = n_hour + 1
            #    minute = minute
            else:
                hour = m_hour
                minute = m_minute

            sleep_time = get_sleep_seconds(hour, minute)
            
            if sleep_time > (10 * 60):
                sleep_time = 10 * 60
                print "sleep %s" % sleep_time
                time.sleep(sleep_time)
                continue
                
            print "sleep %s" % sleep_time
            time.sleep(sleep_time)

            touchTime = datetime.now().replace(hour=hour, minute=minute, second=0)
            set_status(user_name,"client_hello")
            time.sleep(30)
            login_atm(user_name, user_id, user_passwd)
            print "login %s" % touchTime.strftime("%y-%m-%d %H:%M")
        except:
            print "Got a except &&&&&&&&&&&&&&&&&"

if __name__ == '__main__':
    import sys
    auto_touch_door(sys.argv[1],sys.argv[2],sys.argv[3], sys.argv[4], sys.argv[5])
