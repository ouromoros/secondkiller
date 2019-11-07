from driver_util import *
import time
import datetime
import threading
import sys
from taobao import *
from collections import namedtuple

Action = namedtuple('Action', ['pred', 'f'])


class MultiScheduler:
    def __init__(self, driver, window_num):
        self.actions = []
        self.driver = driver
        self.global_lock = threading.Lock()
        for _ in range(window_num - 1):
            open_newtab(driver)
        self.window_num = window_num

    def add_action(self, url, f):
        self.actions.append(Action(url, f))

    def run(self):
        ts = []
        print('starting threads')
        for i in range(self.window_num):
            window = Window(
                self.driver, self.driver.window_handles[i], self.actions, self.global_lock)
            t = threading.Thread(target=window.run)
            ts.append(t)
            t.start()

        print('wait for threads')
        for t in ts:
            t.join()


class Window:
    def __init__(self, driver, window_handle, actions, global_lock):
        self.driver = driver
        self.window_handle = window_handle
        self.actions = actions
        self.global_lock = global_lock

    def run(self):
        while True:
            self.global_lock.acquire()
            self.driver.switch_to.window(self.window_handle)
            print('switched to {}'.format(self.window_handle[-5:]))
            for ac in self.actions:
                if ac.pred(self.driver):
                    finish = ac.f(self.driver)
                    break

            self.global_lock.release()
            if finish:
                # wait for action to complete
                time.sleep(5)
                print('finished!')
                return
            else:
                # yield control
                time.sleep(0)


if __name__ == '__main__':
    link = 'https://detail.tmall.com/item.htm?spm=a1z10.1-b-s.w5003-22197870099.1.4b523b8d3wROYH&id=607115918580&scene=taobao_shop'
    bt = datetime.datetime.strptime("2019-11-07 22:00:00", '%Y-%m-%d %H:%M:%S')

    # driver = get_driver(eager=True)
    driver = get_driver(noimage=True, headless=True, nonblock=True)
    driver.get('https://www.taobao.com/')
    print('driver started')
    s = MultiScheduler(driver, 2)
    user_login(driver)
    print('logged in')
    for window in driver.window_handles:
        driver.switch_to.window(window)
        driver.get(link)

    s.add_action(lambda x: at_link(x, ORDER_URL), order)
    s.add_action(lambda x: at_link(x, SUBMIT_URL), submit)
    wait(driver, bt)

    s.run()
    driver.quit()
