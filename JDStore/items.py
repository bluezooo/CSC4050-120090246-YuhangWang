# Store website URL, change this 
# url = "https://mall.jd.com/view_search-933997-0-99-1-24-1.html"
# url = "https://mall.jd.com/view_search-2746730-23013324-99-1-20-1.html" 
# url = input("Please input the store url")


from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd


#initialize driver
option = webdriver.ChromeOptions()
# Not load pics to reduce loading time
option.add_experimental_option('prefs', {'profile.managed_default_content_settings.images': 2})
driver = webdriver.Chrome(options = option)
driver.implicitly_wait(10)


# init lists
href_list = []
commentsCount = []
plus = []

def get_page_items():
	#J_GoodsList > ul > li:nth-child(20) > div > div.jPic > a > img
	lis = driver.find_elements(By.CSS_SELECTOR, '#J_GoodsList > ul > li')
	for li in lis: 
		href = li.find_element(By.CSS_SELECTOR, 'div.gl-i-wrap > div.jPic > a').get_attribute('href')
		comments = li.find_element(By.CSS_SELECTOR, 'div.jGoodsInfo > div.jExtra > a > em').text
		if comments.endswith("+"):
			comments = comments[:-1]
			plus.append(1)
		else:
			plus.append(0)
		if comments.endswith("万"):
			comments = int(comments[:-1])*10000
		try:
			commentsCount.append(int(comments))
			href_list.append(href)
		except:
			print('error in converting int')
      
  

def get_all_items(url):
	driver.get(url)
	get_page_items()
	number_of_pages = len(driver.find_elements(By.CSS_SELECTOR, '#J_GoodsList > div > a')) + 1
	for i in range(number_of_pages -3):
		driver.find_element(By.CSS_SELECTOR, "#J_GoodsList > div > a:nth-child(%d)"%(i+3)).click()
		time.sleep(0.5)
		get_page_items()
	driver.quit()

def save(filename, format):
    df = pd.DataFrame({
		'URL': href_list,
		'Comments': commentsCount,
		'plus': plus
	})
    df.sort_values(by=['Comments'], ascending= False, inplace = True)
    df = df.astype(str) 
    for i in range(len(df)):
        if df.loc[i,'plus'] == "1":
            df.loc[i,'Comments'] = df.loc[i,'Comments']+"+"
    if format == 'xlsx' or format == 'xls':
        df.to_excel(f'{filename}.xlsx', index=False, columns=['URL', 'Comments'])
    elif format == 'csv':
        df.to_csv(f'{filename}.csv', encoding='utf-8-sig', index=False, columns=['URL', 'Comments'])
    elif format == 'txt':
        with open("items.txt", 'w') as f:
            for line in df['URL']:
                f.write(line+'\n')
    else:
        print('Invalid Format')

# Main
get_all_items(url = "https://mall.jd.com/view_search-933997-0-99-1-24-1.html")
save(filename = "items", format= 'csv')
print("Total number of items: ", len(href_list))
