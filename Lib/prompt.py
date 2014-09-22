__author__ = 'zz'

from threading import Lock
from .setting import connect_fail_prompt_bound
from random import choice
from functools import wraps
from .decorators import threading_lock
from shutil import get_terminal_size


error_lock = Lock()
prompt_lock = Lock()
prompt_detect_error_lock = Lock()
terminal_width, _ = get_terminal_size()


def clear_output(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(' ' * terminal_width, end='\r')
        return func(*args, **kwargs)
    return wrapper


class Prompt:


    def __init__(self, total=0):
        self.total = total
        self.current = 0
        self.init_texts()
        self.randomtext()
        self.error_times = 0
        self.terminal_size = 50
        self.get_terminal_size()

    def get_terminal_size(self):
        c, l = get_terminal_size()
        self.terminal_size = c

    def prompt(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            ret = func(*args, **kwargs)
            self._prompt()
            return ret
        return wrapper

    @threading_lock(prompt_lock)
    @clear_output
    def _prompt(self):
        self.current += 1
        print(format(self.current / self.total, '<8.2%') + self.nowtext, end='\r')
        if self.current % 4 == 0:
            self.randomtext()


    @threading_lock(prompt_detect_error_lock)
    def _detect_error(self):
        self.error_times += 1

    def detect_error(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                self._detect_error()
                raise e
        return wrapper

    @clear_output
    def report(self, title):
        print(format('report', '-^{}'.format(self.terminal_size)))
        print(title)
        print('总计{},成功{},失败{}'.format(self.total, self.total - self.error_times, self.error_times))
        print('-' * self.terminal_size)


    def init_texts(self):
        self.texts = (
            '正在检查线路安全',
            '正在确保控制器',
            '重载思考模型',
            '正在检查插入栓深度',
            '正在检查裙子里面的不明突起',
            '正在解决自涉悖论',
            '正在展开AT力场',
            '正在确保线路057',
            '正在启动过载保护',
            '魔力控制在预期范围内',


        )

    def randomtext(self):
        self.nowtext = choice(self.texts)

    def reset(self, total, prompt):
        self.current = 0
        self.total = total
        self.error_times = 0
        print(prompt)

    @staticmethod
    def session_login_ing():
        print('正在验证身份')

    @staticmethod
    @clear_output
    def operate_user_sure(operate, t):
        print('=' * terminal_width)
        print('operate: {}'.format(operate))
        print('args: {}'.format(t))

    @staticmethod
    def relogin():
        print('身份验证失败,请登陆')

    @staticmethod
    def list_authors(authors):
        print('加入数据库的作者id:')
        for i in authors:
            print(i)

    def list_illusts(self, illusts):
        left = format('{}', '<15')
        right = format('| {}', '<15')

        print(left.format('作者id'), right.format('作品id'))
        for authorid, illustid in illusts:
            print(left.format(authorid), right.format(illustid))


class Error:
    def __init__(self):
        self._connect_fail = 0

    @threading_lock(error_lock)
    @clear_output
    def reconnect(self, try_times):
        print('连接断开,正在尝试第{}次重连'.format(try_times))
        self._connect_fail += 1

        if self._connect_fail > connect_fail_prompt_bound:
            print('当前连接通道不稳定! 请检查网路状况....')
            self._connect_fail = 0

    def unavailble_operate(self, wrong_operate):
        print('{} 操作无法识别'.format(wrong_operate))

    def unavailble_args(self):
        print('参数无法识别,可能有误')

    def login_fail(self):
        print('username or password is wrong, please try again')
        print('静默两秒')

    @clear_output
    def connect_not_ok(self, status_code, reason):
        print('访问失败,错误代号{},原因{}'.format(status_code, reason))

    def exist_authors(self, authors):
        print(' '.join(authors),' 已经存在!')

    def authors_not_exist(self, authors):
        print(' '.join(authors),' 不存在!')