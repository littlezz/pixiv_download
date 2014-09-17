__author__ = 'zz'

from threading import Lock

import Lib.models

from Lib.setting import connect_fail_prompt_bound
from random import choice
from functools import wraps
error_lock = Lock()
prompt_lock = Lock()


def threading_lock(lock):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with lock:
                return func(*args, **kwargs)
        return wrapper
    return decorator

class Prompt:


    def __init__(self,total=0):
        self.total = total
        self.current = 0
        self.init_texts()
        self.randomtext()

    @threading_lock(prompt_lock)
    def prompt(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            ret = func(*args, **kwargs)
            self.current += 1
            self._prompt()
            return ret
        return wrapper

    def _prompt(self):

        print(format(self.current / self.total, '<8.2%') + self.nowtext, end='\r')

        if self.current % 4 == 0:
            self.randomtext()


    def init_texts(self):
        self.texts = (
            '正在检查线路',
            '正在确保控制器',
            '重载思考模型',
        )

    def randomtext(self):
        self.nowtext = choice(self.texts)

    def reset(self, total):
        self.current = 0
        self.total = total







class Error:
    def __init__(self):
        self._connect_fail = 0

    @threading_lock(error_lock)
    def reconnect(self, try_times):
        print('连接失败,正在尝试第{}次重连'.format(try_times))
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