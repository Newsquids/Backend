import requests, json
from datetime import datetime

sites = ["cnbc", "bbc", "reuters", "coindesk", "cointelegraph", "cryptoslate"]

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
            dic["created_time"] = data[3] + ' 00:00'
        else:
            dic["created_time"] = data[3]
        dic["category"] = data[4]
        content = json.dumps(dic)
        rq = requests.post(url="http://52.79.185.65:8000/api/news",data=content)