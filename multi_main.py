from driver_util import *
import time
import datetime
import threading
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
        windows = [Window(driver, self.driver.window_handles[i],
                          self.actions, self.global_lock) for i in range(self.window_num)]
        ts = []
        print('starting threads')
        for window in windows:
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
        self.finished = False
        self.global_lock = global_lock

    def run(self):
        while True:
            self.driver.switch_to.window(self.window_handle)
            for ac in self.actions:
                if ac.pred(self.driver):
                    self.global_lock.acquire()
                    wait_time = ac.f(self.driver)
                    self.global_lock.release()
                    if wait_time == -1:
                        print('finished!')
                        time.sleep(10000000)
                    elif wait_time:
                        time.sleep(wait_time)
                    else:
                        yield
                    break


if __name__ == '__main__':
    link = 'https://detail.tmall.com/item.htm?spm=a1z10.1-b-s.w5003-22197870099.1.4b523b8d3wROYH&id=607115918580&scene=taobao_shop'
    # link = 'https://detail.tmall.com/item.htm?spm=a230r.1.14.23.47cd6aceuNJrF6&id=597960230568&ns=1&abbucket=18&skuId=4333867631862'
    bt = datetime.datetime.strptime("2019-11-06 10:00:00", '%Y-%m-%d %H:%M:%S')

    # driver = get_driver(eager=True)
    driver = get_driver(noimage=True, headless=True, eager=True)
    driver.get('https://www.taobao.com/')
    print('driver started')
    s = MultiScheduler(driver, 10)
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
