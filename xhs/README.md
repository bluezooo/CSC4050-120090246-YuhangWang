## 小红书 Video Crawler

### Usage
Edit and Run `run.sh`, or
```shell
python xhsVideoCrawler.py "https://www.xiaohongshu.com/user/profile/5cc5b0680000000016025b50" 1

python xhsVideoCrawlerParallel.py "https://www.xiaohongshu.com/user/profile/5cc5b0680000000016025b50" 2
```
- The URL as argument 1 must be the user's profile page.
- The number as argument 2 after the url: login_status:
- For login purpose, can store cookies for next time login
  - 0: NOT recommended, possible login and verification needed when crawling data, causing interuption  
  - 1: Read the stored the cookie file only, NOT for first time usage   
  - 2: Recommended: get and store the cookie for next time usage, this requires to login manually.      More details to be seen in MyDriver.py'''

