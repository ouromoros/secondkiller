from driver_util import *
import time
import datetime
import selenium.common.exceptions as se
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

ORDER_URL = 'https://detail.tmall.com/item.htm'
SUBMIT_URL = 'https://buy.tmall.com/order/confirm_order.htm'
LOGIN_URL = 'https://login.taobao.com/'


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
    if at_link(driver, LOGIN_URL):
        driver.get(old_url)
        return False
    else:
        driver.get(old_url)
        return True


def wait(driver, t):
    current_time = datetime.datetime.now()
    if t < current_time:
        print('no wait')
        return
    # Wait and auto refresh until last minute
    print('refreshing', end='')
    while True:
        current_time = datetime.datetime.now()
        if (t - current_time).seconds > 61:
            print('.', end='', flush=True)
            assert really_logged_in(driver)
            time.sleep(60)
        else:
            print()
            break

    # Wait until only 2 seconds left
    print('start...', end='', flush=True)
    if t > current_time:
        time.sleep(max((t - current_time).seconds - 5, 0))
    print('ed!')


def user_login(driver):
    print('please login:')
    driver.get(LOGIN_URL)
    time.sleep(1)
    driver.execute_script("document.getElementById('J_Static2Quick').click();")
    e = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#J_QRCodeImg > img")))
    print(e.get_attribute('src'))
    wait_user(driver)
    # time.sleep(10)
    # assert really_logged_in(driver)


def order(driver):
    print('making order')
    try:
        # try close dialog, selenium click doesn't work because it's wrapped in an iframe
        driver.execute_script(
            "document.getElementById('sufei-dialog-close').click();")

        driver.find_element_by_id('J_LinkBuy').click()
        print('****Ordered****')
        return
    except (se.ElementClickInterceptedException, se.ElementNotInteractableException):
        print('Blocked by something')
    except Exception:
        print("Buy not found")
        refresh(driver)


def submit(driver):
    print('submitting')
    try:
        driver.find_element_by_class_name('go-btn').click()
        print("****Submitted****")
        return -1
    except Exception as e:
        print(e)
