__author__ = 'zz'

from functools import wraps
from requests import Timeout
import socket


timeouts = (Timeout, socket.timeout)


def contain_type(type_=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            ret = func(*args, **kwargs)
            if type:
                return list(type_(i) for i in ret)
        return wrapper
    return decorator


def threading_lock(lock):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with lock:
                return func(*args, **kwargs)
        return wrapper
    return decorator


def retry_connect(retry_times, timeout, error):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try_times = 0
            while True:
                try:
                    ret = func(*args, timeout=timeout, **kwargs)
                    if ret.status_code != 200:
                        error.connect_not_ok(ret.status_code, ret.reason)
                        raise Timeout
                except timeouts:

                    try_times += 1
                    error.reconnect(try_times)
                else:
                    return ret

                if try_times >= retry_times:
                    raise Timeout

        return wrapper
    return decorator


def sema_lock(func):
    @wraps(func)
    def wrapper(self, s, *args, **kwargs):
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


def resolve_timeout(replace_value):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except timeouts as e:
                print(type(e))
                return replace_value
        return wrapper
    return decorator