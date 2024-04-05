from queue import Queue, Empty
import requests
import os

## Download Thread
class Downloader:
    def __init__(self):
        self.download_queue = Queue()
        self.running = True
        print("Download thread starts")

    def add_to_queue(self, info_tuple):
        self.download_queue.put(info_tuple)

    def download(self):
        while self.running:
            try:
                username, video_link, title = self.download_queue.get(timeout=2)
                self.username = username
                if video_link == "":
                    print("invalid Video")
                    return 
                if not os.path.exists(username):
                    os.mkdir(username)
                file_name = f"{username}/{title}.mp4"

                # print ("Downloading file:%s"%(file_name))
                r = self.download_video(video_link)

                with open(file_name, 'wb') as f: 
                    for chunk in r.iter_content(chunk_size = 1024*1024): 
                        if chunk: 
                            f.write(chunk) 
                print ("%s downloaded!"%(file_name) )
            except Empty:
                continue
            except KeyboardInterrupt:
                self.stop()
            except Exception as e:
                print(f"Error downloading {file_name}: {e}")

    def download_video(self, url, max_retries=3):
        retries = 0
        while retries < max_retries:
            try:
                r = requests.get(url, stream=True, timeout=30)
                r.raise_for_status()
                return r
            except requests.exceptions.Timeout:
                print("Timeout xingyerror occurred. Retrying...")
                retries += 1
            except requests.exceptions.RequestException as e:
                print(f"Request error occurred: {e}")
                break
        raise Exception("Failed to download video after multiple retries.")
    
    def stop(self):
        self.running = False
        print('All Downloaded!, check them under folder: ', self.username)