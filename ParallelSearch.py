import threading, time
from threading import Semaphore, Lock   #####Lock().acquire()/ .release()

from SerialSearch import SerialSearch
from MyDriver import MyDriver

class ParallelSearch(SerialSearch):

    def __init__(self, keyword, login_status = 2, pagenum = 8, numthreads = 8, no_repeat = 1):
        '''keyword: the word you want to search in the homepage search box 
            login_status: 0: NOT recommended, possible verification needed when crawling data, causing interuption  1: Read the stored the cookie file only, NOT for first time usage   2: Recommended: get and store the cookie for next time usage, this requires to login manually.      More details to be seen in MyDriver.py
            pagenum: the total page of items you want to get&load
            numthreads: number of threads to accelerate the program'''
        self.mydriver = MyDriver(login_status, browser = 'Chrome')
        self.keyword = keyword
        self.no_repeat = no_repeat
        self.sem = Semaphore(numthreads) ## Maximum Thread
        self.unfinished = set()
        self.Lock = Lock()
        self.IDs, self.prices, self.titles, self.commits, self.shops, self.urls, self.icons, self.pages= [], [], [], [], [], [], [], []
        self.search_result_parse(pagenum, login_status, no_repeat)
        self.mydriver.close()

    def search_result_parse(self, pagenum, login_status = 1, no_repeat = 1):
        self.mydriver.search_keyword(self.keyword)
        page_num = self.page_count(pagenum, login_status)
        self.currentURL = self.mydriver.driver.current_url
        for idx in range(page_num):
            self.sem.acquire()
            threading.Thread(target=self._find_and_append_parallel, args=(idx,login_status,no_repeat)).start()
        # wait for each process to complete
        for thread in threading.enumerate():
            if thread is not threading.current_thread():
                thread.join()   
        print("Retrying on these page id: ", self.unfinished)
        
        for j in range(2):
            for idx in self.unfinished.copy():
                self.sem.acquire()
                threading.Thread(target=self._find_and_append_parallel, args=(idx,  login_status, no_repeat)).start()
            # wait for each process to complete
            for thread in threading.enumerate():
                if thread is not threading.current_thread():
                    thread.join()
            print(self.unfinished)  

    def _find_and_append_parallel(self, idx, login = 1, no_repeat = 1):
        if login == 2:
            login =1
        newdriver = MyDriver(login, browser = 'Chrome')
        newdriver.driver.get(self.currentURL)
        # newdriver.driver.implicitly_wait(10)
        time.sleep(0.2)
        self.load_specific_page(newdriver.driver, idx, no_repeat)
        newdriver.close()
        self.sem.release()
        

        




if __name__ == '__main__':
    search = ParallelSearch(keyword = "电脑", login_status=1, pagenum=10, numthreads = 8, no_repeat = 1)
    search.save_to_excel(combineURL=1, format='xlsx', filename='jd_parallel', sort = 3) ####                    sort!!!
        # https://club.jd.com/comment/productCommentSummaries.action?referenceIds=100075799817&callback=a

