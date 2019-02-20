"""
@author: Julian Sobott
@brief:
@description:

@external_use:

@internal_use:
"""
from thread_testing import get_num_non_dummy_threads
import threading
import time


def func():
    print("function called")
    ThreadGenerator.response()
    # call object of proper thread


class ThreadGenerator:

    @staticmethod
    def response():
        print(threading.current_thread().id_)


class Caller(threading.Thread):

    def __init__(self, id_):
        super().__init__(name=str(id_))
        self.id_ = id_
        self.is_on = True
        self.call_exe = False

    def run(self):
        while self.is_on:
            time.sleep(0.5)
            if self.call_exe:
                self.exe()
                self.call_exe = False

    def exe(self):
        func()


t1 = Caller(0)
t2 = Caller(1)
t1.start()
t2.start()
t1.call_exe = True
t2.call_exe = True

t1.is_on = False
t2.is_on = False