import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

class CookieLogin():
    def __init__(self):
        self.drive = webdriver.Chrome()
        self.url = 'https://passport.jd.com/new/login.aspx?/'
        self.prices, self.titles, self.commits, self.shops, self.urls, self.icons= [], [], [], [], [], []

    def getcookie(self):
        self.drive.get(self.url)

        #扫码登录
        #登录之后的页面会跳转到这里，让浏览器等待，直到url完全匹配
        url='https://www.jd.com/'
        WebDriverWait(self.drive,500).until(EC.url_to_be(url))
        time.sleep(1.3)
        cookieList  = self.drive.get_cookies()
        cookieStr = json.dumps(cookieList)

        with open('Jdcookie.txt', 'w') as f:
            f.write(cookieStr)

        print('cookie已写入')

    def readcookie(self):
        self.drive.get('https://www.jd.com/')
        with open('Jdcookie.txt',mode='r',encoding='utf-8') as f:
            cookie = f.read()
        # from string format to dictionary in python
        cookie = json.loads(cookie)
        self.drive.delete_all_cookies()
        for item in cookie:
            self.drive.add_cookie(item)

    def search_keywords(self, keyword):
        self.drive.get('https://www.jd.com/')
        input_box = self.drive.find_element(By.ID, 'key')
        input_box.send_keys(keyword)
        time.sleep(0.1)
        input_box.send_keys(Keys.ENTER)
        self.drive.implicitly_wait(5)
        # time.sleep(10)

    
    def search_result_parse(self, pagenum = 8):
        
        maxpages = int(self.drive.find_element(By.CSS_SELECTOR, "#J_bottomPage > span.p-skip > em:nth-child(1) > b").text)
        if pagenum == "max":
            # self.drive.implicitly_wait(5)
            # self.drive.execute_script('window.scrollTo(0,document.body.scrollHeight*3/4)')
            # self.drive.implicitly_wait(5)
            page_num = maxpages
        else:
            try:
                pagenum = int(pagenum)
                page_num = min(pagenum, maxpages)
            except:
                print("Error page count")
            
        print(f'Total {maxpages} pages')
        print(f'To load {page_num} pages in total')
        for idx in range(page_num):
            self._find_and_append(idx)

            
            
    def _find_and_append(self, idx):
        input_box = self.drive.find_element(By.CSS_SELECTOR, '#J_bottomPage > span.p-skip > input')
        input_box.send_keys(idx+1)
        time.sleep(0.1)
        input_box.send_keys(Keys.ENTER)
        self.drive.implicitly_wait(3)
        time.sleep(1)
        self.drive.execute_script('window.scrollTo(0,document.body.scrollHeight)')
        # self.drive.implicitly_wait(3)
        items = self.drive.find_elements(By.XPATH, '//*[@id="J_goodsList"]/ul/li')
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
        print(f'Page {idx+1} finished')
        # self.drive.find_element(By.CLASS_NAME, 'pn-next').click()
        # if i +1 == page_num:
        #     break

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

        
    def close(self):
        self.drive.close()

if __name__ == '__main__':
    login = CookieLogin()
    # login.getcookie()
    login.readcookie()
    login.search_keywords("电脑")
    login.search_result_parse(pagenum=9)
    login.save_to_excel(combineURL=1, format='xlsx', filename='jd1')
    login.close()
    
    
    # https://club.jd.com/comment/productCommentSummaries.action?referenceIds=100075799817&callback=a
