from celery import shared_task
from datetime import datetime
from crawler.crawler import Crawl
import asyncio


@shared_task
def crawling_site():
    crawler = Crawl()
    sites = crawler.all_sites
    crawling = crawler.crawling_sites
    for site in sites:
        asyncio.run(crawling(site=site))
    return