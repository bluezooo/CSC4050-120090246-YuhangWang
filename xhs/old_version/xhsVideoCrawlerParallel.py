
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
import os
import sys
from concurrent.futures import ThreadPoolExecutor

try:
    profilePage =  sys.argv[1]
except:
    print('Please run the python file with one argument (user profile page)')
    exit

#initialize driver options  # Not load pics to reduce loading time
option = webdriver.ChromeOptions()
# option.add_experimental_option('prefs', {'profile.managed_default_content_settings.images': 2})
option.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")

## start the driver
def getPostsLink(profilePage):
    driver = webdriver.Chrome(options = option)
    driver.implicitly_wait(10)
    driver.get(profilePage)
    contents = driver.find_element(By.ID, 'userPostedFeeds').find_elements(By.CLASS_NAME, 'note-item')
    username = driver.find_element(By.CSS_SELECTOR,'#userPageContainer > div.user > div > div > div.info > div.basic-info > div.user-basic > div.user-nickname > div').text
    postlist = []
    for content in contents:
        postlist.append(content.find_element(By.CSS_SELECTOR, "div > a").get_attribute("href"))
    print("Downloading for user: ", username)
    driver.close()
    return username, postlist
username, postlist = getPostsLink(profilePage)


## Browsing on each posts 
######################### Parallel Version #########################
def getVideoLinksParallel(postlist):
    # count = 1
    video_links = []
    executor = ThreadPoolExecutor(3)
    
    # future_list = []
    # for current_href in postlist:
    #     future = executor.submit(task, (current_href,))
    #     future_list.append(future)

    # for future in future_list:
    #     while True:
    #         if future.done():
    #             video_links.append(future.result())
    #             break
    # return video_links
    video_links = executor.map(task, postlist)
    print(video_links)
    return video_links

def task(current_href):
    newdriver = webdriver.Chrome()
    newdriver.implicitly_wait(10)
    newdriver.get(current_href)
    src = ''
    try:
        type = newdriver.find_element(By.CSS_SELECTOR,"head > meta:nth-child(50)").get_attribute("content")
        if type == 'video':
            src = newdriver.find_element(By.CSS_SELECTOR,"#noteContainer > div.video-player-media.media-container > div > div > video").get_attribute("src")
            # print("Post ", count, "is a video")
            # video_links.append(src)
        # count += 1
        newdriver.close()
        # print(src)
    except:
        print(current_href, "With network error")
    return src


video_links = getVideoLinksParallel(postlist)

# Download videos
def download_video_series(video_links): 
    has_video = False
    if not os.path.exists(username):
        os.mkdir(username)
    for link in video_links: 
        if link  != '':
        # obtain filename by splitting url and getting  
            file_name = username+'/'+link.split('/')[-1]    
            # print ("Downloading file:%s"%(file_name))
            r = requests.get(link, stream = True) 
            with open(file_name, 'wb') as f: 
                for chunk in r.iter_content(chunk_size = 1024*1024): 
                    if chunk: 
                        f.write(chunk) 
            print ("%s downloaded!\n"%(file_name) )
            has_video = True
    if not has_video:
        print("No videos found")
        return 
    else:
        print ("All videos downloaded!")
        return
download_video_series(video_links)