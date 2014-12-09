import getpass
import os
import pickle
import queue
import threading
import time
from zzlib.decorators import loop, retry_connect
from . import settings
from . import urls
from requests import get as _get
import requests

__author__ = 'zz'


@retry_connect(retry_times=3, timeout=3, error=None)
def requests_get(url, **kwargs):
    return _get(url, **kwargs)


class PixivUser:

    def __init__(self):
        self.session = requests.Session()
        self.phpsessid = ''
        self._logged = False
        self.phpsessid_file = settings.PHPSESSID_FILE

    def login(self):
        try:
            with open(self.phpsessid_file, 'rb') as file:
                phpsessid = pickle.load(file)
        except FileNotFoundError:
            phpsessid=''

        if not phpsessid:
            self._confirm_login()

        resp = requests_get(urls.TEST_LOGGED_URL.format(phpsessid))

        if resp.text:
            self.phpsessid = phpsessid
            self._logged = True
        else:
            self._confirm_login()

        if not self._logged:
            raise RuntimeError


    @loop
    def _confirm_login(self):
        username = input('username:\n')
        password = getpass.getpass('password:\n')

        payload = {'mode': 'login', 'return_to': '', 'pixiv_id': username, 'pass': password, 'skip': 1}

        self._login_resp = self.session.post(urls.LOGIN, data=payload)

        if self._login_resp == urls.SUCCESS_REDIRECT:
            self._logged = True
            self.phpsessid = self._get_phpsessid(self._login_resp.request.headers['cookie'])
            self._write_phpsessid()

            return True
        else:
            # error
            time.sleep(2)


    @staticmethod
    def _get_phpsessid(cookie):
        for s in cookie.split(';'):
            if s.startswith('PHPSESSID'):
                return s[10:]

    def _write_phpsessid(self):
        with open(self.phpsessid_file, 'wb') as file:
            pickle.dump(self.phpsessid, file)

    @retry_connect(retry_times=3, timeout=3, error=None)
    def get(self, url, **kwargs):
        """ 带重连的session 连接"""

        return self.session.get(url, **kwargs)



class UserInputParse:
    def __init__(self):
        self.action = ''

    def parse(self, info: str):
        pass

    def isvalid(self):
        pass


class UserInteract:
    def __init__(self, user):
        self.user = user
        self.parse = UserInputParse()

    @loop
    def process(self):
        """
        获取用户的输入, 调用相应的解析, 调用相应的程序.
        """

        user_input = input()

        self.parse.parse(user_input)
        if not self.parse.isvalid():
            return False

        action = self.parse.action
        getattr(self.user, 'do_' + action)


class AsyncImageDownload:
    def __init__(self, max_threading=4):
        self._lock = threading.Lock()
        self._q = queue.Queue()
        self._sentinel = object()
        self.max_threading = max_threading

    def start(self):
        for i in range(self.max_threading):
            t = threading.Thread(target=self._threading_download)
            t.start()


    def download(self, img_url, save_path):
        self._q.put((img_url, save_path))

    @loop
    def _threading_download(self):
        infos = self._q.get()

        if self._sentinel in infos:
            self.stop()
            return True

        img_url, save_path = infos

        # TODO: 完成下载的部分, 下载需要从中图模式进入大图模式.


    def stop(self):
        self._q.put((self._sentinel, self._sentinel))