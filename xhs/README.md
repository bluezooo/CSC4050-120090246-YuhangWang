## 小红书 Video Crawler
Only posts of video type will be downloaded.

### Overview
Generally three threads:
- Main thread: visit profile page, dynamically (scroll down the page to get all posts) load and analyse the page elements, submit the video post's URL to second thread.
- Second thread: visit post detail page, get the title and real video downloading URL (https://sns-video-hw.xhscdn.net/stream/...........abc.mp4). Finally submit the URL to the download thread.
- Download thread: A FIFO queue is maintained for the entire cycle. After the main thread loads all of the currently loaded posts and no new post appears when scrolling down, the main thread will send the `STOP` signal to the download thread. After the queue be empty, the whole program will stop.

### Files
- `Downloader.py`: class for the download thread
- `MyDriver.py`: class for building webdrivers and getting, storing, and reading cookies
- `xhsCrawler.py`: Main thread. 

### Usage
Edit and Run `run.sh`, or
```shell
python xhsVideoCrawler.py https://www.xiaohongshu.com/user/profile/64b6acd8000000001403faf5 1

python xhsVideoCrawler.py https://www.xiaohongshu.com/user/profile/65d340f6000000000401ddec 2
```
- The URL as `argument 1` must be the user's profile page.
- The number as `argument 2` after the url: `login_status`:
- For login purpose, can store cookies for next time login
  - 0: NOT recommended, possible login and verification needed when crawling data, causing interuption  
  - 1: Read the stored the cookie file only, NOT for first time usage   
  - 2: Recommended: get and store the cookie for next time usage, this requires to login manually.      More details to be seen in MyDriver.py'''

###### Important: In order to get all the posts of a user, you must sign in. Set the `login_status` to be 2 at the first time running, this will save the your cookies in file `xhscookie.txt` after you scan the login QR code manually, so next time before your cookie sessions expire, you can set `login_status` to be 1 to the read the cookie file and add the cookies to the browser

### Troubleshooting
- If Slider two-factor authentication is needed in a browser, do it manually
- If network error occures in the browser, change the IP address such as turning on/off a VPN. Because xiaohongshu.com has some restriction on the request frequency 
- Sometimes, the network error is fixed by turning on VPN but after several seconds, it shows again. Method 1: You can wait until the network recovers to download next post (maybe 1 min) and the program will automitically wait for it, since the program periodically retries will it cannot find certain element on a page. Method 2: Change the IP address when the program is running multiple times.

### Results
- The title of the post will be the name of the video.
- The username will be the videos' folder name.

