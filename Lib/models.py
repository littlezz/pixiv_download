__author__ = 'zz'

from datetime import datetime
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
from .decorators import retry_connect, sema_lock, put_data, loop, resolve_timeout, contain_type, add_nowstrftime
from .database_api import DatabaseApi
from bs4 import BeautifulSoup
from queue import Queue




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

    def __init__(self, floder, list_):
        self._list = list_
        self.floder = floder
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
        self.path = pathjoin(setting.root_folder, self.floder, self.filename)
        try:
            self.image_url = self.patter.match(self.mobile_image).group(1) + self.filename
        #animation url
        except AttributeError:
            self.type = 'animation'

    @sema_lock
    @put_data
    @add_nowstrftime
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

    new_author_queue = Queue()

    def __init__(self, authorid, phpsessid):
        self.authorid = authorid
        self.phpsessid = phpsessid
        self.name = self.get_authorname(authorid)
        if self.name:
            self.flodername = '_'.join((authorid, self.name))
            self._folder_control()

    @classmethod
    def _put_new_author(cls, author_name_and_id):
        cls.new_author_queue.put(author_name_and_id)

    def _folder_control(self):
        """
        保持作者文件夹的命名
        流程:
            找出以authorid开头的文件夹(用split分离('_')取第0项.
            if 存在:
                判断和flodername是否相同,不同就改名
            else:
                建立flodername文件夹
        :return:None
        """
        _floder = list(i for i in os.listdir(setting.root_folder) if i.split('_')[0] == self.authorid)
        if _floder:
            floder = _floder[0]
            if floder != self.flodername:
                os.rename(pathjoin(setting.root_folder, floder), pathjoin(setting.root_folder, self.flodername))
                self._put_new_author((self.name, self.authorid))
        else:
            os.mkdir(pathjoin(setting.root_folder, self.flodername))

    @staticmethod
    @resolve_timeout('')
    def get_authorname(authorid):
        r = requests_get(urls.profile.format(authorid))
        return BeautifulSoup(r.content).table.td.text.strip() if r.status_code == 200 else ''

    def _get_illust(self, pn=1):
        while True:
            req = requests_get(urls.ILLUST_LIST.format(self.authorid, self.phpsessid, pn))
            if not req.text:
                break
            filelike = StringIO(req.text)
            for i in reader(filelike):
                yield Item(self.flodername, i)

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
            authors = self.database.pull_authors_id()

        # update author name
        Author.new_author_queue = Queue()
        exist_illusts = set(illust for author in authors for illust in self.database.get_illusts_id(author))
        download = Downloader(self.phpsessid, authors)
        download.get_item_list()
        update_illusts = list(i for i in download.download_list if i.illust_id not in exist_illusts)
        if update_illusts:
            update_info = download.download(update_illusts)
            self.database.push_record(update_info)
        else:
            update_info = list()
        update_info = sorted(update_info)

        while Author.new_author_queue.qsize():
            author_update = Author.new_author_queue.get()
            self.database.update_authorname(author_update)

        prompt.list_update(update_info)

    def do_add(self, authors):
        # self.database.add_authors(authors)
        # add authors to database
        nowdate = datetime.now().strftime('%y-%m-%d %H:%M')
        with prompt.valid_authorname():
            _authors = [(id, Author.get_authorname(id), nowdate) for id in authors]
            unvalid = list(i[0] for i in _authors if i[1] == '')
            if unvalid:
                error.unvalide_authors(unvalid)
                return

        self.database.add_authors(_authors)
        downloading_item = self.do_download(authors)
        self.database.push_record(downloading_item)


    def do_del(self, authors):
        self.database.delete_authors(authors)

    def do_list(self, _):
        prompt.list_authors(self.database.get_authors_info())

    def do_illusts(self, _):
        prompt.list_illusts(self.database.pull_all_illusts())


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
            exist_authors = self.database.pull_authors_id()
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
            exist_authors = self.database.pull_authors_id()
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
            # the same as del
            return self.check_operate_del(authors)
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


