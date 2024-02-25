
#### For searching keywords or items in JD's homepage, go to directory **`search`**

# items.py

#### Details

1. Add an option to chrome option reduce loading time by avoid loading pictures.

   ```python
   option.add_experimental_option('prefs',{'profile.managed_default_content_settings.images': 2})
   driver = webdriver.Chrome(options= option)
   ```

 2. This program automatically sort the urls by their number of comments.

    If you want to turn off or change the sorting, change `df.sort_values` function in function **save**()

#### Usage

##### necessary packages 

```apl
selenium; time; pandas
```

##### Example Usage
```python
python items.py
```
In this python file, change these two line in the end for your search.
```python
get_all_items(url = "https://mall.jd.com/view_search-933997-0-99-1-24-1.html")
save(filename = "items", format= 'csv')
```

- `format`: xlsx, csv or txt supported

	- **xlsx or csv**: **sorted**, will contain url and detailed comments count for each item
  - **txt**: **sorted**, contains **only url** of each item without its comment count

- `url` can not be a homepage of a store. Instead, it should contain detailed goods information of a store like this:

  <img src="images\ex1.png" alt="ex1" style="zoom: 55%;" />



#### Troubleshooting

1. If `jd.com` requires your login every time you start the program, you can try adding two functions from file `search/MyDriver.py` : `getcookie()` and `readcookie()`

   Theses two functions will equip the `webdriver` object with cookies from you last manual login.

   For more details, please visit [this](https://github.com/bluezooo/jd/blob/main/search/MyDriver.py#L34).

2. For network error, try turning off VPN.

3. For other errors, try changing the browser to `Chrome`, since the core's speed of `Edge` is slow.

4. If some elements fail to load, try increasing waiting time:

   - **implicitly_wait**: `driver.implicitly_wait(10)`, increase 10s to more.

   - **explicitly_wait**: before the fail to load element, change the `find_element` function to this:

     ```python
     from selenium.webdriver.support.wait import WebDriverWait
     from selenium.webdriver.support import expected_conditions as EC
     
     wait = WebDriverWait(driver, timeToWaitDefinedByYou)
     selector = (By.CSS_SELECTOR, 'Your CSS selector from function find_element')
     specificElement = wait.until(EC.presence_of_element_located(selector))
     ```


5. Double check the url's page structure, make sure it is exactly the same format as the previous example
   



 # items_threading.py 

#### Details

###### By assigning each url search to each threads, multiple webdrivers called

Using multiple threads to concurrently search multiple threads and get multiple result files.

Using `Semaphore` to manage the shared memory

#### Usage

##### necessary packages 

```
threading; time; selenium; pandas
```
##### Example usage

```python
python items_threading.py
```
##### Things to change

```python
sem = Semaphore(16) ## Maximum Thread
filename = "items_threading"
format = 'csv'

url3 = "https://mall.jd.com/view_search-933997-0-99-1-24-1.html"
url1 = "https://mall.jd.com/view_search-2746730-23013324-99-1-20-1.html" 
url2 = "https://mall.jd.com/view_search-711685-0-99-1-24-1.html"
url4 = "https://mall.jd.com/view_search-2031298-0-99-1-24-1.html"
url_list = [url1, url2, url3, url4]
```

change the filename, format, and url list.

For each url, there will be a file named by adding its index to the end of the `filename`

##### Expected outputs

<img src="images\ex2.png" alt="ex2" style="zoom: 67%;" />



