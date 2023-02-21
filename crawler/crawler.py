
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException, ElementNotInteractableException, NoSuchAttributeException
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains, ChromeOptions, Chrome
from datetime import datetime, timedelta
from webdriver_manager.chrome import ChromeDriverManager
from news.models import News, NewsChannel, NewsCategory
from django.db import IntegrityError
import asyncio


class Crawl:
    def __init__(self) -> None:
        self.traditional_sites = ["cnbc", "bbc", "reuters"]
        self.crypto_sites = ["coindesk", "cointelegraph", "cryptoslate"]
        self.all_sites = ["cnbc", "bbc", "reuters", "coindesk", "cointelegraph", "cryptoslate"]
        self.sites_categories = {
            "cnbc" : ["world-markets", "economy", "technology", "finance", "health-and-science", "politics"],
            "bbc" : ["news/world", "news/business", "news/technology", "news/science_and_environment", "news/health" ],
            "reuters" : ["world", "business", "legal", "markets"],
            "coindesk" : ["markets", "business", "policy", "tech", "web3"],
            "cointelegraph" : ["tags/defi", "tags/nft", "tags/regulation", "tags/bitcoin", "tags/ethereum", "tags/altcoin", "tags/business"],
            "cryptoslate" : ["crime", "regulation", "cbdcs", "bankruptcy", "analysis", "defi", "nfts", "partnerships", "exchanges", "news/bitcoin", "news/ethereum"]
        }
        # categories for traditional : world, business-economy, science-tech, politic 
        # categories for crypto : crypto, regulation, business, defi, nft, web3, cbdc, crime-bankruptcy
        self.db_category = {
            "cnbc" : {"world-markets" : "world", "economy" : "business-economy", "technology" : "science-tech", "finance"  : "business-economy", "health-and-science" : "science-tech", "politics" : "politic"},
            "bbc" : {"news/world" : "world", "news/business" : "business-economy", "news/technology" : "science-tech", "news/science_and_environment" : "science-tech", "news/health" : "science-tech" },
            "reuters" : {"world" : "world", "business" : "business-economy", "legal" : "politic", "markets" : "world"},
            "coindesk" : {"markets" : "crypto", "business" : "business", "policy" : "regulation", "tech" : "crypto", "web3" : "web3"},
            "cointelegraph" : {"tags/defi" : "defi", "tags/nft" : "nft", "tags/regulation" : "regulation", "tags/bitcoin" : "crypto", "tags/ethereum" : "crypto", "tags/altcoin" : "crypto", "tags/business" : "business"},
            "cryptoslate" : {"crime" : "crime-bankruptcy", "regulation" : "regulation", "cbdcs" : "cbdc", "bankruptcy" : "crime-bankruptcy", "analysis" : "crypto", "defi" : "defi", "nfts" : "nft", "partnerships" : "business", "exchanges" : "business", "news/bitcoin" : "crypto", "news/ethereum" : "crypto"}

        }
    def check_link_exists(self, link:str):
        exist_or_not = News.objects.filter(link=link).exists()
        return exist_or_not
    
    def save_data(self, category:str, channel:str, **kwargs):
        cat = NewsCategory.objects.get(category_name=category)
        ch = NewsChannel.objects.get(channel_name=channel)
        try:
            News.objects.create(channel=ch, category=cat, **kwargs)
            return True
        except IntegrityError:
            return False

    def get_dict_or_data(self, site:str, dict:bool=False):
        if dict == True:
            with open(f"/Users/s/Desktop/Study/Toyproject/Newsquids/Backend/crawler/files/{site}/new_link.txt","r") as f:
                read_file = f.read()
        else:
            with open(f"/Users/s/Desktop/Study/Toyproject/Newsquids/Backend/crawler/files/{site}/new_data.txt","r") as f:
                read_file = f.read()
        return eval(read_file)
    
    def update_dict_or_data(self, site:str, data:str, dict:bool=False):
        if dict == True:
            with open(f"/Users/s/Desktop/Study/Toyproject/Newsquids/Backend/crawler/files/{site}/new_link.txt","w") as f:
                f.write(data)
        else:
            with open(f"/Users/s/Desktop/Study/Toyproject/Newsquids/Backend/crawler/files/{site}/new_data.txt","w") as f:
                f.write(data)
        return
    
    def get_data_or_None(self, data):
        try:
            obj = data
        except NoSuchElementException:
            obj = None
        return obj

    def preprocess_time(self, site:str, link:str, time:str):
        if time == None or len(time) < 10:
            return 0
        try:
            if site == "cnbc":
                day = link.split('cnbc.com/')[1][:10].replace('/','-')
                if 'UPDATED' in time:
                    if '2023' in time:
                        tem = time.split('2023')
                    elif '2022' in time:
                        tem = time.split('2022')
                    other = tem[1][:5]
                    if other[1] == ':':
                        other = '0' + other[:-1]
                    return (f'{day} {other}')
                else:
                    tem = time.split('T')
                    other = tem[1][:5]
                    return (f'{day} {other}')
            elif site == "bbc":
                tem = time.split('T')
                day = tem[0]
                other = tem[1][:5]
                return (f'{day} {other}')
            elif site == "reuters":
                tem = time.split(',')[1].split(":")
                day = link[-11:-1]
                hour = tem[0][5:]
                if len(hour) == 1:
                    hour = '0'+hour
                minute = tem[1][:2]
                return (f'{day} {hour}:{minute}')
            elif site == "coindesk":
                if '2023' in link:
                    tem_link = link.split('2023')
                    tem_date = tem_link[1][:6].replace('/','-')
                    day = '2023'+tem_date
                elif '2022' in time:
                    tem_link = link.split('2022')
                    tem_date = tem_link[1][:6].replace('/','-')
                    day = '2022'+tem_date
                tem = time.split(':')
                if tem[0][-2] == ' ':
                    hour = tem[0][-1]
                    if 'p.m' in time:
                        hour = str(int(hour) + 12)
                    minute = tem[1][:2]
                elif tem[0][-2] != ' ':
                    hour = tem[0][-2:]
                    if 'p.m' in time:
                        hour = str(int(hour) + 12)
                    minute = tem[1][:2]
                if len(hour) == 1:
                    hour = '0' + hour
                return(f'{day} {hour}:{minute}')
            elif site == "cointelegraph":
                return time
            elif site == "cryptoslate":
                tem = time.split(',')
                dt = []
                tem_d = tem[1][1:17].split(" ")
                dt += list(map(int,tem_d[0].split('-')))
                dt += list(map(int,tem_d[1].split(':')))
                dt += [0,0]
                tem_dt = datetime(*dt)
                if 'day' in tem[0]:
                    tem_dt - timedelta(days=int(tem[0][:2]))
                elif 'min' in tem[0]:
                    tem_dt - timedelta(minutes=float(tem[0][:2]))
                elif 'hour' in tem[0]:
                    tem_dt - timedelta(hours=int(tem[0][:2]))
                year = tem_dt.year
                month = str(tem_dt.month)
                if len(month) == 1:
                    month = '0' + month
                day = str(tem_dt.day)
                if len(day) == 1:
                    day = '0' + day
                hour = str(tem_dt.hour)
                if len(hour) == 1:
                    hour = '0' + hour
                minute = str(tem_dt.minute)
                if len(minute) == 1:
                    minute = '0' + minute
                return(f'{year}-{month}-{day} {hour}:{minute}')
        except IndexError:
            return 0

    async def crawling_sites(self, site:str):
        ops = ChromeOptions()
        ops.add_argument("--headless")
        ops.add_argument("--no-sandbox")
        web = Chrome(ChromeDriverManager().install(), options=ops)
        tem_web = Chrome(ChromeDriverManager().install(), options=ops)
        tem_web.set_page_load_timeout(30)
        base_url = f"https://www.{site}.com"
        for category in self.sites_categories[site]:
            print(f'{site} : {category} 크롤링을 시작합니다.')
            url = base_url + f"/{category}"
            await asyncio.sleep(1)
            web.get(url)
            if site == 'cnbc':
                titles = web.find_elements(By.CLASS_NAME,"Card-title")
                for title in titles:
                    link = title.get_attribute("href")
                    if self.check_link_exists(link=link):
                        print("이미 존재하는 주소입니다.")
                        continue
                    headline = title.text
                    print(f"{site}의 {link} 크롤링 중...")
                    tem_web.get(link)
                    tem_web.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    await asyncio.sleep(3)
                    try:
                        image = tem_web.find_element(By.TAG_NAME, "picture").find_element(By.TAG_NAME,"img").get_attribute("src")
                    except NoSuchElementException or NoSuchAttributeException:
                        image = None
                    time_obj = tem_web.find_elements(By.TAG_NAME, "time")
                    for t in time_obj: 
                        pub_time = t.get_attribute("datetime")
                        if pub_time == None:
                            pub_time = f'{t.text}T{t.find_element(By.TAG_NAME, "span").text}'
                        break
                    time = self.preprocess_time(site=site,link=link,time=pub_time)
                    if not time:
                        continue
                    cat = self.db_category[site][category]
                    data = {"link" : link, "headline" : headline, "image" : image, "created_time" : time}
                    if self.save_data(channel=site, category=cat, kwargs=data):
                        print(f"{site}의 {link} 크롤링 완료")
                    else:
                        print(f"{site}의 {link} 크롤링 실패")
                    await asyncio.sleep(2.2)
            elif site == 'bbc':
                boxes = web.find_elements(By.CLASS_NAME,"gs-c-promo")
                for box in boxes:
                    try:
                        link = box.find_element(By.TAG_NAME,'a').get_attribute("href")
                        if 'news' not in link or 'live' in link:
                            continue
                    except NoSuchElementException or NoSuchAttributeException:
                        continue
                    if self.check_link_exists(link=link):
                        print("이미 존재하는 주소입니다.")
                        continue
                    headline = box.find_element(By.TAG_NAME,'h3').text
                    print(f"{site}의 {link} 크롤링 중...")
                    try:
                        tem_web.get(link)
                    except TimeoutException or WebDriverException:
                        print(f"{site}의 {link} 크롤링 실패")
                        continue
                    tem_web.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    await asyncio.sleep(2.4)
                    try:
                        image = tem_web.find_element(By.TAG_NAME, "img").get_attribute('src')
                    except NoSuchElementException or NoSuchAttributeException:
                        image = None
                    try:
                        pub_time = tem_web.find_element(By.TAG_NAME,'time').get_attribute("datetime")
                    except NoSuchElementException or NoSuchAttributeException:
                        continue
                    time = self.preprocess_time(site=site,link=link,time=pub_time)
                    if not time:
                        continue
                    cat = self.db_category[site][category]
                    data = {"link" : link, "headline" : headline, "image" : image, "created_time" : time}
                    if self.save_data(channel=site, category=cat, kwargs=data):
                        print(f"{site}의 {link} 크롤링 완료")
                    else:
                        print(f"{site}의 {link} 크롤링 실패")
                    await asyncio.sleep(2.2)
            elif site == 'reuters':
                await asyncio.sleep(2)
                li_boxes = web.find_elements(By.CLASS_NAME,"story-card")
                for box in li_boxes:
                    try:
                        link_element = box.find_element(By.CLASS_NAME,"media-story-card__heading__eqhp9")
                        link = link_element.get_attribute('href')
                        if self.check_link_exists(link=link):
                            print("이미 존재하는 주소입니다.")
                            continue
                    except NoSuchElementException or NoSuchAttributeException:
                        continue
                    print(f"{site}의 {link} 크롤링 중...")
                    action = ActionChains(web)
                    action.move_to_element(link_element)
                    action.perform()
                    await asyncio.sleep(2)
                    try:
                        tem_web.get(link)
                    except TimeoutException:
                        continue
                    try:
                        headline = tem_web.find_element(By.TAG_NAME,"h1").text
                    except NoSuchElementException:
                        print(f'{site}의 {link}에서 에러가 발생했습니다')
                        continue
                    pub_times = tem_web.find_element(By.TAG_NAME,"time").find_elements(By.TAG_NAME,'span')
                    pub_time = pub_times[1].text + pub_times[2].text
                    time = self.preprocess_time(site=site,link=link,time=pub_time)
                    if not time:
                        continue
                    try:
                        image = box.find_element(By.TAG_NAME, "img").get_attribute('src')
                    except NoSuchElementException or NoSuchAttributeException:
                        image = None
                    cat = self.db_category[site][category]
                    data = {"link" : link, "headline" : headline, "image" : image, "created_time" : time}
                    if self.save_data(channel=site, category=cat, kwargs=data):
                        print(f"{site}의 {link} 크롤링 완료")
                    else:
                        print(f"{site}의 {link} 크롤링 실패")
            elif site == "coindesk":
                web.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                await asyncio.sleep(4)
                boxes = web.find_elements(By.CLASS_NAME,"WDSwd")
                action = ActionChains(web)
                for box in boxes:
                    try:
                        btn = web.find_element(By.ID,"CybotCookiebotDialogBodyButtonAccept")
                        action.click(btn)
                        action.perform()
                        await asyncio.sleep(3)
                    except NoSuchElementException:
                        pass
                    except ElementNotInteractableException:
                        pass
                    try:
                        link = box.get_attribute("href")
                        if self.check_link_exists(link=link):
                            print("이미 존재하는 주소입니다.")
                            continue
                    except NoSuchAttributeException:
                        continue
                    try:
                        print(f"{site}의 {link} 크롤링 중...")
                        await asyncio.sleep(2.6)
                        tem_web.get(link)
                        try:
                            headline = tem_web.find_element(By.TAG_NAME, "h1").text
                            if len(headline) < 10:
                                headline = tem_web.find_element(By.CLASS_NAME,"at-headline").find_element(By.TAG_NAME,'h1').text
                                if len(headline) < 10:
                                    continue
                        except NoSuchElementException:
                            continue
                        try:
                            image = box.find_element(By.TAG_NAME,"img").get_attribute("src")
                        except NoSuchElementException or NoSuchAttributeException:
                            image = None
                        try:
                            pub_time = tem_web.find_element(By.CLASS_NAME,"at-created").find_element(By.TAG_NAME,"span").text
                        except NoSuchElementException:
                            try:
                                pub_time = tem_web.find_element(By.CLASS_NAME, "fUOSEs").text
                            except NoSuchElementException:
                                continue
                        time = self.preprocess_time(site=site,link=link,time=pub_time)
                        if not time:
                            continue
                        cat = self.db_category[site][category]
                        data = {"link" : link, "headline" : headline, "image" : image, "created_time" : time}
                        if self.save_data(channel=site, category=cat, kwargs=data):
                            print(f"{site}의 {link} 크롤링 완료")
                        else:
                            print(f"{site}의 {link} 크롤링 실패")
                    except TimeoutException:
                        print(f"{site}의 {link} 크롤링 실패")
                        continue
            elif site == "cointelegraph":
                await asyncio.sleep(2)
                web.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                await asyncio.sleep(2)
                boxes = web.find_elements(By.CLASS_NAME,"posts-listing__item")
                action = ActionChains(web)
                for box in boxes:
                    link = box.find_element(By.TAG_NAME, "a").get_attribute("href")
                    if self.check_link_exists(link=link):
                        print("이미 존재하는 주소입니다.")
                        continue
                    try:
                        print(f"{site}의 {link} 크롤링 중...")
                        await asyncio.sleep(2.6)
                        headline = box.find_element(By.CLASS_NAME, "post-card-inline__title").text
                        try:
                            image = box.find_element(By.TAG_NAME, "img").get_attribute("src")
                        except NoSuchElementException or NoSuchAttributeException:
                            image = None
                        try:
                            pub_time = box.find_element(By.TAG_NAME, "time").get_attribute("datetime")
                        except NoSuchElementException or NoSuchAttributeException:
                            continue
                        time = self.preprocess_time(site=site,link=link,time=pub_time)
                        if not time:
                            continue
                        cat = self.db_category[site][category]
                        data = {"link" : link, "headline" : headline, "image" : image, "created_time" : time}
                        if self.save_data(channel=site, category=cat, kwargs=data):
                            print(f"{site}의 {link} 크롤링 완료")
                        else:
                            print(f"{site}의 {link} 크롤링 실패")
                    except TimeoutException or WebDriverException:
                        print(f"{site}의 {link} 크롤링 실패")
                        continue
            elif site == "cryptoslate":
                await asyncio.sleep(2)
                web.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                await asyncio.sleep(2)
                body = web.find_element(By.CLASS_NAME, "news-feed")
                boxes = body.find_elements(By.TAG_NAME,"article")
                action = ActionChains(web)
                for box in boxes:
                    link_element = box.find_element(By.TAG_NAME, "a")
                    link = link_element.get_attribute("href")
                    action.move_to_element(link_element)
                    if self.check_link_exists(link=link):
                        print("이미 존재하는 주소입니다.")
                        continue
                    try:
                        print(f"{site}의 {link} 크롤링 중...")
                        action.perform()
                        await asyncio.sleep(2)
                        headline = box.find_element(By.TAG_NAME, "h2").text
                        try:
                            image = box.find_element(By.TAG_NAME, "img").get_attribute("src")
                        except NoSuchElementException or NoSuchAttributeException:
                            image = None
                        try:
                            pub_time = f'{box.find_element(By.CLASS_NAME, "read").text}, {datetime.now()}'
                        except NoSuchElementException:
                            continue
                        time = self.preprocess_time(site=site,link=link,time=pub_time)
                        if not time:
                            continue
                        cat = self.db_category[site][category]
                        data = {"link" : link, "headline" : headline, "image" : image, "created_time" : time}
                        if self.save_data(channel=site, category=cat, kwargs=data):
                            print(f"{site}의 {link} 크롤링 완료")
                        else:
                            print(f"{site}의 {link} 크롤링 실패")
                    except TimeoutException or WebDriverException:
                        print(f"{site}의 {link} 크롤링 실패")
                        continue
                await asyncio.sleep(2.6)
        web.quit()
        tem_web.quit()
        print(f'{site}의 크롤링 완료')
        return

async def main ():
    crawler = Crawl()
    sites = crawler.all_sites
    await asyncio.gather(*[crawler.crawling_sites(site) for site in sites])
    return

if __name__=='__main__':
    start = datetime.now()
    asyncio.run(main())
    print(f'{start} 크롤링 시작')
    print(f'{datetime.now()} 크롤링 종료')