__author__ = 'zz'

import getpass
from requests import get as _requests_get
from requests import post as _requests_post
from . import urls
import pickle
import os
from io import StringIO
from . import setting
from csv import reader
import re
import threading
from collections import deque
from .urls import referer as referer_template
from os.path import join as pathjoin
import time
from .prompt import Error, Prompt
from .decorators import retry_connect, sema_lock, put_data, loop, resolve_timeout, contain_type
import sqlite3
from bs4 import BeautifulSoup
import logging
logging.basicConfig(level=logging.WARNING, format='%(funcName)s: %(message)s')


error = Error()
prompt = Prompt()


@retry_connect(setting.RETRY_TIMES, setting.TIMEOUT, error)
def requests_get(url, **kwargs):
    return _requests_get(url, **kwargs)


@retry_connect(setting.RETRY_TIMES, setting.TIMEOUT, error)
def requests_post(url, data=None, **kwargs):
    return _requests_post(url, data, **kwargs)


def exist_or_create(path):
    if not os.path.exists(path):
        os.mkdir(path)


class Item:
    patter = re.compile(r'(.*?)mobile')

    def __init__(self, list_):
        self._list = list_
        self.illust_id = list_[0]
        self.author_id = list_[1]
        self.extensions = list_[2]
        self.title = list_[3]
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
    @put_data
    @prompt.prompt
    @resolve_timeout(None)
    @prompt.detect_error
    def download(self):
        if not os.path.exists(self.path):

            headers = {'referer': referer_template.format(self.illust_id)}
            cookies = {'PHPSESSID': self.phpsessid}
            req = requests_get(self.image_url, headers=headers, cookies=cookies)

            with open(self.path, 'wb') as f:
                f.write(req.content)

        return self.author_id, self.illust_id, self.title

    @classmethod
    def set_phpsessid(cls, phpsessid):
        cls.phpsessid = phpsessid


class Author:

    def __init__(self, authorid, phpsessid):
        self.authorid = authorid
        self.phpsessid = phpsessid
        self.name = self.get_authorname()
        exist_or_create(pathjoin(setting.root_folder, '_'.join((authorid, self.name))))

    @resolve_timeout('')
    def get_authorname(self):
        r = requests_get(urls.profile.format(self.authorid))
        return BeautifulSoup(r.content).table.td.text.strip()

    def _get_illust(self, pn=1):
        while True:
            req = requests_get(urls.ILLUST_LIST.format(self.authorid, self.phpsessid, pn))
            if not req.text:
                break
            filelike = StringIO(req.text)
            for i in reader(filelike):
                yield Item(i)

            pn += 1


    @sema_lock
    @put_data
    @prompt.prompt
    @resolve_timeout([])
    @prompt.detect_error
    def get_illusts(self, support_types=None):
        """
        在这里和数据库对比过滤已经下载过的.
        在两个装饰器下,这个方法变得有点奇怪,他实际接受两个二外的参数,sema 和 deque.
        :return: a list include instance of Item
        """
        if not support_types:
            support_types = ('image',)

        return list(item for item in self._get_illust() if item.type in support_types)




class User:

    #只用在这里修改即可,在Parse和User在添加相应的方法
    support_operate = ('download', 'exit', 'add', 'del', 'list', 'illusts', 'update')

    def __init__(self):
        self.database = DatabaseApi()
        self.logined = False
        self.phpsessid_file = setting.PHPSEESID_FILE
        self.phpsessid = self.read_phpsessid()
        self.req = None

    @staticmethod
    def _get_phpsessid(cookie):
        for s in cookie.split(';'):
            if s.startswith('PHPSESSID'):
                return s[10:]

    @loop
    def _login(self):
        username = input('username:\n')
        password = getpass.getpass('password:\n')

        payload = {'mode': 'login', 'return_to': '', 'pixiv_id': username, 'pass': password, 'skip': 1}
        self.req = requests_post(urls.LOGIN, data=payload)
        if self.req.url == urls.SUCCESS_REDIRECT:
            self.phpsessid = self._get_phpsessid(self.req.request.headers['cookie'])
            self.write_phpsessid()
            self.login_ok()
            return True
        else:
            error.login_fail()
            time.sleep(2)

    def login(self):

        if self.check_logined():
            self.login_ok()
            return

        Prompt.relogin()
        self._login()

    def login_ok(self):
        self.logined = True
        #print('login success!',self.phpsessid)
        Prompt.login_ok()

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
        Prompt.session_login_ing()

        if self.phpsessid == '0':
            return False

        req = requests_get(urls.TEST_LOGGED_URL.format(self.phpsessid))
        if req.text:
            return True
        else:
            return False

    @loop
    def interactive(self):
        parse = Parse(self.support_operate, self.database)
        parse.parse(input(setting.input_prompt))
        parse.user_sure()
        if parse.status and parse.sure:
            getattr(self, 'do_' + parse.operate)(parse.args)


    def do_download(self, authors):
        download = Downloader(self.phpsessid, authors)
        return download.download()


    def do_exit(self, _):
        print('bye')
        self.database.conn.close()
        exit(0)


    def do_update(self, authors):
        if not authors:
            authors = self.database.pull_authors()
        exist_illusts = set(illust for author in authors for illust in self.database.get_illusts(author))
        download = Downloader(self.phpsessid, authors)
        download.get_item_list()
        update_illusts = list(i for i in download.download_list if i.illust_id not in exist_illusts)
        if update_illusts:
            update_info = download.download(update_illusts)
            self.database.push_record(update_info)
        else:
            update_info = list()
        update_info = sorted(update_info)
        prompt.list_update(update_info)

    def do_add(self, authors):
        self.database.add_authors(authors)
        downloading_item = self.do_download(authors)
        self.database.push_record(downloading_item)


    def do_del(self, authors):
        self.database.delete_authors(authors)

    def do_list(self, _):
        exist_authors = self.database.pull_authors()
        prompt.list_authors(exist_authors)

    def do_illusts(self, _):
        illusts = self.database.pull_all_illusts()
        prompt.list_illusts(illusts)


class Parse:
    patter = re.compile(r'[,;\s]\s*')

    def __init__(self, support_key, database):
        self.database = database
        self._keys = support_key
        self.status = False
        self.sure = False
        self.operate = ''
        self.args = list()

    def parse(self, st: str):
        st = st.lower()
        operate, *args = self.patter.split(st)

        if operate not in self._keys:
            error.unavailble_operate(operate)
            return
        check = getattr(self, 'check_operate_' + operate)
        self.status = check(args)
        if self.status:
            self.operate = operate
            self.args = args

    def user_sure(self):
        if not self.status:
            return
        Prompt.operate_user_sure(self.operate, self.args)
        _input = input('Is This Ok? [y/N]:')
        if _input == 'y':
            self.sure = True

    @staticmethod
    def _validated_authors(authors):
        """
        not empty, can int() for each item
        :return:
        """
        if authors:
            try:
                list(map(int,authors))
            except ValueError:
                pass
            else:
                return True

        error.unavailble_args()
        return False

    def check_operate_download(self, authors):
        return self._validated_authors(authors)

    def check_operate_exit(self, _):
        """
        do nothing
        :param _: useless param
        :return: return True
        """
        return True

    def check_operate_add(self, authors):

        if self._validated_authors(authors):
            exists = []
            exist_authors = self.database.pull_authors()
            for i in exist_authors:
                if i in authors:
                    exists.append(i)

            if exists:
                error.exist_authors(exists)
                return False
            else:
                return True

    def check_operate_del(self, authors):
        if self._validated_authors(authors):
            not_exists = []
            exist_authors = self.database.pull_authors()
            for i in authors:
                if i not in exist_authors:
                    not_exists.append(i)

            if not_exists:
                error.authors_not_exist(not_exists)
                return False
            else:
                return True

    def check_operate_list(self, _):
        return True

    def check_operate_illusts(self, _):
        return True

    def check_operate_update(self, authors):
        if authors:
            return self._validated_authors(authors)
        else:
            return True

class Downloader:

    def __init__(self, phpsessid, author_list):
        self.phpsessid = phpsessid
        self.author_list = author_list
        self.download_list = list()
        self.complete_info = deque() # download return (authorid, illustid)
        self.sema = threading.Semaphore(setting.THREAD_NUMS)
        self._deque = deque()
        exist_or_create(setting.root_folder)

    def get_item_list(self):
        threading_list = []
        prompt.reset(len(self.author_list), '正在获取作者作品列表')

        for author in self.author_list:
            a = Author(author, self.phpsessid)
            t = threading.Thread(target=a.get_illusts, args=(self.sema, self._deque))
            threading_list.append(t)
            t.start()

        [t.join() for t in threading_list]
        for lt in self._deque:
            self.download_list.extend(lt)

        prompt.report('获取作者列表')



    def _threading_download(self):
        Item.set_phpsessid(self.phpsessid)
        threading_list = []
        for item in self.download_list:
            t = threading.Thread(target=item.download, args=(self.sema, self.complete_info))
            threading_list.append(t)
            t.start()

        [t.join() for t in threading_list]

    def download(self, download_list=None):
        """
        :param download_list:
        :return: comelete_info
        """
        if download_list:
            self.download_list = download_list
        else:
            self.get_item_list()
        prompt.reset(len(self.download_list), '正在下载')
        self._threading_download()
        prompt.report('下载图片')

        return self.complete_info



class DatabaseApi:
    dbfile = setting.DATABASE

    def __init__(self):
        if not os.path.exists(self.dbfile):
            self.create_database(self.dbfile)
        self.conn = sqlite3.connect(self.dbfile)

    @contain_type(str)
    def pull_authors(self):
        with self.conn:
            cur = self.conn.cursor()
            cur.execute('select * from Authors')
            return (i[0] for i in cur.fetchall())

    @contain_type(str)
    def get_illusts(self, author):
        with self.conn:
            cur = self.conn.cursor()
            cur.execute('SELECT id FROM Illusts WHERE author=?', (author,))
            return (i[0] for i in cur.fetchall())

    @staticmethod
    def create_database(dbfile):
        with sqlite3.connect(dbfile) as conn:
            cur = conn.cursor()
            cur.executescript("""
                CREATE TABLE Authors(id INTEGER PRIMARY KEY );
                CREATE TABLE Illusts(author INTEGER , id INTEGER PRIMARY KEY, title TEXT );
            """)

    def add_authors(self, authors_id):
        """
        :param authors_id: list,里面的类型应该为可以转话为int的类型,比如纯数字str或者int.所以不用特别转为int,保证纯数字即可.
        :return:
        """
        with self.conn:
            cur = self.conn.cursor()
            for i in authors_id:
                cur.execute('INSERT INTO Authors values (?)', (i,))

    def push_record(self, data):
        """
        :param data:[(authors_id:int,illust_id:int)]
        :return: None
        """
        with self.conn:
            cur = self.conn.cursor()
            cur.executemany('INSERT INTO Illusts VALUES (?,?,?)',data)

    def delete_authors(self, authors_id):
        with self.conn:
            cur = self.conn.cursor()
            for i in authors_id:
                cur.execute('DELETE FROM Authors WHERE id=?',(i,))
                cur.execute('DELETE FROM Illusts WHERE author=?',(i,))

    def pull_all_illusts(self):
        with self.conn:
            cur = self.conn.cursor()
            cur.execute('SELECT * FROM Illusts ORDER BY author')
            return list(cur.fetchall())


