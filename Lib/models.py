__author__ = 'zz'

import getpass
import requests
from requests import get as _requests_get
from requests import post as _requests_post
from Lib import urls
import pickle
import os
from io import StringIO
from Lib import setting
from csv import reader
from functools import wraps
from requests.exceptions import Timeout
import re



def retry_connect(retry_times, timeout):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try_times = 0
            while True:
                try:
                    ret = func(*args, timeout=timeout,**kwargs)
                except Timeout:
                    try_times += 1
                else:
                    return ret

                if try_times >= retry_times:
                    raise Timeout

        return wrapper
    return decorator


@retry_connect(setting.RETRY_TIMES, setting.TIMEOUT)
def requests_get(url, **kwargs):
    return _requests_get(url, **kwargs)


@retry_connect(setting.RETRY_TIMES, setting.TIMEOUT)
def requests_post(url, data=None, **kwargs):
    return _requests_post(url, data, **kwargs)



class Item:
    patter=re.compile(r'(.*?)mobile')

    def __init__(self, list_):
        self.illust_id = list_[0]
        self.author_id = list_[1]
        self.extensions =  list_[2]
        self.mobile_image = list_[9]
        self._dealwith_image()

    def _dealwith_image(self):
        self.filename = self.mobile_image.split('/')[-1].split('_')[0] + '.' + self.extensions
        self.image_url = self.patter.match(self.mobile_image).group(1) + self.filename







class Author:

    def __init__(self, userid, phpsessid):
        self.userid = userid
        self.phpsessid = phpsessid

    def _get_illust(self, pn=1):
        while True:
            req = requests.get(urls.ILLUST_LIST.format(self.userid, self.phpsessid, pn))
            if not req.text:
                break
            filelike = StringIO(req.text)
            for i in reader(filelike):
                yield Item(i)

            pn += 1

    def download_list(self):
        """
        在这里和数据库对比过滤已经下载过的.
        :return: a list include instance of Item
        """

        return list(self._get_illust())




class User:

    def __init__(self):
        self.logined = False
        self.phpsessid_file = setting.PHPSEESID_FILE
        self.phpsessid = self.read_phpsessid()
        self.req = None

    def login(self):

        def get_phpsessid(cookie):
            for s in cookie.split(';'):
                if s.startswith('PHPSESSID'):
                    return s[10:]

        if self.check_logined():
            self.login_ok()
            return

        while True:
            username = input('username:\n')
            password = getpass.getpass('password:\n')

            payload = {'mode': 'login', 'return_to': '', 'pixiv_id': username, 'pass': password, 'skip': 1}
            self.req = requests.post(urls.LOGIN, data=payload)
            if self.req.url == urls.SUCCESS_REDIRECT:
                self.phpsessid = get_phpsessid(self.req.request.headers['cookie'])
                self.write_phpsessid()
                self.login_ok()
                break
            else:
                print('username or password is wrong, please try again\n')

    def login_ok(self):
        self.logined = True
        print('login success!',self.phpsessid)

    def read_phpsessid(self):
        if os.path.exists(self.phpsessid_file):
            with open(self.phpsessid_file, 'rb') as f:
                return pickle.load(f)
        else:
            return '0'

    def write_phpsessid(self):
        with open(self.phpsessid_file, 'wb') as f:
            pickle.dump(self.phpsessid, f)

    def check_logined(self):
        req = requests.get(urls.TEST_LOGGED_URL.format(self.phpsessid))
        if req.text:
            return True
        else:
            return False


class DataBaseApi:
    pass
