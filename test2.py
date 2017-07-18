# -*- coding:utf-8 -*-
from multiprocessing import Pool
from threading import Thread
from time import sleep

def hello():
    sleep(1)
    print("hello")

def main(p):
    p.apply_async(hello)
    p.apply_async(hello)
    p.close()
    print("hey")
    p.join()

def main2(p):
    mt = MonThread(p)
    mt.start()
    return

class MonThread(Thread):
    def __init__(self,p):
        Thread.__init__(self)
        self.daemon = False
        self.p = p
    def run(self):
        main(p)


if __name__=="__main__":
    p = Pool()
    main2(p)

    print("coucou")