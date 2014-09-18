__author__ = 'zz'

from threading import Lock
from .setting import connect_fail_prompt_bound
from random import choice
from functools import wraps
from .decorators import threading_lock


error_lock = Lock()
prompt_lock = Lock()
prompt_detect_error_lock = Lock()

class Prompt:


    def __init__(self, total=0):
        self.total = total
        self.current = 0
        self.init_texts()
        self.randomtext()
        self.error_times = 0

    def prompt(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            ret = func(*args, **kwargs)
            self._prompt()
            return ret
        return wrapper

    @threading_lock(prompt_lock)
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

    def report(self, title):
        print(format('report', '-^25'))
        print(title)
        print('总计{},成功{},失败{}'.format(self.total, self.total - self.error_times, self.error_times))
        print('-'*25)


    def init_texts(self):
        self.texts = (
            '正在检查线路',
            '正在确保控制器',
            '重载思考模型',
            '神经连接断开率超过30%!',
        )

    def randomtext(self):
        self.nowtext = choice(self.texts)

    def reset(self, total):
        self.current = 0
        self.total = total
        self.error_times = 0

    @staticmethod
    def session_login_ing():
        print('正在验证身份')

    @staticmethod
    def operate_user_sure(operate, t):
        print('='*25)
        print('operate: {}'.format(operate))
        print('args: {}'.format(t))

    @staticmethod
    def relogin():
        print('身份验证失败,请登陆')



class Error:
    def __init__(self):
        self._connect_fail = 0

    @threading_lock(error_lock)
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

    def connect_not_ok(self, status_code, reason):
        print('访问失败,错误代号{},原因{}'.format(status_code, reason))