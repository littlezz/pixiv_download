__author__ = 'zz'

import getpass
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
import threading
from collections import deque
from Lib.urls import referer as referer_template
from os.path import join as pathjoin

def retry_connect(retry_times, timeout):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try_times = 0
            while True:
                try:
                    ret = func(*args, timeout=timeout, **kwargs)
                    if ret.status_code != 200:
                        print(ret.status_code,ret.reason)
                        raise Timeout
                except Timeout:

                    try_times += 1
                    print('faild ',try_times)
                else:
                    return ret

                if try_times >= retry_times:
                    raise Timeout

        return wrapper
    return decorator

"""
def sema_lock(s=SEMA):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with s:
                return func(*args, **kwargs)

        return wrapper
    return decorator
"""
def sema_lock(func):
    @wraps(func)
    def wrapper(self,s, *args, **kwargs):
        with s:
            return func(self, *args, **kwargs)

    return wrapper

def put_data(func):
    @wraps(func)
    def wrapper(self, _deque, *args, **kwargs):
        ret_list = func(self, *args, **kwargs)
        _deque.append(ret_list)

    return wrapper


def loop(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        while True:
            ret = func(*args, **kwargs)
            if ret:
                break
    return wrapper



@retry_connect(setting.RETRY_TIMES, setting.TIMEOUT)
def requests_get(url, **kwargs):
    return _requests_get(url, **kwargs)


@retry_connect(setting.RETRY_TIMES, setting.TIMEOUT)
def requests_post(url, data=None, **kwargs):
    return _requests_post(url, data, **kwargs)




def exist_or_create(path):
    if not os.path.exists(path):
        os.mkdir(path)




class Item:
    patter=re.compile(r'(.*?)mobile')

    def __init__(self, list_):
        self._list = list_
        self.illust_id = list_[0]
        self.author_id = list_[1]
        self.extensions =  list_[2]
        self.mobile_image = list_[9]
        self.page = list_[19]
        self.type = 'image'
        self._dealwith_type()
        self._dealwith_image()

    def _dealwith_type(self):
        if self.page:
            self.type = 'manga'

    def _dealwith_image(self):
        self.filename = self.mobile_image.split('/')[-1].split('_')[0] + '.' + self.extensions
        self.path = pathjoin(setting.root_folder, self.author_id, self.filename)
        try:
            self.image_url = self.patter.match(self.mobile_image).group(1) + self.filename
        #animation url
        except AttributeError:
            self.type = 'animation'

    @sema_lock
    def download(self):
        if os.path.exists(self.path):
            return
        headers = {'referer': referer_template.format(self.illust_id)}
        cookies = {'PHPSESSID': self.phpsessid}
        req = requests_get(self.image_url, headers=headers, cookies=cookies)

        with open(self.path, 'wb') as f:
            f.write(req.content)

    @classmethod
    def set_phpsessid(cls, phpsessid):
        cls.phpsessid = phpsessid


class Author:

    def __init__(self, authorid, phpsessid):
        self.authorid = authorid
        self.phpsessid = phpsessid
        exist_or_create(pathjoin(setting.root_folder, authorid))

    def _get_illust(self, pn=1):
        while True:
            print('doing',self.authorid,'page',pn)
            req = requests_get(urls.ILLUST_LIST.format(self.authorid, self.phpsessid, pn))
            if not req.text:
                break
            filelike = StringIO(req.text)
            for i in reader(filelike):
                yield Item(i)

            pn += 1


    @sema_lock
    @put_data
    def get_illusts(self, support_types=None):
        """
        在这里和数据库对比过滤已经下载过的.
        在两个装饰器下,这个方法变得有点奇怪,他实际接受两个二外的参数,sema 和 deque.
        :return: a list include instance of Item
        """
        if not support_types:
            support_types = ('image',)
        print('support',support_types)
        return list(item for item in self._get_illust() if item.type in support_types)




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
            self.req = requests_post(urls.LOGIN, data=payload)
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
        if self.phpsessid == '0':
            return False

        req = requests_get(urls.TEST_LOGGED_URL.format(self.phpsessid))
        if req.text:
            return True
        else:
            return False

    def interactive(self):
        pass

class Downloader:

    def __init__(self, phpsessid, *author_list):
        self.phpsessid = phpsessid
        self.author_list = author_list
        self.download_list = list()
        self.sema = threading.Semaphore(setting.THREAD_NUMS)
        self._deque = deque()
        exist_or_create(setting.root_folder)

    def _get_download_list(self):
        threading_list = []
        for author in self.author_list:
            a = Author(author, self.phpsessid)
            t = threading.Thread(target=a.get_illusts, args=(self.sema, self._deque))
            threading_list.append(t)
            t.start()

        [t.join() for t in threading_list]
        for lt in self._deque:
            self.download_list.extend(lt)




    def download_all(self):
        Item.set_phpsessid(self.phpsessid)
        self._get_download_list()

        threading_list = []
        for item in self.download_list:
            t = threading.Thread(target=item.download, args=(self.sema,))
            threading_list.append(t)
            t.start()

        [t.join() for t in threading_list]











class DatabaseApi:
    pass
