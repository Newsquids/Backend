
import selenium
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException, ElementNotInteractableException, NoSuchAttributeException
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains, ChromeOptions
from datetime import datetime, timedelta
from webdriver_manager.chrome import ChromeDriverManager
import asyncio
# traditional : cnbc, bbc, reuters, (bloomberg, wsj)
# categories for lunch : world, tech, economy, environment, energy, politic
# cnbc's categories : world-markets, economy, technology, finance, health-and-science, politics,
# bbc's categories : world, business, technology, science_and_environment 
# reuters's categories : world, business, legal, markets

# crypto : coindesk, cointelegraph, cryptoslate
# categories for lunch : 
# coindesk's categories : markets, business, policy, tech, web3
# cointelegraph's categories : tags/defi, /nft, /regulation, /bitcoin, /ethereum, /altcoin, /business
# cryptoslate's categories : regulation, cbdcs, bankruptcy, analysis, defi, nfts, partnerships, exchanges, /news/bitcoin, /ethereum

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
            "cryptoslate" : ["regulation", "cbdcs", "bankruptcy", "analysis", "defi", "nfts", "partnerships", "exchanges", "news/bitcoin", "news/ethereum"]
        }

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
    
    def log_error(self, site:str, failed_link:str):
        with open(f"/Users/s/Desktop/Study/Toyproject/Newsquids/Backend/crawler/files/{site}/errors.txt","r") as f:
            read_file = f.read()
        tem = eval(read_file)
        tem.append(failed_link)
        with open(f"/Users/s/Desktop/Study/Toyproject/Newsquids/Backend/crawler/files/{site}/errors.txt","w") as f:
            f.write(str(tem))
        return

    def get_data_or_None(self, data):
        try:
            obj = data
        except NoSuchElementException:
            obj = None
        return obj

    def preprocess_time(self, site:str, link:str, time:str ):
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
        ops.add_argument("headless")
        web = selenium.webdriver.Chrome(ChromeDriverManager().install(), options=ops)
        tem_web = selenium.webdriver.Chrome(ChromeDriverManager().install(), options=ops)
        base_url = f"https://www.{site}.com"
        for category in self.sites_categories[site]:
            print(f'{site} : {category} 크롤링을 시작합니다.')
            url = base_url + f"/{category}"
            await asyncio.sleep(1)
            web.get(url)
            if site == 'cnbc':
                link_dict = self.get_dict_or_data(site=site, dict=True)
                titles = web.find_elements(By.CLASS_NAME,"Card-title")
                for title in titles:
                    data = self.get_dict_or_data(site=site)
                    link = title.get_attribute("href")
                    try:
                        link_dict[link]
                        print("이미 존재하는 주소입니다.")
                    except KeyError:
                        headline = title.text
                        link_dict[link] = 1
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
                        data.append([link,headline,image,time])
                        self.update_dict_or_data(site=site, data=str(link_dict), dict=True)
                        self.update_dict_or_data(site=site, data=str(data))
                        print(f"{site}의 {link} 크롤링 완료")
                        await asyncio.sleep(2.2)
            elif site == 'bbc':
                boxes = web.find_elements(By.CLASS_NAME,"gs-c-promo")
                link_dict = self.get_dict_or_data(site=site, dict=True)
                for box in boxes:
                    data = self.get_dict_or_data(site=site)
                    try:
                        link = box.find_element(By.TAG_NAME,'a').get_attribute("href")
                        if 'news' not in link or 'live' in link:
                            continue
                    except NoSuchElementException or NoSuchAttributeException:
                        continue
                    try:
                        link_dict[link]
                        print("이미 존재하는 주소입니다.")
                    except KeyError:
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
                        data.append([link,headline,image,time])
                        link_dict[link] = 1
                        self.update_dict_or_data(site=site, data=str(link_dict), dict=True)
                        self.update_dict_or_data(site=site, data=str(data))
                        print(f"{site}의 {link} 크롤링 완료")
                        await asyncio.sleep(3.2)
                    except WebDriverException:
                        self.log_error(site=site, failed_link=link)
                        print(f'{link} 크롤링 중 에러 발생')
            elif site == 'reuters':
                await asyncio.sleep(2)
                li_boxes = web.find_elements(By.CLASS_NAME,"story-card")
                link_dict = self.get_dict_or_data(site=site, dict=True)
                for box in li_boxes:
                    data = self.get_dict_or_data(site=site)
                    try:
                        link_element = box.find_element(By.CLASS_NAME,"media-story-card__heading__eqhp9")
                        link = link_element.get_attribute('href')
                        link_dict[link]
                        print("이미 존재하는 주소입니다.")
                    except NoSuchElementException or NoSuchAttributeException:
                        continue
                    except KeyError:
                        print(f"{site}의 {link} 크롤링 중...")
                        action = ActionChains(web)
                        action.move_to_element(link_element)
                        action.perform()
                        try:
                            tem_web.get(link)
                        except TimeoutException:
                            continue
                        await asyncio.sleep(2)
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
                        data.append([link,headline,image,time])
                        link_dict[link] = 1
                        self.update_dict_or_data(site=site, data=str(link_dict), dict=True)
                        self.update_dict_or_data(site=site, data=str(data))
                        print(f"{site}의 {link} 크롤링 완료")
                    except TimeoutException:
                        print(f'{link}에서 에러가 발생했습니다')
                        self.log_error(site=site, failed_link=link)
                        continue
            elif site == "coindesk":
                link_dict = self.get_dict_or_data(site=site, dict=True)
                data = self.get_dict_or_data(site=site)
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
                        link_dict[link]
                        print("이미 존재하는 주소입니다.")
                        continue
                    except NoSuchAttributeException:
                        continue
                    except KeyError:
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
                        data.append([link,headline,image,time])
                        link_dict[link] = 1
                        self.update_dict_or_data(site=site, data=str(link_dict), dict=True)
                        self.update_dict_or_data(site=site, data=str(data))
                        print(f"{site}의 {link} 크롤링 완료")
                    except TimeoutException:
                        print(f'{link}에서 에러가 발생했습니다')
                        self.log_error(site=site, failed_link=link)
                        continue
            elif site == "cointelegraph":
                link_dict = self.get_dict_or_data(site=site, dict=True)
                data = self.get_dict_or_data(site=site)
                await asyncio.sleep(3)
                web.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                await asyncio.sleep(2)
                boxes = web.find_elements(By.CLASS_NAME,"posts-listing__item")
                action = ActionChains(web)
                for box in boxes:
                    link = box.find_element(By.TAG_NAME, "a").get_attribute("href")
                    try:
                        link_dict[link]
                        print("이미 존재하는 주소입니다.")
                        continue
                    except KeyError:
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
                        data.append([link,headline,image,time])
                        link_dict[link] = 1
                        self.update_dict_or_data(site=site, data=str(link_dict), dict=True)
                        self.update_dict_or_data(site=site, data=str(data))
                        print(f"{site}의 {link} 크롤링 완료")
                    except TimeoutException or WebDriverException:
                        print(f'{link}에서 에러가 발생했습니다')
                        self.log_error(site=site, failed_link=link)
                        continue
            elif site == "cryptoslate":
                link_dict = self.get_dict_or_data(site=site, dict=True)
                data = self.get_dict_or_data(site=site)
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
                    try:
                        link_dict[link]
                        print("이미 존재하는 주소입니다.")
                        continue
                    except KeyError:
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
                        data.append([link,headline,image,time])
                        link_dict[link] = 1
                        self.update_dict_or_data(site=site, data=str(link_dict), dict=True)
                        self.update_dict_or_data(site=site, data=str(data))
                        print(f"{site}의 {link} 크롤링 완료")
                    except TimeoutException or WebDriverException:
                        print(f'{link}에서 에러가 발생했습니다')
                        self.log_error(site=site, failed_link=link)
                        continue
                await asyncio.sleep(2.6)
        web.quit()
        tem_web.quit()
        print(f'{site}의 크롤링 완료')
        return

async def main ():
    crawler = Crawl()
    sites = crawler.all_sites
    sites = sites[4:]
    await asyncio.gather(*[crawler.crawling_sites(site) for site in sites])
    return

start = datetime.now()
asyncio.run(main())
print(f'{start} 크롤링 시작')
print(f'{datetime.now()} 크롤링 종료')