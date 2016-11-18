# coding: utf-8

import web
import json
import base64
import os

urls=(
    '/article/status','command_trigger',
    '/article/verify','verify_image_code',
    '/article/home','home_index',
)

render = web.template.render('static')

import subprocess

def fetch_executed_cmd_status(cmd):
    popen = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        close_fds=False
    )
    error_info = popen.stderr.read()
    status = popen.wait()
    return status, error_info

app = web.application(urls,globals())

def update_db(section,item,value):
    import ConfigParser
    cf = ConfigParser.ConfigParser()
    cf.read('db.ini')
    if not cf.has_section(section):
        cf.add_section(section)
    cf.set(section,item, value)
    cf.write(open('db.ini', "w"))

def get_db(section,item):
    import ConfigParser
    cf = ConfigParser.ConfigParser()
    cf.read('db.ini')
    return cf.get(section,item)

class verify_image_code:
    #上传验证码图片
    def GET(self):

        data = web.input(name="",query=None)

        ret="OK"

        if data['query'] is not None:
            byte_cts = bytes(data['query'])
            with open("static"+ os.sep + data['name']+'.png', 'wb') as f:
                f.write(base64.urlsafe_b64decode(byte_cts))
            web.header('content-type','text/json')
            return json.dumps({'success':"save code ok"})
        else:
            ret = get_db(data['name'],"code")
            web.header('content-type','text/json')
            return json.dumps({'code':ret})

    def POST(self):

        data=web.input(name="", txt_pas=None)

        if data['txt_pas'] is not None:
            update_db(data['name'],"code", data['txt_pas'])
            update_db(data['name'],"status", "plz_submit")
            try:
                os.remove("static"+ os.sep + data['name']+'.png')
            except Exception as e:
                pass
        return json.dumps({'verify_code':data['txt_pas']})

class command_trigger:
    def GET(self):
        data=web.input(name="",status=None)

        if data['status'] is not None:
            update_db(data['name'],"status", data['status'])

        status = get_db(data['name'],"status")

        web.header('content-type','text/json')
        return json.dumps({'status':status})


    def POST(self):
        data=web.input(name="",status=None)
        update_db(data['name'],"status","server_hello")

        return json.dumps({'status':get_db(data['name'],"status")})

class home_index:
    def GET(self):

        return render.index(get_db("xie","status"),get_db("li","status"))

if __name__ == '__main__':
        app.run()