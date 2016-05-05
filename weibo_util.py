# encoding:utf8
__author__ = 'brianyang'

import re
import json
import requests
import cookielib
import rsa
import urllib
import urllib2
import binascii
import base64
from optparse import OptionParser

cookie_file = 'cookie.txt'


def pre_login():
    pre_login_url = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=MTUyNTUxMjY3OTY%3D&rsakt=mod&checkpin=1&client=ssologin.js%28v1.4.18%29&_=1458836718537'
    pre_response = requests.get(pre_login_url).text
    pre_content_regex = r'\((.*?)\)'
    patten = re.search(pre_content_regex, pre_response)
    nonce = None
    pubkey = None
    servertime = None
    rsakv = None
    if patten.groups():
        pre_content = patten.group(1)
        pre_result = json.loads(pre_content)
        nonce = pre_result.get("nonce")
        pubkey = pre_result.get('pubkey')
        servertime = pre_result.get('servertime')
        rsakv = pre_result.get("rsakv")
    return nonce, pubkey, servertime, rsakv


def generate_form_data(nonce, pubkey, servertime, rsakv, username, password):
    rsa_public_key = int(pubkey, 16)
    key = rsa.PublicKey(rsa_public_key, 65537)
    message = str(servertime) + '\t' + str(nonce) + '\n' + str(password)
    passwd = rsa.encrypt(message, key)
    passwd = binascii.b2a_hex(passwd)
    username = urllib2.quote(username)
    username = base64.encodestring(username)
    form_data = {
        'entry': 'weibo',
        'gateway': '1',
        'from': '',
        'savestate': '7',
        'useticket': '1',
        'pagerefer': 'http://weibo.com/p/1005052679342531/home?from=page_100505&mod=TAB&pids=plc_main',
        'vsnf': '1',
        'su': username,
        'service': 'miniblog',
        'servertime': servertime,
        'nonce': nonce,
        'pwencode': 'rsa2',
        'rsakv': rsakv,
        'sp': passwd,
        'sr': '1366*768',
        'encoding': 'UTF-8',
        'prelt': '115',
        'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
        'returntype': 'META'
    }
    form_data = urllib.urlencode(form_data)
    return form_data


def login(form_data):
    url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)'
    headers = ('User-Agent', 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0')
    cookie = cookielib.MozillaCookieJar(cookie_file)
    handler = urllib2.HTTPCookieProcessor(cookie)
    opener = urllib2.build_opener(handler)
    opener.addheaders.append(headers)
    req = opener.open(url, form_data)
    redirect_result = req.read()
    login_pattern = r'location.replace\(\'(.*?)\'\)'
    login_url = re.search(login_pattern, redirect_result).group(1)
    opener.open(login_url).read()
    cookie.save(cookie_file, ignore_discard=True, ignore_expires=True)


def request_image_url(image_path):
    cookie = cookielib.MozillaCookieJar()
    cookie.load(cookie_file, ignore_expires=True, ignore_discard=True)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
    image_url = 'http://picupload.service.weibo.com/interface/pic_upload.php?mime=image%2Fjpeg&data=base64&url=0&markpos=1&logo=&nick=0&marks=1&app=miniblog'
    b = base64.b64encode(file(image_path).read())
    data = urllib.urlencode({'b64_data': b})
    result = opener.open(image_url, data).read()
    result = re.sub(r"<meta.*</script>", "", result)
    image_result = json.loads(result)
    image_id = image_result.get('data').get('pics').get('pic_1').get('pid')
    return 'http://ww3.sinaimg.cn/large/%s' % image_id


def get_image(image_path, username=None, password=None):
    url = ''
    try:
        url = request_image_url(image_path)
    except:
        try:
            if not (username and password):
                username = raw_input("输入新浪微博用户名：")
                password = raw_input("输入新浪微博密码：")
            nonce, pubkey, servertime, rsakv = pre_login()
            form_data = generate_form_data(nonce, pubkey, servertime, rsakv, username, password)
            login(form_data)
            url = request_image_url(image_path)
        except Exception, e:
            print "登录失败,程序退出"
            exit()
    return url


if __name__ == '__main__':
    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)
    parser.add_option("-f", "--file", dest='filepath', help='image file path')
    parser.add_option("-u", "--username", dest="username", help="weibo username")
    parser.add_option("-p", "--password", dest="password", help="weibo password")
    (options, args) = parser.parse_args()
    filename = options.filepath
    username = options.username
    password = options.password
    if not filename:
        parser.error("Incorrect number of arguments")
    print get_image(filename, username, password)


