from selenium.webdriver.common.by import By
from selenium import webdriver
import sys
import time
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import threading
import logging
import random
from selenium.webdriver.remote.remote_connection import LOGGER
LOGGER.setLevel(logging.WARNING) # No "handshake failed" will be displayed

from MyDriver import MyDriver
from Downloader import Downloader

##---------Maximum--threads----------------------------------------------------
max_drivers = 1
sem=threading.Semaphore(max_drivers)

sleep = 0.9

try:
    profilePage =  sys.argv[1]
    login_status = int(sys.argv[2])
except:
    print('Please run the python file with two argument (user profile page url and login status (0, 1, 2))')
    exit
try:
    startsfrom = int(sys.argv[3]) - 1
except:
    startsfrom = 0
    print('Starting from post 1')
#download thread
downloader = Downloader()
downloader_thread = threading.Thread(target=downloader.download)
downloader_thread.start()
import json


# start a new driver
def new_driver():
    option = webdriver.ChromeOptions()
    option.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
    option.add_argument('--incognito')
    option.add_experimental_option('excludeSwitches', ['enable-logging'])

    option.add_argument("--disable-blink-features")
    option.add_argument("--disable-blink-features=AutomationControlled")

    # option.add_argument("--headless")  # Runs Chrome in headless mode
    option.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
    newdriver = webdriver.Chrome(options= option)
    newdriver.implicitly_wait(10) 
    newdriver.get('https://www.xiaohongshu.com')
    newdriver.refresh()
    if login_status == 1 or login_status == 2:
        try:
            with open('xhscookie.txt',mode='r',encoding='utf-8') as f:
                cookie = f.read()
            cookie = json.loads(cookie)
            newdriver.delete_all_cookies()
            for item in cookie:
                time.sleep(sleep)
                newdriver.add_cookie(item)
            time.sleep(sleep)
        except:
            print('"xhscookie.txt" file does not exist, try to set the login_status to 2!')
    # newdriver = MyDriver(login).driver

    #Method 2
    # option = webdriver.ChromeOptions()
    # option.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
    # option.add_argument('--incognito')
    # option.add_argument("--headless")  # Runs Chrome in headless mode
    # option.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
    # option.add_experimental_option('excludeSwitches', ['enable-logging'])
    # newdriver = webdriver.Chrome(options= option)

    return newdriver

#visit profile page
def getPostsLink(profilePage):
    mydriver = MyDriver(login =login_status)
    driver = mydriver.driver
    driver.get(profilePage)
    time.sleep(sleep)
    count = 5
    while True:
        try:
            username = driver.find_element(By.CSS_SELECTOR,'#userPageContainer > div.user > div > div > div.info > div.basic-info > div.user-basic > div.user-nickname > div').text
            # postlist = set()
            postindex = set()
            contents = driver.find_element(By.ID, 'userPostedFeeds').find_elements(By.CLASS_NAME, 'note-item')
            
            break
        except:
            time.sleep(sleep)
            count -= 1
            driver.refresh()

    last_index = []
    visited = set(list(range(startsfrom)))
    
    newdriverlist = [new_driver() for i in range(max_drivers)]

    for i in range(50):
        time.sleep(sleep)
        WebDriverWait(driver, 30, poll_frequency=1.5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="userPostedFeeds"]//section')))
        time.sleep(sleep)
        try:
            contents = driver.find_element(By.ID, 'userPostedFeeds').find_elements(By.CLASS_NAME, 'note-item')
        except:
            time.sleep(sleep)
            driver.refresh()
        current_index = []
        for content in contents:
            index =  content.get_attribute("data-index")
            current_index.append(int(index))
            if int(index) in visited:
                continue
            else:
                visited.add(int(index))
            try:
                WebDriverWait(content, 0.5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div > a.cover.ld.mask > span")))
                print('Post %s is a video, submiited to downloading queue'%(index))
            except:
                print('Post %s is an article, jumping to next post'%(index))
                # continue
            else:
                # ele = 
                # time.sleep(sleep)
                current_href = content.find_element(By.CSS_SELECTOR, "div > a").get_attribute("href")
                # postlist.add(current_href)
                postindex.add(index)
                getVideoLink(newdriverlist[int(index)%max_drivers], username, index, current_href)
                
        
        if last_index == current_index:
            downloader.stop()
            break
        last_index = current_index
        # postindex.add(i for i in current_index)
        print(current_index)
        driver.execute_script(f'document.documentElement.scrollTop={(i+1)*1500}')
        time.sleep(sleep)

    # print("User: ", username)
    # driver.close()
    # newdriver.close()
    return postindex


#visit video page
def getVideoLink(newdriver, username, index, current_href):

    def thread_task(newdriver, index, current_href):
        newdriver.get(current_href)
        time.sleep(sleep)
        try:
            src = WebDriverWait(newdriver, 10, poll_frequency=0.9).until(EC.presence_of_element_located((By.NAME, "og:video"))).get_attribute("content")
            time.sleep(sleep)
            title = WebDriverWait(newdriver, 10, poll_frequency=0.8).until(EC.presence_of_element_located((By.NAME, "og:title"))).get_attribute("content")
            sem.release()
            title = title.rstrip(" - 小红书")
            downloader.add_to_queue((username, index, src, title))
        except:
            sem.release()
            print("Manual operation needed in one webdriver, check it")
            getVideoLink(newdriver, username, index, current_href)

    # newdriver.refresh()
    time.sleep(sleep)
    sem.acquire()
    thread = threading.Thread(target=thread_task, args=(newdriver, index, current_href))
    thread.start()

postindex = getPostsLink(profilePage)
print(len(postindex), 'videos found, number:')
print(sorted(postindex))

downloader.stop()
downloader_thread.join()