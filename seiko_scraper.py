from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys 
from selenium.common.exceptions import NoSuchElementException        
import urllib.request
import pandas as pd
import base64
import io
from PIL import Image 
from bs4 import BeautifulSoup
import pprint
import time
import sqlite3
import time
from datetime import date


def get_cur_rec():
    connection_obj = sqlite3.connect('watches.db')
    cursor_obj = connection_obj.cursor()    
    cursor_obj.execute("SELECT DISTINCT model FROM WATCHES")
    out = cursor_obj.fetchall()
    res = list(map(lambda x: x[0], out))
    return res


def init_db():
    # Connecting to sqlite
    # connection object
    connection_obj = sqlite3.connect('watches.db')    
    # cursor object
    cursor_obj = connection_obj.cursor()    
    # Drop the GEEK table if already exists.
    # cursor_obj.execute("DROP TABLE IF EXISTS WATCHES")    
    
    # Creating table
    table = """ CREATE TABLE WATCHES (
                brand TEXT NOT NULL,
                model TEXT,
                weight TEXT,
                water_resistance TEXT,
                lug_to_lug TEXT,
                jewel_count TEXT,
                diameter TEXT,
                thickness TEXT,
                lug_width TEXT,
                crystal TEXT,
                lume TEXT,
                case_material TEXT,
                power_reserve TEXT,
                more_info TEXT,
                movement_name TEXT,
                movement_type TEXT,
                processed_date TEXT,
                img BLOB
            ); """    
    cursor_obj.execute(table)    
    print("Table is Ready")    
    # Close the connection
    connection_obj.close()


def check_exists(driver, css_selector):
    try:
        driver.find_element(By.CSS_SELECTOR, css_selector)
    except NoSuchElementException:
        return False
    return True


def print_watch_info(watch_info_dict):
    for k in watch_info_dict:
        if k is not 'img':
            print(f'{k}: {watch_info_dict[k]}')


def handle_spec_element(soup, more_info, pic_blob):
    dlTag = soup.find_all("dl", {"class":"_list"})
    dtdds = []
    for tag in dlTag:
        keys = tag.find_all("dt")
        vals = tag.find_all("dd")
        for i in range(len(keys)):
            strip_keys = keys[i].text.strip()
            strip_vals = list(filter(None, [x.strip() for x in vals[i].text.split('\n')]))
            dtdds.append((strip_keys, strip_vals))
    
    info_collection = {'more_info': more_info, 'img': pic_blob, 'processed_date': date.today().strftime("%b-%d-%Y")}    

    for j in dtdds:
        if isinstance(j[1], list):
            if len(j[1]) > 1:
                for c in j[1]:
                    if ":" in c:
                        info_collection[c.split(":")[0]] = c.split(":")[1]
            else:
                info_collection[j[0]] = j[1][0]
        else:
            info_collection[j[0]] = j[1]
    # pprint.pprint(info_collection)
    return info_collection
    

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
            return False
    return False


def convertToBinaryData(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData


def write_file(data, filename):
    # Convert binary data to proper format and write it on Hard Disk
    with open(filename, 'wb') as file:
        file.write(data)


def populate_db(watch_info_element, w):
        # populate info into sqlite3
    conn = sqlite3.connect('watches.db')
    sql = ''' INSERT INTO watches (brand, model, weight, water_resistance, lug_to_lug, jewel_count, diameter, thickness, lug_width, crystal, 
            lume, case_material, power_reserve, more_info, movement_name, movement_type, processed_date, img)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()

    insert_data = []
    insert_data.append('seiko')
    insert_data.append(w)
    keys = ['Weight', 'Water Resistance', 'Lug-to-lug', 'Jewels', 'Diameter', 'Thickness', 'Distance between lugs', 'Crystal', 'LumiBrite', 'Case Material', 'Power reserve', 'more_info', 'Caliber Number', 'Movement Type', 'processed_date', 'img']
    for k in keys:
        if k in watch_info_element:
            insert_data.append(watch_info_element[k])
        else:
            insert_data.append(None)
    cur.execute(sql, insert_data)
    conn.commit()
    print(f"population successful with {w}")


def get_names(e):
    name_eles = e.find_element(By.CLASS_NAME, '_info').get_attribute('innerHTML')
    divTag = BeautifulSoup(name_eles, 'html.parser').find_all("div")        
    more_info = ', '.join([x.text.strip() for x in divTag])
    names = more_info.split(",")[0]
    return [names, e]

def main():
    """Echo the input arguments to standard output"""
    driver = webdriver.Chrome()
    driver.get("https://www.grand-seiko.com/ca-en/collections/all?page=1")
    # driver.get("https://www.seikowatches.com/ca-en/watchfinder?page=1")
    # watchlist_div_selector = '#app > div > div.watchfinder-result > div > div.watchfinder-list > div.row.row-cols-2.row-cols-md-4.gy-1.gy-md-3.gx-1.gx-md-3'
    watchlist_div_selector = '#app > div > div > div > div.row.gx-1.gx-md-2'
    button_selector = '#app > div > div.watchfinder-result > div > div.watchfinder-list > div.watchfinder-list-more > button'
    
    watch_info = {} # to store all watch info
    timeout = 5
    try:
        watchlist_div = EC.presence_of_element_located((By.CSS_SELECTOR, watchlist_div_selector))
        WebDriverWait(driver, timeout).until(watchlist_div)

        # load_button = EC.presence_of_element_located((By.CSS_SELECTOR, button_selector))
        # WebDriverWait(driver, timeout).until(load_button)

        pagination = True
        if pagination:
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
            
        print(driver.current_url)

        # At this point, the preconditions are:
        # 1. we reached the max page, and 
        # 2. all watch elements (seriesProducts-item) are loaded.
        # first, get the model name
        elem_list = driver.find_elements(By.CLASS_NAME, 'seriesProducts-item')
        print(len(elem_list))
        
        # names = list(map(get_names, elem_list))
        # elem_dict = {}
        # for n in names:
        #     elem_dict[n[0]] = n[1]
        
    #     cur_rec = get_cur_rec()

    #     tmp_list = []
    #     for model in elem_dict:
    #         if model not in cur_rec:
    #             tmp_list.append(model)

    #     print(tmp_list)


    #     for model_name in tmp_list:
    #         e = elem_dict[model_name]
    #         more_info = ""            
    #         # now get image files
    #         watch_img_src = e.find_element(By.CLASS_NAME, '_image').get_attribute("src")  # select the image tag
    #         try:
    #             tmp_pic_file = urllib.request.urlretrieve(watch_img_src, "tmpimg.png")
    #             pic_blob = convertToBinaryData("tmpimg.png")
    #         except Exception as ex:
    #             print(ex)
    #             pic_blob = None
    #             pass

    #         # then, open the watch page, then scrape off the info
    #         try:
    #             ActionChains(driver).key_down(Keys.CONTROL).click(e).perform()  # open up the watch page in a new tab
    #             driver.switch_to.window(driver.window_handles[1])               # view new tab
    #             watch_spec_html = driver.find_element(By.CLASS_NAME, 'productSpec-items').get_attribute('innerHTML')
    #             soup = BeautifulSoup(watch_spec_html, 'html.parser')             # parse seiko spec element here
    #             watch_info[model_name] = handle_spec_element(soup, more_info, pic_blob)
    #             # print_watch_info(watch_info[model_name])
    #             print(model_name)
    #             driver.close()
    #             driver.switch_to.window(driver.window_handles[0])
    #         except Exception as ex:
    #             print(ex)
    #             break
    #             pass
            
    #         populate_db(watch_info[model_name], model_name)

    # except Exception as exc:
    #     print(exc)
    #     raise
    # except TimeoutException:
    #     print("Timed out waiting for list div to load")
    #     raise
    
    # print(len(watch_info))
    # df = pd.DataFrame.from_dict(watch_info)
    # df.to_csv('seiko.csv')
    # driver.close()

if __name__ == '__main__':
    # init_db()
    main()