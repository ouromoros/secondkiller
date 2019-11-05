from drivers import *
import time
import datetime

class YieldException(Exception):
    pass

class Action:
    def __init__(self, pred, f):
        self.pred = pred
        self.f = f

class Scheduler:
    def __init__(self, driver):
        self.actions = []
        self.driver = driver
    
    def __del__(self):
        self.driver.quit()
    
    def add_action(self, url, f):
        self.actions.append(Action(url, f))
    
    def run(self):
        while True:
            for ac in self.actions:
                if ac.pred(self.driver):
                    if ac.f(self.driver): return
                    break

def logged_in(driver):
    try:
        driver.find_element_by_partial_link_text("请登录")
        return False
    except Exception:
        return True

def user_login(driver):
    print('请扫描打开网址扫描二维码登陆：')
    driver.find_element_by_partial_link_text("请登录").click()
    print(driver.find_element_by_id("J_QRCodeImg").find_element_by_tag_name("img").get_attribute('src'))
    wait_user(driver)

def wait(driver, t):
    current_time = datetime.datetime.now()
    if t < current_time: return
    # Wait and auto refresh until last minute
    while True:
        current_time = datetime.datetime.now()
        if (t - current_time).seconds > 31:
            refresh(driver)
            assert logged_in(driver)
            time.sleep(30)
        else:
            break
    
    # Wait until only 2 seconds left
    while t > current_time and (t - current_time).seconds > 2:
        pass

order_url = 'https://detail.tmall.com/item.htm'
submit_url = 'https://buy.tmall.com/order/confirm_order.htm'
login_url = 'https://login.taobao.com/'

# link = 'https://detail.tmall.com/item.htm?spm=a1z10.1-b-s.w5003-22197870099.1.4b523b8d3wROYH&id=607115918580&scene=taobao_shop'
link = 'https://detail.tmall.com/item.htm?spm=a1z10.3-b-s.w4011-18407891890.127.6a8f65e9L5kPiY&id=45211019354&rn=3f47a7f4546d18ab6b06cce8bd95dd3d&abbucket=13&skuId=85241778963'
bt = datetime.datetime.strptime("2019-11-05 10:50:00", '%Y-%m-%d %H:%M:%S')

## TODO: ADD Wait for element (maybe)
def order(driver):
    wait(driver, bt)
    try:
        driver.find_element_by_id('J_LinkBuy').click()
        # driver.execute_script("document.getElementById('J_LinkBuy').click();")
        print('已经点击购买按钮')
    except Exception as e:
        refresh(driver)
        print(e)

def submit(driver):
    try:
        driver.find_element_by_class_name('go-btn').click()
        # driver.execute_script("document.getElementById('go-btn').click();")
        print("已经点击提交订单按钮")
        return True
    except Exception as e:
        print(e)

def goto_order(driver):
    driver.get(link)

if __name__ == '__main__':
    driver = get_driver(headless=True, noimage=True)
    driver.get('https://www.taobao.com/')
    s = Scheduler(driver)
    s.add_action(lambda x: not logged_in(x), user_login)
    s.add_action(lambda x: at_link(x, login_url), wait_user)
    s.add_action(lambda x: at_link(x, order_url), order)
    s.add_action(lambda x: at_link(x, submit_url), submit)
    s.add_action(lambda x: True, goto_order)
    s.run()
    s.driver.quit()
