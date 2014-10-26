#!/usr/bin/python

import threading
from time import ctime
from Queue import Queue


class MyThread(threading.Thread):
    q = Queue(maxsize=0)

    def __init__(self, func, args, name=""):
        threading.Thread.__init__(self)
        self.name = name
        self.func = func
        self.args = args
        # self.res = ""

    @staticmethod
    def getResult():
        return MyThread.q

    def run(self):
        print 'starting', self.name, 'at:', ctime()
        # self.res = self.func(*self.args)
        MyThread.q.put(self.func(*self.args))
        print self.name, 'finished at:', ctime()
