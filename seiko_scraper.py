from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys 
from selenium.common.exceptions import NoSuchElementException        

from bs4 import BeautifulSoup
import pprint
import time

def check_exists(driver, css_selector):
    try:
        driver.find_element(By.CSS_SELECTOR, css_selector)
    except NoSuchElementException:
        return False
    return True


def handle_spec_element(soup):
    dlTag = soup.find_all("dl", {"class":"_list"})
    dtdds = []
    for tag in dlTag:
        keys = tag.find_all("dt")
        vals = tag.find_all("dd")
        for i in range(len(keys)):
            strip_keys = keys[i].text.strip()
            strip_vals = list(filter(None, [x.strip() for x in vals[i].text.split('\n')]))

            dtdds.append((strip_keys, strip_vals))

    info_collection = {}
    for j in dtdds:
        info_collection[j[0]] = j[1]
    
    pprint.pprint(info_collection)
    

def find_element_click(driver, by, expression, search_window=None, timeout=32, ignore_exception=None,
                       poll_frequency=4):
    """It find the element and click then  handle all type of exception during click

    :param poll_frequency:
    :param by:
    :param expression:
    :param timeout:
    :param ignore_exception:list It is a list of exception which is need to ignore.
    :return:
    """
    if ignore_exception is None:
        ignore_exception = []

    ignore_exception.append(NoSuchElementException)
    if search_window is None:
        search_window = driver

    end_time = time.time() + timeout
    while True:
        try:
            web_element = search_window.find_element(by=by, value=expression)
            web_element.click()
            return True
        except tuple(ignore_exception) as e:
            self.logger.debug(str(e))
            if time.time() > end_time:
                self.logger.exception(e)
                time.sleep(poll_frequency)
                break
        except Exception as e:
            raise
    return False


def main():
    """Echo the input arguments to standard output"""
    driver = webdriver.Chrome()
    driver.get("https://www.seikowatches.com/ca-en/watchfinder?page=1")
    watchlist_div_selector = '#app > div > div.watchfinder-result > div > div.watchfinder-list > div.row.row-cols-2.row-cols-md-4.gy-1.gy-md-3.gx-1.gx-md-3'
    button_selector = '#app > div > div.watchfinder-result > div > div.watchfinder-list > div.watchfinder-list-more > button'
    
    timeout = 5
    try:
        element_present = EC.presence_of_element_located((By.CSS_SELECTOR, watchlist_div_selector))
        WebDriverWait(driver, timeout).until(element_present)

        element_present = EC.presence_of_element_located((By.CSS_SELECTOR, button_selector))
        WebDriverWait(driver, timeout).until(element_present)

        while check_exists(driver, button_selector):           
            # Get scroll height
            last_height = driver.execute_script("return document.body.scrollHeight")
            # Scroll down to bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Lets hop on to the next page
            more_button = find_element_click(driver, By.CSS_SELECTOR, button_selector)

            # Wait to load page
            time.sleep(timeout)

            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

            # try:
            #     element_present = EC.presence_of_element_located((By.CSS_SELECTOR, button_selector))
            #     WebDriverWait(driver, timeout).until(element_present)
            # except TimeoutException:
            #     print(f"Timed out waiting for next page button")

        print(driver.current_url)


        # elem_list = driver.find_elements(By.CLASS_NAME, 'seriesProducts-item')
        # for e in elem_list:
        #     ActionChains(driver) \
        #         .key_down(Keys.CONTROL) \
        #         .click(e) \
        #         .perform()
        #     driver.switch_to.window(driver.window_handles[1])

        #     watch_spec_html = driver.find_element(By.CLASS_NAME, 'productSpec-items').get_attribute('innerHTML')
        #     soup = BeautifulSoup(watch_spec_html, 'html.parser')
        #     # handle each seiko spec element here
        #     handle_spec_element(soup)
        #     driver.close()
        #     driver.switch_to.window(driver.window_handles[0])

    except TimeoutException:
        print("Timed out waiting for list div to load")




    driver.close()


if __name__ == '__main__':
    main()