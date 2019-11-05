def get(driver, url):
    driver.execute_script("window.location.href = '{}';".format(url))

def click_by_id(driver, element_id):
    driver.execute_script("document.getElementById('{}').click();".format(element_id))

def click_by_query(driver, query):
    driver.execute_script("document.querySelector('{}').click()".format(query))

def open_newtab(driver):
    return driver.execute_script("window.open();")
