import os
import queue
import threading
from zzlib.decorators import loop, retry_connect
from requests import get as _get

__author__ = 'zz'


@retry_connect(retry_times=3, timeout=3, error=None)
def requests_get(url, **kwargs):
    return _get(url, **kwargs)


class PixivUser:

    def __init__(self):
        pass

    def login(self):
        pass


class UserInputParse:
    def __init__(self):
        self.action = ''

    def parse(self, info:str):
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