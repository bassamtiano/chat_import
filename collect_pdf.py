import threading
import time
import sys

import json
import requests

from selenium import webdriver
from bs4 import BeautifulSoup

import trafilatura

from tqdm import tqdm

class DataCollection():
    def __init__(self,
                 lang,
                 num_pages,
                 num_item_per_page):
        self.thread_local = threading.local()
        self.lang = lang
        
        self.num_pages = num_pages
        self.num_item_per_page = num_item_per_page
    
    def get_driver(self):
        driver = getattr(self.thread_local, 'driver', None)
        # Cek browser sudah run atau belum
        if driver is None:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--headless=new')
            # chrome_options.add_experimental_option('prefs', {
            #     "download.default_directory": "C:/Users/XXXX/Desktop", #Change default directory for downloads
            #     "download.prompt_for_download": False, #To auto download the file
            #     "download.directory_upgrade": True,
            #     "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
            # })
            driver = webdriver.Chrome(options = chrome_options)
            
            # firefox_options = webdriver.FirefoxOptions()
            # firefox_options.add_argument('--headless=new')
            # driver = webdriver.Firefox(options = firefox_options)
            
            # edge_options = webdriver.EdgeOptions()
            # edge_options.add_argument('--headless=new')
            # driver = webdriver.Edge(options = edge_options)
            setattr(self.thread_local, 'driver', driver)
        
        return driver
    
    def fetch_search_result(self, url, page, query = "no_name"):
        driver = self.get_driver()
        driver.implicitly_wait(5)
        driver.get(url)
        
        page_content = BeautifulSoup(driver.page_source, "html.parser")
        search_lists = page_content.find_all("div", attrs={"class": 'MjjYud'})
        search_lists = search_lists[:self.num_item_per_page]
        for i_cnt, cnt in enumerate(tqdm(search_lists)):
            title = cnt.find_all("h3", attrs={"class":  'DKV0Md'})
            
            if len(title) > 0:
                title = title[0].text
                root_url = cnt.find("cite").text.split(" › ")[0]
                source_url = cnt.find_all("a", attrs={"jsname": "UWckNb"})[0]["href"]
                
                try:
                    response = requests.get(source_url, stream = True)
                    file_name = source_url.split("/")[-1]
                
                    with open(f'datasets/references/{file_name}', 'wb') as fd:
                        fd.write(response.content)
                except:
                    print(f"{source_url} is missing")
                
        
        
    
    def search(self, query):
        
        datasets = []
        for i_p in range(self.num_pages):
            start_index = i_p * 10
            url = "https://www.google.com/search?"\
            f"q={query}&"\
            f"hl={self.lang}&"\
            f"lr={self.lang}&"\
            f"start={start_index}"
            self.fetch_search_result(url, i_p, query)


if __name__ == "__main__":
    data_collect = DataCollection(lang = "id", num_pages = 20, num_item_per_page = 5)
    data_collect.search(query = 'site%3Aperaturan.bpk.go.id%2F+ext%3Apdf%C2%A0"impor"')