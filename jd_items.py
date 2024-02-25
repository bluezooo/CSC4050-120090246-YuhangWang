# Store website URL, change this 
url = "https://mall.jd.com/view_search-933997-0-99-1-24-1.html"
url = "https://mall.jd.com/view_search-2746730-23013324-99-1-20-1.html" 
# url = input("Please input the store url")


from selenium import webdriver
from selenium.webdriver.common.by import By
import time

driver = webdriver.Chrome()
href_list = []

def get_page_items():
	driver.implicitly_wait(10)
	lis = driver.find_elements(By.CSS_SELECTOR, '#J_GoodsList > ul > li')
	for li in lis: 
		href = li.find_element(By.CSS_SELECTOR, 'div.gl-i-wrap > div.jPic > a').get_attribute('href')
		href_list.append(href)

def get_all_items():
	driver.get(url)
	get_page_items()
	number_of_pages = len(driver.find_elements(By.CSS_SELECTOR, '#J_GoodsList > div > a')) + 1
	for i in range(number_of_pages -3):
		driver.find_element(By.CSS_SELECTOR, "#J_GoodsList > div > a:nth-child(%d)"%(i+3)).click()
		time.sleep(0.5)
		get_page_items()
	driver.quit()

def save_to_txt(href_list):
	with open("jd_items.txt", 'w') as f:
		for line in href_list:
			f.write(line+'\n')

# Main
get_all_items()
save_to_txt(href_list)
print("Total number of items: ", len(href_list))
