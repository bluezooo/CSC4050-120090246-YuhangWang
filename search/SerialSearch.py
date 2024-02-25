import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from MyDriver import MyDriver
import pandas as pd

class SerialSearch():
    
    def __init__(self, keyword, login_status = 2, pagenum = 8, no_repeat = 1):
        '''keyword: the word you want to search in the homepage search box 
            login_status: 0: NOT recommended, possible verification needed when crawling data, causing interuption  1: Read the stored the cookie file only, NOT for first time usage   2: Recommended: get and store the cookie for next time usage, this requires to login manually.      More details to be seen in MyDriver.py
            pagenum: the total page of items you want to get&load'''
        self.mydriver = MyDriver(login_status, browser = 'Chrome')
        self.keyword = keyword
        self.no_repeat = no_repeat
        self.IDs, self.prices, self.titles, self.commits, self.shops, self.urls, self.icons, self.pages= [], [], [], [], [], [], [], []
        self.unfinished = set()
        self.Lock = None
        self.search_result_parse(pagenum, login_status, no_repeat)
        self.mydriver.close()
        
    def search_result_parse(self, pagenum, login_status = 1, no_repeat = 1):
        self.mydriver.search_keyword(self.keyword)
        page_num = self.page_count(pagenum, login_status)
        for idx in range(page_num):
            self._find_and_append(idx, no_repeat)
        # for j in range(2):
        for j in range(2):
            for idx in self.unfinished.copy():
                self._find_and_append(idx, no_repeat)
            print(self.unfinished)  
    
    def page_count(self, pagenum, login_status = 1):
        # self.mydriver.driver.implicitly_wait(15)
        # self.mydriver.driver.execute_script('window.scrollTo(0,document.body.scrollHeight*3/4)')
        # self.mydriver.driver.implicitly_wait(30)
        maxpages = 0
        # while not maxpages:
        try:
            maxpages = WebDriverWait(self.mydriver.driver, 15).until(\
                EC.presence_of_element_located((By.CSS_SELECTOR, "#J_bottomPage > span.p-skip > em:nth-child(1) > b")))
            # maxpages = int(self.mydriver.driver.find_element(By.CSS_SELECTOR, "#J_bottomPage > span.p-skip > em:nth-child(1) > b").text)
            maxpages = int(maxpages.text)
            # self.mydriver.driver.implicitly_wait(5)
            if pagenum == "max":
                page_num = maxpages
            else:
                try:
                    pagenum = int(pagenum)
                    page_num = min(pagenum, maxpages)
                except:
                    print("Error page count")
        except:
            self.mydriver.search_keyword(self.keyword)
            print('Max pages not found, restarting... Restart the program may help')
            page_num = self.page_count(pagenum, login_status)
    
        print(f'Total {maxpages} pages')
        print(f'To load {page_num} pages in total')
        return page_num

    def _find_and_append(self, idx, no_repeat = 1):

        self.load_specific_page(self.mydriver.driver, idx, no_repeat)
    
    def page_jump(self, mydriver, page_number):

        # try:
        # mydriver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
        time.sleep(1)
        input = WebDriverWait(mydriver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#J_bottomPage > span.p-skip > input')))
        submit = WebDriverWait(mydriver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_bottomPage > span.p-skip > a')))
        input.clear()
        input.send_keys(page_number)
        
        submit.click()
        WebDriverWait(mydriver, 30).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#J_topPage > span > b"), str(page_number))
        )# 判断翻页成功,高亮的按钮数字与设置的页码一样

        WebDriverWait(mydriver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#J_goodsList > ul > li:nth-child(30)"))
        )#等到30个商品都加载出来


        js = "return action=document.body.scrollHeight"
        height = 0
        new_height = mydriver.execute_script(js)
        while height < new_height:
            # 将滚动条调整至页面底部
            for i in range(height, new_height, 500):
                mydriver.execute_script('window.scrollTo(0, {})'.format(i))
                time.sleep(1)
            height = new_height
            time.sleep(0.1)
            new_height = mydriver.execute_script(js)
        for time1 in range(5):
            try:
                reload = WebDriverWait(mydriver, (time1+1)*5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#J_scroll_loading > span > a")))
                reload.click()
                break
            except:
                continue
        WebDriverWait(mydriver,20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#J_goodsList > ul > li:nth-child(60)"))
        )#等到60个商品都加载出来
        # WebDriverWait(mydriver, 10).until(
        #     EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#J_bottomPage > span.p-num > a.curr"), str(page_number))
        # )# 判断翻页成功,高亮的按钮数字与设置的页码一样
      # except:
        #     print('Error in next_page, restarting...')
        #     return self.page_jump(mydriver, page_number)

    def load_specific_page(self, mydriver, pageid, no_repeat = 1):
                    # mydriver.implicitly_wait(implicitWaitTime)
            # mydriver.execute_script('window.scrollTo(0,document.body.scrollHeight*3/4)')
            # mydriver.implicitly_wait(implicitWaitTime)   
            # input_box = WebDriverWait(mydriver, 15).until(\
            #     EC.presence_of_element_located((By.CSS_SELECTOR, '#J_bottomPage > span.p-skip > input')))
            # # input_box = mydriver.find_element(By.CSS_SELECTOR, '#J_bottomPage > span.p-skip > input')
            # input_box.send_keys(Keys.BACKSPACE)
            # input_box.send_keys(Keys.BACKSPACE)
            # input_box.send_keys(Keys.BACKSPACE)
            # input_box.send_keys(pageid+1)
            # time.sleep(0.1)
            # input_box.send_keys(Keys.ENTER)
            # # mydriver.implicitly_wait(implicitWaitTime)
            # time.sleep(1)
            # mydriver.execute_script('window.scrollTo(0,document.body.scrollHeight)')
            
            
            
        # try:
        self.page_jump(mydriver, pageid+1)
        items = WebDriverWait(mydriver, 10).until(\
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="J_goodsList"]/ul/li')))
        # items = mydriver.find_elements(By.XPATH, '//*[@id="J_goodsList"]/ul/li')
        for item in items:
            # price = item.find_element(By.CLASS_NAME, 'p-price').text
            # title = item.find_element(By.CLASS_NAME, 'p-name').text
            # commit = item.find_element(By.CLASS_NAME, 'p-commit').text
            # shop = item.find_element(By.CLASS_NAME, 'p-shop').text
            # url = item.find_element(By.CSS_SELECTOR, "div > div.p-img > a").get_attribute('href')
            # icons = item.find_elements(By.CSS_SELECTOR, 'div > div.p-icons > i')
            url = WebDriverWait(item, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div > div.p-img > a"))).get_attribute('href')
            id = url.split('/')[-1].split('.html')[0]
            
            if id not in self.IDs or no_repeat != 1:
                price =  WebDriverWait(item, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'p-price > strong > i'))).text
                title = WebDriverWait(item, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'p-name'))).text
                commit = WebDriverWait(item, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'p-commit > strong > a'))).text
                shop = WebDriverWait(item, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'p-shop'))).text
                if commit.endswith("+"):
                    commit = commit[:-1]
                if commit.endswith("万"):
                    commit = int(commit[:-1])*10000
                if self.Lock != None: self.Lock.acquire()
                self.IDs.append(id)
                self.prices.append(float(price))
                self.titles.append(title)
                self.commits.append(int(commit))
                self.shops.append(shop)
                self.urls.append(url)
                self.pages.append(pageid+1)
                try:
                    icons = item.find_elements(By.CSS_SELECTOR, 'div > div.p-icons > i')
                    icons_list = [it.text for it in icons]
                    self.icons.append(icons_list)
                except:
                    self.icons.append([])
                    continue
                
                if self.Lock!= None: self.Lock.release()

            
        print(f'Page {pageid+1} finished, loaded {len(items)} pages')

        if pageid in self.unfinished:
            self.unfinished.remove(pageid)   

        # except:
        #     self.unfinished.add(pageid)
        #     print(f"Error in finding elements in page {pageid+1}")

    def save_to_excel(self, format = 'xlsx', combineURL = 1, filename = 'jd', sort = 1):
        '''format: xlsx or csv
            combineURL: 1: generate HYPERLINK in the 商品 column     0: generate a single URL column like "https://item.jd.com/100077643920.html" with its HYPERLINK attached, and the number in this link is the product ID.
            filename: the file name, no need to add suffixes like "xlsx"
            sort: 1: by price, descending   2: by price, ascending     3: by comments, descending   4: by comments, ascending'''
        
        if combineURL == 1:
            df = pd.DataFrame({
            'IDs' : self.IDs,
            'Prices': self.prices,
            'Items': self.titles,
            'Comments': self.commits,
            'Shops': self.shops,
            'Icons': self.icons,
            'Pages': self.pages
            })
            for i in range(len(self.titles)):
                df.loc[i,'Items'] = '=HYPERLINK("'+ self.urls[i] + '","' + self.titles[i] + '")'

        else:
            df = pd.DataFrame({
            'IDs' : self.IDs,
            'Prices': self.prices,
            'Items': self.titles,
            'Comments': self.commits,
            'Shops': self.shops,
            'Urls': self.urls,
            'Icons': self.icons,
            'Pages': self.pages
            })
            for i in range(len(self.titles)):
                df.loc[i,'Urls'] = '=HYPERLINK("'+ self.urls[i] + '","' + self.urls[i] + '")'
                
        if self.no_repeat == 1:
            df.drop_duplicates(subset=['IDs'], inplace= True)
        if sort == 1:
            df.sort_values(by=['Prices'], ascending= False, inplace = True)
        elif sort == 2:
            df.sort_values(by=['Prices'], ascending= True, inplace = True)
        elif sort == 3:
            df.sort_values(by=['Comments'], ascending= False, inplace = True)
        elif sort == 4:
            df.sort_values(by=['Comments'], ascending= True, inplace = True)
        
        # 存为excel
        # df.drop(columns=df.columns[0], axis=1, inplace=True)
        if format == 'xlsx':
            df.to_excel(f'{filename}.xlsx', index=False)
        elif format == 'csv':
            df.to_csv(f'{filename}.csv', encoding='utf-8-sig', index=False)
        else:
            print('Invalid Format')

if __name__ == '__main__':
    search = SerialSearch(keyword = "电脑", login_status=1, pagenum=10, no_repeat=1)
    search.save_to_excel(combineURL=1, format='xlsx', filename='jd_serial', sort = 3)

