from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys 
from bs4 import BeautifulSoup
import pprint

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
    



def main():
    """Echo the input arguments to standard output"""
    driver = webdriver.Chrome()
    driver.get("https://www.seikowatches.com/ca-en/watchfinder?page=1")

    timeout = 20
    try:
        element_present = EC.presence_of_element_located((By.XPATH, '/html/body/main/div/div/div[2]/div/div[2]/div/div[3]/div[1]/div[1]'))
        WebDriverWait(driver, timeout).until(element_present)
        
        elem_list = driver.find_elements(By.CLASS_NAME, 'seriesProducts-item')
        for e in elem_list:
            ActionChains(driver) \
                .key_down(Keys.CONTROL) \
                .click(e) \
                .perform()
            driver.switch_to.window(driver.window_handles[1])

            watch_spec_html = driver.find_element(By.CLASS_NAME, 'productSpec-items').get_attribute('innerHTML')
            soup = BeautifulSoup(watch_spec_html, 'html.parser')
            # print(soup.prettify())
            # handle each seiko spec element here
            handle_spec_element(soup)

            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            
            break
    except TimeoutException:
        print("Timed out waiting for page to load")

    # assert "Python" in driver.title
    # elem.clear()
    # elem.send_keys("pycon")
    # elem.send_keys(Keys.RETURN)
    # assert "No results found." not in driver.page_source
    driver.close()


if __name__ == '__main__':
    main()