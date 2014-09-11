__author__ = 'zz'

import getpass
import requests
from Lib import urls
import pickle
import os
from Lib import setting


class Author:

    def __init__(self, userid):
        self.userid = userid

    def get_illust(self, pn=0):
        pass


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
