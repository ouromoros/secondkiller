from driver_util import *
import time
import datetime
import nonblock_driver as nb
import selenium.common.exceptions as se
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Action:
    def __init__(self, pred, f):
        self.pred = pred
        self.f = f

class MultiScheduler:
    def __init__(self, driver, window_num):
        self.actions = []
        self.driver = driver
        for _ in range(window_num - 1):
            nb.open_newtab(driver)
        self.window_num = window_num
    
    def add_action(self, url, f):
        self.actions.append(Action(url, f))
    
    def run(self):
        windows = [Window(driver, self.driver.window_handles[i], self.actions) for i in range(self.window_num)]
        while True:
            for window in windows:
                window.run()

class Window:
    def __init__(self, driver, window_handle, actions):
        self.driver = driver
        self.window_handle = window_handle
        self.actions = actions
        self.finished = False

    def run(self):
        self.driver.switch_to.window(self.window_handle)
        for ac in self.actions:
            if ac.pred(self.driver):
                self.finished = ac.f(self.driver)
                if self.finished:
                    print('finish')
                break


order_url = 'https://detail.tmall.com/item.htm'
submit_url = 'https://buy.tmall.com/order/confirm_order.htm'
login_url = 'https://login.taobao.com/'

link = 'https://detail.tmall.com/item.htm?spm=a1z10.1-b-s.w5003-22197870099.1.4b523b8d3wROYH&id=607115918580&scene=taobao_shop'
# link = 'https://detail.tmall.com/item.htm?spm=a1z10.3-b-s.w4011-18407891890.127.6a8f65e9L5kPiY&id=45211019354&rn=3f47a7f4546d18ab6b06cce8bd95dd3d&abbucket=13&skuId=85241778963'
bt = datetime.datetime.strptime("2019-11-05 11:50:00", '%Y-%m-%d %H:%M:%S')

def user_login(driver):
    print('please login:')
    # driver.find_element_by_partial_link_text("请登录").click()
    driver.get(login_url)
    e =  WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#J_QRCodeImg > img")))
    print(e.get_attribute('src'))
    wait_user(driver)

def wait(driver, t):
    current_time = datetime.datetime.now()
    if t < current_time: return
    print('start...', end='', flush=True)
    while t > current_time and (t - current_time).seconds > 2:
        pass
    print('ed!')

def order(driver):
    print('making order')
    try:
        driver.find_element_by_id('J_LinkBuy').click()
        print('****Ordered****')
    except se.ElementClickInterceptedException:
        print('Blocked by something')
        driver.find_element_by_partial_link_text('关闭').click()

        driver.find_element_by_id('J_LinkBuy').click()
        print('****Ordered****')
    except Exception:
        print("Buy not found")
        refresh(driver)

def submit(driver):
    print('submitting')
    try:
        driver.find_element_by_class_name('go-btn').click()
        print("****Submitted****")
        return True
    except Exception as e:
        print(e)

def goto_order(driver):
    print('goto order page')
    driver.get(link)

if __name__ == '__main__':
    driver = get_driver(noimage=True, headless=True, eager=True)
    driver.get('https://www.taobao.com/')
    s = MultiScheduler(driver, 2)

    user_login(driver)
    s.add_action(lambda x: at_link(x, order_url), order)
    s.add_action(lambda x: at_link(x, submit_url), submit)
    s.add_action(lambda x: True, goto_order)

    wait(driver, bt)
    s.run()
    s.driver.quit()
