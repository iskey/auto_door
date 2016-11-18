import os, time, subprocess
import re

import urllib.request
import urllib.parse
import http.cookiejar
import requests
import random

from bs4 import BeautifulSoup

import pytesseract
from PIL import Image,ImageEnhance,ImageFilter,ImageGrab, ImageDraw



gitlab_headers={
'Accept':'image/gif, image/jpeg, image/pjpeg, image/pjpeg, application/x-shockwave-flash, application/x-ms-application, application/x-ms-xbap, application/vnd.ms-xpsdocument, application/xaml+xml, application/vnd.ms-excel, application/vnd.ms-powerpoint, application/msword, */*',
#'Referer':'http://atm.zte.com.cn/atm/Application/AboutMy/netchkinout.aspx?menuId=ssb.atm.menu.item.onlinecheck',
'Accept-Language':'zh-cn',
'User-Agent':'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; InfoPath.2; .NET4.0C; TCO_20160823182603)',
'Content-Type':'application/x-www-form-urlencoded',
#'Accept-Encoding':'gzip, deflate',
#'Host':'atm.zte.com.cn',
#'Content-Length':'918',
'Connection': 'Keep-Alive',
'Pragma':'no-cache',
}

gitlab_login_data={
    'utf8':'✓',
    'user[login]':'xieych',
    'user[password]':'123456789',
    'user[remember_me]':"0"
}

def login_gitlab(url):
    cj = http.cookiejar.CookieJar()
    opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    login_url=url+ 'users/sign_in'

    opener.addheaders=[]
    for k,v in gitlab_headers.items():
        opener.addheaders.append((k,v))

    urllib.request.install_opener(opener)

    response = urllib.request.urlopen(url).read()
    with open("output1.html", 'wb') as f:
        f.write(response)

    soup=BeautifulSoup(response)
    csrf_param=soup.find(attrs={"name":"csrf-param"})['content']
    print(csrf_param)

    csrf_token=soup.find(attrs={"name":"csrf-token"})['content']
    print(csrf_token)
    gitlab_login_data.update({'authenticity_token':csrf_token})

    login_data_en=urllib.parse.urlencode(gitlab_login_data)
    login_data_en = login_data_en.encode(encoding='utf-8')

    full_url =urllib.request.Request(login_url, login_data_en)
    response = urllib.request.urlopen(full_url).read()
    with open("output2.html", "wb") as f:
        f.write(response)


    response = urllib.request.urlopen("http://10.80.216.226:81/bsp/hmpu_boot/commit/4ac2ed8ea43f479e654e4d99c8b63010e9480d65").read()
    with open("output3.html", "wb") as f:
        f.write(response)


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
    'txtUserName':'10164521',
    'btnLogin.x':25,
    'btnLogin.y':8,
    'PassWord':'xiaoxie123~',
    'rdoList':'zh-CN'
}

def binary(in_file,out_file='binary.jpg'):
    img=Image.open(in_file)
    new_img =  img.convert('L')
    threshold = 130
    table = []
    for i in range(256):
        if i < threshold:
            table.append(0)
        else:
            table.append(1)
    out = new_img.point(table,'1')
    out.save(out_file)

#切割图片
def division(self,img):
    font=[]
    print('enter division')
    for i in range(4):
        x=7+i*13
        y=3
        font.append(img.crop((x,y,x+9,y+13)))
    return font

def code_ocr(file):
    binary(file,'binary.jpg')
    img=Image.open('binary.jpg')
    vcode=pytesseract.image_to_string(img)
    return vcode

def login_atm():
    cj = http.cookiejar.CookieJar()
    opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    opener.addheaders=[]
    for k,v in tms_headers.items():
        opener.addheaders.append((k,v))

    urllib.request.install_opener(opener)

    url = "http://tms.zte.com.cn/tms/login.aspx"
    print(url)
    response = urllib.request.urlopen(url).read()
    with open("login_ui.html", 'wb') as f:
        f.write(response)
    time.sleep(5)

    soup=BeautifulSoup(response)
    event_validation=soup.find(attrs={"name":"__EVENTVALIDATION"})['value']
    print(event_validation)
    view_state=soup.find(attrs={"name":"__VIEWSTATE"})['value']
    print(view_state)
    tms_login_data.update({'__VIEWSTATE':view_state})
    tms_login_data.update({'__EVENTVALIDATION':event_validation})


    tms_login_data_en=urllib.parse.urlencode(tms_login_data)
    tms_login_data_en = tms_login_data_en.encode(encoding='utf-8')

    #real login
    full_url =urllib.request.Request(url, tms_login_data_en)
    response = urllib.request.urlopen(full_url).read()
    with open("login_result.html", "wb") as f:
        f.write(response)
    time.sleep(5)


    #进入刷卡界面
    url = "http://atm.zte.com.cn/atm/Application/AboutMy/netchkinout.aspx?menuId=ssb.atm.menu.item.onlinecheck"
    print(url)
    response = urllib.request.urlopen(url).read()
    with open("onlinecheck.html", "wb") as f:
        f.write(response)

    #准备填充提交表单及验证码
    submit_soup=BeautifulSoup(response)
    submit_event_validation=submit_soup.find(attrs={"name":"__EVENTVALIDATION"})['value']
    print(submit_event_validation)

    submit_view_state=submit_soup.find(attrs={"name":"__VIEWSTATE"})['value']
    print(submit_view_state)
    tms_submit_data={
        '__VIEWSTATE':submit_view_state,
        '__EVENTVALIDATION':submit_event_validation,
        'btnSubmit':"提交",
        'hidEmpInfo':10164521,
        'hidLanguage':'zh-CN'
    }

    #获取验证码
    random_num = random.randint(0,1000)
    url= "http://atm.zte.com.cn/atm/Application/AboutMy/CheckCode.aspx?x=%s" % random_num
    print(url)
    response = urllib.request.urlopen(url).read()
    vcode_file = "vcode.png"
    with open(vcode_file, "wb") as f:
        f.write(response)
    yzm = input("请输入验证码:")
    print(yzm)
    tms_submit_data.update({'txtpas':yzm})
    time.sleep(5)

    #准备提交刷卡
    url = "http://atm.zte.com.cn/atm/Application/AboutMy/netchkinout.aspx?menuId=ssb.atm.menu.item.onlinecheck"
    print(url)
    tms_submit_data_en=urllib.parse.urlencode(tms_submit_data)
    tms_submit_data_en = tms_submit_data_en.encode(encoding='utf-8')
    full_url =urllib.request.Request(url, tms_submit_data_en)

    #real login
    response = urllib.request.urlopen(full_url).read()
    with open("submit_result.html", "wb") as f:
        f.write(response)

    return


#login_gitlab('http://10.80.216.226:81/')
#http://atm.zte.com.cn/atm/Application/AboutMy/CheckCode.aspx?x=1532
#http://atm.zte.com.cn/atm/Application/AboutMy/netchkinout.aspx?menuId=ssb.atm.menu.item.onlinecheck
 #atm_url='/atm/Application/AboutMy/netchkinout.aspx?menuId=ssb.atm.menu.item.onlinecheck'

import re
import os
from PIL import *

def code_ocr2(file):
    print("Ocr..."+ file)
    import re
    binary(file,'binary.jpg')
    img=Image.open('binary.jpg')
    #使用ImageEnhance可以增强图片的识别率
    enhancer = ImageEnhance.Contrast(img)
    enhancer = enhancer.enhance(4)
    vcode=pytesseract.image_to_string(img,lang="eng",config="-psm 8")
    #vcode=re.sub("\W", "", vcode)
    return vcode

def RGB2BlackWhite(filename):
    im=Image.open(filename)
    print("image info,",im.format,im.mode,im.size)
    (w,h)=im.size
    R=0
    G=0
    B=0

    for x in range(w):
        for y in range(h):
            pos=(x,y)
            rgb=im.getpixel( pos )
            #print(rgb)
            (r,g,b)=rgb
            R=R+r
            G=G+g
            B=B+b

    rate1=R*1000/(R+G+B)
    rate2=G*1000/(R+G+B)
    rate3=B*1000/(R+G+B)

    print("rate:",rate1,rate2,rate3)


    for x in range(w):
        for y in range(h):
            pos=(x,y)
            rgb=im.getpixel( pos )
            (r,g,b)=rgb
            n= r*rate1/1000 + g*rate2/1000 + b*rate3/1000
            #print "n:",n
            if n>=170:
                im.putpixel( pos,(255,255,255))
            else:
                im.putpixel( pos,(0,0,0))

    im.save("blackwhite.bmp")

def saveAsBmp(fname):
    pos1=fname.rfind('.')
    fname1=fname[0:pos1]
    fname1=fname1+'_2.bmp'
    im = Image.open(fname)
    new_im = Image.new("RGB", im.size)
    new_im.paste(im)
    new_im.save(fname1)
    return fname1

#filename=saveAsBmp('vcode/20.png')
#RGB2BlackWhite(filename)
#print(code_ocr2('blackwhite.bmp'))


def gather_vcode():
    cj = http.cookiejar.CookieJar()
    opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    opener.addheaders=[]
    for k,v in tms_headers.items():
        opener.addheaders.append((k,v))

    urllib.request.install_opener(opener)

    for i in range(100):
        random_num = random.randint(0,1000)
        url= "http://atm.zte.com.cn/atm/Application/AboutMy/CheckCode.aspx?x=%s" % random_num
        print(url)
        response = urllib.request.urlopen(url).read()

        vcode_file = "vcode/%s.png" % i
        with open(vcode_file, "wb") as f:
            f.write(response)

        time.sleep(5)

    return

#合成图片
def union_pic():
    img_size=None
    s_img_path='vcode/'
    img=Image.open(s_img_path+'0.png')
    img_size= ( img.width*10,img.height*10)
    s_img_height= img.height
    s_img_width= img.width

    new_img=Image.new("RGBA", img_size, (255,255,255))
    Draw = ImageDraw.ImageDraw(new_img, "RGBA")

    for i in range(100):
        img_item = s_img_path + '%s.png' % i
        print(img_item)
        with Image.open(img_item) as f:
            new_img.paste(f, (int(i/10)*s_img_width, i%10*s_img_height))

    new_img.save('iskey.png')


#login_atm()

'''
cj = http.cookiejar.CookieJar()
opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

opener.addheaders=[]
for k,v in tms_headers.items():
    opener.addheaders.append((k,v))

urllib.request.install_opener(opener)
random_num = random.randint(0,1000)
url= "http://atm.zte.com.cn/atm/Application/AboutMy/CheckCode.aspx?x=%s" % random_num
response = urllib.request.Request.g
print(response.content)
vcode_file = "vcode.png"
with open(vcode_file, "wb") as f:
    f.write(response)
'''
'''
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import urllib2

register_openers()

datagen, headers = multipart_encode({
                     'image': open('/Users/luo/img1.jpg', 'rb')
                   })

request = urllib2.Request('http://localhost:4567/', datagen, headers)
print urllib2.urlopen(request).read()
'''

import base64

#with open('vcode.png', 'rb') as f:
    #ct = f.read()
    #cts = base64.urlsafe_b64encode(ct)
    #cts = base64.encodebytes(ct)

    #print(cts)

    #print(type(cts))

    #urllib.request.urlopen("http://127.0.0.1:8080/web_stats?query=%s" % cts)
    #cnt = urllib.request.urlopen("http://127.0.0.1:8080/web_stats").read()
    #with open('vcode.txt', 'wc') as ff:
    #    ff.write(cts)

def post_to_master():
    cj = http.cookiejar.CookieJar()
    opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    urllib.request.install_opener(opener)


    with open('vcode.png', 'rb') as f:
        ct = f.read()
        #cts = base64.b64encode(ct)
        cts = base64.urlsafe_b64encode(ct)

        print(type(cts))

        #with open('out.png', 'wb') as ff:
        #    ff.write(base64.decodebytes(cts))

        #print(type(cts))
    url= "http://10.80.60.25:8080/web_stats?query=%s" % cts
    print(url)
    response = urllib.request.urlopen(url).read()


post_to_master()