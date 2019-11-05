from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import random

def get_driver(profile=None, headless=False, noimage=False, eager=False):
    option = webdriver.ChromeOptions()
    option.add_argument('disable-infobars')
    option.add_argument('--hide-scrollbars')
    # for headless
    option.add_argument('window-size=1920x1080')
    # possible bug?
    option.add_argument('--disable-gpu')
    # enable redirect
    option.add_argument("--disable-web-security")
    # disable log
    option.add_argument("--log-level=3")
    # disable selenium flag
    option.add_experimental_option('excludeSwitches', ['enable-automation']) 

    if profile:
        option.add_argument("user-data-dir={}".format(profile))
    if headless:
        option.add_argument('--headless')
    if noimage:
        prefs = {"profile.managed_default_content_settings.images": 2}
        option.add_experimental_option("prefs", prefs)
    
    caps = DesiredCapabilities().CHROME
    if eager:
        #caps["pageLoadStrategy"] = "normal"  #  complete
        caps["pageLoadStrategy"] = "eager"  #  interactive
        #caps["pageLoadStrategy"] = "none"

    # To avoid mysterious bug
    option.add_argument("--remote-debugging-port={}".format(random.randint(10000, 65535)))
    
    driver = webdriver.Chrome(options=option, desired_capabilities=caps)
    return driver

def wait_user(driver):
    old_url = driver.current_url
    while driver.current_url == old_url:
        pass

def refresh(driver):
    driver.get(driver.current_url)

def at_link(driver, url):
    return driver.current_url[:len(url)] == url
