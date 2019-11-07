from driver_util import *
import time
import datetime
import threading
from taobao import *
from collections import namedtuple

Action = namedtuple('Action', ['pred', 'f'])


class Scheduler:
    def __init__(self, driver):
        self.actions = []
        self.driver = driver

    def add_action(self, url, f):
        self.actions.append(Action(url, f))

    def run(self):
        while True:
            for ac in self.actions:
                if ac.pred(self.driver):
                    if ac.f(self.driver):
                        # wait for action to complete
                        time.sleep(5)
                        print('finished!')
                        return
                    break


if __name__ == '__main__':
    link = 'https://detail.tmall.com/item.htm?spm=a1z10.1-b-s.w5003-22197870099.1.4b523b8d3wROYH&id=607115918580&scene=taobao_shop'
    bt = datetime.datetime.strptime("2019-11-07 22:00:00", '%Y-%m-%d %H:%M:%S')

    driver = get_driver(headless=False, noimage=True, nonblock=True)
    # driver = get_driver()
    print('driver started')
    driver.get('https://www.taobao.com/')
    user_login(driver)
    print('logged in')
    driver.get(link)

    s = Scheduler(driver)
    s.add_action(lambda x: at_link(x, ORDER_URL), order)
    s.add_action(lambda x: at_link(x, SUBMIT_URL), submit)
    wait(driver, bt)

    s.run()
    driver.quit()
