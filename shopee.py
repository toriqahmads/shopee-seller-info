import requests
import json
from selenium import webdriver
from time import sleep
import os
from selenium.webdriver.chrome.options import Options
import urllib
import math
import csv

class Shopee :
    cookie = ""
    token = ""
    datas = []
    seller = []
    page = 0
    keyword = ""
    path = ""

    def __init__(self, keyword, path) :
        self.keyword = keyword
        self.path = path
        self.page = self.getTotal()
        
    def getTotal(self) :
        headers = {'user-agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
        url = "https://shopee.co.id/api/v2/search_items/?by=relevancy&keyword={}&limit=50&locations=Jawa%2520Tengah&order=desc&page_type=search".format(urllib.quote(self.keyword))
        res = requests.get(url, headers = headers).json()
        return int(math.ceil(float(float(res['total_count'])/50)))
    
    def getSellerId(self, page) :
        page = page*60
        headers = {'user-agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
        url = "https://shopee.co.id/api/v2/search_items/?by=relevancy&keyword={}&limit=50&locations=Jawa%2520Tengah&newest={}&order=desc&page_type=search".format(urllib.quote(self.keyword), page)
        res = requests.get(url, headers = headers).json()

        for data in res['items'] :
            if data['shopid'] not in self.datas :
                self.datas.append(data['shopid'])

    def getCookie(self) :
        url = "https://shopee.co.id/"
        co = Options()
        co.add_argument("--nosandbox")
        dp = os.getcwd()+"\\chromedriver.exe"
        driver = webdriver.Chrome(executable_path = dp, chrome_options = co)
        driver.get(url)
        self.cookie = ';'.join(['{}={}'.format(item['name'], item['value'])
                    for item in driver.get_cookies()])
        self.token = driver.get_cookie('csrftoken')['value']          
        driver.quit()
        
    def getSeller(self, shopid) :
        data = {'shop_ids':[shopid]}
        url = "https://shopee.co.id/api/v1/shops/"
        headers = {'x-csrftoken': self.token,
                   'cookie': self.cookie,
                   'content-type': 'application/json',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
                   'referer': 'https://shopee.co.id/'
                   }
        req = requests.post(url, data=json.dumps(data), headers=headers)
        res = req.json()

        for data in res:
            if "DEMAK" in data['place'] :
                data = {'sellerid': data['shopid'],
                        'username': data['username'],
                        'name': data['name'],
                        'verified': data['is_shopee_verified'],
                        'good_rate': data['rating_good'],
                        'bad_rate': data['rating_bad'],
                        'star': data['total_avg_star'],
                        'followers': data['follower_count'],
                        'city': data['place'],
                        'url': 'https://shopee.co.id/{}'.format(data['username'])
                        }
                if data not in self.seller :
                    self.seller.append(data)

    def convertToCsv(self) :
        keys = self.seller[0].keys()
        with open(r"%s.csv" % self.path, "wb+") as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(self.seller)
        
    def getAllSellerInfo(self) :
        for data in self.datas :
            self.getSeller(data)

    def exe(self) :
        for i in range(0, self.page) :
            self.getSellerId(i)
        self.getCookie()
        self.getAllSellerInfo()
        self.convertToCsv()

c = Shopee("khimar", "D:\sellershope")
c.exe()
print c.datas
