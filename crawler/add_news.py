import requests, json
from crawler import Crawl
from datetime import datetime

crawler = Crawl()
sites = crawler.all_sites

for site in sites:
    with open(f'/Users/s/Desktop/Study/Toyproject/Newsquids/Backend/crawler/files/{site}/new_data.txt' , "r") as f:
        file = f.read()

    dummy_data = eval(file)

    for data in dummy_data:
        dic = {}
        dic["channel"] = site
        dic["category"] = "all"
        dic["link"] = data[0]
        dic["headline"] = data[1]
        dic["image"] = data[2]
        if site == "cointelegraph":
            dic["create_time"] = data[3] + ' 00:00'
        else:
            dic["create_time"] = data[3]
        dic["category"] = data[4]
        content = json.dumps(dic)
        rq = requests.post(url="http://3.36.90.21:8000/api/news",data=content)