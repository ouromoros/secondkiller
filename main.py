from driver_util import *
import selenium.common.exceptions as se
import time
import datetime
import threading

class Action:
    def __init__(self, pred, f):
        self.pred = pred
        self.f = f

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
                    if ac.f(self.driver): return
                    break

order_url = 'https://detail.tmall.com/item.htm'
submit_url = 'https://buy.tmall.com/order/confirm_order.htm'
login_url = 'https://login.taobao.com/'
link = 'https://detail.tmall.com/item.htm?spm=a1z10.1-b-s.w5003-22197870099.1.4b523b8d3wROYH&id=607115918580&scene=taobao_shop'
# link = 'https://detail.tmall.com/item.htm?spm=a1z10.3-b-s.w4011-18407891890.127.6a8f65e9L5kPiY&id=45211019354&rn=3f47a7f4546d18ab6b06cce8bd95dd3d&abbucket=13&skuId=85241778963'
bt = datetime.datetime.strptime("2019-11-05 22:00:00", '%Y-%m-%d %H:%M:%S')


def logged_in(driver):
    try:
        driver.find_element_by_partial_link_text("请登录")
        return False
    except Exception:
        return True

def really_logged_in(driver):
    old_url = driver.current_url
    mytaobao_url = 'https://i.taobao.com/'
    driver.get(mytaobao_url)
    if at_link(driver, login_url):
        driver.get(old_url)
        return False
    else:
        driver.get(old_url)
        return True



def user_login(driver):
    print('please login:')
    # driver.find_element_by_partial_link_text("请登录").click()
    driver.get(login_url)
    print(driver.find_element_by_css_selector('#J_QRCodeImg > img').get_attribute('src'))
    wait_user(driver)

def wait(driver, t):
    current_time = datetime.datetime.now()
    if t < current_time: return
    # Wait and auto refresh until last minute
    print('refreshing', end='')
    while True:
        current_time = datetime.datetime.now()
        if (t - current_time).seconds > 31:
            print('.', end='', flush=True)
            assert really_logged_in(driver)
            time.sleep(30)
        else:
            print()
            break
    
    # Wait until only 2 seconds left
    print('start...', end='', flush=True)
    while t > current_time and (t - current_time).seconds > 2:
        pass
    print('ed!')

def order(driver):
    wait(driver, bt)
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
    ts = []
    for i in range(5):
        driver = get_driver(headless=True, noimage=True)
        print('driver started')
        # driver = get_driver()
        driver.get('https://www.taobao.com/')
        user_login(driver)

        s = Scheduler(driver)
        # s.add_action(lambda x: not logged_in(x), user_login)
        # s.add_action(lambda x: at_link(x, login_url), wait_user)
        s.add_action(lambda x: at_link(x, order_url), order)
        s.add_action(lambda x: at_link(x, submit_url), submit)
        s.add_action(lambda x: True, goto_order)

        t = threading.Thread(target=s.run)
        t.start()
        ts.append(t)

    for t in ts:
        t.join()
    
