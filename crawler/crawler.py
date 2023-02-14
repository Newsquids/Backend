import selenium, time, datetime
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
import random, asyncio

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

class Crawler:
    def __init__(self) -> None:
        self.traditional_sites = ["cnbc", "bbc", "reuters"]
        self.crypto_sites = ["coindesk", "cointelegraph", "cryptoslate"]
        self.sites_categories = {
            "cnbc" : ["world-markets", "economy", "technology", "finance", "health-and-science", "politics"],
            "bbc" : ["news/world", "news/business", "news/technology", "news/science_and_environment", "news/health" ],
            "reuters" : ["world", "business", "legal", "markets"],
            "coindesk" : ["markets", "business", "policy", "tech", "web3"],
            "cointelegraph" : ["tags/defi", "tags/nft", "tags/regulation", "tags/bitcoin", "tags/ethereum", "tags/altcoin", "tags/business"],
            "cryptoslate" : ["regulation", "cbdcs", "bankruptcy", "analysis", "defi", "nfts", "partnerships", "exchanges", "news/bitcoin", "news/ethereum"]
        }

    def get_link_dict(self, site:str):
        with open(f"/Users/s/Desktop/Study/Toyproject/Newsquids/Crawler/files/{site}/links.txt","r") as f:
            read_file = f.read()
        return eval(read_file)

    def update_link_dict(self, site:str, data:str):
        with open(f"/Users/s/Desktop/Study/Toyproject/Newsquids/Crawler/files/{site}/links.txt","w") as f:
            f.write(data)
        return
    
    def log_error(self, site:str, failed_link:str):
        with open(f"/Users/s/Desktop/Study/Toyproject/Newsquids/Crawler/files/{site}/errors.txt","r") as f:
            read_file = f.read()
        tem = eval(read_file)
        tem.append(failed_link)
        with open(f"/Users/s/Desktop/Study/Toyproject/Newsquids/Crawler/files/{site}/errors.txt","w") as f:
            f.write(str(tem))
        return


crawler = Crawler()

async def crawling_sites(site:str):
    web = selenium.webdriver.Chrome()
    tem_web = selenium.webdriver.Chrome()
    base_url = f"https://www.{site}.com"
    for category in crawler.sites_categories[site]:
        print(f'{site} : {category} 크롤링을 시작합니다.')
        url = base_url + f"/{category}"
        await asyncio.sleep(1)
        web.get(url)
        if site == 'cnbc':
            titles = web.find_elements(By.CLASS_NAME,"Card-title")
            for title in titles:
                link_dict = crawler.get_link_dict(site=site)
                link = title.get_attribute("href")
                try:
                    link_dict[link]
                    print("이미 존재하는 주소입니다.")
                except KeyError:
                    headline = title.text
                    link_dict[link] = [headline]
                    print(f"{site}의 {link} 크롤링 중...")
                    tem_web.get(link)
                    tem_web.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    await asyncio.sleep(4.6)
                    try:
                        image = tem_web.find_element(By.TAG_NAME, "picture")
                        image_src = image.find_element(By.TAG_NAME,"img").get_attribute("src")
                    except NoSuchElementException:
                        image_src = None
                    time_obj = tem_web.find_elements(By.TAG_NAME, "time")
                    for t in time_obj: 
                        pub_time = t.get_attribute("datetime")
                        if pub_time == None:
                            pub_time = f'{t.text}T{t.find_element(By.TAG_NAME, "span").text}'
                        break
                    contexts = []
                    for group in tem_web.find_elements(By.CLASS_NAME,"group"):
                        for context in group.find_elements(By.TAG_NAME,"p"):
                            if context.text != '':
                                contexts.append(context.text)
                    link_dict[link].append(image_src)
                    link_dict[link].append(pub_time)
                    link_dict[link].append(contexts)
                    print(f"{site}의 {link} 크롤링 완료")
                    crawler.update_link_dict(site=site, data=str(link_dict))
                    await asyncio.sleep(4.2)
        elif site == 'bbc':
            boxes = web.find_elements(By.CLASS_NAME,"gs-c-promo")
            for box in boxes:
                link_dict = crawler.get_link_dict(site=site)
                try:
                    link = box.find_element(By.TAG_NAME,'a').get_attribute("href")
                except NoSuchElementException:
                    continue
                if 'news' not in link or 'live' in link:
                    continue
                try:
                    link_dict[link]
                    print("이미 존재하는 주소입니다.")
                except KeyError:
                    headline = box.find_element(By.TAG_NAME,'h3').text
                    link_dict[link] = [headline]
                    print(f"{site}의 {link} 크롤링 중...")
                    tem_web.get(link)
                    tem_web.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    await asyncio.sleep(2.4)
                    try:
                        image = tem_web.find_element(By.TAG_NAME, "img").get_attribute('src')
                    except NoSuchElementException:
                        image = ''
                    try:
                        pub_time = tem_web.find_element(By.TAG_NAME,'time').get_attribute("datetime")
                    except NoSuchElementException:
                        pub_time = None
                    tem_contexts = []
                    contexts = tem_web.find_elements(By.CLASS_NAME,'ep2nwvo0')
                    for context in contexts:
                        tem_contexts.append(context.text)
                    link_dict[link].append(image)
                    link_dict[link].append(pub_time)
                    link_dict[link].append(tem_contexts)
                    crawler.update_link_dict(site=site, data=str(link_dict))
                    print(f"{site}의 {link} 크롤링 완료")
                except WebDriverException:
                    crawler.log_error(site=site, failed_link=link)
                    print(f'{link} 크롤링 중 에러 발생')
                await asyncio.sleep(3.5)
        elif site == 'reuters':
            await asyncio.sleep(3)
            link_dict = crawler.get_link_dict(site=site)
            li_boxes = web.find_elements(By.CLASS_NAME,"story-card")
            for box in li_boxes:
                try:
                    link_element = box.find_element(By.CLASS_NAME,"media-story-card__heading__eqhp9")
                    link = link_element.get_attribute('href')
                    action = ActionChains(web)
                    action.move_to_element(link_element)
                    action.perform()
                except NoSuchElementException:
                    continue
                try:
                    link_dict[link]
                    print("이미 존재하는 주소입니다.")
                    continue
                except KeyError:
                    print(f"{site}의 {link} 크롤링 중...")
                    tem_web.get(link)
                    await asyncio.sleep(3)
                    headline = tem_web.find_element(By.TAG_NAME,"h1").text
                    pub_times = tem_web.find_element(By.TAG_NAME,"time").find_elements(By.TAG_NAME,'span')
                    pub_time = pub_times[1].text + pub_times[2].text
                    try:
                        image = box.find_element(By.TAG_NAME, "img").get_attribute('src')
                    except NoSuchElementException:
                        image = None
                    link_dict[link] = [headline,image,pub_time,[]]
                    crawler.update_link_dict(site=site, data=str(link_dict))
                    print(f"{site}의 {link} 크롤링 완료")
                except TimeoutException:
                    print(f'{link}에서 에러가 발생했습니다')
                    crawler.log_error(site=site, failed_link=link)
                    continue
        elif site == "coindesk":
            1
    print(f'{site}의 크롤링 완료')
    return

year = datetime.datetime.now().year
month = datetime.datetime.now().month
day = datetime.datetime.now().day


# for site in crypto_sites:
#     base_url = f"https://www.{site}.com"
#     for category in sites_categories[site]:
#         url = base_url + f"/{category}"
#         time.sleep(1)
#         web.get(url)
#         time.sleep(3)
#     break

asyncio.run(crawling_sites("coindesk"))