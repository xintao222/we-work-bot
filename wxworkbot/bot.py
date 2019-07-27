import types
import requests
import logging
import time
import sys
from threading import Thread

DEBUG = sys.flags.debug


class Bot(Thread):

    def __init__(self, url):
        super().__init__()
        self.msg_type = 'text'
        # TODO check url
        self.url = url
        self._sleep_seconds = 60
        self._check_counter = -1
        self._check_fn = None
        self._check_args = []
        self._check_kwargs = {}
        self._text = ''
        self._text_render_fn = None
        self._text_render_args = []
        self._text_render_kwargs = {}
        self._mentioned_list = []
        self._mentioned_mobile_list = []
        self._send_counter = -1

    def __get_text__(self):
        if self._text_render_fn:
            return self._text_render_fn(*self._text_render_args, **self._text_render_kwargs)
        elif self._text:
            return self._text
        else:
            raise KeyError("请设置发送的消息")

    def every(self, second=60, minute=0, hour=0, day=0):
        self._sleep_seconds = second + minute*60 + hour*3600 + day*86400
        return self

    def check(self, fn, args=None, kwargs=None):
        """
        Function used for setting checking function.
        :param fn: callback function
        :param args: list, the args to send to the function as fn(*args, **kwargs)
        :param kwargs: dict, the kwargs to send to the function as fn(*args, **kwargs)
        :return: self
        """
        assert isinstance(fn, types.FunctionType)
        assert args is None or isinstance(args, list)
        assert kwargs is None or isinstance(kwargs, dict)
        self._check_fn = fn
        self._check_args = args or []
        self._check_kwargs = kwargs or {}
        return self

    def __check__(self):
        """
        Function to call the callback function and get a bool value to determine whether to send the message
        :return: bool
        """
        if self._check_fn:
            return self._check_fn(*self._check_args, **self._check_kwargs)
        return True

    def set_text(self, text):
        assert isinstance(text, str)
        self._text = text
        return self

    def render_text(self, fn, args, kwargs):
        assert isinstance(fn, types.FunctionType)
        assert args is None or isinstance(args, list)
        assert kwargs is None or isinstance(kwargs, dict)
        self._text_render_fn = fn
        self._text_render_args = args or []
        self._text_render_kwargs = kwargs or {}
        return self

    def set_mentioned_list(self, ls):
        assert isinstance(ls, list)
        self._mentioned_list = ls
        return self

    def set_mentioned_mobile_list(self, ls):
        assert isinstance(ls, list)
        self._mentioned_mobile_list = ls
        return self

    def set_checker_counter(self, n=-1):
        self._check_counter = n
        return self

    def set_send_counter(self, n=-1):
        self._send_counter = n
        return self

    def send(self):
        if self.msg_type == 'text':
            req_body = {
                        "msgtype": "text",
                        "text": {
                                "content": self.__get_text__(),
                                "mentioned_list": self._mentioned_list,
                                "mentioned_mobile_list": self._mentioned_mobile_list
                                }
                        }
            if DEBUG:
                return self.url, req_body
            else:
                rsp = requests.post(self.url, json=req_body)
                if rsp.status_code != 200:
                    logging.error(rsp)
        elif self.msg_type == 'markdown':
            raise NotImplemented
        else:
            raise TypeError('Not supported message type')

    def run(self):
        while self._send_counter and self._check_counter:
            self._check_counter -= 1
            if self.__check__():
                self.send()
                self._send_counter -= 1
            time.sleep(self._sleep_seconds)




