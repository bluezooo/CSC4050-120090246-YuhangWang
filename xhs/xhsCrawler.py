from selenium.webdriver.common.by import By
from selenium import webdriver
import sys
import time
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import threading
import logging
from selenium.webdriver.remote.remote_connection import LOGGER
LOGGER.setLevel(logging.WARNING) # No "handshake failed" will be displayed

from MyDriver import MyDriver
from Downloader import Downloader

##---------Maximum--threads----------------------------------------------------
sem=threading.Semaphore(1)

try:
    profilePage =  sys.argv[1]
    login_status = int(sys.argv[2])
except:
    print('Please run the python file with two argument (user profile page url and login status (0, 1, 2))')
    exit

#download thread
downloader = Downloader()
downloader_thread = threading.Thread(target=downloader.download)
downloader_thread.start()
import json
#visit profile page
def getPostsLink(profilePage):
    mydriver = MyDriver(login =login_status)
    driver = mydriver.driver
    driver.get(profilePage)
    time.sleep(1)

    username = driver.find_element(By.CSS_SELECTOR,'#userPageContainer > div.user > div > div > div.info > div.basic-info > div.user-basic > div.user-nickname > div').text
    # postlist = set()
    postindex = set()
    contents = driver.find_element(By.ID, 'userPostedFeeds').find_elements(By.CLASS_NAME, 'note-item')
    last_index = []
    visited = set()


    option = webdriver.ChromeOptions()
    # option.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
    # option.add_argument('--incognito')
    # option.add_experimental_option('excludeSwitches', ['enable-logging'])
    # option.add_argument("--headless")  # Runs Chrome in headless mode
    # option.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
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
                time.sleep(0.4)
                newdriver.add_cookie(item)
            time.sleep(0.4)
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

    for i in range(50):
        WebDriverWait(driver, 10, poll_frequency=0.8).until(EC.presence_of_element_located((By.XPATH, '//*[@id="userPostedFeeds"]//section')))
        time.sleep(0.3)
        try:
            contents = driver.find_element(By.ID, 'userPostedFeeds').find_elements(By.CLASS_NAME, 'note-item')
        except:
            driver.refresh()
        current_index = []
        for content in contents:
            index = content.get_attribute("data-index")
            current_index.append(index)
            if index in visited:
                continue
            else:
                visited.add(index)
            try:
                WebDriverWait(content, 0.5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div > a.cover.ld.mask > span")))
                print('Post %s is a video, submiited to downloading queue'%(index))
            except:
                print('Post %s is an article, jumping to next post'%(index))
                # continue
            else:
                ele = content.find_element(By.CSS_SELECTOR, "div > a")
                time.sleep(0.2)
                current_href = ele.get_attribute("href")
                # postlist.add(current_href)
                postindex.add(index)
                getVideoLink(newdriver, username, current_href)
                
        
        if last_index == current_index:
            downloader.stop()
            break
        last_index = current_index
        # postindex.add(i for i in current_index)
        print(current_index)
        driver.execute_script(f'document.documentElement.scrollTop={(i+1)*1500}')
        time.sleep(0.1)

    # print("User: ", username)
    driver.close()
    newdriver.close()
    return postindex


#visit video page
def getVideoLink(newdriver, username, current_href):

    def thread_task(newdriver, current_href):
        newdriver.get(current_href)
        time.sleep(0.6)
        # try:
        #     type = WebDriverWait(newdriver, 30, poll_frequency=0.7).until(EC.presence_of_element_located((By.NAME, "og:type"))).get_attribute("content")
        #     # type = newdriver.find_element(By.CSS_SELECTOR,"head > meta:nth-child(50)").get_attribute("content")
        #     time.sleep(0.4)
        #     if type == 'video':
        #         # time.sleep(0.2)
        #         src = WebDriverWait(newdriver, 30, poll_frequency=0.9).until(EC.presence_of_element_located((By.NAME, "og:video"))).get_attribute("content")
        #         time.sleep(0.4)
        #         title = WebDriverWait(newdriver, 30, poll_frequency=0.8).until(EC.presence_of_element_located((By.NAME, "og:title"))).get_attribute("content")
        #         title = title.rstrip(" - 小红书")
        #     # newdriver.close()
        #         downloader.add_to_queue((username, src, title))
        #     sem.release()
        try:
            src = WebDriverWait(newdriver, 30, poll_frequency=0.9).until(EC.presence_of_element_located((By.NAME, "og:video"))).get_attribute("content")
            time.sleep(0.4)
            title = WebDriverWait(newdriver, 30, poll_frequency=0.8).until(EC.presence_of_element_located((By.NAME, "og:title"))).get_attribute("content")
            sem.release()
            title = title.rstrip(" - 小红书")
            downloader.add_to_queue((username, src, title))
        except:
            sem.release()
            print("Manual operation needed in one webdriver, check it")
            getVideoLink(newdriver, username, current_href)

    newdriver.refresh()
    time.sleep(0.5)
    sem.acquire()
    thread = threading.Thread(target=thread_task, args=(newdriver, current_href))
    thread.start()
    # while running:# turn off current thread
    #     pass

postindex = getPostsLink(profilePage)
print(len(postindex), 'videos found, number:')
print(sorted(postindex))

downloader.stop()
downloader_thread.join()