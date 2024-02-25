import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json


class MyDriver():
    def __init__(self, browser = 'Chrome'):
        if browser == 'Edge':
            self.driver = webdriver.Edge()
        elif browser == 'Firefox':
            self.driver = webdriver.Firefox()
        else:
            self.driver = webdriver.Chrome()
        
    def getcookie(self):
        self.driver.get('https://passport.jd.com/new/login.aspx?/')

        #扫码登录
        #登录之后的页面会跳转到这里，让浏览器等待，直到url完全匹配
        url='https://www.jd.com/'
        WebDriverWait(self.driver,500).until(EC.url_to_be(url))
        time.sleep(1.3)
        cookieList  = self.driver.get_cookies()
        cookieStr = json.dumps(cookieList)

        with open('Jdcookie.txt', 'w') as f:
            f.write(cookieStr)

        print('cookie已写入')

    def readcookie(self):
        self.driver.get('https://www.jd.com/')
        with open('Jdcookie.txt',mode='r',encoding='utf-8') as f:
            cookie = f.read()
        # from string format to dictionary in python
        cookie = json.loads(cookie)
        self.driver.delete_all_cookies()
        for item in cookie:
            self.driver.add_cookie(item)
              
    def search_keyword(self, keyword):
        self.driver.get('https://www.jd.com/')
        input_box = self.driver.find_element(By.ID, 'key')
        input_box.send_keys(keyword)
        time.sleep(0.1)
        input_box.send_keys(Keys.ENTER)
        self.driver.implicitly_wait(30)
        time.sleep(0.2)
        
    def close(self):
        self.driver.close()

class SerialSearching():
    
    def __init__(self, keyword, pagenum = 8):
        self.mydriver = MyDriver(browser = 'Chrome')
        self.keyword = keyword
        self.prices, self.titles, self.commits, self.shops, self.urls, self.icons= [], [], [], [], [], []
        self.search_result_parse(pagenum)
        self.mydriver.close()
        
    def search_result_parse(self, pagenum):
        self.mydriver.search_keyword(self.keyword)
        page_num = self.page_count(pagenum)
        for idx in range(page_num):
            self._find_and_append(idx)
    
    def page_count(self, pagenum):
        self.mydriver.driver.implicitly_wait(15)
        self.mydriver.driver.execute_script('window.scrollTo(0,document.body.scrollHeight*3/4)')
        self.mydriver.driver.implicitly_wait(30)
        maxpages = 0
        while not maxpages:
            try:
                maxpages = int(self.mydriver.driver.find_element(By.CSS_SELECTOR, "#J_bottomPage > span.p-skip > em:nth-child(1) > b").text)
                self.mydriver.driver.implicitly_wait(15)
            except:
                print('Max pages not found, restarting...')
        if pagenum == "max":
            page_num = maxpages
        else:
            try:
                pagenum = int(pagenum)
                page_num = min(pagenum, maxpages)
            except:
                print("Error page count")
        print(f'Total {maxpages} pages')
        print(f'To load {page_num} pages in total')
        return page_num

    


    def _find_and_append(self, idx):

        self.load_specific_page(self.mydriver, idx)
        
    def load_specific_page(self, mydriver, pageid):
        try:
            mydriver.implicitly_wait(5)
            mydriver.execute_script('window.scrollTo(0,document.body.scrollHeight*3/4)')
            mydriver.implicitly_wait(5)   
            input_box = mydriver.find_element(By.CSS_SELECTOR, '#J_bottomPage > span.p-skip > input')
            input_box.send_keys(pageid+1)
            time.sleep(0.1)
            input_box.send_keys(Keys.ENTER)
            mydriver.implicitly_wait(3)
            time.sleep(1)
            mydriver.execute_script('window.scrollTo(0,document.body.scrollHeight)')
            # self.drive.implicitly_wait(3)
            items = mydriver.find_elements(By.XPATH, '//*[@id="J_goodsList"]/ul/li')
            for item in items:
                price = item.find_element(By.CLASS_NAME, 'p-price').text
                title = item.find_element(By.CLASS_NAME, 'p-name').text
                commit = item.find_element(By.CLASS_NAME, 'p-commit').text
                shop = item.find_element(By.CLASS_NAME, 'p-shop').text
                url = item.find_element(By.CSS_SELECTOR, "div > div.p-img > a").get_attribute('href')
                icons = item.find_elements(By.CSS_SELECTOR, 'div > div.p-icons > i')
                icons_list = [it.text for it in icons]
                self.prices.append(price)
                self.titles.append(title)
                self.commits.append(commit)
                self.shops.append(shop)
                self.urls.append(url)
                self.icons.append(icons_list)
            print(f'Page {pageid+1} finished')

        except:
            print(f"Error in finding elements in page {pageid+1}")

    def save_to_excel(self, format = 'xlsx', combineURL = 1, filename = 'jd'):
        if combineURL == 1:
            df = pd.DataFrame({
            '价格': self.prices,
            '商品': self.titles,
            '评论': self.commits,
            '店铺': self.shops,
            '标签': self.icons
            })
            for i in range(len(self.titles)):
                df['商品'][i] = '=HYPERLINK("'+ self.urls[i] + '","' + self.titles[i] + '")'

        else:
            df = pd.DataFrame({
            '价格': self.prices,
            '商品': self.titles,
            '评论': self.commits,
            '店铺': self.shops,
            '商品链接': self.urls,
            '标签': self.icons
            })
            for i in range(len(self.titles)):
                df['商品链接'][i] = '=HYPERLINK("'+ self.urls[i] + '","' + self.urls[i] + '")'
        
        # 存为excel
        if format == 'xlsx':
            df.to_excel(f'{filename}.xlsx')
        elif format == 'csv':
            df.to_csv(f'{filename}.csv', encoding='utf-8-sig')
        else:
            print('Invalid Format')






import threading
from threading import Semaphore

class ParallelSearching(SerialSearching):

    def __init__(self, keyword, pagenum = 8):
        self.mydriver = MyDriver(browser = 'Chrome')
        self.keyword = keyword
        self.sem = Semaphore(16) ## Maximum Thread
        self.prices, self.titles, self.commits, self.shops, self.urls, self.icons= [], [], [], [], [], []
        self.search_result_parse_parallel(pagenum)
        self.mydriver.close()

    def search_result_parse_parallel(self, pagenum):
        self.mydriver.search_keyword(self.keyword)
        page_num = self.page_count(self, pagenum)
        
        for idx in range(page_num):
            self.sem.acquire()
            threading.Thread(target=self._find_and_append_parallel, args=(idx,)).start()
        # wait for each process to complete
        for thread in threading.enumerate():
            # if thread is not threading.current_thread():
            thread.join()


    def _find_and_append_parallel(self, idx):

        currentURL = self.mydriver.driver.current_url
        newdriver = MyDriver(browser = 'Chrome')
        newdriver.readcookie()
        newdriver.driver.get(currentURL)
        newdriver.driver.implicitly_wait(7)
        time.sleep(0.2)
        self.load_specific_page(newdriver, idx)
        newdriver.close()
        self.sem.release()
        
    # def load_specific_page(self, mydriver, pageid):
    #     try:
    #         mydriver.implicitly_wait(5)
    #         mydriver.execute_script('window.scrollTo(0,document.body.scrollHeight*3/4)')
    #         mydriver.implicitly_wait(5)   
    #         input_box = mydriver.find_element(By.CSS_SELECTOR, '#J_bottomPage > span.p-skip > input')
    #         input_box.send_keys(pageid+1)
    #         time.sleep(0.1)
    #         input_box.send_keys(Keys.ENTER)
    #         mydriver.implicitly_wait(3)
    #         time.sleep(1)
    #         mydriver.execute_script('window.scrollTo(0,document.body.scrollHeight)')
    #         # self.drive.implicitly_wait(3)
    #         items = mydriver.find_elements(By.XPATH, '//*[@id="J_goodsList"]/ul/li')
    #         for item in items:
    #             price = item.find_element(By.CLASS_NAME, 'p-price').text
    #             title = item.find_element(By.CLASS_NAME, 'p-name').text
    #             commit = item.find_element(By.CLASS_NAME, 'p-commit').text
    #             shop = item.find_element(By.CLASS_NAME, 'p-shop').text
    #             url = item.find_element(By.CSS_SELECTOR, "div > div.p-img > a").get_attribute('href')
    #             icons = item.find_elements(By.CSS_SELECTOR, 'div > div.p-icons > i')
    #             icons_list = [it.text for it in icons]
    #             self.prices.append(price)
    #             self.titles.append(title)
    #             self.commits.append(commit)
    #             self.shops.append(shop)
    #             self.urls.append(url)
    #             self.icons.append(icons_list)
    #         print(f'Page {pageid+1} finished')

    #     except:
    #         print(f"Error in finding elements in page {pageid+1}")


        
    # def save_to_excel(self, format = 'xlsx', combineURL = 1, filename = 'jd'):
    #     if combineURL == 1:
    #         df = pd.DataFrame({
    #         '价格': self.prices,
    #         '商品': self.titles,
    #         '评论': self.commits,
    #         '店铺': self.shops,
    #         '标签': self.icons
    #         })
    #         for i in range(len(self.titles)):
    #             df['商品'][i] = '=HYPERLINK("'+ self.urls[i] + '","' + self.titles[i] + '")'

    #     else:
    #         df = pd.DataFrame({
    #         '价格': self.prices,
    #         '商品': self.titles,
    #         '评论': self.commits,
    #         '店铺': self.shops,
    #         '商品链接': self.urls,
    #         '标签': self.icons
    #         })
    #         for i in range(len(self.titles)):
    #             df['商品链接'][i] = '=HYPERLINK("'+ self.urls[i] + '","' + self.urls[i] + '")'
        
    #     # 存为excel
    #     if format == 'xlsx':
    #         df.to_excel(f'{filename}.xlsx')
    #     elif format == 'csv':
    #         df.to_csv(f'{filename}.csv', encoding='utf-8-sig')
    #     else:
    #         print('Invalid Format')



if __name__ == '__main__':
    login = SearchInHomepage()
    login.getcookie(login.drive)
    login.readcookie(login.drive)
    login.search_keywords("电脑")
    login.search_result_parse(pagenum=50, my_threading= 1)
    login.save_to_excel(combineURL=1, format='xlsx', filename='jd1')
    login.close()
    
    
    # https://club.jd.com/comment/productCommentSummaries.action?referenceIds=100075799817&callback=a
