
# def browser_thread(driver: webdriver.Chrome, idx: int):
#     url_list = ['https://www.csdn.net/', 'https://www.baidu.com',
#                 'https://music.163.com/', 'https://y.qq.com/', 'https://cn.vuejs.org/']

#     try:
#         driver.execute_script(f"window.open('{url_list[idx]}')")
#         driver.switch_to.window(driver.window_handles[-1])
#         driver.save_screenshot(f'{idx}.png')
#         return True
#     except Exception:
#         return False


url3 = "https://mall.jd.com/view_search-933997-0-99-1-24-1.html"
url1 = "https://mall.jd.com/view_search-2746730-23013324-99-1-20-1.html" 
url2 = "https://mall.jd.com/view_search-711685-0-99-1-24-1.html"
url4 = "https://mall.jd.com/view_search-2031298-0-99-1-24-1.html"
url_list = [url1, url2, url3, url4]   #*4


from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import threading
from threading import Semaphore
sem = Semaphore(16) ## Maximum Thread

def get_page_items(driver, href_list):
    driver.implicitly_wait(10)
    lis = driver.find_elements(By.CSS_SELECTOR, '#J_GoodsList > ul > li')
    for li in lis: 
        href = li.find_element(By.CSS_SELECTOR, 'div.gl-i-wrap > div.jPic > a').get_attribute('href')
        href_list.append(href)
  
  
def save_to_txt(href_list, name):
    with open(name,'w') as f:
        for line in href_list:
            f.write(line+'\n')

def get_all_items(idx):
    try:
        driver = webdriver.Chrome()
        href_list  = []
        driver.get(url_list[idx])
        get_page_items(driver, href_list)
        number_of_pages = len(driver.find_elements(By.CSS_SELECTOR, '#J_GoodsList > div > a')) + 1
        for i in range(number_of_pages -3):
            driver.find_element(By.CSS_SELECTOR, "#J_GoodsList > div > a:nth-child(%d)"%(i+3)).click()
            time.sleep(0.5)
            get_page_items(driver, href_list)
        save_to_txt(href_list, f"jd_items{idx}.txt")
        print("Total number of items: ", len(href_list))
        driver.quit()
    except Exception:
        pass
    
    sem.release()

# Semaphore 管理一个计数器，每调用一次 acquire() 方法，计数器就减一，每调用一次 release() 方法，计数器就加一。
# 计时器的值默认为 1 ，计数器的值不能小于 0，当计数器的值为 0 时，调用 acquire() 的线程就会等待，直到 release() 被调用。
# 因此，可以利用这个特性来控制线程数量
for idx in range(len(url_list)):
    sem.acquire()
    threading.Thread(target=get_all_items, args=(idx,)).start()

# wait for each process to complete
for thread in threading.enumerate():
    if thread is not threading.current_thread():
        thread.join()





